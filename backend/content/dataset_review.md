# Evaluator dataset review

Version: rag-evaluator-reviewed-v1. Authored and manually reviewed during implementation on 13 November 2026. Each case has an immutable content hash generated from its full lesson.

The complete baseline lesson is in example_lesson.json. It is teaching/test data, not an approved submission. The code in app/dataset.py applies inspectable mutations and records expected verdicts for relevant checks; unspecified checks are not scored as correct by default.

Calibration: simple correct lesson, wrong definition, perfect-answer guarantee, first-use jargon, unsupported scholarship answer.

Holdout: retraining misconception, missing worked example, incorrect practice answer, valid paraphrase, embedded instruction next to a factual error.

The holdout is excluded from prompt-improvement comparisons. A live report records its actual use. After it has been run, call it the fixed held-out test set, not an unseen dataset. Do not change the rubric or labels to hide disagreements. These ten authored examples are small and not independent population samples, so their results are limited evidence.
