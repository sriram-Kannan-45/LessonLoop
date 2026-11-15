# Sprint acceptance audit

Audited 14 November 2026 against the implementation brief. Gemini Flash-Lite/Flash are primary. The user later authorized Groq fallback only when Gemini quota/rate limits are reached; actual providers are recorded per response. Historical runs keep their original model and prompt snapshots.

| Sprint | Implemented and verified | Acceptance evidence |
| --- | --- | --- |
| 1 — Setup | Complete | Health/configuration, ignored backend/.env, manual Gemini connection check. |
| 2 — Sources and rubric | Complete | Automatic topic references and a generic fourteen-check rubric; explicit unreviewed provenance, frozen revisions/claims; reviewed primary RAG snapshots retained. |
| 3 — Workflow | Complete | Real LangGraph, all-check release gate, actual rejection feedback, maximum three drafts, review/error/interrupted outcomes. |
| 4 — Persistence | Complete | SQLite immutable attempts, checks/events, snapshots, history, feedback, prompt versions; restart tests. |
| 5 — Cross-run learning | Live acceptance pending | Two natural independent terminology failures; last comparison stopped on the earlier key’s daily 20-request quota; the user chose to leave live acceptance pending. New paired-normal-and-targeted-v2 protocol awaits live verification before any activation. Prompt content and selected memory are both capped at four learned instructions. |
| 6 — API and React | Complete | Create/progress/reader/reports/attempts/history/memory/feedback/rollback/exports; normal workflow exercised through React. |
| 7 — Verification | Automated checks complete; current live dataset report pending | 118 backend tests, TypeScript/build, 42 desktop/mobile browser tests; historical live disagreements preserved; current-model dataset rerun remains pending as requested. |
| 8 — Deliverables | Complete | Approved lesson/audit/rejection log, clean HTML, README, design, verification and checklist. |
| 9 — Demonstration | Recording materials complete | 15–20-minute script, exact app actions, privacy checklist and saved real deliberate-error backup. Human face-visible recording/upload remains external. |

## Current real natural failures and correction

- b0ba902b21e64ce3a8f38a1ff446ef1d: APPROVED after two drafts. Actual first-draft failures: TERMS_EXPLAINED and NO_PREREQUISITES.
- 9d8c5b6391ed485aa5806045ca0ae0ae: APPROVED after two drafts. Actual first-draft failure: TERMS_EXPLAINED.
- Both used generator-v1, evaluator-v6-term-context, the same frozen references and mandatory rubric. Neither used deliberate-error injection.
- Experiment 0f6314b8c6bf4608a4e3c96588f31d20 ended ERROR on HTTP 429 during the final arm. No candidate was activated. The daily quota limit and reset are recorded in submission/quota-blocker.json. Qualifying activation and subsequent live memory reuse remain pending; they are not replaced by mocked test evidence.

## External finishing steps

The software cannot supply a human face-visible recording. Use docs/VIDEO_WALKTHROUGH.md, record/upload the walkthrough and verify its sharing link. If the assessment requires a Google Docs/Notion link, import the finished clean HTML/Markdown and publish it with the required access. No public document/video URL or assessment submission is claimed.

## Groq backup update

Automatic quota-only fallback is implemented and transport/browser-tested. Add GROQ_API_KEY in backend/.env and restart to enable real Groq use. The user has now set the key. Real run 2b13bb0094e348b8935480142a81deb8 verified automatic Gemini-quota -> Groq evaluation fallback and ended APPROVED, 14/14 on draft one. Broader judge accuracy and Groq generation remain unverified live. The subsequent dynamic-topic tests completed full three-group Groq evaluations; their actual verdicts are recorded separately in submission/topics-live-verification.json. Actual providers are shown per draft and in audit JSON, and mixed-provider prompt comparisons cannot activate a candidate.

## Any-topic update

The default studio assignment is now any entered subject, with references collected at run time. There is no RAG topic whitelist. A retrieval failure produces an actionable unapproved error. New generic teaching prompts and rubric checks assess the requested subject. Prior RAG calibration and cross-run learning acceptance remain limited to RAG; they are not proof of general subject accuracy. Actual new-topic inference results are recorded separately in submission/topics-live-verification.json.

Final real dynamic-topic run 1788f8f75349482599aac245224ac0ba completed all three drafts and nine Groq evaluation groups without technical retries. Photosynthesis remained NEEDS_REVIEW at 12/14 due to grounding and terminology failures. Dynamic operation is verified; a successful new-topic approval and general subject accuracy are not claimed.

## FreeLLM update — 15 November 2026

The user-authorized local router is configured as an optional third provider. Groq quota, output truncation and transient service failures can continue through FreeLLM, with per-response provenance and all release checks intact. An isolated diagnostic with controlled primary/Groq failures and real FreeLLM inference approved Performance testing at 14/14 on draft one. The current default local output budget is 8,192. Original learning/calibration acceptance boundaries remain unchanged; one router integration example is not broad judge accuracy evidence.
