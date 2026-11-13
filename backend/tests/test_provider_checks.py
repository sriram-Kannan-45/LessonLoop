from datetime import datetime
from unittest.mock import AsyncMock

import httpx
import openai
import pytest
from google.genai import errors
from pydantic import SecretStr

from app.services import providers


@pytest.fixture
def configured(settings):
    settings.gemini_api_key = SecretStr("gemini-test-secret")
    settings.gemini_model = "gemini-test-model"
    settings.openai_api_key = SecretStr("openai-test-secret")
    settings.openai_model = "openai-test-model"
    return settings


@pytest.mark.parametrize("provider", ["gemini", "openai"])
def test_missing_settings(client, provider):
    response = client.post(f"/api/providers/{provider}/check")
    assert response.status_code == 503
    assert response.json()["error_code"] == "NOT_CONFIGURED"
    assert response.json()["provider"] == provider
    assert "backend/.env" in response.json()["message"]


def test_unsupported_provider(client):
    assert client.post("/api/providers/unknown/check").status_code == 422


@pytest.mark.parametrize("provider", ["gemini", "openai"])
def test_success_maps_actual_text_and_metadata(client, configured, monkeypatch, provider):
    request = AsyncMock(return_value="LessonLoop connection OK.")
    monkeypatch.setattr(providers, f"request_{provider}", request)
    response = client.post(f"/api/providers/{provider}/check")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "LessonLoop connection OK."
    assert data["model"] == f"{provider}-test-model"
    assert data["provider"] == provider
    assert data["status"] == "success"
    assert data["latency_ms"] >= 0
    assert datetime.fromisoformat(data["checked_at"]).utcoffset().total_seconds() == 0
    request.assert_awaited_once_with(f"{provider}-test-secret", f"{provider}-test-model", 30)


def openai_error(kind, status):
    response = httpx.Response(status, request=httpx.Request("POST", "https://api.openai.com/v1/responses"))
    return kind("secret-provider-diagnostic", response=response, body={"secret": "do-not-expose"})


@pytest.mark.parametrize("provider,exception,status,code", [
    ("gemini", TimeoutError("secret-provider-diagnostic"), 504, "TIMEOUT"),
    ("openai", openai.APITimeoutError(request=httpx.Request("POST", "https://example.com")), 504, "TIMEOUT"),
    ("openai", openai_error(openai.AuthenticationError, 401), 401, "INVALID_CREDENTIALS"),
    ("gemini", errors.ClientError(400, {"error": {"message": "secret-provider-diagnostic", "details": [{"reason": "API_KEY_INVALID"}]}}), 401, "INVALID_CREDENTIALS"),
    ("gemini", errors.ClientError(403, {"message": "secret-provider-diagnostic"}), 403, "MODEL_UNAVAILABLE"),
    ("openai", openai_error(openai.NotFoundError, 404), 404, "MODEL_UNAVAILABLE"),
    ("gemini", errors.ClientError(429, {"message": "secret-provider-diagnostic"}), 429, "RATE_LIMIT_OR_QUOTA"),
    ("openai", openai_error(openai.RateLimitError, 429), 429, "RATE_LIMIT_OR_QUOTA"),
    ("gemini", httpx.ConnectError("secret-provider-diagnostic"), 502, "PROVIDER_FAILURE"),
    ("openai", RuntimeError("secret-provider-diagnostic"), 502, "PROVIDER_FAILURE"),
])
def test_errors_are_sanitized(client, configured, monkeypatch, provider, exception, status, code):
    monkeypatch.setattr(providers, f"request_{provider}", AsyncMock(side_effect=exception))
    response = client.post(f"/api/providers/{provider}/check")
    assert response.status_code == status
    assert response.json()["error_code"] == code
    assert response.json()["status"] == "error"
    assert "secret" not in response.text
    assert "diagnostic" not in response.text


@pytest.mark.parametrize("message", [None, "", " \n "])
def test_unusable_provider_response(client, configured, monkeypatch, message):
    monkeypatch.setattr(providers, "request_openai", AsyncMock(return_value=message))
    response = client.post("/api/providers/openai/check")
    assert response.status_code == 502
    assert response.json()["error_code"] == "EMPTY_RESPONSE"


def test_key_echo_is_redacted(client, configured, monkeypatch):
    monkeypatch.setattr(providers, "request_openai", AsyncMock(return_value="openai-test-secret gemini-test-secret"))
    response = client.post("/api/providers/openai/check")
    assert response.json()["message"] == "[redacted] [redacted]"


def test_overall_deadline(client, configured, monkeypatch):
    import asyncio

    async def slow_request(*args):
        await asyncio.sleep(0.1)
        return "too late"

    configured.provider_timeout_seconds = 0.01
    monkeypatch.setattr(providers, "request_openai", slow_request)
    assert client.post("/api/providers/openai/check").json()["error_code"] == "TIMEOUT"


def test_diagnostics_disabled_outside_development(client, configured):
    configured.app_env = "production"
    response = client.post("/api/providers/openai/check")
    assert response.status_code == 403
    assert response.json()["error_code"] == "DIAGNOSTICS_DISABLED"
    providers.request_openai.assert_not_called()


def test_untrusted_origin_cannot_trigger_paid_request(client, configured):
    response = client.post("/api/providers/gemini/check", headers={"Origin": "https://untrusted.example"})
    assert response.status_code == 403
    providers.request_gemini.assert_not_called()
