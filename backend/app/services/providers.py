import asyncio
from datetime import datetime, timezone
from time import perf_counter

import httpx
from google import genai
from google.genai import errors, types

from app.config import Settings
from app.schemas import CheckSuccess, Provider, ProviderStatus

PROMPT = "Reply with only: LessonLoop connection OK."


class ProviderFailure(Exception):
    def __init__(self, code: str, message: str, status_code: int):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(code)


def provider_settings(settings: Settings, provider: Provider):
    return settings.gemini_api_key, settings.gemini_model


def configuration_status(settings: Settings, provider: Provider) -> ProviderStatus:
    key, model = provider_settings(settings, provider)
    return ProviderStatus(configured=bool(key and model), model=model)


async def request_gemini(key: str, model: str, timeout: float) -> str | None:
    async with genai.Client(
        api_key=key,
        http_options=types.HttpOptions(
            timeout=int(timeout * 1000),
            retry_options=types.HttpRetryOptions(attempts=1),
        ),
    ).aio as client:
        response = await client.models.generate_content(
            model=model,
            contents=PROMPT,
            config=types.GenerateContentConfig(max_output_tokens=64),
        )
        return response.text


def map_failure(exc: Exception) -> ProviderFailure:
    if isinstance(exc, (TimeoutError, httpx.TimeoutException)):
        return ProviderFailure("TIMEOUT", "The provider took too long. Try again in a moment.", 504)
    status = getattr(exc, "status_code", None) or getattr(exc, "code", None)
    if status == 401:
        return ProviderFailure("INVALID_CREDENTIALS", "The API key was rejected. Update it in backend/.env and restart the backend.", 401)
    if status in (403, 404):
        return ProviderFailure("MODEL_UNAVAILABLE", "The model is unavailable or access was denied. Check the model ID and account permissions.", 403 if status == 403 else 404)
    if status == 429:
        return ProviderFailure("RATE_LIMIT_OR_QUOTA", "The provider limit was reached. Check your API quota and billing before retrying.", 429)
    # Gemini reports invalid API keys as 400 with a structured reason.
    if isinstance(exc, errors.APIError) and status == 400:
        details = getattr(exc, "details", None)
        if isinstance(details, dict):
            details = details.get("error", details).get("details", [])
        if isinstance(details, list) and any(
            isinstance(item, dict) and item.get("reason") == "API_KEY_INVALID" for item in details
        ):
            return ProviderFailure("INVALID_CREDENTIALS", "The API key was rejected. Update it in backend/.env and restart the backend.", 401)
    return ProviderFailure("PROVIDER_FAILURE", "The provider request failed. Check your connection, model ID, and provider service, then retry.", 502)


async def check_provider(settings: Settings, provider: Provider) -> CheckSuccess:
    key, model = provider_settings(settings, provider)
    if not key or not model:
        raise ProviderFailure("NOT_CONFIGURED", "Add the Gemini API key and model to backend/.env, then restart the backend.", 503)
    started = perf_counter()
    try:
        async with asyncio.timeout(settings.provider_timeout_seconds):
            message = await request_gemini(key.get_secret_value(), model, settings.provider_timeout_seconds)
    except Exception as exc:
        raise map_failure(exc) from None
    if not isinstance(message, str) or not message.strip():
        raise ProviderFailure("EMPTY_RESPONSE", "The provider returned no usable text. Check the model and try again.", 502)
    # Provider text is untrusted: prevent accidental key echoes even from a mock or proxy.
    message = message.replace(key.get_secret_value(), "[redacted]")
    return CheckSuccess(
        provider=provider, model=model, message=message.strip()[:500],
        latency_ms=round((perf_counter() - started) * 1000),
        checked_at=datetime.now(timezone.utc),
    )
