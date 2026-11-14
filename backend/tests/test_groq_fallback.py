"""Quota failover over an in-memory Groq HTTP transport; no paid requests."""
import asyncio
import copy
import json
import time
from unittest.mock import AsyncMock

import httpx
import pytest
from fastapi.testclient import TestClient

from app.content import MODEL_CHECK_IDS, RUBRIC, SOURCE_PACK
from app.dataset import BASE
from app.lesson_schemas import Lesson, RunRequest
from app.main import create_app
from app.services import groq, lesson_ai
from app.services.lesson_ai import EVALUATION_GROUPS, LessonAI, WorkflowError

REAL_GENERATE, REAL_EVALUATE = LessonAI.generate, LessonAI.evaluate
REAL_GROQ_REQUEST = groq.request_groq
REAL_HTTP_CLIENT = httpx.AsyncClient


def checks(ids):
    return {"checks": [{"check_id": key, "passed": True, "evidence": BASE["title"],
                        "reason": "Mocked fallback test judgment.", "required_change": "",
                        "claim_ids": [], "missing_content": False, "evidence_path": ""} for key in ids]}


def response(value, model="qwen/qwen3.8-27b"):
    return httpx.Response(200, json={"model": model, "choices": [{"message": {"content": json.dumps(value)}, "finish_reason": "stop"}],
                                    "usage": {"prompt_tokens": 300, "completion_tokens": 200, "total_tokens": 500}})


@pytest.fixture
def fallback(settings, monkeypatch):
    settings.gemini_api_key = "fake-gemini-key"
    settings.gemini_model = "gemini-test-generator"
    settings.gemini_evaluator_model = "gemini-test-evaluator"
    settings.groq_api_key = "fake-groq-key"
    settings.groq_min_interval_seconds = 0
    settings.technical_retries = 0
    primary = AsyncMock(side_effect=WorkflowError("RATE_LIMIT_OR_QUOTA", "Gemini limit reached.", {
        "provider": "gemini", "provider_http_status": 429, "retry_after_seconds": 3600}))
    monkeypatch.setattr(LessonAI, "_call_gemini", primary)
    monkeypatch.setattr(LessonAI, "generate", REAL_GENERATE)
    monkeypatch.setattr(LessonAI, "evaluate", REAL_EVALUATE)
    monkeypatch.setattr(groq, "request_groq", REAL_GROQ_REQUEST)
    def unexpected_request(request):
        raise AssertionError("Unexpected HTTP request in a no-network test.")
    wire(monkeypatch, unexpected_request)
    return settings, primary


def wire(monkeypatch, handler):
    def client(**kwargs):
        return REAL_HTTP_CLIENT(**kwargs, transport=httpx.MockTransport(handler))
    monkeypatch.setattr(groq.httpx, "AsyncClient", client)


def test_quota_fallback_caches_per_model_and_returns_to_gemini_after_reset(fallback, monkeypatch):
    settings, primary = fallback
    primary.side_effect = [WorkflowError("RATE_LIMIT_OR_QUOTA", "Gemini limit reached.", {"retry_after_seconds": 3600}), (BASE, {})]
    requests, events = [], []
    clock = [1000]
    monkeypatch.setattr(lesson_ai.time, "time", lambda: clock[0])

    def handle(request):
        assert request.url == groq.ENDPOINT
        assert request.headers["Authorization"] == "Bearer fake-groq-key"
        body = json.loads(request.content)
        assert body["model"] == settings.groq_model
        assert "thinking_config" not in body
        assert body["response_format"]["json_schema"]["strict"] is True
        assert "required_output_schema" not in body["messages"][1]["content"]
        requests.append(body)
        return response(BASE)

    wire(monkeypatch, handle)
    ai = LessonAI(settings)

    async def run():
        for _ in range(2):
            _, usage = await ai.call(ai.generator_model, "Return JSON", {}, Lesson, on_provider_event=events.append)
            assert usage["provider"] == "groq" and usage["fallback"] is True
        assert primary.await_count == 1
        clock[0] = 5000
        _, usage = await ai.call(ai.generator_model, "Return JSON", {}, Lesson)
        assert usage["provider"] == "gemini" and usage["fallback"] is False

    asyncio.run(run())
    assert len(requests) == 2
    assert primary.await_count == 2
    assert sum(event["type"] == "PROVIDER_FALLBACK" for event in events) == 2


@pytest.mark.parametrize("code", ["INVALID_CREDENTIALS", "SERVICE_UNAVAILABLE", "MALFORMED_OUTPUT", "INVALID_EVIDENCE", "NOT_CONFIGURED"])
def test_non_quota_failures_never_switch_to_groq(fallback, code):
    settings, primary = fallback
    primary.side_effect = WorkflowError(code, "Mocked primary failure.")
    with pytest.raises(WorkflowError) as error:
        asyncio.run(LessonAI(settings).call(settings.gemini_model, "Test", {}, Lesson))
    assert error.value.code == code
    assert primary.await_count == 1


@pytest.mark.parametrize("missing_key", [True, False])
def test_missing_key_or_disabled_fallback_does_not_make_a_groq_request(fallback, missing_key):
    settings, primary = fallback
    if missing_key:
        settings.groq_api_key = None
    else:
        settings.groq_fallback_enabled = False
    with pytest.raises(WorkflowError) as error:
        asyncio.run(LessonAI(settings).call(settings.gemini_model, "Test", {}, Lesson))
    assert error.value.code == "RATE_LIMIT_OR_QUOTA"
    assert error.value.diagnostics["fallback_configured"] is False
    assert primary.await_count == 1


