import asyncio
import copy
import json
from unittest.mock import AsyncMock

import httpx
import pytest
from fastapi.testclient import TestClient

from app.dataset import BASE
from app.lesson_schemas import Lesson
from app.main import create_app
from app.services import freellm
from app.services.lesson_ai import LessonAI, WorkflowError

REAL_REQUEST = freellm.request_freellm
REAL_CLIENT = httpx.AsyncClient
REAL_GENERATE, REAL_EVALUATE = LessonAI.generate, LessonAI.evaluate


def setup(settings, monkeypatch, code="RATE_LIMIT_OR_QUOTA"):
    settings.gemini_api_key = "fake-primary-key"
    settings.gemini_model = settings.gemini_evaluator_model = "mocked-primary"
    settings.groq_api_key = "fake-groq-key"
    settings.freellm_api_key = "fake-local-router-key"
    settings.technical_retries = 0
    monkeypatch.setattr(LessonAI, "_call_gemini", AsyncMock(side_effect=WorkflowError("RATE_LIMIT_OR_QUOTA", "Mocked quota")))
    backup = AsyncMock(side_effect=WorkflowError(code, "Mocked Groq failure", {"provider_error_code": "json_validate_failed"} if code == "INVALID_REQUEST" else None))
    monkeypatch.setattr(LessonAI, "_call_groq", backup)
    monkeypatch.setattr(freellm, "request_freellm", REAL_REQUEST)
    return backup


def wire(monkeypatch, handler):
    monkeypatch.setattr(freellm.httpx, "AsyncClient", lambda **kwargs: REAL_CLIENT(**kwargs, transport=httpx.MockTransport(handler)))


@pytest.mark.parametrize("code", ["RATE_LIMIT_OR_QUOTA", "OUTPUT_TRUNCATED", "CONNECTION_ERROR", "INVALID_REQUEST"])
def test_local_router_completes_workflow_after_groq_failure_without_repeating_groq(settings, monkeypatch, code):
    groq = setup(settings, monkeypatch, code)
    monkeypatch.setattr(LessonAI, "generate", REAL_GENERATE)
    monkeypatch.setattr(LessonAI, "evaluate", REAL_EVALUATE)
    requests = []
    def handler(request):
        assert str(request.url) == "http://127.0.0.1:31415/v1/chat/completions"
        assert request.headers["authorization"] == "Bearer fake-local-router-key"
        body = json.loads(request.content)
        payload = json.loads(body["messages"][1]["content"].split("\n", 1)[1])
        assert body["model"] == "auto" and body["response_format"] == {"type": "json_object"}
        assert body["max_tokens"] == settings.freellm_max_output_tokens == 8192
        assert "required_output_schema" in payload
        requests.append(body)
        if "expected_check_ids" in payload:
            value = {"checks": [{"check_id": key, "passed": True, "evidence": BASE["title"], "reason": "Mocked local-router verdict.", "required_change": "", "claim_ids": [], "missing_content": False} for key in payload["expected_check_ids"]]}
        else:
            value = copy.deepcopy(BASE)
            value["why_it_matters"] += " fake-primary-key fake-groq-key fake-local-router-key"
        return httpx.Response(200, json={"model": "reported/router-model", "choices": [{"finish_reason": "stop", "message": {"content": json.dumps(value)}}], "usage": {"total_tokens": 200}})
    wire(monkeypatch, handler)
    with TestClient(create_app(settings=settings)) as client:
        ident = client.post('/api/runs', json={"reference_pack_id": "rag-primary-v1"}).json()['id']
        for _ in range(300):
            run = client.get('/api/runs/' + ident).json()
            if run['status'] != 'RUNNING': break
        assert run['status'] == 'APPROVED'
        assert len(run['attempts'][0]['evaluation']) == 14
        assert run['providers_used'] == [{"provider": "freellm", "model": "reported/router-model"}]
        assert len(requests) == 4 and groq.await_count == 1
        assert not any(key in json.dumps(run) for key in ['fake-primary-key', 'fake-groq-key', 'fake-local-router-key'])
        events = client.get('/api/runs/' + ident + '/events').json()['events']
        assert any(e['details'].get('provider') == 'freellm' and 'freellm' in e['message'] for e in events)


@pytest.mark.parametrize("status,finish,content,code", [(401, "stop", "{}", "INVALID_CREDENTIALS"), (429, "stop", "{}", "RATE_LIMIT_OR_QUOTA"), (200, "length", "{}", "OUTPUT_TRUNCATED"), (200, "stop", "bad json", "MALFORMED_OUTPUT")])
def test_router_errors_remain_unapproved_and_never_expose_raw_private_errors(settings, monkeypatch, status, finish, content, code):
    setup(settings, monkeypatch)
    wire(monkeypatch, lambda request: httpx.Response(status, json={"error": {"message": "fake-local-router-key"}, "choices": [{"finish_reason": finish, "message": {"content": content}}]}))
    with pytest.raises(WorkflowError) as exc:
        asyncio.run(LessonAI(settings).call('mocked-primary', 'Return JSON', {}, Lesson))
    assert exc.value.code == code
    assert 'fake-local-router-key' not in json.dumps(exc.value.public())


def test_groq_auth_failure_does_not_route_around_invalid_credentials(settings, monkeypatch):
    setup(settings, monkeypatch, 'INVALID_CREDENTIALS')
    wire(monkeypatch, lambda request: pytest.fail('Unexpected local-router request'))
    with pytest.raises(WorkflowError) as exc:
        asyncio.run(LessonAI(settings).call('mocked-primary', 'Return JSON', {}, Lesson))
    assert exc.value.code == 'INVALID_CREDENTIALS'


@pytest.mark.parametrize('url', ['http://remote.example/v1', 'https://name:password@example.com/v1', 'http://127.0.0.1:31415/v1?token=private'])
def test_router_base_url_rejects_plaintext_remote_and_embedded_credentials(settings, url):
    with pytest.raises(ValueError):
        settings.freellm_base_url = url


def test_other_groq_invalid_requests_are_not_misclassified_as_json_failures(settings, monkeypatch):
    setup(settings, monkeypatch)
    monkeypatch.setattr(LessonAI, '_call_groq', AsyncMock(side_effect=WorkflowError('INVALID_REQUEST', 'Other invalid request', {'provider_error_code':'invalid_api_key'})))
    wire(monkeypatch, lambda request: pytest.fail('Unexpected local-router request'))
    with pytest.raises(WorkflowError) as exc:
        asyncio.run(LessonAI(settings).call('mocked-primary', 'Return JSON', {}, Lesson))
    assert exc.value.code == 'INVALID_REQUEST'
