import json
import sqlite3

from fastapi import APIRouter, Query, Request
from fastapi.responses import Response

from app.content import PROMPTS, RUBRIC, SOURCE_PACK, supports_topic
from app.exports import audit_report, markdown_lesson
from app.improvements import INSTRUCTIONS
from app.dataset import DATASET_VERSION
from app.lesson_schemas import FeedbackRequest, FeedbackReview, ImprovementRequest, LEARNER, RollbackRequest, RunRequest

router = APIRouter(prefix="/api")


class ApiProblem(Exception):
    def __init__(self, status, code, message):
        self.status, self.code, self.message = status, code, message


def runtime(request):
    return request.app.state.runtime


def local_only(request):
    config = runtime(request).settings
    origin = request.headers.get("origin")
    if config.app_env != "development" or origin and origin != config.frontend_origin:
        raise ApiProblem(403, "LOCAL_ONLY", "This workspace accepts changes only in local development from the configured frontend.")


def not_busy(current):
    if current.busy:
        raise ApiProblem(409, "WORKSPACE_BUSY", "One run or comparison is already active. Wait for it to finish before starting another.")


def find_run(current, run_id):
    run = current.repository.get_run(run_id)
    if not run:
        raise ApiProblem(404, "RUN_NOT_FOUND", "This run was not found. Open a run from history or start a new one.")
    return run


@router.get("/workspace")
async def workspace(request: Request):
    current = runtime(request)
    return {"source_pack": SOURCE_PACK, "rubric": RUBRIC, "learner_profile": LEARNER,
            "learner_preset": "india_beginner", "generator_model": current.ai.generator_model,
            "evaluator_model": current.ai.evaluator_model, "provider": "gemini", "max_retries": 2,
            "provider_note": "Separate Gemini calls for generation and evaluation. Same-provider judgments can share mistakes.",
            "configured": bool(current.settings.gemini_api_key and current.ai.generator_model and current.ai.evaluator_model),
            "busy": current.busy, "active_prompt_version": current.repository.active_prompt()["version"],
            "improvement_categories": list(INSTRUCTIONS), "demo_enabled": current.settings.app_env == "development"}


@router.post("/runs", status_code=202)
async def create_run(body: RunRequest, request: Request):
    local_only(request)
    current = runtime(request)
    not_busy(current)
    if not supports_topic(body.topic, body.reference_pack_id):
        raise ApiProblem(422, "UNSUPPORTED_TOPIC", "Only Introduction to RAG has a reviewed reference pack. Choose RAG, or add and review a topic-specific pack before generating another topic.")
    if not current.settings.gemini_api_key or not current.ai.generator_model or not current.ai.evaluator_model:
        raise ApiProblem(503, "NOT_CONFIGURED", "Add the Gemini API key and model to backend/.env and restart the backend.")
    try:
        run_id = current.repository.create_run(body, current.ai.generator_model, current.ai.evaluator_model)
    except sqlite3.IntegrityError:
        raise ApiProblem(409, "WORKSPACE_BUSY", "A run is already active. Wait for it to finish.") from None
    current.start_run(run_id)
    return {"id": run_id, "status": "RUNNING"}


@router.get("/runs")
async def runs(request: Request, limit: int = Query(20, ge=1, le=50), offset: int = Query(0, ge=0)):
    return runtime(request).repository.history(limit, offset)


@router.get("/runs/{run_id}")
async def run_detail(run_id: str, request: Request):
    return find_run(runtime(request), run_id)


@router.get("/runs/{run_id}/events")
async def run_events(run_id: str, request: Request, after: int = Query(0, ge=0)):
    current = runtime(request)
    find_run(current, run_id)
    events = current.repository.events(run_id, after)
    return {"events": events, "next_cursor": events[-1]["sequence"] if events else after}


@router.post("/runs/{run_id}/feedback", status_code=201)
async def feedback(run_id: str, body: FeedbackRequest, request: Request):
    local_only(request)
    current = runtime(request)
    find_run(current, run_id)
    message = body.message
    if current.settings.gemini_api_key:
        message = message.replace(current.settings.gemini_api_key.get_secret_value(), "[redacted]")
    return current.repository.feedback(run_id, body.category, message)


@router.post("/feedback/{feedback_id}/review")
async def review_feedback(feedback_id: str, body: FeedbackReview, request: Request):
    local_only(request)
    current = runtime(request)
    note = body.review_note
    if current.settings.gemini_api_key:
        note = note.replace(current.settings.gemini_api_key.get_secret_value(), "[redacted]")
    result = current.repository.review_feedback(feedback_id, body.action, note)
    if not result:
        raise ApiProblem(404, "FEEDBACK_NOT_FOUND", "That feedback record was not found.")
    return result


@router.get("/memory")
async def memory(request: Request):
    return runtime(request).repository.memory()


@router.post("/improvements", status_code=202)
async def improve(body: ImprovementRequest, request: Request):
    local_only(request)
    current = runtime(request)
    not_busy(current)
    if body.category not in INSTRUCTIONS:
        raise ApiProblem(422, "UNSUPPORTED_CATEGORY", "Choose a model-evaluated failure category from the memory screen.")
    supports = current.repository.supporting_runs(body.category)
    if len(supports) < 2:
        raise ApiProblem(422, "MORE_EVIDENCE_NEEDED", "This category needs failures from at least two independent completed runs; retries within one run count only once.")
    if len(current.repository.active_prompt()["memory_ids"]) >= 4:
        raise ApiProblem(409, "MEMORY_LIMIT", "Four instructions are already loaded. Roll back to a smaller validated prompt before adding another.")
    if not current.settings.gemini_api_key:
        raise ApiProblem(503, "NOT_CONFIGURED", "Add the Gemini key and model before running a paid comparison.")
    experiment_id = current.repository.create_experiment(body.category, INSTRUCTIONS[body.category], supports, DATASET_VERSION)
    current.start_improvement(experiment_id)
    return {"id": experiment_id, "status": "RUNNING"}


@router.get("/improvements/{experiment_id}")
async def improvement(experiment_id: str, request: Request):
    result = runtime(request).repository.experiment(experiment_id)
    if not result:
        raise ApiProblem(404, "EXPERIMENT_NOT_FOUND", "That comparison was not found.")
    return result


@router.post("/prompts/rollback")
async def rollback(body: RollbackRequest, request: Request):
    local_only(request)
    current = runtime(request)
    not_busy(current)
    result = current.repository.rollback(body.prompt_version)
    if not result:
        raise ApiProblem(422, "UNVALIDATED_PROMPT", "Choose the original prompt or a version activated by a completed comparison.")
    return result


@router.get("/runs/{run_id}/export")
async def export(run_id: str, request: Request, format: str = Query("markdown", pattern="^(markdown|json)$")):
    current = runtime(request)
    run = find_run(current, run_id)
    if format == "json":
        content = json.dumps(audit_report(current.repository, run_id), ensure_ascii=False, indent=2)
        extension, media_type = "json", "application/json"
    else:
        lesson = run["final_lesson"] or run["review_draft"]
        if not lesson:
            raise ApiProblem(409, "NO_DRAFT", "This run has no saved draft to export yet.")
        content = markdown_lesson(lesson, run["status"], run_id, run["source_snapshot"]["sources"])
        extension, media_type = "md", "text/markdown"
    label = "approved" if run["status"] == "APPROVED" else "review-not-approved"
    return Response(content, media_type=media_type, headers={"Content-Disposition": f'attachment; filename="lessonloop-{label}-{run_id}.{extension}"'})
