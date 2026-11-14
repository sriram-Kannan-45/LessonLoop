# Sprint verification

Audited 14 November 2026 on Windows. The user explicitly chose Gemini only. Current settings generate with gemini-3.5-flash-lite and evaluate with gemini-3.5-flash in three separate focused requests. Earlier runs retain their original model/prompt snapshots.

## Current checks

| Check | Observed result |
| --- | --- |
| Backend pytest | 54 passed; mocked inference/in-memory SDK HTTP transport, no paid calls. |
| TypeScript and production build | Passed. |
| Desktop/mobile Playwright | 24 passed, installed Edge; inference mocked, real local health/configuration checked. |
| Real browser review | Current Flash model label visible; desktop reader and mobile memory page have no JavaScript errors; mobile page has no horizontal overflow. |
| Persistence | Actual server restart preserved approved runs, failure observations, inactive proposals and generator-v1. No active job was abandoned during the final restart. |

Tests enforce complete strict check IDs/booleans, evidence provenance, all-fourteen release, actual correction feedback, the three-draft limit, NEEDS_REVIEW exhaustion, technical errors, restart interruption, immutable attempts, unverified-feedback isolation, successful mocked activation/reuse/rollback, and safe exports. New tests cover per-group repair/incomplete rejection, bounded prompt text as well as memory IDs, preserving comparison drafts on evaluator failure, quota diagnostics without automatic quota retries, and model-vs-Python release counts.

## Real normal runs with the current evaluator

- b0ba902b21e64ce3a8f38a1ff446ef1d: APPROVED, two drafts, final 14/14. First draft failed TERMS_EXPLAINED and NO_PREREQUISITES. Actual feedback drove the correction. This is the current final lesson in submission/final-lesson/ and submission/lesson-for-google-docs.html.
- 9d8c5b6391ed485aa5806045ca0ae0ae: APPROVED, two drafts, final 14/14. First draft failed TERMS_EXPLAINED. Export: submission/second-natural-run/.
- Both are natural failures without deliberate-error injection, generator-v1, evaluator-v6-term-context, references rag-primary-v1.1 and rubric beginner-rag-v1.1.
- The earlier normal run a791fca8f9004ca1828c59ef1b63794e was started through the real React interface and approved under evaluator-v3. Its original artifacts remain in submission/earlier-approved-v3/; they are not relabelled as current-protocol results.

## Real deliberate-error backup

Saved run d7f428ad985b4aceba7b8a17610bfeef was APPROVED after two drafts. Draft one was actually generated and preserved before replacing its limitations with the false always-correct guarantee. The real evaluator rejected SOURCES and HONEST_LIMITATIONS, without receiving a demo flag. The next draft passed. Original, altered draft, evidence, changes and events remain in submission/backup-demo/. This is a saved historical live backup, not a newly recorded current-evaluator demo.

## Evaluator evidence and known defects

| Historical report | Evaluated / authored | Technical errors | Model-wide false approvals | Per-check false passes |
| --- | --- | --- | --- | --- |
| evaluator-v2-first-report.json | 5 / 10 | 5 | 1 | 6 |
| evaluator-calibration.json, v3 | 7 / 10 | 3 | 0 | 6 |
| evaluator-v4-calibration.json | 3 / 5 | 2 | 0 | 2 |
| evaluator-calibration-v5.json | 4 / 5 | 1 | 0 | 2 |

The old reports' overall approval field measures all twelve model checks, not the final Python release gate. The CLI now reports false_model_approval and the fourteen-check release decision separately. Technical errors are not successful judgments. There were no false overall rejections on completed labelled cases in these historical reports; this is a tiny authored set, not a general accuracy claim.

Five reviewed calibration and five fixed holdout fixtures are inspectable in app/dataset.py. Holdout is excluded from prompt comparisons. It was already used in v2/v3 diagnostics and is explicitly not unseen. No current Flash calibration/holdout report is claimed: its daily quota was exhausted before that work. Precise credential/quota evidence is in submission/quota-blocker.json.

Flash-Lite also falsely passed undefined weights and pipeline in naturally generated lessons. A same-draft real trial with Flash correctly rejected terminology/prerequisite failures; submission/evaluator-flash-trial.json records it. This motivated the explicit evaluator model change. Earlier Flash-Lite approvals remain historical. A separate unsuccessful gemini-3.8-flash trial remains in submission/model-trial.json; it was not silently adopted.

## Learning: implemented, live acceptance still pending

Two independent completed natural runs support TERMS_EXPLAINED. Multiple attempts in one run count once. Earlier HONEST_LIMITATIONS observations came from clearly identified deliberate-error demos.

- Historical complete experiment 360b5fbb9d7241208287721aa94a8835 ended NO_IMPROVEMENT, correctly inactive; submission/prompt-improvement-v4.json.
- Current experiment 0f6314b8c6bf4608a4e3c96588f31d20 completed three arms, then ended ERROR on HTTP 429 during the fourth evaluation. Completed baselines had no target failure; no qualifying benefit is claimed. The candidate stayed inactive; submission/prompt-improvement-v6.json.
- A sanitized SDK probe confirmed GenerateRequestsPerDayPerProjectPerModel-FreeTier, limit 20, and a 4651-second retry delay. Estimated next reset: 14 November 08:00 UTC / 13:30 IST. Billing was not changed.
- The audited paired-normal-and-targeted-v2 protocol now compares the actual normal UI assignment without a correct seed in the first pair, then the same targeted calibration seed in the second pair. This addresses a coverage flaw: the correct seed hid natural jargon failures. It is tested offline but has not yet run live.
- Actual prompt text and selected memory are both capped at four instructions. Comparison drafts and generation usage are persisted before evaluation; partial groups/failed comparisons never approve or activate.
- Zero active learned instructions. Real qualifying activation and subsequent reuse remain unobserved and cannot be marked complete. Mocked tests demonstrate the implementation, persistence and rollback, not real-model improvement.

## Deliverables and completion boundary

The implementation, API, UI, exports, tests, design, clean lesson document and recording materials are ready. Sprint 5 still needs a qualifying live comparison and a later real run selecting its instruction; current-protocol dataset validation also needs quota. See docs/SPRINT_STATUS.md and submission/quota-blocker.json. Provider failures and model false passes remain practical limitations.

Current approved artifacts: submission/final-lesson/. Clean importable document: submission/lesson-for-google-docs.html. Saved real demonstration: submission/backup-demo/. Recording script: docs/VIDEO_WALKTHROUGH.md. Checklist: docs/SUBMISSION_CHECKLIST.md.

A human must record/upload the face-visible video and publish/import the lesson if a Google Docs/Notion sharing link is required. No video, public document URL or assessment submission is invented. GitHub synchronization is reported only after a verified push.

Runtime: Python 3.11.16, FastAPI 0.162.6, google-genai 2.34.0, LangGraph 1.2.21, pytest 9.2.0, React 19.3.1, TypeScript 5.9.3, Vite 7.3.8 and Playwright 1.65.0. Exact pins remain in requirements/lockfiles. Secrets, databases, caches and generated QA files are ignored.