@pytest.mark.parametrize("status,code", [(401, "INVALID_CREDENTIALS"), (429, "RATE_LIMIT_OR_QUOTA")])
def test_secondary_key_and_quota_failures_stop_without_bouncing_between_providers(fallback, monkeypatch, status, code):
    settings, primary = fallback
    requests = []

    def handle(request):
        requests.append(request)
        return httpx.Response(status, json={"error": {"message": "private fake-groq-key"}})

    wire(monkeypatch, handle)
    with pytest.raises(WorkflowError) as error:
        asyncio.run(LessonAI(settings).call(settings.gemini_model, "Test", {}, Lesson))
    assert error.value.code == code
    assert error.value.diagnostics["provider"] == "groq"
    assert "fake-groq-key" not in json.dumps(error.value.public())
    assert len(requests) == primary.await_count == 1


@pytest.mark.parametrize("invalid_boolean", [False, True])
def test_full_workflow_persists_actual_providers_and_rejects_invalid_groq_verdicts(fallback, monkeypatch, invalid_boolean):
    settings, primary = fallback
    requests = []

    def handle(request):
        body = json.loads(request.content)
        payload = json.loads(body["messages"][1]["content"].split("\n", 1)[1])
        requests.append(body)
        if "expected_check_ids" in payload:
            result = checks(payload["expected_check_ids"])
            if invalid_boolean:
                result["checks"][0]["passed"] = "true"
            shape = body["response_format"]["json_schema"]["schema"]["properties"]["checks"]["items"]
            assert shape["additionalProperties"] is False
            assert "evidence_path" in shape["required"]
            return response(result)
        assert "required_structure" not in payload
        return response(BASE)

    wire(monkeypatch, handle)
    with TestClient(create_app(settings=settings, ai=LessonAI(settings))) as client:
        run_id = client.post("/api/runs", json={}).json()["id"]
        for _ in range(100):
            run = client.get("/api/runs/" + run_id).json()
            if run["status"] != "RUNNING":
                break
        assert run["attempts"][0]["generation_usage"]["provider"] == "groq"
        assert run["generator_model"] == settings.gemini_model  # Configured primary snapshot.
        if invalid_boolean:
            assert run["status"] == "ERROR" and run["final_lesson"] is None
            assert run["error"]["code"] == "INVALID_EVALUATION"
        else:
            assert run["status"] == "APPROVED"
            assert len(run["attempts"][0]["evaluation"]) == 14
            assert all(item["provider"] == "groq" for item in run["attempts"][0]["evaluator_usage"]["group_usage"])
            audit = client.get(f"/api/runs/{run_id}/export?format=json").json()
            assert audit["audit_version"] == "lessonloop-audit-v2"
            assert any(event["stage"] == "PROVIDER_FALLBACK" for event in audit["events"])
            assert run["providers_used"] == [{"provider": "groq", "model": settings.groq_model}]
        assert "fake-groq-key" not in json.dumps(run)
        assert "fake-gemini-key" not in json.dumps(run)
    assert primary.await_count == 2  # Separate generator/evaluator quota caches.


def test_groq_requests_are_paced_and_both_keys_are_redacted(fallback, monkeypatch):
    settings, _ = fallback
    settings.groq_min_interval_seconds = 65
    pauses = AsyncMock()
    monkeypatch.setattr(lesson_ai.asyncio, "sleep", pauses)
    draft = copy.deepcopy(BASE)
    draft["why_it_matters"] += " fake-gemini-key fake-groq-key"
    wire(monkeypatch, lambda request: response(draft))
    ai = LessonAI(settings)
    events = []

    async def run():
        await ai.call(ai.generator_model, "Test", {}, Lesson)
        ai._groq_last_request[settings.groq_model] = time.monotonic() - 5
        value, _ = await ai.call(ai.generator_model, "Test", {}, Lesson, on_provider_event=events.append)
        assert "fake-gemini-key" not in json.dumps(value)
        assert "fake-groq-key" not in json.dumps(value)

    asyncio.run(run())
    assert any(59 < call.args[0] <= 60 for call in pauses.await_args_list)
    assert any(event["type"] == "PROVIDER_WAIT" for event in events)


def test_evaluator_quota_does_not_disable_a_healthy_generator(fallback, monkeypatch):
    settings, primary = fallback

    async def gemini(model, *args, **kwargs):
        if model == settings.gemini_evaluator_model:
            raise WorkflowError("RATE_LIMIT_OR_QUOTA", "Mocked evaluator quota.", {"retry_after_seconds": 3600})
        return BASE, {}

    primary.side_effect = gemini
    wire(monkeypatch, lambda request: response(checks(EVALUATION_GROUPS[0])))
    ai = LessonAI(settings)

    async def run():
        await ai.evaluate_group(BASE, SOURCE_PACK, RUBRIC, EVALUATION_GROUPS[0])
        _, usage = await ai.generate({"topic": "Introduction to RAG", "source_pack": SOURCE_PACK, "instructions": "Test"})
        assert usage["provider"] == "gemini"

    asyncio.run(run())
