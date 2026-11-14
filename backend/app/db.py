import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from app.content import PROMPTS, RUBRIC, SOURCE_PACK


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def identifier() -> str:
    return uuid4().hex


def encode(value):
    return json.dumps(value, ensure_ascii=False)


def decode_row(row):
    if row is None:
        return None
    result = dict(row)
    for key in list(result):
        if key.endswith("_json"):
            value = result.pop(key)
            result[key[:-5]] = json.loads(value) if value is not None else None
    return result


SCHEMA = """
CREATE TABLE IF NOT EXISTS reference_packs(version TEXT PRIMARY KEY, content_json TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS prompt_versions(
 version TEXT PRIMARY KEY, instructions TEXT NOT NULL, parent TEXT REFERENCES prompt_versions(version),
 active INTEGER NOT NULL DEFAULT 0, memory_ids_json TEXT NOT NULL DEFAULT '[]', created_at TEXT NOT NULL);
CREATE UNIQUE INDEX IF NOT EXISTS one_active_prompt ON prompt_versions(active) WHERE active=1;
CREATE TABLE IF NOT EXISTS runs(
 id TEXT PRIMARY KEY, topic TEXT NOT NULL, learner_profile TEXT NOT NULL,
 status TEXT NOT NULL, stage TEXT NOT NULL, started_at TEXT NOT NULL, finished_at TEXT,
 source_pack_version TEXT NOT NULL REFERENCES reference_packs(version), source_snapshot_json TEXT NOT NULL,
 rubric_version TEXT NOT NULL, rubric_snapshot_json TEXT NOT NULL,
 generator_prompt_version TEXT NOT NULL REFERENCES prompt_versions(version), evaluator_prompt_version TEXT NOT NULL,
 generator_model TEXT NOT NULL, evaluator_model TEXT NOT NULL, provider TEXT NOT NULL DEFAULT 'gemini',
 selected_memory_json TEXT NOT NULL, retry_count INTEGER NOT NULL DEFAULT 0 CHECK(retry_count BETWEEN 0 AND 2),
 demo_error INTEGER NOT NULL DEFAULT 0, error_json TEXT);
CREATE UNIQUE INDEX IF NOT EXISTS one_active_run ON runs((1)) WHERE status='RUNNING';
CREATE INDEX IF NOT EXISTS run_history ON runs(started_at DESC);
CREATE TABLE IF NOT EXISTS attempts(
 id INTEGER PRIMARY KEY AUTOINCREMENT, run_id TEXT NOT NULL REFERENCES runs(id),
 number INTEGER NOT NULL CHECK(number BETWEEN 1 AND 3), created_at TEXT NOT NULL,
 original_draft_json TEXT, draft_json TEXT NOT NULL, evaluation_json TEXT,
 status TEXT NOT NULL, generation_usage_json TEXT, evaluator_usage_json TEXT,
 diagnostics_json TEXT NOT NULL, UNIQUE(run_id,number));
CREATE TABLE IF NOT EXISTS check_results(
 attempt_id INTEGER NOT NULL REFERENCES attempts(id), check_id TEXT NOT NULL,
 passed INTEGER NOT NULL CHECK(passed IN (0,1)), result_json TEXT NOT NULL,
 PRIMARY KEY(attempt_id,check_id));
CREATE TABLE IF NOT EXISTS workflow_events(
 sequence INTEGER PRIMARY KEY AUTOINCREMENT, run_id TEXT NOT NULL REFERENCES runs(id),
 stage TEXT NOT NULL, message TEXT NOT NULL, details_json TEXT NOT NULL, created_at TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS run_events ON workflow_events(run_id,sequence);
CREATE TABLE IF NOT EXISTS failure_observations(
 id INTEGER PRIMARY KEY AUTOINCREMENT, run_id TEXT NOT NULL REFERENCES runs(id), category TEXT NOT NULL,
 evidence TEXT NOT NULL, created_at TEXT NOT NULL, UNIQUE(run_id,category));
CREATE TABLE IF NOT EXISTS human_feedback(
 id TEXT PRIMARY KEY, run_id TEXT NOT NULL REFERENCES runs(id), category TEXT NOT NULL,
 message TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'unverified', review_note TEXT,
 created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS memory_instructions(
 id TEXT PRIMARY KEY, topic TEXT NOT NULL, learner_profile TEXT NOT NULL, category TEXT NOT NULL,
 instruction TEXT NOT NULL, status TEXT NOT NULL, origin TEXT NOT NULL,
 supporting_runs_json TEXT NOT NULL, prompt_version TEXT, created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS improvement_experiments(
 id TEXT PRIMARY KEY, category TEXT NOT NULL, status TEXT NOT NULL, stage TEXT NOT NULL,
 baseline_prompt_version TEXT NOT NULL REFERENCES prompt_versions(version),
 candidate_prompt_version TEXT NOT NULL REFERENCES prompt_versions(version),
 memory_id TEXT NOT NULL REFERENCES memory_instructions(id), dataset_version TEXT NOT NULL,
 results_json TEXT NOT NULL DEFAULT '[]', error_json TEXT, created_at TEXT NOT NULL, finished_at TEXT);
CREATE UNIQUE INDEX IF NOT EXISTS one_active_experiment ON improvement_experiments((1)) WHERE status='RUNNING';
"""


