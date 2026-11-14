import asyncio
import copy
import json
from unittest.mock import AsyncMock

import httpx
import pytest
from fastapi.testclient import TestClient

from app import topics, workflow
from app.content import MODEL_CHECK_IDS, PROMPTS, SOURCE_PACK
from app.dataset import BASE
from app.db import Repository
from app.lesson_schemas import RunRequest
from app.main import create_app
from app.quality import releasable, source_claim_mappings, structure_checks, validate_evaluation
from app.services.lesson_ai import LessonAI, WorkflowError, evaluation_groups
from app.services.groq import request_groq as REAL_GROQ_REQUEST

REAL_COLLECT = topics.collect_topic_references
REAL_EVALUATE = LessonAI.evaluate
REAL_HTTP_CLIENT = httpx.AsyncClient


def passage(topic):
    return f"{topic} is the subject of this authored test reference. It describes the central concepts and their relationships in plain words. This is a deterministic fixture, not a real live source."


def pack(topic):
    notes = [{"id": "N1", "text": passage(topic), "claim_ids": ["T01"]}]
    return {"id": "auto", "version": "test-topic-" + topic, "topic": topic, "status": "retrieved", "review_note": "Mocked topic source.",
            "sources": [{"id": "S1", "title": topic, "url": "https://en.wikipedia.org/wiki/Test", "accessed_at": "2026-11-14", "notes": notes}],
            "claims": [{"id": "T01", "note_ids": ["N1"], "source_ids": ["S1"]}]}


def lesson_for(topic, source_pack):
    text = source_pack["sources"][0]["notes"][0]["text"]
    return {"title": "Learning " + topic, "learning_objectives": ["Explain " + topic, "Apply its main idea"],
            "prerequisites": "No prior specialist knowledge is required.", "what_it_is": text,
            "why_it_matters": "This test lesson connects the topic to a familiar everyday situation.",
            "how_it_works": ["Read the supplied facts.", "Identify their relationship.", "Apply them to the example."],
            "worked_example": {"context": "Illustrative teaching example for " + topic, "learner_question": "What does the reference explain?",
                               "source_passage": text, "retrieved_information": text, "supported_answer": "It explains " + topic,
                               "missing_information_question": "Which local classroom teaches this next week?", "missing_information_answer": "The reference does not give a classroom or timetable."},
            "limitations": "The reference is introductory and does not cover every specialist detail.",
            "recap": ["Define the subject.", "Connect its ideas.", "Use the reference facts."],
            "practice_questions": [{"question": "What subject is introduced?", "answer": topic}, {"question": "Where do the facts come from?", "answer": "The supplied reference."}, {"question": "Is a timetable supplied?", "answer": "No timetable is supplied."}],
            "source_references": [{"source_id": source["id"], "claim_ids": [source["notes"][0]["claim_ids"][0]]} for source in source_pack["sources"]]}


def verdicts(lesson, ids, claim="T01"):
    return {"checks": [{"check_id": key, "passed": True, "evidence": lesson["title"], "reason": "Mocked topic test judgment.",
                        "required_change": "", "claim_ids": [claim], "missing_content": False} for key in ids]}


class TopicAI:
    generator_model = evaluator_model = "mocked-topic-model"

    def __init__(self):
        self.contexts = []

    async def generate(self, context, *args, **kwargs):
        self.contexts.append(copy.deepcopy(context))
        return lesson_for(context["topic"], context["source_pack"]), {"provider": "gemini", "model": self.generator_model}

    async def evaluate(self, lesson, source_pack, rubric, *args, **kwargs):
        ids = [check["id"] for check in rubric["checks"] if check["evaluator"] == "model"]
        claim = source_pack["claims"][0]["id"]
        return verdicts(lesson, ids, claim), {"provider": "gemini", "model": self.evaluator_model}


def wiki_transport(monkeypatch, query_topic, empty=False, status=200):
    requests = []

    def handle(request):
        requests.append(request)
        assert request.url.host == "en.wikipedia.org"
        assert request.url.path == "/w/api.php"
        if status != 200:
            return httpx.Response(status)
        if request.url.params.get("list") == "search":
            return httpx.Response(200, json={"query": {"search": [] if empty else [{"pageid": 123, "title": query_topic}]}})
        assert request.url.params["exintro"] == "1" and request.url.params["exlimit"] == "3"
        return httpx.Response(200, json={"query": {"pages": [{"pageid": 123, "title": query_topic, "extract": passage(query_topic), "revisions": [{"revid": 789, "timestamp": "2026-11-14T00:00:00Z"}]}]}})

    def client(**kwargs):
        return REAL_HTTP_CLIENT(**kwargs, transport=httpx.MockTransport(handle))

    monkeypatch.setattr(topics.httpx, "AsyncClient", client)
    monkeypatch.setattr(workflow, "collect_topic_references", REAL_COLLECT)
    return requests


