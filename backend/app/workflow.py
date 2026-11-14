import copy
from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from app.content import SOURCE_PACK
from app.lesson_schemas import MAX_RETRIES
from app.quality import diagnostics, releasable, structure_checks, validate_evaluation
from app.services.lesson_ai import WorkflowError
from app.topics import collect_topic_references


class RunState(TypedDict, total=False):
    run_id: str
    topic: str
    learner_profile: str
    source_pack_version: str
    rubric_version: str
    generator_prompt_version: str
    evaluator_prompt_version: str
    selected_memory_ids: list[str]
    context: dict
    current_lesson: dict
    evaluation_results: list[dict]
    failure_feedback: list[dict]
    attempts: list[int]
    retry_count: int
    status: str
    error: dict | None
    attempt_id: int
    structure: list[dict]


def build_graph(repository, ai):
    def provider_events(run_id):
        def record(event):
            if event["type"] == "PROVIDER_FALLBACK":
                message = f"Gemini quota reached. Switching {event['role']} to Groq ({event['model']})."
            elif event["type"] == "PROVIDER_WAIT":
                message = f"Waiting {event['wait_seconds']} seconds before the next Groq request to respect its token allowance."
            else:
                message = f"{event['role'].capitalize()} response received from {event['provider']} ({event['model']})."
            repository.event(run_id, event["type"], message, event)
        return record

    def retry_event(run_id, role):
        return lambda number, code: repository.event(run_id, "TECHNICAL_RETRY", f"Retrying {role} request after a temporary failure.", {"role": role, "technical_retry": number, "code": code})

    async def load_context(state):
        run = repository.get_run(state["run_id"])
        if run["source_snapshot"].get("status") == "pending":
            repository.event(run["id"], "RESEARCHING", "Finding public references for the requested topic.", {"topic": run["topic"]})
            pack = await collect_topic_references(run["topic"])
            repository.freeze_topic_references(run["id"], pack)
            repository.event(run["id"], "REFERENCES_READY", "Topic references retrieved and frozen for this run. They are automatically collected, not human-reviewed.", {"source_count": len(pack["sources"]), "source_pack_version": pack["version"]})
            run = repository.get_run(run["id"])
        prompt = repository.prompt(run["generator_prompt_version"])
        repository.event(run["id"], "LOADING_CONTEXT", "Loaded frozen references, rubric, learner profile, and validated memory.", {"selected_memory_ids": [memory["id"] for memory in run["selected_memory"]]})
        return {"topic": run["topic"], "learner_profile": run["learner_profile"],
                "source_pack_version": run["source_pack_version"], "rubric_version": run["rubric_version"],
                "generator_prompt_version": run["generator_prompt_version"], "evaluator_prompt_version": run["evaluator_prompt_version"],
                "selected_memory_ids": [memory["id"] for memory in run["selected_memory"]],
                "context": {"topic": run["topic"], "source_pack": run["source_snapshot"], "rubric": run["rubric_snapshot"], "instructions": prompt["instructions"], "memory": run["selected_memory"], "demo_error": bool(run["demo_error"])},
                "retry_count": 0, "attempts": [], "failure_feedback": [], "status": "RUNNING", "error": None}

    async def generate_lesson(state):
        number = len(state["attempts"]) + 1
        stage = "GENERATING" if number == 1 else "REWRITING"
        repository.event(state["run_id"], stage, f"{'Creating' if number == 1 else 'Revising'} draft {number} of 3.", {"attempt": number, "failed_check_ids": [check["check_id"] for check in state["failure_feedback"]]})
        draft, usage = await ai.generate(state["context"], state.get("current_lesson"), state["failure_feedback"], retry_event(state["run_id"], "generation"), on_provider_event=provider_events(state["run_id"]))
        original = None
        if number == 1 and state["context"]["demo_error"]:
            original = copy.deepcopy(draft)
            draft = copy.deepcopy(draft)
            if isinstance(draft, dict):
                # Deliberately change a factual claim. No verdict is hardcoded.
                draft["limitations"] = "Two is greater than ten. This lesson is guaranteed correct in every situation and has no assumptions or limitations." if state["context"]["rubric"].get("kind") == "general" else "RAG guarantees that the AI answer is always correct."
            repository.event(state["run_id"], "DEMO_MUTATION", "Development demonstration: inserted a factual error into draft 1. The evaluator receives only the altered lesson, with no demo label.", {"attempt": 1})
        attempt_id = repository.add_attempt(state["run_id"], number, draft, original, usage, diagnostics(draft))
        return {"current_lesson": draft, "attempt_id": attempt_id, "attempts": [*state["attempts"], attempt_id], "retry_count": number - 1}

    async def validate_structure(state):
        repository.event(state["run_id"], "VALIDATING", "Checking the lesson structure and approved reference identifiers.")
        _, checks = structure_checks(state["current_lesson"], state["context"]["source_pack"])
        return {"structure": checks}

    async def evaluate_lesson(state):
        checks = list(state["structure"])
        if checks[0]["passed"]:
            repository.event(state["run_id"], "EVALUATING", "Checking the frozen rubric in three focused passes, separate from generation.", {"attempt": len(state["attempts"]), "evaluation_groups": 3})
            raw, usage = await ai.evaluate(state["current_lesson"], state["context"]["source_pack"], state["context"]["rubric"], retry_event(state["run_id"], "evaluation"), on_provider_event=provider_events(state["run_id"]))
            try:
                checks.extend(validate_evaluation(raw, state["current_lesson"], expected_ids=[item["id"] for item in state["context"]["rubric"]["checks"] if item["evaluator"] == "model"], source_pack=state["context"]["source_pack"]))
            except WorkflowError:
                repository.event(state["run_id"], "INVALID_EVALUATION", "The evaluator response failed local validation. It cannot approve a lesson.", {"attempt": len(state["attempts"]), "response": raw})
                raise
        else:
            usage = {}
        approved = releasable(checks, state["context"]["rubric"])
        repository.evaluate_attempt(state["attempt_id"], checks, usage, approved)
        failed = [check for check in checks if not check["passed"]]
        repository.event(state["run_id"], "VERDICT", "All mandatory checks passed." if approved else f"Draft {len(state['attempts'])} needs corrections.", {"failed_check_ids": [check["check_id"] for check in failed], "passed_checks": sum(check["passed"] for check in checks), "evaluated_checks": len(checks)})
        return {"evaluation_results": checks, "failure_feedback": failed,
                "status": "APPROVED" if approved else "NEEDS_REVIEW" if state["retry_count"] >= MAX_RETRIES else "RUNNING"}

    def route_result(state):
        return "persist_final_result" if state["status"] in ("APPROVED", "NEEDS_REVIEW") else "generate_lesson"

    async def persist_final_result(state):
        repository.finish(state["run_id"], state["status"])
        return {}

    graph = StateGraph(RunState)
    for name, node in [("load_context", load_context), ("generate_lesson", generate_lesson), ("validate_structure", validate_structure), ("evaluate_lesson", evaluate_lesson), ("persist_final_result", persist_final_result)]:
        graph.add_node(name, node)
    graph.add_edge(START, "load_context")
    graph.add_edge("load_context", "generate_lesson")
    graph.add_edge("generate_lesson", "validate_structure")
    graph.add_edge("validate_structure", "evaluate_lesson")
    graph.add_conditional_edges("evaluate_lesson", route_result, ["generate_lesson", "persist_final_result"])
    graph.add_edge("persist_final_result", END)
    return graph.compile()


async def execute_run(repository, ai, run_id):
    try:
        return await build_graph(repository, ai).ainvoke({"run_id": run_id}, {"recursion_limit": 30})
    except WorkflowError as exc:
        repository.finish(run_id, "ERROR", exc.public())
    except Exception:
        repository.finish(run_id, "ERROR", {"code": "WORKFLOW_FAILURE", "message": "The workflow stopped unexpectedly. No lesson was approved. Check the local setup and start a new run."})
    return None
