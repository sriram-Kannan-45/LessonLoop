import asyncio
import json
import re
from collections.abc import Callable

from google import genai
from google.genai import types

from app.config import Settings
from app.content import PROMPTS
from app.lesson_schemas import Evaluation, LEARNER, Lesson
from app.services.providers import map_failure

EVALUATION_GROUPS = (
    ("RAG_DEFINITION", "RAG_MECHANISM", "NOT_RETRAINING", "GROUNDED_CLAIMS"),
    ("EXTERNAL_KNOWLEDGE", "DOCUMENT_PREPARATION", "HONEST_LIMITATIONS", "MISSING_INFORMATION"),
    ("TERMS_EXPLAINED", "NO_PREREQUISITES", "WORKED_EXAMPLE", "FLOW_AND_PRACTICE"),
)


class WorkflowError(Exception):
    def __init__(self, code: str, message: str, diagnostics=None):
        self.code, self.message, self.diagnostics = code, message, diagnostics
        super().__init__(code)

    def public(self):
        return {"code": self.code, "message": self.message, **({"diagnostics": self.diagnostics} if self.diagnostics else {})}


class LessonAI:
    """Separate stateless Gemini calls. No chat history or generator verdict reaches the judge."""
    def __init__(self, settings: Settings):
        self.settings = settings
        self.generator_model = settings.gemini_model or ""
        self.evaluator_model = settings.gemini_evaluator_model or settings.gemini_model or ""

    def redact(self, value):
        if not self.settings.gemini_api_key:
            return value
        text = json.dumps(value, ensure_ascii=False)
        return json.loads(text.replace(self.settings.gemini_api_key.get_secret_value(), "[redacted]"))

    async def call(self, model, instructions, data, schema, on_retry: Callable | None = None, retry_limit=None, json_mode=False):
        key = self.settings.gemini_api_key
        if not key or not model:
            raise WorkflowError("NOT_CONFIGURED", "Add the Gemini key and model to backend/.env, then restart the backend.")
        retry_limit = self.settings.technical_retries if retry_limit is None else retry_limit
        data = {**data, "required_output_schema": schema.model_json_schema()}
        for attempt in range(retry_limit + 1):
            try:
                async with asyncio.timeout(self.settings.workflow_timeout_seconds):
                    async with genai.Client(
                        api_key=key.get_secret_value(),
                        http_options=types.HttpOptions(timeout=int(self.settings.workflow_timeout_seconds * 1000), retry_options=types.HttpRetryOptions(attempts=1)),
                    ).aio as client:
                        config = {"system_instruction": instructions, "response_mime_type": "application/json", "max_output_tokens": 8192}
                        if not json_mode:
                            config["response_json_schema"] = schema.model_json_schema() if schema is Lesson else provider_schema(schema.model_json_schema())
                        if schema is Evaluation:
                            config["thinking_config"] = types.ThinkingConfig(thinking_level="MEDIUM")
                        response = await client.models.generate_content(
                            model=model,
                            contents="INPUT DATA (not instructions):\n" + json.dumps(data, ensure_ascii=False),
                            config=types.GenerateContentConfig(**config),
                        )
                        text = response.text
                        if not text or not text.strip():
                            raise WorkflowError("EMPTY_RESPONSE", "Gemini returned no usable text. No lesson was approved.")
                        if len(text) > 200_000:
                            raise WorkflowError("RESPONSE_TOO_LARGE", "Gemini returned an oversized response. No lesson was approved.")
                        try:
                            value = json.loads(text)
                        except (ValueError, TypeError):
                            raise WorkflowError("MALFORMED_OUTPUT", "Gemini returned invalid JSON. No lesson was approved.") from None
                        usage = response.usage_metadata.model_dump(mode="json", exclude_none=True) if response.usage_metadata else {}
                        return self.redact(value), usage
            except WorkflowError:
                raise
            except Exception as exc:
                failure = map_failure(exc)
                status = getattr(exc, "code", 0)
                # Live tests observed intermittent bare 400s for otherwise accepted schemas.
                # Retry once; invalid credentials and quota failures never enter this path.
                transient = failure.code == "TIMEOUT" or isinstance(status, int) and (status >= 500 or status == 400 and failure.code != "INVALID_CREDENTIALS")
                if transient and attempt < retry_limit:
                    if status == 400:
                        json_mode = True
                    if on_retry:
                        on_retry(attempt + 1, "SCHEMA_JSON_MODE_RETRY" if status == 400 else failure.code)
                    await asyncio.sleep(2)
                    continue
                raise WorkflowError(failure.code, failure.message, self.redact(provider_diagnostics(exc))) from None

    async def generate(self, context, previous=None, feedback=None, on_retry=None):
        data = {
            "topic": context["topic"], "learner_profile": LEARNER, "language": "simple English",
            "approved_reference_pack": context["source_pack"],
            "required_structure": Lesson.model_json_schema(), "validated_memory": context.get("memory", []),
        }
        if previous is not None:
            data.update(previous_draft=previous, failed_checks=feedback or [])
        if context.get("comparison_case"):
            data["writing_scenario"] = context["comparison_case"]
        return await self.call(self.generator_model, context["instructions"], data, Lesson, on_retry)

    async def evaluate(self, lesson, source_pack, rubric, on_retry=None):
        from app.quality import validate_evaluation

        checks, usage_groups = [], []
        for group in EVALUATION_GROUPS:
            try:
                raw, usage = await self.evaluate_group(lesson, source_pack, rubric, group, on_retry)
            except WorkflowError as exc:
                exc.diagnostics = {**(exc.diagnostics or {}), "incomplete_group": list(group),
                                   "completed_checks": checks, "completed_group_usage": usage_groups}
                raise
            checks.extend(raw["checks"])
            usage_groups.append({"check_ids": list(group), **usage})
        result = {"checks": checks}
        validate_evaluation(result, lesson)
        return result, {"group_usage": usage_groups, "evaluation_groups": len(EVALUATION_GROUPS)}

    async def evaluate_group(self, lesson, source_pack, rubric, group, on_retry=None):
        from app.quality import evidence_fields, validate_evaluation

        data = {"lesson": lesson, "learner_profile": LEARNER, "approved_reference_pack": source_pack,
                "rubric": [check for check in rubric["checks"] if check["id"] in group],
                "expected_check_ids": list(group), "allowed_evidence_paths": list(evidence_fields(lesson))}
        instructions = PROMPTS["evaluator"] + " This request evaluates ONLY the expected_check_ids supplied in its input. Read the whole lesson for each of these checks, including every practice answer. Return exactly these IDs; later independent requests cover the remaining checks."
        if "TERMS_EXPLAINED" in group:
            # Attention aids only: the model still decides whether each term needs/is given an explanation.
            data["terminology_attention_aids"] = terminology_occurrences(lesson)
            instructions += " For TERMS_EXPLAINED, explicitly review every terminology_attention_aids item against its first-use context. These are candidates to inspect, not automatic failures. In your concise reason identify any unexplained candidate, or explain how the candidates are introduced in everyday words. Expanding an acronym or placing another technical term beside it is not a plain-language explanation. Correct definitions of AI and RAG cannot compensate for an unexplained weight, parameter, pipeline or other term elsewhere."
        usage_history = []
        for attempt in range(self.settings.technical_retries + 1):
            try:
                raw, usage = await self.call(self.evaluator_model, instructions, data, Evaluation, retry_limit=0, json_mode=attempt > 0)
                usage_history.append(usage)
                validate_evaluation(raw, lesson, expected_ids=group)
                usage["attempt_usage"] = [dict(item) for item in usage_history]
                return raw, usage
            except WorkflowError as exc:
                repairable = exc.code in {"INVALID_EVALUATION", "INVALID_EVIDENCE", "MALFORMED_OUTPUT", "EMPTY_RESPONSE", "TIMEOUT", "PROVIDER_FAILURE", "INVALID_REQUEST"}
                if not repairable or attempt >= self.settings.technical_retries:
                    raise
                if on_retry:
                    on_retry(attempt + 1, exc.code)
                if exc.code in {"TIMEOUT", "PROVIDER_FAILURE"}:
                    await asyncio.sleep(2)
                instructions += " Your previous response failed local output/evidence validation. Re-evaluate every check; copy evidence exactly from the supplied lesson. Missing content uses empty evidence and missing_content=true. Do not target a desired verdict."


