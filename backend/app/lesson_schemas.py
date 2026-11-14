from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, StrictBool, field_validator


LEARNER = "India grade 12 graduate, non-English-medium education, limited English vocabulary; no prior AI, coding, database, embeddings, or machine-learning knowledge; beginning an AI career."
PRESET = "india_beginner"
MAX_RETRIES = 2


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Practice(StrictModel):
    question: str = Field(min_length=5, max_length=600)
    answer: str = Field(min_length=3, max_length=1200)


class WorkedExample(StrictModel):
    context: str = Field(min_length=10, max_length=1200)
    learner_question: str = Field(min_length=5, max_length=500)
    source_passage: str = Field(min_length=10, max_length=1600)
    retrieved_information: str = Field(min_length=10, max_length=1400)
    supported_answer: str = Field(min_length=5, max_length=1200)
    missing_information_question: str = Field(min_length=5, max_length=500)
    missing_information_answer: str = Field(min_length=5, max_length=1000)


class LessonReference(StrictModel):
    source_id: str
    claim_ids: list[str] = Field(min_length=1, max_length=15)


class Lesson(StrictModel):
    title: str = Field(min_length=5, max_length=180)
    learning_objectives: list[str] = Field(min_length=2, max_length=5)
    prerequisites: str = Field(min_length=10, max_length=1800)
    what_it_is: str = Field(min_length=20, max_length=5000)
    why_it_matters: str = Field(min_length=20, max_length=4000)
    how_it_works: list[str] = Field(min_length=3, max_length=7)
    worked_example: WorkedExample
    limitations: str = Field(min_length=20, max_length=4000)
    recap: list[str] = Field(min_length=3, max_length=6)
    practice_questions: list[Practice] = Field(min_length=3, max_length=3)
    source_references: list[LessonReference] = Field(min_length=1, max_length=6)


class CheckResult(StrictModel):
    check_id: str
    passed: StrictBool
    evidence: str = Field(max_length=2000)
    reason: str = Field(min_length=5, max_length=1500)
    required_change: str = Field(max_length=1500)
    claim_ids: list[str] = Field(max_length=15)
    missing_content: StrictBool
    evidence_path: str = Field(default="", max_length=100)


class Evaluation(StrictModel):
    checks: list[CheckResult] = Field(min_length=1, max_length=20)


class RunStatus(str, Enum):
    running = "RUNNING"
    approved = "APPROVED"
    review = "NEEDS_REVIEW"
    error = "ERROR"
    interrupted = "INTERRUPTED"


class RunRequest(StrictModel):
    topic: str = Field(default="Introduction to RAG", min_length=3, max_length=160)
    learner_profile: Literal["india_beginner"] = PRESET
    reference_pack_id: Literal["rag-primary-v1"] = "rag-primary-v1"
    demo_error: bool = False

    @field_validator("topic")
    @classmethod
    def topic_not_blank(cls, value):
        value = value.strip()
        if len(value) < 3:
            raise ValueError("Enter a topic with at least three characters.")
        return value


class FeedbackRequest(StrictModel):
    category: Literal["factual_issue", "confusing_language", "missing_example", "correction"]
    message: str = Field(min_length=5, max_length=2000)


class FeedbackReview(StrictModel):
    action: Literal["verified", "dismissed"]
    review_note: str = Field(min_length=10, max_length=1000)


class ImprovementRequest(StrictModel):
    category: str = Field(min_length=3, max_length=80)


class RollbackRequest(StrictModel):
    prompt_version: str = Field(min_length=3, max_length=100)
