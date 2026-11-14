"""Exercise real SDK serialization over an in-memory HTTP transport, with no network."""
import asyncio
import json
from unittest.mock import AsyncMock

import httpx
import pytest
from google import genai

from app.services import providers
from app.services import lesson_ai
from app.services.providers import request_gemini
from app.services.lesson_ai import EVALUATION_GROUPS, LessonAI, WorkflowError
from app.dataset import BASE
from app.content import MODEL_CHECK_IDS, PROMPTS, RUBRIC, SOURCE_PACK
from app.lesson_schemas import Lesson

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
        payload = json.loads(body["contents"][0]["parts"][0]["text"].split("\n", 1)[1])
        assert payload["approved_source_claim_mappings"]["S3"] == ["C03", "C04"]
        assert "P01" in payload["approved_source_claim_mappings"]["S4"]
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
        payload = json.loads(requests[-1]["contents"][0]["parts"][0]["text"].split("\n", 1)[1])
        raw["checks"] = [item for item in raw["checks"] if item["check_id"] in payload["expected_check_ids"]]
        if len(requests) == 1:
            raw["checks"].pop()
        return model_response(raw)

    install_transport(monkeypatch, handle)
    retries = []
    raw, usage = asyncio.run(real_evaluate(LessonAI(settings), BASE, SOURCE_PACK, RUBRIC, on_retry=lambda n, code: retries.append(code)))
    assert len(requests) == 4
    assert retries == ["INVALID_EVALUATION"]
    assert len(raw["checks"]) == 12
    assert len(usage["group_usage"]) == 3
    assert len(usage["group_usage"][0]["attempt_usage"]) == 2
    assert [item["check_ids"] for item in usage["group_usage"]] == [list(group) for group in EVALUATION_GROUPS]
    json.dumps(usage)  # No recursive structures enter SQLite.
    assert requests[0]["generationConfig"]["thinkingConfig"]["thinking_level"] == "MEDIUM"
    payload = json.loads(requests[0]["contents"][0]["parts"][0]["text"].split("\n", 1)[1])
    assert "demo_error" not in payload
    assert "generator_prompt" not in payload


@pytest.mark.parametrize("retry_limit", [0, 1, 2])
def test_incomplete_group_never_returns_partial_approval(settings, monkeypatch, retry_limit):
    settings.technical_retries = retry_limit
    calls = []

    async def partial_call(self, model, instructions, data, schema, **kwargs):
        calls.append(data["expected_check_ids"])
        checks = [item for item in model_checks()["checks"] if item["check_id"] in data["expected_check_ids"]]
        if len(calls) > 1:
            checks.pop()
        return {"checks": checks}, {}

    monkeypatch.setattr(LessonAI, "call", partial_call)
    with pytest.raises(WorkflowError, match="INVALID_EVALUATION") as error:
        asyncio.run(real_evaluate(LessonAI(settings), BASE, SOURCE_PACK, RUBRIC))
    assert len(error.value.diagnostics["completed_checks"]) == 4
    assert error.value.diagnostics["incomplete_group"] == list(EVALUATION_GROUPS[1])
    assert calls == [list(EVALUATION_GROUPS[0])] + [list(EVALUATION_GROUPS[1])] * (retry_limit + 1)
    assert len({key for group in EVALUATION_GROUPS for key in group}) == len(MODEL_CHECK_IDS) == 12


def test_daily_quota_is_not_retried_and_exposes_only_safe_recovery_details(settings, monkeypatch):
    settings.gemini_api_key = "fake-test-key"
    requests = []

    def handle(request):
        requests.append(request)
        return httpx.Response(429, json={"error": {"code": 429, "status": "RESOURCE_EXHAUSTED", "message": "private fake-test-key",
            "details": [{"@type": "type.googleapis.com/google.rpc.QuotaFailure", "violations": [{
                "quotaMetric": "generate_content_free_tier_requests", "quotaId": "GenerateRequestsPerDayPerProjectPerModel-FreeTier",
                "quotaValue": "20", "quotaDimensions": {"private_project": "do-not-export"}}]},
                {"@type": "type.googleapis.com/google.rpc.RetryInfo", "retryDelay": "4651s"}]}})

    install_transport(monkeypatch, handle)
    with pytest.raises(WorkflowError) as error:
        asyncio.run(LessonAI(settings).call("gemini-3.5-flash", "Test", {}, Lesson))
    assert error.value.code == "RATE_LIMIT_OR_QUOTA"
    assert error.value.diagnostics["retry_after_seconds"] == 4651
    assert error.value.diagnostics["quota_limits"][0]["quotaValue"] == "20"
    assert len(requests) == 1
    assert "fake-test-key" not in json.dumps(error.value.public())
    assert "do-not-export" not in json.dumps(error.value.public())