@pytest.mark.parametrize("topic", ["Photosynthesis", "Python programming", "French Revolution"])
def test_any_subject_gets_its_own_references_prompt_rubric_and_saved_lesson(settings, monkeypatch, topic):
    settings.gemini_api_key = "fake-test-key"
    requests = wiki_transport(monkeypatch, topic)
    ai = TopicAI()
    with TestClient(create_app(settings=settings, ai=ai)) as client:
        workspace = client.get("/api/workspace").json()
        assert workspace["topic_mode"] == "dynamic" and workspace["source_pack"]["id"] == "auto"
        assert workspace["rubric"]["kind"] == "general"
        result = client.post("/api/runs", json={"topic": topic})
        assert result.status_code == 202
        run_id = result.json()["id"]
        for _ in range(150):
            run = client.get("/api/runs/" + run_id).json()
            if run["status"] != "RUNNING":
                break
        assert run["status"] == "APPROVED"
        assert run["final_lesson"]["title"] == "Learning " + topic
        assert run["source_snapshot"]["topic"] == topic
        assert run["source_snapshot"]["id"] == "auto"
        assert run["source_snapshot"]["sources"][0]["revision_id"] == 789
        assert "not a human-reviewed" in run["source_snapshot"]["review_note"]
        assert run["rubric_snapshot"]["kind"] == "general"
        assert "RAG_DEFINITION" not in {check["check_id"] for check in run["attempts"][0]["evaluation"]}
        assert len(run["attempts"][0]["evaluation"]) == 14
        assert run["generator_prompt_version"] == PROMPTS["topic_generator_version"]
        assert ai.contexts[0]["instructions"] == PROMPTS["topic_generator"]
        assert ai.contexts[0]["memory"] == []
        events = client.get(f"/api/runs/{run_id}/events").json()["events"]
        stages = [event["stage"] for event in events]
        assert stages.index("REFERENCES_READY") < stages.index("GENERATING")
        exported = client.get(f"/api/runs/{run_id}/export?format=markdown").text
        assert "Learning " + topic in exported and "en.wikipedia.org" in exported
    repo = Repository(settings.database_path)
    saved = repo.get_run(run_id)
    assert saved["source_snapshot"] == run["source_snapshot"]
    with pytest.raises(ValueError):
        repo.freeze_topic_references(run_id, pack(topic))
    assert len(requests) == 2


@pytest.mark.parametrize("empty,status,code", [(True, 200, "REFERENCES_NOT_FOUND"), (False, 503, "REFERENCES_UNAVAILABLE")])
def test_reference_failure_stops_without_inventing_sources_or_calling_generation(settings, monkeypatch, empty, status, code):
    settings.gemini_api_key = "fake-test-key"
    wiki_transport(monkeypatch, "An arbitrary new topic", empty=empty, status=status)
    ai = TopicAI()
    with TestClient(create_app(settings=settings, ai=ai)) as client:
        run_id = client.post("/api/runs", json={"topic": "An arbitrary new topic"}).json()["id"]
        for _ in range(100):
            run = client.get("/api/runs/" + run_id).json()
            if run["status"] != "RUNNING":
                break
        assert run["status"] == "ERROR" and run["error"]["code"] == code
        assert run["attempt_count"] == 0 and run["final_lesson"] is None
        assert ai.contexts == []


def test_older_clients_can_request_other_subjects_without_the_old_whitelist(settings, monkeypatch):
    settings.gemini_api_key = "fake-test-key"
    wiki_transport(monkeypatch, "Biology")
    with TestClient(create_app(settings=settings, ai=TopicAI())) as client:
        response = client.post("/api/runs", json={"topic": "Biology", "reference_pack_id": "rag-primary-v1"})
        assert response.status_code == 202
        for _ in range(100):
            run = client.get("/api/runs/" + response.json()["id"]).json()
            if run["status"] != "RUNNING":
                break
        assert run["source_snapshot"]["id"] == "auto"
        assert run["status"] == "APPROVED"


def test_reference_requests_never_fetch_arbitrary_topic_urls(monkeypatch):
    requests = wiki_transport(monkeypatch, "A topic")
    result = asyncio.run(REAL_COLLECT("https://127.0.0.1/private"))
    assert result["topic"] == "https://127.0.0.1/private"
    assert all(request.url.host == "en.wikipedia.org" for request in requests)


def test_dynamic_claims_and_release_use_the_run_pack_and_rubric():
    source_pack = pack("Biology")
    rubric = topics.topic_rubric("Biology")
    lesson = lesson_for("Biology", source_pack)
    _, code_checks = structure_checks(lesson, source_pack)
    ids = [item["id"] for item in rubric["checks"] if item["evaluator"] == "model"]
    raw = verdicts(lesson, ids)
    validated = validate_evaluation(raw, lesson, expected_ids=ids, source_pack=source_pack)
    assert releasable(code_checks + validated, rubric)
    assert not releasable(code_checks + validated)  # The old RAG rubric cannot approve this subject.
    raw["checks"][0]["claim_ids"] = ["unknown"]
    with pytest.raises(WorkflowError):
        validate_evaluation(raw, lesson, expected_ids=ids, source_pack=source_pack)
    source_pack["sources"][0]["id"] = "S4"
    assert "P01" not in source_claim_mappings(source_pack)["S4"]


