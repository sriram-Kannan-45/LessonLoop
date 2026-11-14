import asyncio
import json

from app.cli import calibrate
from app.content import MODEL_CHECK_IDS
from app.services.lesson_ai import LessonAI


def test_calibration_distinguishes_model_false_pass_from_python_release(settings, monkeypatch, tmp_path):
    async def optimistic_judge(self, lesson, *args, **kwargs):
        return {"checks": [{"check_id": key, "passed": True, "evidence": lesson["title"],
                            "reason": "Deliberately optimistic test judge.", "required_change": "",
                            "claim_ids": [], "missing_content": False} for key in MODEL_CHECK_IDS]}, {}

    monkeypatch.setattr(LessonAI, "evaluate", optimistic_judge)
    output = tmp_path / "calibration.json"
    asyncio.run(calibrate(settings, "holdout", output))
    report = json.loads(output.read_text(encoding="utf-8"))
    missing = next(row for row in report["cases"] if row["id"] == "missing-example")
    assert missing["false_model_approval"] is True
    assert missing["release_decision"] is False
    assert missing["false_approval"] is False
    assert any(not check["passed"] for check in missing["code_checks"])
    assert report["summary"]["false_model_approvals"] > report["summary"]["false_approvals"]