@pytest.mark.parametrize("recovers", [True, False])
def test_busy_generation_has_bounded_backoff_and_keeps_its_model_and_schema(settings, monkeypatch, recovers):
    settings.gemini_api_key = "fake-test-key"
    settings.gemini_model = "gemini-3.5-flash-lite"
    settings.technical_retries = 2
    requests = []
    pause = AsyncMock()
    monkeypatch.setattr(lesson_ai.asyncio, "sleep", pause)
    monkeypatch.setattr(lesson_ai.random, "uniform", lambda low, high: 0.5)

    def handle(request):
        requests.append(json.loads(request.content))
        if recovers and len(requests) == 3:
            return model_response(BASE)
        return httpx.Response(503, json={"error": {"code": 503, "status": "UNAVAILABLE", "message": "private diagnostic"}})

    install_transport(monkeypatch, handle)
    retries = []
    run = real_generate(LessonAI(settings), {"topic": "Introduction to RAG", "source_pack": SOURCE_PACK, "instructions": PROMPTS["generator"]}, on_retry=lambda n, code: retries.append((n, code)))
    if recovers:
        draft, _ = asyncio.run(run)
        assert draft["title"] == BASE["title"]
    else:
        with pytest.raises(WorkflowError) as error:
            asyncio.run(run)
        assert error.value.code == "SERVICE_UNAVAILABLE"
        assert error.value.diagnostics["provider_http_status"] == 503
    assert len(requests) == 3
    assert all(body == requests[0] for body in requests)
    assert retries == [(1, "SERVICE_UNAVAILABLE"), (2, "SERVICE_UNAVAILABLE")]
    assert [call.args[0] for call in pause.await_args_list] == [4.5, 8.5]


def test_evaluator_busy_retry_keeps_native_schema_and_does_not_claim_format_error(settings, monkeypatch):
    settings.gemini_api_key = "fake-test-key"
    settings.gemini_model = "gemini-3.5-flash"
    requests = []
    monkeypatch.setattr(lesson_ai.asyncio, "sleep", AsyncMock())

    def handle(request):
        body = json.loads(request.content)
        requests.append(body)
        if len(requests) == 1:
            return httpx.Response(503, json={"error": {"code": 503, "status": "UNAVAILABLE"}})
        payload = json.loads(body["contents"][0]["parts"][0]["text"].split("\n", 1)[1])
        return model_response({"checks": [item for item in model_checks()["checks"] if item["check_id"] in payload["expected_check_ids"]]})

    install_transport(monkeypatch, handle)
    raw, _ = asyncio.run(real_evaluate(LessonAI(settings), BASE, SOURCE_PACK, RUBRIC))
    assert len(raw["checks"]) == 12
    assert len(requests) == 4
    assert requests[0] == requests[1]
    assert all("responseJsonSchema" in body["generationConfig"] for body in requests)


def test_long_provider_backoff_is_returned_without_a_background_retry(settings, monkeypatch):
    settings.gemini_api_key = "fake-test-key"
    requests = []

    def handle(request):
        requests.append(request)
        return httpx.Response(503, json={"error": {"code": 503, "status": "UNAVAILABLE", "details": [
            {"@type": "type.googleapis.com/google.rpc.RetryInfo", "retryDelay": "120s"}]}})

    install_transport(monkeypatch, handle)
    with pytest.raises(WorkflowError) as error:
        asyncio.run(LessonAI(settings).call("gemini-3.5-flash", "Test", {}, Lesson))
    assert error.value.diagnostics["retry_after_seconds"] == 120
    assert len(requests) == 1


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
