import hashlib
import json
from pathlib import Path

CONTENT_DIR = Path(__file__).resolve().parents[1] / "content"


def load_json(name: str):
    return json.loads((CONTENT_DIR / name).read_text(encoding="utf-8"))


def canonical_hash(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


SOURCE_PACK = load_json("rag_sources.json")
for source in SOURCE_PACK["sources"]:
    source["notes_sha256"] = canonical_hash(source["notes"])
SOURCE_PACK["content_sha256"] = canonical_hash(SOURCE_PACK)
RUBRIC = load_json("rubric.json")
RUBRIC["content_sha256"] = canonical_hash(RUBRIC)
PROMPTS = load_json("prompts.json")
MODEL_CHECK_IDS = [check["id"] for check in RUBRIC["checks"] if check["evaluator"] == "model"]
ALL_CHECK_IDS = [check["id"] for check in RUBRIC["checks"]]
CLAIM_IDS = {claim["id"] for claim in SOURCE_PACK["claims"]}


def supports_topic(topic: str, pack_id: str) -> bool:
    return pack_id == SOURCE_PACK["id"] and " ".join(topic.lower().split()) in SOURCE_PACK["approved_topics"]


def lesson_text(value) -> str:
    if isinstance(value, dict):
        return "\n".join(lesson_text(item) for item in value.values())
    if isinstance(value, list):
        return "\n".join(lesson_text(item) for item in value)
    return str(value)
