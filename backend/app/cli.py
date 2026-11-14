"""Local assessment utilities. Never prints keys or raw provider exceptions."""
import argparse
import asyncio
import json
from pathlib import Path

import httpx

from app.config import Settings
from app.content import PROMPTS, RUBRIC, SOURCE_PACK, canonical_hash
from app.dataset import DATASET_VERSION, labelled_examples
from app.db import Repository, now
from app.exports import audit_report, markdown_lesson
from app.quality import releasable, structure_checks, validate_evaluation
from app.services.lesson_ai import EVALUATION_GROUPS, LessonAI, WorkflowError


async def calibrate(settings, split, output):
    repo = Repository(settings.database_path)
    if (any(row["status"] == "RUNNING" for row in repo.history(50)["items"])
            or any(row["status"] == "RUNNING" for row in repo.memory()["experiments"])):
        raise WorkflowError("WORKSPACE_BUSY", "Wait for active runs and prompt comparisons before starting evaluator calibration.")
    ai = LessonAI(settings)
    report = {"dataset_version": DATASET_VERSION, "split": split, "started_at": now(), "provider": "gemini",
              "model": ai.evaluator_model, "rubric_version": RUBRIC["version"], "rubric_sha256": RUBRIC["content_sha256"],
              "evaluator_prompt_version": PROMPTS["evaluator_version"], "source_pack_version": SOURCE_PACK["version"],
              "evaluation_groups": [list(group) for group in EVALUATION_GROUPS],
              "provider_note": "Model field is the configured Gemini primary. Actual provider/model per group is in usage; quota fallback can use Groq.",
              "cases": [], "note": "Small authored dataset. Holdout is excluded from prompt comparisons. Report actual disagreements; do not treat format validation as correctness."}
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    for example in labelled_examples(None if split == "all" else split):
        row = {"id": example["id"], "split": example["split"], "description": example["description"], "content_sha256": example["content_sha256"], "expected": example["expected"]}
        row["technical_retries"] = []
        row["provider_events"] = []
        try:
            raw, usage = await ai.evaluate(example["lesson"], SOURCE_PACK, RUBRIC, on_retry=lambda number, code: row["technical_retries"].append({"number": number, "code": code}), on_provider_event=row["provider_events"].append)
            checks = validate_evaluation(raw, example["lesson"])
            _, code_checks = structure_checks(example["lesson"])
            release = releasable([*code_checks, *checks])
            actual = {check["check_id"]: check["passed"] for check in checks}
            disagreements = [{"check_id": check_id, "expected": expected, "actual": actual[check_id], "kind": "false_pass" if actual[check_id] else "false_rejection"} for check_id, expected in example["expected"].items() if actual[check_id] != expected]
            row.update(checks=checks, code_checks=code_checks, release_decision=release, usage=usage, disagreements=disagreements,
                       false_model_approval=any(expected is False for expected in example["expected"].values()) and all(actual.values()),
                       false_approval=any(expected is False for expected in example["expected"].values()) and release,
                       false_rejection=all(example["expected"].values()) and any(not actual[key] for key in example["expected"]))
        except WorkflowError as exc:
            row["error"] = exc.public()
        report["cases"].append(row)
        path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        print(json.dumps({"case": row["id"], "status": "ERROR" if "error" in row else "evaluated", "disagreements": row.get("disagreements", []), "error": row.get("error")}), flush=True)
    cases = report["cases"]
    report["finished_at"] = now()
    report["summary"] = {"cases": len(cases), "evaluated": sum("checks" in case for case in cases),
                         "technical_errors": sum("error" in case for case in cases),
                         "false_approvals": sum(case.get("false_approval", False) for case in cases),
                         "false_model_approvals": sum(case.get("false_model_approval", False) for case in cases),
                         "false_rejections": sum(case.get("false_rejection", False) for case in cases),
                         "per_check_false_passes": sum(item["kind"] == "false_pass" for case in cases for item in case.get("disagreements", [])),
                         "per_check_false_rejections": sum(item["kind"] == "false_rejection" for case in cases for item in case.get("disagreements", []))}
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report["summary"]))