def test_real_evaluator_method_uses_dynamic_groups_and_subject_instructions(settings, monkeypatch):
    settings.gemini_api_key = "fake-test-key"
    settings.gemini_model = "mocked-model"
    source_pack = pack("Photosynthesis")
    rubric = topics.topic_rubric("Photosynthesis")
    lesson = lesson_for("Photosynthesis", source_pack)
    requested = []

    async def primary(self, model, instructions, data, schema, *args, **kwargs):
        assert instructions.startswith(PROMPTS["topic_evaluator"])
        assert data["topic"] == "Photosynthesis"
        requested.append(data["expected_check_ids"])
        return verdicts(lesson, data["expected_check_ids"]), {}

    monkeypatch.setattr(LessonAI, "_call_gemini", primary)
    raw, usage = asyncio.run(REAL_EVALUATE(LessonAI(settings), lesson, source_pack, rubric))
    assert len(raw["checks"]) == 12 and len(requested) == 3
    assert requested == [list(group) for group in evaluation_groups(rubric)]
    assert usage["evaluation_groups"] == 3


def test_rag_memory_and_failure_counts_do_not_leak_to_other_subjects(settings):
    repo = Repository(settings.database_path)
    support = repo.create_run(RunRequest(reference_pack_id="rag-primary-v1"), "mocked", "mocked")
    repo.finish(support, "ERROR")
    experiment = repo.create_experiment("TERMS_EXPLAINED", "Explain RAG retrieval before its first use.", [support], "mocked-scope-test")
    repo.finish_experiment(experiment, "ACTIVATED", [{"mocked": True}])
    new = repo.create_run(RunRequest(topic="Photosynthesis"), "mocked", "mocked")
    assert repo.get_run(new)["selected_memory"] == []
    assert "Explain RAG retrieval before its first use." not in repo.prompt(repo.get_run(new)["generator_prompt_version"])["instructions"]
    repo.finish(new, "ERROR")
    note = repo.feedback(new, "confusing_language", "Mocked subject-specific observation.")
    repo.review_feedback(note["id"], "verified", "Mocked reviewed photosynthesis terminology failure.")
    assert new not in repo.supporting_runs("TERMS_EXPLAINED")


@pytest.mark.parametrize("json_mode", [False, True])
def test_topic_provider_schema_selects_existing_evidence_without_prescribing_verdicts(settings, monkeypatch, json_mode):
    from app.lesson_schemas import Evaluation
    from app.quality import evidence_fields
    from app.services import groq
    from app.services.lesson_ai import response_schema

    settings.groq_api_key = "fake-topic-key"
    source_pack = pack("Biology")
    lesson = lesson_for("Biology", source_pack)
    ids = list(evaluation_groups(topics.topic_rubric("Biology"))[0])
    data = {"evidence_mode": "field_selection", "expected_check_ids": ids,
            "allowed_evidence_paths": list(evidence_fields(lesson)), "approved_reference_pack": source_pack}
    raw = verdicts(lesson, ids)
    for check in raw["checks"]:
        check.update(evidence="", evidence_path="what_it_is")

    def handle(request):
        body = json.loads(request.content)
        assert body["max_completion_tokens"] == 900
        if json_mode:
            payload = json.loads(body["messages"][1]["content"].split("\n", 1)[1])
            props = payload["required_output_schema"]["$defs"]["CheckResult"]["properties"]
        else:
            props = body["response_format"]["json_schema"]["schema"]["properties"]["checks"]["items"]["properties"]
        assert props["evidence"]["enum"] == [""]
        assert "what_it_is" in props["evidence_path"]["enum"]
        assert props["check_id"]["enum"] == ids
        assert props["claim_ids"]["items"]["enum"] == [item["id"] for item in source_pack["claims"]]
        assert props["passed"] == {"type": "boolean"} or props["passed"]["type"] == "boolean"
        assert "enum" not in props["passed"]
        return httpx.Response(200, json={"choices": [{"message": {"content": json.dumps(raw)}, "finish_reason": "stop"}]})

    monkeypatch.setattr(groq.httpx, "AsyncClient", lambda **kwargs: REAL_HTTP_CLIENT(**kwargs, transport=httpx.MockTransport(handle)))
    value, _ = asyncio.run(REAL_GROQ_REQUEST(settings, "mocked-model", "Return JSON", data, Evaluation, json_mode))
    checks = validate_evaluation(value, lesson, expected_ids=ids, source_pack=source_pack)
    assert all(check["evidence"] == lesson["what_it_is"] for check in checks)
    # Legacy runs keep their original output contract.
    assert "enum" not in response_schema(Evaluation, {})["$defs"]["CheckResult"]["properties"]["evidence"]
