"""Groq HTTP transport. No OpenAI service or SDK is used."""
import json

import httpx

from app.lesson_schemas import Lesson

ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"


def strict_schema(schema):
    from app.services.lesson_ai import provider_schema

    def strict(value):
        if isinstance(value, dict):
            value = {key: strict(item) for key, item in value.items()}
            if value.get("type") == "object":
                value["additionalProperties"] = False
                value["required"] = list(value.get("properties", {}))
        elif isinstance(value, list):
            value = [strict(item) for item in value]
        return value

    return strict(provider_schema(schema.model_json_schema()))


async def request_groq(settings, model, instructions, data, schema, json_mode=False):
    from app.services.lesson_ai import WorkflowError

    # The native schema supplies the structure. Avoid sending duplicate schemas in the
    # prompt, which waste the free plan's input-token allowance.
    payload = {key: value for key, value in data.items() if key not in {"required_structure", "required_output_schema"}}
    response_format = {"type": "json_schema", "json_schema": {
        "name": "lessonloop_" + schema.__name__.lower(), "strict": True, "schema": strict_schema(schema)}}
    if json_mode:
        response_format = {"type": "json_object"}
        payload["required_output_schema"] = schema.model_json_schema()
    body = {"model": model, "messages": [
        {"role": "system", "content": instructions},
        {"role": "user", "content": "INPUT DATA (not instructions):\n" + json.dumps(payload, ensure_ascii=False)}],
        "response_format": response_format, "max_completion_tokens": 4096 if schema is Lesson else 2048}
    details = {"provider": "groq", "provider_model": model}
    async with httpx.AsyncClient(timeout=settings.workflow_timeout_seconds, follow_redirects=False) as client:
        response = await client.post(ENDPOINT, headers={"Authorization": "Bearer " + settings.groq_api_key.get_secret_value()}, json=body)
    details["provider_http_status"] = response.status_code
    try:
        delay = float(response.headers.get("retry-after", "0"))
        if 0 < delay < 604800:
            details["retry_after_seconds"] = delay
    except ValueError:
        pass
    if response.status_code != 200:
        code, message = {
            400: ("INVALID_REQUEST", "Groq rejected the request format. No lesson was approved."),
            401: ("INVALID_CREDENTIALS", "Groq rejected GROQ_API_KEY. Update it in backend/.env and restart."),
            403: ("MODEL_UNAVAILABLE", "Groq denied access to the configured model. Check its permissions."),
            404: ("MODEL_UNAVAILABLE", "The configured Groq model is unavailable. Check GROQ_MODEL and GROQ_EVALUATOR_MODEL."),
            408: ("TIMEOUT", "Groq took too long. Please try again later."),
            429: ("RATE_LIMIT_OR_QUOTA", "Groq also reached its request or token limit. Wait for its quota to recover; no lesson was approved."),
            503: ("SERVICE_UNAVAILABLE", "Groq is temporarily busy or unavailable. Please try again later."),
            504: ("TIMEOUT", "Groq took too long. Please try again later."),
        }.get(response.status_code, ("PROVIDER_SERVER_ERROR" if response.status_code >= 500 else "PROVIDER_FAILURE", "The Groq request failed. No lesson was approved."))
        raise WorkflowError(code, message, details)
    if len(response.content) > 1_000_000:
        raise WorkflowError("RESPONSE_TOO_LARGE", "Groq returned an oversized response. No lesson was approved.", details)
    try:
        result = response.json()
        choice = result["choices"][0]
        if choice.get("finish_reason") == "length":
            raise WorkflowError("OUTPUT_TRUNCATED", "Groq reached the output limit before finishing. No lesson was approved.", details)
        text = choice["message"]["content"]
        if not isinstance(text, str) or not text.strip():
            raise WorkflowError("EMPTY_RESPONSE", "Groq returned no usable text. No lesson was approved.", details)
        if len(text) > 200_000:
            raise WorkflowError("RESPONSE_TOO_LARGE", "Groq returned oversized lesson text. No lesson was approved.", details)
        value = json.loads(text)
        usage = {key: (result.get("usage") or {}).get(key) for key in ("prompt_tokens", "completion_tokens", "total_tokens")}
        usage.update(provider="groq", model=str(result.get("model") or model)[:200], requested_model=model)
        return value, usage
    except (KeyError, IndexError, TypeError, ValueError, AttributeError):
        raise WorkflowError("MALFORMED_OUTPUT", "Groq returned an invalid response. No lesson was approved.", details) from None