def export_run(settings, run_id, output):
    repo = Repository(settings.database_path)
    run = repo.get_run(run_id)
    if not run:
        raise WorkflowError("NOT_FOUND", "The requested run does not exist.")
    folder = Path(output)
    folder.mkdir(parents=True, exist_ok=True)
    audit = audit_report(repo, run_id)
    (folder / "audit.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
    (folder / "run-metadata.json").write_text(json.dumps({key: value for key, value in run.items() if key not in ("attempts", "final_lesson", "review_draft", "source_snapshot", "rubric_snapshot")}, ensure_ascii=False, indent=2), encoding="utf-8")
    lesson = run["final_lesson"] or run["review_draft"]
    if lesson:
        filename = "lesson-approved.md" if run["status"] == "APPROVED" else "lesson-review-not-approved.md"
        (folder / filename).write_text(markdown_lesson(lesson, run["status"], run_id, run["source_snapshot"]["sources"]), encoding="utf-8")
    lines = ["# Rejection history", "", f"Run: `{run_id}`. Final status: **{run['status']}**.", ""]
    for attempt in run["attempts"]:
        lines += [f"## Draft {attempt['number']} — {attempt['status']}", ""]
        if attempt["original_draft"]:
            lines += ["Development factual-error injection was applied to this draft. Original and altered text are in the audit.", ""]
        for check in attempt["evaluation"] or []:
            if not check["passed"]:
                lines += [f"### {check['check_id']}", "", "Reason: " + check["reason"], "", "Evidence: " + (check["evidence"] or "Missing content; no quote."), "", "Required correction: " + check["required_change"], ""]
        if attempt["evaluation"] and all(item["passed"] for item in attempt["evaluation"]):
            lines += ["All mandatory checks passed.", ""]
    (folder / "rejection-log.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"run_id": run_id, "status": run["status"], "output": str(folder.resolve())}))


def main():
    parser = argparse.ArgumentParser(description="LessonLoop assessment tools")
    sub = parser.add_subparsers(dest="command", required=True)
    calibration = sub.add_parser("calibrate")
    calibration.add_argument("--split", choices=["calibration", "holdout", "all"], default="calibration")
    calibration.add_argument("--out", default="../submission/evaluator-calibration.json")
    export = sub.add_parser("export")
    export.add_argument("run_id")
    export.add_argument("--out", default="../submission/final-lesson")
    run = sub.add_parser("run")
    run.add_argument("--demo-error", action="store_true")
    run.add_argument("--wait", action="store_true")
    args = parser.parse_args()
    settings = Settings()
    try:
        if args.command == "calibrate":
            asyncio.run(calibrate(settings, args.split, args.out))
        elif args.command == "export":
            export_run(settings, args.run_id, args.out)
        elif args.command == "run":
            base = f"http://127.0.0.1:{settings.backend_port}/api"
            with httpx.Client(timeout=15) as client:
                response = client.post(base + "/runs", json={"demo_error": args.demo_error})
                if response.status_code != 202:
                    print(response.text)
                    raise SystemExit(1)
                run_id = response.json()["id"]
                print(json.dumps({"id": run_id, "status": "RUNNING"}), flush=True)
                if args.wait:
                    import time
                    previous_stage = None
                    for _ in range(600):
                        current = client.get(base + "/runs/" + run_id).json()
                        if current["status"] != "RUNNING":
                            print(json.dumps({"id": run_id, "status": current["status"], "attempts": current["attempt_count"], "error": current["error"]}))
                            return
                        stage = (current["stage"], current["attempt_count"])
                        if stage != previous_stage:
                            print(json.dumps({"id": run_id, "stage": stage[0], "saved_drafts": stage[1]}), flush=True)
                            previous_stage = stage
                        time.sleep(2)
                    raise WorkflowError("WAIT_LIMIT", "The CLI wait limit ended. Inspect the run in the app; no status was invented.")
    except WorkflowError as exc:
        print(json.dumps(exc.public()))
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