class Repository:
    def __init__(self, path: Path | str):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connection() as conn:
            conn.executescript(SCHEMA)
            conn.execute("INSERT OR IGNORE INTO reference_packs VALUES(?,?)", (SOURCE_PACK["version"], encode(SOURCE_PACK)))
            conn.execute("INSERT OR IGNORE INTO prompt_versions(version,instructions,active,created_at) VALUES(?,?,?,?)",
                         (PROMPTS["generator_version"], PROMPTS["generator"], 1 if not conn.execute("SELECT 1 FROM prompt_versions WHERE active=1").fetchone() else 0, now()))

    @contextmanager
    def connection(self):
        conn = sqlite3.connect(self.path, timeout=5)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("PRAGMA journal_mode=WAL")
        try:
            with conn:
                yield conn
        finally:
            conn.close()

    def interrupt_active(self):
        message = {"code": "PROCESS_RESTARTED", "message": "The local server stopped before this work finished. Start a new run; previous drafts are preserved."}
        with self.connection() as conn:
            active = conn.execute("SELECT id FROM runs WHERE status='RUNNING'").fetchall()
            conn.execute("UPDATE runs SET status='INTERRUPTED',stage='INTERRUPTED',finished_at=?,error_json=? WHERE status='RUNNING'", (now(), encode(message)))
            conn.execute("UPDATE improvement_experiments SET status='INTERRUPTED',stage='INTERRUPTED',finished_at=?,error_json=? WHERE status='RUNNING'", (now(), encode(message)))
            for row in active:
                conn.execute("INSERT INTO workflow_events(run_id,stage,message,details_json,created_at) VALUES(?,?,?,?,?)", (row["id"], "INTERRUPTED", message["message"], "{}", now()))

    def active_prompt(self):
        with self.connection() as conn:
            return decode_row(conn.execute("SELECT * FROM prompt_versions WHERE active=1").fetchone())

    def prompt(self, version):
        with self.connection() as conn:
            return decode_row(conn.execute("SELECT * FROM prompt_versions WHERE version=?", (version,)).fetchone())

    def selected_memory(self, prompt, topic, learner):
        with self.connection() as conn:
            rows = conn.execute("SELECT * FROM memory_instructions WHERE status='active' AND topic=? AND learner_profile=? ORDER BY created_at DESC LIMIT 4", (topic, learner)).fetchall()
        return [decode_row(row) for row in rows if row["id"] in prompt["memory_ids"]]

    def create_run(self, request, generator_model, evaluator_model):
        prompt = self.active_prompt()
        memory = self.selected_memory(prompt, "Introduction to RAG", request.learner_profile)
        run_id = identifier()
        with self.connection() as conn:
            conn.execute("""INSERT INTO runs(id,topic,learner_profile,status,stage,started_at,
             source_pack_version,source_snapshot_json,rubric_version,rubric_snapshot_json,
             generator_prompt_version,evaluator_prompt_version,generator_model,evaluator_model,
             selected_memory_json,demo_error) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                         (run_id, request.topic, request.learner_profile, "RUNNING", "QUEUED", now(), SOURCE_PACK["version"], encode(SOURCE_PACK), RUBRIC["version"], encode(RUBRIC), prompt["version"], PROMPTS["evaluator_version"], generator_model, evaluator_model, encode(memory), int(request.demo_error)))
        self.event(run_id, "QUEUED", "Run accepted. Up to three drafts; every mandatory check must pass.")
        return run_id

    def event(self, run_id, stage, message, details=None):
        with self.connection() as conn:
            conn.execute("INSERT INTO workflow_events(run_id,stage,message,details_json,created_at) VALUES(?,?,?,?,?)", (run_id, stage, message, encode(details or {}), now()))
            conn.execute("UPDATE runs SET stage=? WHERE id=? AND status='RUNNING'", (stage, run_id))

    def events(self, run_id, after=0, limit=100):
        with self.connection() as conn:
            return [decode_row(row) for row in conn.execute("SELECT * FROM workflow_events WHERE run_id=? AND sequence>? ORDER BY sequence LIMIT ?", (run_id, after, limit))]

    def add_attempt(self, run_id, number, draft, original, usage, diagnostics):
        with self.connection() as conn:
            cursor = conn.execute("INSERT INTO attempts(run_id,number,created_at,original_draft_json,draft_json,status,generation_usage_json,diagnostics_json) VALUES(?,?,?,?,?,?,?,?)", (run_id, number, now(), encode(original) if original else None, encode(draft), "GENERATED", encode(usage), encode(diagnostics)))
            conn.execute("UPDATE runs SET retry_count=? WHERE id=?", (number - 1, run_id))
            return cursor.lastrowid

    def evaluate_attempt(self, attempt_id, results, usage, approved):
        with self.connection() as conn:
            cursor = conn.execute("UPDATE attempts SET evaluation_json=?, evaluator_usage_json=?,status=? WHERE id=? AND evaluation_json IS NULL", (encode(results), encode(usage), "APPROVED" if approved else "REJECTED", attempt_id))
            if cursor.rowcount != 1:
                raise ValueError("An evaluated attempt cannot be overwritten.")
            for result in results:
                conn.execute("INSERT INTO check_results VALUES(?,?,?,?)", (attempt_id, result["check_id"], int(result["passed"]), encode(result)))
                if not result["passed"]:
                    run_id = conn.execute("SELECT run_id FROM attempts WHERE id=?", (attempt_id,)).fetchone()[0]
                    conn.execute("INSERT OR IGNORE INTO failure_observations(run_id,category,evidence,created_at) VALUES(?,?,?,?)", (run_id, result["check_id"], result["reason"], now()))

    def finish(self, run_id, status, error=None):
        with self.connection() as conn:
            conn.execute("UPDATE runs SET status=?,stage=?,finished_at=?,error_json=? WHERE id=?", (status, status, now(), encode(error) if error else None, run_id))
        self.event(run_id, status, {"APPROVED": "All mandatory checks passed. Lesson released.", "NEEDS_REVIEW": "Three drafts used. Unresolved failures remain; this lesson is not approved.", "ERROR": "A technical problem stopped the run. Previous drafts remain available.", "INTERRUPTED": "The run was interrupted; drafts are preserved."}.get(status, status), error)

    def get_run(self, run_id):
        with self.connection() as conn:
            run = decode_row(conn.execute("SELECT * FROM runs WHERE id=?", (run_id,)).fetchone())
            if run is None:
                return None
            run["attempts"] = [decode_row(row) for row in conn.execute("SELECT * FROM attempts WHERE run_id=? ORDER BY number", (run_id,))]
            run["feedback"] = [decode_row(row) for row in conn.execute("SELECT * FROM human_feedback WHERE run_id=? ORDER BY created_at", (run_id,))]
        run["final_lesson"] = run["attempts"][-1]["draft"] if run["status"] == "APPROVED" and run["attempts"] else None
        run["review_draft"] = run["attempts"][-1]["draft"] if run["status"] != "APPROVED" and run["attempts"] else None
        run["attempt_count"] = len(run["attempts"])
        return run

    def history(self, limit=20, offset=0):
        with self.connection() as conn:
            rows = conn.execute("SELECT r.id,r.topic,r.status,r.stage,r.started_at,r.finished_at,(SELECT COUNT(*) FROM attempts a WHERE a.run_id=r.id) AS attempt_count FROM runs r ORDER BY r.started_at DESC LIMIT ? OFFSET ?", (limit, offset)).fetchall()
            return {"items": [dict(row) for row in rows], "total": conn.execute("SELECT COUNT(*) FROM runs").fetchone()[0], "limit": limit, "offset": offset}

    def feedback(self, run_id, category, message):
        feedback_id = identifier()
        with self.connection() as conn:
            conn.execute("INSERT INTO human_feedback(id,run_id,category,message,created_at) VALUES(?,?,?,?,?)", (feedback_id, run_id, category, message, now()))
        return {"id": feedback_id, "status": "unverified", "message": "Feedback saved as an unverified observation. It will not enter active prompts automatically."}

    def review_feedback(self, feedback_id, action, note):
        with self.connection() as conn:
            row = conn.execute("SELECT * FROM human_feedback WHERE id=?", (feedback_id,)).fetchone()
            if not row:
                return None
            conn.execute("UPDATE human_feedback SET status=?,review_note=? WHERE id=?", (action, note, feedback_id))
            # A human review is evidence, never permission to execute the feedback text.
            categories = {"confusing_language": "TERMS_EXPLAINED", "factual_issue": "GROUNDED_CLAIMS", "missing_example": "WORKED_EXAMPLE", "correction": "GROUNDED_CLAIMS"}
            if action == "verified":
                conn.execute("INSERT OR IGNORE INTO failure_observations(run_id,category,evidence,created_at) VALUES(?,?,?,?)", (row["run_id"], categories[row["category"]], "Human-reviewed observation: " + note, now()))
        return {"id": feedback_id, "status": action, "review_note": note}

    def memory(self):
        with self.connection() as conn:
            instructions = [decode_row(row) for row in conn.execute("SELECT * FROM memory_instructions ORDER BY created_at DESC")]
            failures = [dict(row) for row in conn.execute("SELECT f.category,COUNT(DISTINCT f.run_id) AS independent_runs FROM failure_observations f JOIN runs r ON r.id=f.run_id WHERE r.status!='RUNNING' GROUP BY f.category ORDER BY independent_runs DESC")]
            versions = [decode_row(row) for row in conn.execute("SELECT * FROM prompt_versions ORDER BY created_at DESC")]
            experiments = [decode_row(row) for row in conn.execute("SELECT * FROM improvement_experiments ORDER BY created_at DESC LIMIT 20")]
        return {"instructions": instructions, "failure_categories": failures, "prompt_versions": versions, "experiments": experiments, "active_prompt_version": self.active_prompt()["version"]}

    def supporting_runs(self, category):
        with self.connection() as conn:
            return [row[0] for row in conn.execute("SELECT DISTINCT f.run_id FROM failure_observations f JOIN runs r ON r.id=f.run_id WHERE f.category=? AND r.status!='RUNNING' ORDER BY f.run_id", (category,))]

    def create_experiment(self, category, instruction, supports, dataset_version):
        baseline = self.active_prompt()
        experiment_id, memory_id = identifier(), identifier()
        candidate = "generator-" + experiment_id[:12]
        with self.connection() as conn:
            demo_count = sum(bool(conn.execute("SELECT demo_error FROM runs WHERE id=?", (run_id,)).fetchone()[0]) for run_id in supports)
            origin = f"Repeated failures across {len(supports)} independent runs, including {demo_count} deliberate-error demonstrations; controlled comparison required"
            conn.execute("INSERT INTO memory_instructions VALUES(?,?,?,?,?,?,?,?,?,?)", (memory_id, "Introduction to RAG", "india_beginner", category, instruction, "proposed", origin, encode(supports), candidate, now()))
            conn.execute("INSERT INTO prompt_versions VALUES(?,?,?,?,?,?)", (candidate, baseline["instructions"] + "\nAdditional teaching instruction: " + instruction, baseline["version"], 0, encode([*baseline["memory_ids"], memory_id][-4:]), now()))
            conn.execute("INSERT INTO improvement_experiments(id,category,status,stage,baseline_prompt_version,candidate_prompt_version,memory_id,dataset_version,created_at) VALUES(?,?,?,?,?,?,?,?,?)", (experiment_id, category, "RUNNING", "QUEUED", baseline["version"], candidate, memory_id, dataset_version, now()))
        return experiment_id

    def experiment(self, experiment_id):
        with self.connection() as conn:
            return decode_row(conn.execute("SELECT * FROM improvement_experiments WHERE id=?", (experiment_id,)).fetchone())

    def update_experiment(self, experiment_id, stage, results):
        with self.connection() as conn:
            conn.execute("UPDATE improvement_experiments SET stage=?,results_json=? WHERE id=?", (stage, encode(results), experiment_id))

    def finish_experiment(self, experiment_id, status, results, error=None):
        with self.connection() as conn:
            row = conn.execute("SELECT * FROM improvement_experiments WHERE id=?", (experiment_id,)).fetchone()
            conn.execute("UPDATE improvement_experiments SET status=?,stage=?,results_json=?,error_json=?,finished_at=? WHERE id=?", (status, status, encode(results), encode(error) if error else None, now(), experiment_id))
            conn.execute("UPDATE memory_instructions SET status=? WHERE id=?", ("active" if status == "ACTIVATED" else "rejected", row["memory_id"]))
            if status == "ACTIVATED":
                conn.execute("UPDATE prompt_versions SET active=0")
                conn.execute("UPDATE prompt_versions SET active=1 WHERE version=?", (row["candidate_prompt_version"],))

    def rollback(self, version):
        with self.connection() as conn:
            prompt = decode_row(conn.execute("SELECT * FROM prompt_versions WHERE version=?", (version,)).fetchone())
            if not prompt:
                return None
            if version != PROMPTS["generator_version"]:
                verified = conn.execute("SELECT 1 FROM improvement_experiments WHERE candidate_prompt_version=? AND status='ACTIVATED'", (version,)).fetchone()
                if not verified:
                    return None
            conn.execute("UPDATE prompt_versions SET active=0")
            conn.execute("UPDATE prompt_versions SET active=1 WHERE version=?", (version,))
            conn.execute("UPDATE memory_instructions SET status='rolled_back' WHERE status='active'")
            for memory_id in prompt["memory_ids"]:
                conn.execute("UPDATE memory_instructions SET status='active' WHERE id=?", (memory_id,))
        return {"active_prompt_version": version}