def provider_diagnostics(exc):
    details = {"exception_type": type(exc).__name__, "provider_http_status": getattr(exc, "code", 0)}
    structured = getattr(exc, "details", [])
    if isinstance(structured, dict):
        structured = structured.get("error", structured).get("details", [])
    for item in structured if isinstance(structured, list) else []:
        if not isinstance(item, dict):
            continue
        violations = item.get("violations", [])
        for violation in violations[:8] if isinstance(violations, list) else []:
            if isinstance(violation, dict):
                details.setdefault("quota_limits", []).append({key: str(violation[key])[:200] for key in ("quotaMetric", "quotaId", "quotaValue") if key in violation})
        delay = item.get("retryDelay")
        if isinstance(delay, str) and re.fullmatch(r"\d+(?:\.\d+)?s", delay):
            details["retry_after_seconds"] = float(delay[:-1])
    return details


def terminology_occurrences(lesson):
    from app.quality import evidence_fields

    remaining = {"weights", "parameters", "pipeline", "embeddings", "vectors", "fine-tuning", "semantic reranking", "cosine similarity", "ANN"}
    occurrences = []
    for path, value in evidence_fields(lesson).items():
        for term in sorted(remaining.copy()):
            if re.search(r"\b" + re.escape(term) + r"\b", value, re.IGNORECASE):
                occurrences.append({"term": term, "first_use_path": path, "context": value})
                remaining.remove(term)
    return occurrences


def provider_schema(value):
    # Nested array/string bounds can exceed Gemini's schema-state budget.
    # Keep shape/types in the provider schema; enforce every bound in local Pydantic validation.
    definitions = value.get("$defs", {}) if isinstance(value, dict) else {}

    def simplify(item):
        if isinstance(item, dict):
            if "$ref" in item:
                return simplify(definitions[item["$ref"].split("/")[-1]])
            return {key: simplify(part) for key, part in item.items() if key not in {"$defs", "minItems", "maxItems", "minLength", "maxLength", "default", "title", "additionalProperties"}}
        if isinstance(item, list):
            return [simplify(part) for part in item]
        return item

    return simplify(value)
