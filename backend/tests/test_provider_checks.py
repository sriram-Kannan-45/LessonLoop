from datetime import datetime
from unittest.mock import AsyncMock

import httpx
import pytest
from google.genai import errors
from pydantic import SecretStr

from app.services import providers


@pytest.fixture
def configured(settings):
    settings.gemini_api_key = SecretStr("gemini-test-secret")
    settings.gemini_model = "gemini-test-model"
    return settings


def test_missing_settings(client):
    response = client.post("/api/providers/gemini/check")
    assert response.status_code == 503
    assert response.json()["error_code"] == "NOT_CONFIGURED"
    assert response.json()["provider"] == "gemini"
    assert "backend/.env" in response.json()["message"]


@pytest.mark.parametrize("provider", ["unknown", "openai"])
def test_unsupported_provider(client, provider):
    assert client.post(f"/api/providers/{provider}/check").status_code == 422
    providers.request_gemini.assert_not_called()


def test_success_maps_actual_text_and_metadata(client, configured, monkeypatch):
    request = AsyncMock(return_value="LessonLoop connection OK.")
    monkeypatch.setattr(providers, "request_gemini", request)
    response = client.post("/api/providers/gemini/check")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "LessonLoop connection OK."
    assert data["model"] == "gemini-test-model"
    assert data["provider"] == "gemini"
    assert data["status"] == "success"
    assert data["latency_ms"] >= 0
    assert datetime.fromisoformat(data["checked_at"]).utcoffset().total_seconds() == 0
    request.assert_awaited_once_with("gemini-test-secret", "gemini-test-model", 30)


@pytest.mark.parametrize("exception,status,code", [
    (TimeoutError("secret-provider-diagnostic"), 504, "TIMEOUT"),
    (httpx.ReadTimeout("secret-provider-diagnostic"), 504, "TIMEOUT"),
    (errors.ClientError(401, {"message": "secret-provider-diagnostic"}), 401, "INVALID_CREDENTIALS"),
    (errors.ClientError(400, {"error": {"message": "secret-provider-diagnostic", "details": [{"reason": "API_KEY_INVALID"}]}}), 401, "INVALID_CREDENTIALS"),
    (errors.ClientError(403, {"message": "secret-provider-diagnostic"}), 403, "MODEL_UNAVAILABLE"),
    (errors.ClientError(404, {"message": "secret-provider-diagnostic"}), 404, "MODEL_UNAVAILABLE"),
    (errors.ClientError(429, {"message": "secret-provider-diagnostic"}), 429, "RATE_LIMIT_OR_QUOTA"),
    (httpx.ConnectError("secret-provider-diagnostic"), 502, "PROVIDER_FAILURE"),
    (RuntimeError("secret-provider-diagnostic"), 502, "PROVIDER_FAILURE"),
])
def test_errors_are_sanitized(client, configured, monkeypatch, exception, status, code):
    monkeypatch.setattr(providers, "request_gemini", AsyncMock(side_effect=exception))
    response = client.post("/api/providers/gemini/check")
    assert response.status_code == status
    assert response.json()["error_code"] == code
    assert response.json()["status"] == "error"
    assert "secret" not in response.text
    assert "diagnostic" not in response.text


@pytest.mark.parametrize("message", [None, "", "   "])
def test_unusable_provider_response(client, configured, monkeypatch, message):
    monkeypatch.setattr(providers, "request_gemini", AsyncMock(return_value=message))
    response = client.post("/api/providers/gemini/check")
    assert response.status_code == 502
    assert response.json()["error_code"] == "EMPTY_RESPONSE"


def test_key_echo_is_redacted(client, configured, monkeypatch):
    monkeypatch.setattr(providers, "request_gemini", AsyncMock(return_value="gemini-test-secret"))
    response = client.post("/api/providers/gemini/check")
    assert response.json()["message"] == "[redacted]"


def test_overall_deadline(client, configured, monkeypatch):
    import asyncio

    async def slow_request(*args):
        await asyncio.sleep(0.1)
        return "too late"

    configured.provider_timeout_seconds = 0.01
    monkeypatch.setattr(providers, "request_gemini", slow_request)
    assert client.post("/api/providers/gemini/check").json()["error_code"] == "TIMEOUT"


def test_diagnostics_disabled_outside_development(client, configured):
    configured.app_env = "production"
    response = client.post("/api/providers/gemini/check")
    assert response.status_code == 403
    assert response.json()["error_code"] == "DIAGNOSTICS_DISABLED"
    providers.request_gemini.assert_not_called()


def test_untrusted_origin_cannot_trigger_paid_request(client, configured):
    response = client.post("/api/providers/gemini/check", headers={"Origin": "https://untrusted.example"})
    assert response.status_code == 403
    providers.request_gemini.assert_not_called()
