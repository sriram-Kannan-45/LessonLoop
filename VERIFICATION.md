# Sprint verification

Audited 14 November 2026 on Windows. The user originally chose Gemini only and later explicitly requested automatic Groq fallback on Gemini quota/rate limits. Primary settings remain gemini-3.5-flash-lite for generation and gemini-3.5-flash for three evaluation groups. Configured Groq models can handle affected calls; actual usage is recorded. Earlier runs retain their original model/prompt snapshots.

## Current checks

| Check | Observed result |
| --- | --- |
| Backend pytest | 91 passed; mocked inference/in-memory SDK HTTP transport, no paid calls. |
| TypeScript and production build | Passed. |
| Desktop/mobile Playwright | 34 passed, installed Edge; inference mocked, real local health/configuration checked. |
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

Five reviewed calibration and five fixed holdout fixtures are inspectable in app/dataset.py. Holdout is excluded from prompt comparisons. It was already used in v2/v3 diagnostics and is explicitly not unseen. No current Flash calibration/holdout report is claimed. The earlier daily quota was exhausted before that work, and the user chose to leave those checks pending. A later key connection check and the provider-recovery workflow do not substitute for dataset validation. Precise credential/quota evidence is in submission/quota-blocker.json.

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

## Provider recovery fix

The reported failed run 36bcb7eab9224e069482430174503add returned HTTP 503 from Gemini during generation and saved no draft. A subsequent real generation request using the configured key returned a valid lesson, confirming the failure was intermittent. The fix distinguishes temporary service failures from credential/model errors, adds up to two bounded technical retries with increasing backoff and jitter, honors short provider retry delays, and keeps the same native schema on availability retries. Format-only repair remains separate. Authentication and quota errors are not retried automatically; the three-content-draft limit is unchanged. React now explains old 503 diagnostics and offers an explicit Try again action, preserving the failed run and its original request settings. SDK-transport tests exercise recovery after two 503s, exhaustion, schema preservation and long retry instructions. Desktop/mobile browser tests exercise explicit recovery and immutable failed history.

The real Try again test e92eaa409983478aacd9ae1b303fcb5d finished NEEDS_REVIEW after three drafts, with no provider error. It detected the deliberately injected false guarantee; a wrong S3:C06 source mapping remained. Its honest 13/14 result is in submission/provider-recovery.json. This exposed ambiguous source feedback: the validator now names the invalid pairs and supplies the allowed mapping in its correction, and generation receives the same compact approved mapping. The acceptance rule is unchanged; claims are never automatically relabelled or approved. A targeted regression test keeps this failure actionable.

Final normal-mode live verification after the citation correction: fe2597a7169142e4a82f9de226521cb6, started through the real React Generate lesson button, APPROVED after two drafts with all 14 checks passed. Draft one failed TERMS_EXPLAINED; the actual feedback drove the rewrite. Both source checks passed. No provider error or browser JavaScript error occurred. The structured result is in submission/provider-normal-recovery.json. This verifies the current provider-recovery workflow, not the separately pending learned-memory or evaluator-dataset acceptance checks.

## Groq quota fallback verification

Deterministic in-memory HTTP transports verify the fallback boundaries; a later real app run also verified actual Groq evaluation failover, as detailed below. Tests exercise Gemini quota -> Groq generation/evaluation, per-model cooldown reuse and expiry, a healthy generator while only its evaluator quota is exhausted, disabled/missing backup configuration, invalid backup credentials and backup quota, no fallback on non-quota errors, native strict schema serialization, redaction of both keys, request pacing and real workflow/API persistence of actual providers. Invalid Groq booleans fail local evaluation and cannot approve a lesson. Provider/model drift makes a prompt comparison ineligible for activation. Browser tests cover backup readiness, missing-key guidance and actual saved provider identities on desktop/mobile.

The user subsequently added GROQ_API_KEY to the ignored backend/.env. The backend was restarted to load it. A real React run, 2b13bb0094e348b8935480142a81deb8, finished APPROVED on draft one with all fourteen checks passed. Generation used Gemini Flash-Lite. The first two evaluation groups used Gemini Flash; its real quota response then caused automatic fallback to Groq Qwen 3.8 27B for TERMS_EXPLAINED, NO_PREREQUISITES, WORKED_EXAMPLE and FLOW_AND_PRACTICE. That Groq request returned valid native strict JSON and locally validated evidence, using 5,502 prompt tokens and 584 completion tokens. The browser displayed both actual evaluator providers, fourteen saved PASS results and zero JavaScript errors. No primary failure was injected for this run.

The live result and token/provider records are in submission/groq-live-verification.json. Full audit, actual approved lesson and run metadata are in submission/groq-live-lesson/. This proves account access and one real evaluation fallback; it does not establish general judge accuracy. Groq generation fallback, complete Groq-only evaluation and cooldown expiry remain transport-tested rather than exercised in this live run. The separately pending learned-memory and evaluator-dataset acceptance work was not resumed. No key is stored in the evidence or Git.

## Dynamic topic generation

The studio now accepts a free-text subject with `reference_pack_id=auto`. Real Wikipedia search and revision-pinned excerpts are retrieved before generation, frozen in the run, and shown with their access time and CC BY-SA license. These secondary references are explicitly not human-reviewed. Missing/unavailable references stop the run before any model generation. No arbitrary user URL is fetched.

New subjects use generator-topic-v2 and evaluator-topic-v3-compact-evidence, plus twelve universal subject-aware model checks and the two local structure/source checks. The evaluator selects an existing lesson field; Python supplies its exact evidence text. Schema constraints restrict check IDs, claim IDs and evidence paths without constraining verdicts. All fourteen checks must still pass. Legacy reviewed RAG snapshots, prompts and exports remain readable. RAG calibration and learning acceptance do not generalize to the new subjects.

Offline tests cover Photosynthesis, Python programming and the French Revolution, frozen references, empty/error retrieval, older-client compatibility, exact release IDs, dynamic claim mappings, topic isolation of learned instructions, and native/JSON-mode evidence selection. Four new desktop/mobile cases verify free-text requests and reading each run's saved rubric. `submission/topics-live-verification.json` records actual live attempts, including failed integrations, without relabelling them as approvals.

A live Groq diagnostic identified an account-specific output allowance of 1,000 tokens per minute. A rejected evaluation was estimated at 1,377 output tokens even though the ordinary 8,000-token allowance was available. Evaluation responses now have a 900-token cap and concise reasons/corrections; oversized-request errors explain that waiting alone cannot fix them. This is separate from an exhausted daily quota. The generation response budget remains 4,096, and live Groq generation remains unverified under this account's output allowance.

The final compact-output React run `1788f8f75349482599aac245224ac0ba` completed all nine real Groq evaluation groups over three naturally generated Photosynthesis drafts, with zero technical retries. Generation used Gemini. It ended **NEEDS_REVIEW, 12/14**, with GROUNDED_CLAIMS and TERMS_EXPLAINED still failing. The final feedback identified an unsupported statement about artificial photosynthesis and an unexplained use of "biomimics". The release gate correctly retained review status. This verifies the dynamic-topic retrieval/generation/evaluation/rewrite path and real quota fallback, not a successful general-topic approval or broad model accuracy. Earlier format/quota failures remain in the same verification report. Desktop/mobile review showed the topic-specific fourteen-check rubric, real references, no browser errors and no horizontal overflow. Existing approved RAG histories remained approved after restart.
