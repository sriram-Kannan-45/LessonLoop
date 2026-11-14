import re

from pydantic import ValidationError

from app.content import ALL_CHECK_IDS, CLAIM_IDS, MODEL_CHECK_IDS, SOURCE_PACK, lesson_text
from app.lesson_schemas import CheckResult, Evaluation, Lesson
from app.services.lesson_ai import WorkflowError


def result(check_id, passed, evidence, reason, required_change="", claim_ids=None, missing=False):
    return CheckResult(check_id=check_id, passed=passed, evidence=evidence, reason=reason,
                       required_change=required_change, claim_ids=claim_ids or [], missing_content=missing).model_dump()


def structure_checks(draft, source_pack=SOURCE_PACK):
    try:
        lesson = Lesson.model_validate(draft)
    except ValidationError as exc:
        fields = ", ".join(".".join(map(str, err["loc"])) for err in exc.errors(include_input=False)[:8])
        return None, [result("STRUCTURE", False, "", "Required lesson structure is missing or malformed: " + fields,
                             "Return all required sections, a complete worked example, and exactly three questions with answers.", missing=True)]
    checks = [result("STRUCTURE", True, "Validated structured lesson", "All required sections and exactly three practice answers are present.")]
    allowed = {source["id"]: {claim for note in source["notes"] for claim in note["claim_ids"]} for source in source_pack["sources"]}
    valid = all(ref.source_id in allowed and all(claim in allowed[ref.source_id] or claim == "P01" and ref.source_id == "S4" for claim in ref.claim_ids) for ref in lesson.source_references)
    explicitly_illustrative = bool(re.search(r"\b(illustrative|fictional|invented)\b", lesson.worked_example.context + " " + lesson.worked_example.source_passage, re.IGNORECASE))
    valid = valid and explicitly_illustrative
    checks.append(result("SOURCES", valid, ", ".join(ref.source_id for ref in lesson.source_references),
                         "Source/claim identifiers match the pack and the teaching notice is explicitly labelled illustrative." if valid else "A source mapping is unknown or the invented notice lacks an explicit illustrative label.",
                         "" if valid else "Use approved source/claim IDs. Label worked_example.context as an illustrative or invented notice; prefer the reviewed Asha College teaching notice from the source pack."))
    return lesson, checks


def validate_evaluation(raw, lesson, expected_ids=None):
    try:
        evaluation = Evaluation.model_validate(raw)
    except ValidationError:
        raise WorkflowError("INVALID_EVALUATION", "Evaluator output did not match the required check schema. No lesson was approved.") from None
    ids = [check.check_id for check in evaluation.checks]
    if len(ids) != len(set(ids)) or set(ids) != set(expected_ids if expected_ids is not None else MODEL_CHECK_IDS):
        raise WorkflowError("INVALID_EVALUATION", "Evaluator omitted, duplicated, or invented a check ID. No lesson was approved.")
    text = " ".join(lesson_text(lesson).split())
    for check in evaluation.checks:
        if not check.evidence and check.evidence_path and not check.missing_content:
            selected = evidence_fields(lesson).get(check.evidence_path)
            if selected is None:
                raise WorkflowError("INVALID_EVIDENCE", "Evaluator selected a nonexistent lesson field. No lesson was approved.")
            # Python supplies the actual field text; the model never invents a quotation.
            check.evidence = selected[:2000]
        evidence = " ".join(check.evidence.split())
        if not set(check.claim_ids).issubset(CLAIM_IDS):
            raise WorkflowError("INVALID_EVIDENCE", "Evaluator cited an unknown source claim. No lesson was approved.")
        if check.passed and (check.missing_content or not evidence):
            raise WorkflowError("INVALID_EVIDENCE", "A passing check lacked lesson evidence. No lesson was approved.")
        if evidence and not evidence_supported(evidence, text):
            raise WorkflowError("INVALID_EVIDENCE", "Evaluator evidence was not an exact lesson excerpt. No lesson was approved.")
        if not check.passed and not check.required_change.strip():
            raise WorkflowError("INVALID_EVALUATION", "A failed check lacked an actionable correction. No lesson was approved.")
        if not check.passed and not evidence and not check.missing_content:
            raise WorkflowError("INVALID_EVIDENCE", "Evaluator failed a check without an excerpt or a missing-content explanation.")
    return [check.model_dump() for check in evaluation.checks]


def evidence_fields(value, prefix=""):
    fields = {}
    if isinstance(value, dict):
        for key, item in value.items():
            if key == "source_references":
                continue
            fields.update(evidence_fields(item, f"{prefix}.{key}" if prefix else key))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            fields.update(evidence_fields(item, f"{prefix}.{index}"))
    elif isinstance(value, str):
        fields[prefix] = value
    return fields


def evidence_supported(evidence, text):
    # A quote may use omission marks to cite several places in the lesson.
    # This verifies provenance, not the evaluator's interpretation of the quote.
    fragments = [part.strip() for part in re.split(r"\.{3}|…", evidence) if part.strip()]
    for fragment in fragments:
        if fragment not in text:
            return False
    return bool(fragments)


def releasable(checks):
    ids = [check["check_id"] for check in checks]
    return len(ids) == len(set(ids)) and set(ids) == set(ALL_CHECK_IDS) and all(check["passed"] is True for check in checks)


def diagnostics(draft):
    text = lesson_text(draft)
    sentences = [sentence.split() for sentence in re.split(r"[.!?]+", text) if sentence.strip()]
    return {"word_count": len(text.split()), "sentences_over_25_words": sum(len(s) > 25 for s in sentences),
            "note": "Diagnostics only. Neither word count nor sentence length decides approval."}
