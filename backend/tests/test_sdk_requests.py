"""Exercise real SDK serialization over an in-memory HTTP transport, with no network."""
import asyncio
import json

import httpx
from google import genai

from app.services import providers
from app.services.providers import request_gemini


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
