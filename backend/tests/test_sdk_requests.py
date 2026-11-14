"""Exercise real SDK serialization over an in-memory HTTP transport, with no network."""
import asyncio
import json

import httpx
from google import genai

from app.services import providers
from app.services.providers import request_gemini
from app.services.lesson_ai import LessonAI
from app.dataset import BASE
from app.content import MODEL_CHECK_IDS, PROMPTS, RUBRIC, SOURCE_PACK

# Retain the real methods before the autouse no-network fixture patches public role calls.
real_generate = LessonAI.generate
real_evaluate = LessonAI.evaluate


def install_transport(monkeypatch, handler):
    original = genai.Client

    def client(**kwargs):
        kwargs["http_options"].async_client_args = {"transport": httpx.MockTransport(handler)}
        return original(**kwargs)

    monkeypatch.setattr(genai, "Client", client)


def model_response(data):
    return httpx.Response(200, json={"candidates": [{"content": {"role": "model", "parts": [{"text": json.dumps(data)}]}, "finishReason": "STOP"}], "usageMetadata": {"promptTokenCount": 10, "candidatesTokenCount": 10, "totalTokenCount": 20}})


def model_checks():
    return {"checks": [{"check_id": key, "passed": True, "evidence": BASE["title"], "reason": "Mocked SDK test judgment.", "required_change": "", "claim_ids": [], "missing_content": False} for key in MODEL_CHECK_IDS]}


def test_workflow_schema_argument_fallback_is_bounded_and_same_model(settings, monkeypatch):
    settings.gemini_api_key = "fake-test-key"
    settings.gemini_model = "gemini-3.5-flash-lite"
    requests = []

    def handle(request):
        body = json.loads(request.content)
        requests.append(body)
        if len(requests) == 1:
            assert "responseJsonSchema" in body["generationConfig"]
            return httpx.Response(400, json={"error": {"code": 400, "status": "INVALID_ARGUMENT", "message": "Mocked schema rejection"}})
        assert "responseJsonSchema" not in body["generationConfig"]
        assert body["generationConfig"]["responseMimeType"] == "application/json"
        assert "required_output_schema" in body["contents"][0]["parts"][0]["text"]
        return model_response(BASE)

    install_transport(monkeypatch, handle)
    retries = []
    ai = LessonAI(settings)
    lesson, usage = asyncio.run(real_generate(ai, {"topic": "Introduction to RAG", "source_pack": SOURCE_PACK, "instructions": PROMPTS["generator"], "memory": []}, on_retry=lambda n, code: retries.append(code)))
    assert len(requests) == 2
    assert retries == ["SCHEMA_JSON_MODE_RETRY"]
    assert lesson["title"] == BASE["title"]


def test_evaluator_repairs_format_once_and_preserves_usage(settings, monkeypatch):
    settings.gemini_api_key = "fake-test-key"
    settings.gemini_model = "gemini-3.5-flash-lite"
    requests = []

    def handle(request):
        requests.append(json.loads(request.content))
        raw = model_checks()
        if len(requests) == 1:
            raw["checks"].pop()
        return model_response(raw)

    install_transport(monkeypatch, handle)
    retries = []
    raw, usage = asyncio.run(real_evaluate(LessonAI(settings), BASE, SOURCE_PACK, RUBRIC, on_retry=lambda n, code: retries.append(code)))
    assert len(requests) == 2
    assert retries == ["INVALID_EVALUATION"]
    assert len(raw["checks"]) == 12
    assert len(usage["attempt_usage"]) == 2
    json.dumps(usage)  # No recursive structures enter SQLite.
    assert requests[0]["generationConfig"]["thinkingConfig"]["thinking_level"] == "MEDIUM"
    payload = json.loads(requests[0]["contents"][0]["parts"][0]["text"].split("\n", 1)[1])
    assert "demo_error" not in payload
    assert "generator_prompt" not in payload


def test_gemini_sdk_uses_configured_model_and_no_retries(monkeypatch):
    requests = []
    original_client = genai.Client

    def handle(request):
        requests.append(request)
        assert request.url.path.endswith("/models/gemini-3.5-flash-lite:generateContent")
        body = json.loads(request.content)
        assert body["generationConfig"]["maxOutputTokens"] == 64
        return httpx.Response(200, json={"candidates": [{"content": {"role": "model", "parts": [{"text": "SDK connection OK"}]}, "finishReason": "STOP"}]})

    def client(**kwargs):
        options = kwargs["http_options"]
        assert options.timeout == 5000
        assert options.retry_options.attempts == 1
        options.async_client_args = {"transport": httpx.MockTransport(handle)}
        return original_client(**kwargs)

    monkeypatch.setattr(providers.genai, "Client", client)
    assert asyncio.run(request_gemini("fake-key", "gemini-3.5-flash-lite", 5)) == "SDK connection OK"
    assert len(requests) == 1
