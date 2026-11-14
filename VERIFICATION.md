# Sprints 2 to 9 verification

Implementation and verification work completed across 13–14 November 2026 on Windows. Live artifacts retain their own UTC timestamps. The user explicitly chose Gemini only, superseding the brief's OpenAI requirement. Both roles use separate calls to gemini-3.5-flash-lite. Implementation, mocked tests, live evidence, and pending human steps are distinguished below.

## Automated verification

| Check | Actual result |
| --- | --- |
| Backend pytest | **49 passed**; provider inference mocked/in-memory HTTP transport. |
| Frontend TypeScript | **Passed**. |
| Production build | **Passed**, Vite 7.3.8. |
| Desktop/mobile browser tests | **24 passed**, installed Edge, 1440 px desktop and 390 px mobile. Inference mocked; health/configuration uses the real local backend. |
| Visual review | Desktop studio, real reader, quality report, history/memory, narrow reader/report, and clean document print pages inspected. |
| Export download | Browser downloaded and read the Markdown contents; approved/review labels tested. |
| Secrets | Environment/database/generated QA folders ignored; source and staged-artifact scans run before push without displaying keys. |

The backend tests enforce all mandatory checks, strict booleans, complete unique IDs, source/evidence validity, the three-draft maximum, actual failed-check feedback, immutable attempts, NEEDS_REVIEW exhaustion, technical errors, restart interruption, unverified-feedback isolation, bounded comparison activation, persistent selected memory, and rollback. SDK transport tests verify the same-model JSON-format retry and the maximum two evaluator requests, without a network call.

## Real application runs

### Final normal run started through React

- ID: `a791fca8f9004ca1828c59ef1b63794e`.
- Final status: **APPROVED**, one draft, **14/14 mandatory checks passed**.
- Generator/evaluator model: gemini-3.5-flash-lite in separate calls.
- Frozen source pack: rag-primary-v1.1. Frozen rubric: beginner-rag-v1.1. Evaluator prompt: evaluator-v3.
- The worked example explicitly labels Asha College and its notice as invented teaching material.
- Actual exports are in submission/final-lesson/. The clean HTML version is generated from this approved draft, not manually edited into a claimed approval.
- The current evaluator-v4 evidence-selector protocol is tested separately below; this saved v3 run is not relabelled as a v4 run.

### Deliberate-error demonstration

- Saved live backup ID: `d7f428ad985b4aceba7b8a17610bfeef`.
- Final status: **APPROVED**, two drafts.
- Draft 1 was generated, the original preserved, then the false always-correct claim injected.
- Actual rejected checks: SOURCES and HONEST_LIMITATIONS. The evaluator received no demo flag or desired verdict.
- Draft 2 passed all fourteen checks. The audit contains both drafts, the original pre-mutation draft, actual evidence, requested changes, and events.
- Exports are in submission/backup-demo/.

Additional early live runs failed with provider request errors or invalid model evidence. They remain ERROR in local history; none was silently promoted. A real browser error run also recorded zero JavaScript page errors. Repeated application restarts preserved approved and failed history. Active-run interruption is exercised deterministically by tests rather than claimed as a surviving background job.

## Live evaluator evidence

| Report | Evaluated / authored | Technical errors | False overall approvals | Per-check false passes |
| --- | --- | --- | --- | --- |
| evaluator-v2-first-report.json | 5 / 10 | 5 | 1 | 6 |
| evaluator-calibration.json, v3 | 7 / 10 | 3 | 0 | 6 |
| evaluator-v4-calibration.json | 3 / 5 | 2 | 0 | 2 |

There were zero recorded false overall rejections on the completed labelled cases in these reports. That does not make the judge universally accurate. Unlabelled checks are not counted as correctly classified by default. Technical failures are not counted as successful judgments. The v4 technical failures include actual provider HTTP 503 service errors. A false per-check pass remains a defect even when another check prevents overall approval.

The five calibration examples and five fixed holdout examples are manually authored/reviewed teaching fixtures, not independent population samples. Holdout is excluded from prompt-improvement comparisons. It was first run with v2; the v3 reused-set report explicitly records this history and is not presented as unseen validation. The v4 report is calibration-only. Earlier reports and labels are preserved rather than overwritten to hide disagreements.

A disclosed trial of gemini-3.8-flash did not produce a usable evaluator response. Its minimal request ended HTTP 504 DEADLINE_EXCEEDED. The app was not silently switched to that unverified model; see submission/model-trial.json.

## Memory and controlled improvement

- HONEST_LIMITATIONS has supporting failed verdicts from two independent completed runs. Multiple attempts in one run count once. Those supporting runs came from deliberate-error demonstrations and are identified as such.
- Completed live experiment: `360b5fbb9d7241208287721aa94a8835`, **NO_IMPROVEMENT**.
- Both baseline and candidate were generated/evaluated on the same correct-lesson and perfect-guarantee calibration scenarios, with a fixed rubric. All four arms completed.
- There were no per-check regressions, no newly fixed checks, and no targeted baseline failure fixed by the candidate. The candidate correctly remained inactive.
- Earlier comparisons stopped on technical errors/invalid evidence and remained inactive. Their records are preserved.
- **Zero active learned instructions. Live learned-memory activation/reuse is not demonstrated.** Deterministic mocked tests exercise an actual successful comparison gate, selection in a later run after repository reopening, and rollback. This must not be described as real-model improvement evidence.
- Persistent observations/proposals/versions/outcomes are exported in submission/memory-evidence.json. The completed real comparison is submission/prompt-improvement-v4.json.

## Submission artifacts and external steps

- Actual approved Markdown, rejection log, audit, metadata: submission/final-lesson/.
- Saved live deliberate-error backup: submission/backup-demo/.
- Clean document: submission/lesson-for-google-docs.html. Its four A4 print pages were rendered and visually inspected. It still needs human import/copy and sharing if a Google Docs/Notion URL is required; no connected Word/document session was available.
- Design: docs/DESIGN.md. Face-visible recording script: docs/VIDEO_WALKTHROUGH.md. Final checklist: docs/SUBMISSION_CHECKLIST.md.
- Real repository: https://github.com/sriram-Kannan-45/LessonLoop. Push status is verified at task completion.
- The human must record/upload the face-visible video and supply its real sharing link. No video, document sharing URL, or assessment submission is invented.

## Completion boundary

The workflow, API, UI, persistence, comparison gate, tests, and submission preparation are implemented. Normal generation and deliberate-error rejection/rewrite have real successful runs. The original requirement for observed live learned-memory benefit/reuse remains **unmet** because no candidate showed a qualifying benefit; the system correctly refused activation. Further model-quality evidence, a passing controlled improvement, and a later run selecting its instruction are needed before claiming that criterion complete. Model false passes and intermittent provider failures also limit reliability. Human document/video publishing remains pending.

## Runtime notes

Python 3.11.16, FastAPI 0.162.6, Uvicorn 0.54.0, google-genai 2.34.0, LangGraph 1.2.21, pydantic-settings 2.16.3, pytest 9.2.0, HTTPX 0.28.1, React 19.3.1, TypeScript 5.9.3, Tailwind 4.3.5, Playwright 1.65.0. Full dependency pins are in the backend requirements files and frontend lockfile. No new backend service was added. The broken global Python installation and global environment variables were not changed.
