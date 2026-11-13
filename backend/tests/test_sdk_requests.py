"""Exercise real SDK serialization over an in-memory HTTP transport, with no network."""
import asyncio
import json

import httpx
from google import genai
from openai import AsyncOpenAI

from app.services import providers
from app.services.providers import request_gemini, request_openai


def test_openai_sdk_uses_responses_and_no_retries(monkeypatch):
    requests = []

    def handle(request):
        requests.append(request)
        assert request.url.path == "/v1/responses"
        body = json.loads(request.content)
        assert body["model"] == "gpt-4.1-mini"
        assert body["max_output_tokens"] == 64
        assert body["store"] is False
        return httpx.Response(200, json={
            "id": "resp_test", "created_at": 0, "object": "response", "status": "completed",
            "model": body["model"], "output": [{"type": "message", "id": "msg_test", "role": "assistant", "status": "completed", "content": [{"type": "output_text", "text": "SDK connection OK", "annotations": []}]}],
        })

    def client(**kwargs):
        assert kwargs["max_retries"] == 0
        assert kwargs["timeout"] == 5
        return AsyncOpenAI(**kwargs, http_client=httpx.AsyncClient(transport=httpx.MockTransport(handle)))

    monkeypatch.setattr(providers.openai, "AsyncOpenAI", client)
    assert asyncio.run(request_openai("fake-key", "gpt-4.1-mini", 5)) == "SDK connection OK"
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
