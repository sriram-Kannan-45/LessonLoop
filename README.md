# LessonLoop

LessonLoop creates and evaluates beginner lessons about the topic you enter: science, programming, history, mathematics and other subjects with usable public references. The learner is an Indian grade-12 graduate with limited English vocabulary and no assumed specialist background. New runs collect topic references automatically; there is no RAG-only subject whitelist.

Gemini is the primary generator and evaluator. On a Gemini quota/rate-limit response, the affected call automatically switches to configured Groq backup. Separate evaluation calls judge twelve rubric checks, and Python enforces two structure/reference checks. **Every mandatory check must pass** before release. Actual failures drive at most two rewrites; unresolved drafts end **NEEDS_REVIEW**.

The user originally chose Gemini only and later explicitly requested **Groq quota fallback**. Groq is called directly over HTTPS with a Qwen model by default; no OpenAI SDK is used. An optional FreeLLM router controls its own upstream providers. Separate calls and provider fallback do not guarantee accurate or independent judgments. [VERIFICATION.md](VERIFICATION.md) separates actual live results from mocked tests. [Sprint acceptance status](docs/SPRINT_STATUS.md) maps every sprint to its evidence and remaining human steps.

## Implemented system

React, TypeScript, Vite, and Tailwind provide a lesson studio, real event progress, reader, quality report, adjacent draft comparisons, feedback, history, memory, and downloads. FastAPI runs an actual LangGraph and persists structured records in SQLite. Source notes, claims, rubric, prompts, model identities, usage, and selected memory are versioned/auditable.

```mermaid
flowchart LR
  UI[React] --> API[FastAPI single local task]
  API --> L[Search topic references and freeze sources rubric prompt memory]
  L --> G[Gemini generation]
  G -->|Gemini quota| GB[Groq generation]
  GB --> S[Python structure and reference checks]
  G --> S
  S --> E[Separate Gemini evaluation]
  E -->|Gemini quota| EB[Groq evaluation]
  EB --> D{Every mandatory check passes?}
  E --> D
  D -->|Yes| A[APPROVED]
  D -->|No and fewer than 2 retries| G
  D -->|No after draft 3| R[NEEDS_REVIEW]
  G -->|Technical failure| X[ERROR]
  E -->|Malformed verdict or failure| X
  A --> DB[(SQLite history and memory)]
  R --> DB
  X --> DB
```

LangGraph makes nodes/state/conditional edges inspectable. Python decides release instead of averaging scores. SQLite is sufficient for this single-user assessment. One in-process task slot is shared by runs and improvements. Work does not survive a restart: unfinished records become INTERRUPTED, while saved drafts and completed history remain.

## Prerequisites and installation

Use working Python 3.11+, Node.js 20.19+ or 22.12+, npm, Git, and a Gemini API key with access to the configured models. Tested here with Python 3.11.16 and Node 24.14.0. Browser tests use installed Edge.

PowerShell from the project root:

```powershell
py -3.11 -m venv backend\.venv
.\backend\.venv\Scripts\python.exe -m pip install -r backend\requirements-dev.txt
cd frontend
npm ci
cd ..
if (-not (Test-Path backend\.env)) { Copy-Item backend\.env.example backend\.env }
if (-not (Test-Path frontend\.env)) { Copy-Item frontend\.env.example frontend\.env }
```

This machine's Python 3.12 cannot import `encodings`; the project already uses a working uv-managed 3.11. To recreate that environment:

```powershell
uv venv --python 3.11 backend\.venv
uv pip install --python backend\.venv\Scripts\python.exe -r backend\requirements-dev.txt
```

Activation is optional. Direct executable commands avoid PowerShell activation-policy problems. Optional activation: `.\backend\.venv\Scripts\Activate.ps1`. Use npm.cmd if npm's PowerShell wrapper is blocked. Exact dependency versions are locked in the requirements files and package-lock.json.

## Environment

Enter the key locally in backend/.env, never in chat or frontend settings:

```dotenv
APP_NAME=LessonLoop
APP_ENV=development
BACKEND_HOST=127.0.0.1
BACKEND_PORT=8000
FRONTEND_ORIGIN=http://localhost:5173
GEMINI_API_KEY=
GEMINI_MODEL=gemini-3.5-flash-lite
GEMINI_EVALUATOR_MODEL=gemini-3.5-flash
GROQ_FALLBACK_ENABLED=true
GROQ_API_KEY=
GROQ_MODEL=qwen/qwen3.8-27b
GROQ_EVALUATOR_MODEL=qwen/qwen3.8-27b
GROQ_MIN_INTERVAL_SECONDS=65
PROVIDER_TIMEOUT_SECONDS=30
WORKFLOW_TIMEOUT_SECONDS=90
TECHNICAL_RETRIES=2
```

The checked-in example uses Gemini 3.5 Flash-Lite for generation and Gemini 3.5 Flash for evaluation. Flash caught undefined technical terms missed by Flash-Lite in the recorded same-draft trial. The optional evaluator model defaults to GEMINI_MODEL when omitted. Gemini remains primary; only its HTTP 429 quota/rate-limit result authorizes automatic Groq use. Primary model labels and actual per-response providers are visible and recorded. No fallback occurs for invalid Gemini credentials, malformed verdicts or ordinary service outages. DATABASE_PATH optionally changes the SQLite file; relative values resolve under backend/. Default: backend/data/lessonloop.sqlite3.

Process environment variables override file values. The backend resolves .env from its source location; blank provider settings mean missing configuration. Restart after edits. Frontend .env contains only `VITE_API_BASE_URL=http://127.0.0.1:8000`. All VITE values are public; never put keys there.

## Start in two terminals

Backend, from the project root:

```powershell
cd backend
.\.venv\Scripts\python.exe -m app.main
```

Frontend, from the project root:

```powershell
cd frontend
npm run dev
```

Open [the app](http://localhost:5173), [Connections](http://localhost:5173/?view=connections), or [API docs](http://127.0.0.1:8000/docs). Health is at http://127.0.0.1:8000/api/health.

Use exactly localhost:5173 to match CORS. Vite uses a strict port. Update the backend URL and allowed origin together if ports change. Use **one backend process/worker**; this local task runner is not a distributed job system.

## Normal demonstration

1. Enter a subject such as Photosynthesis, Python programming or the French Revolution. Keep the beginner learner and automatic topic references selected.
2. Leave factual-error injection unchecked; click Generate lesson once.
3. Expand live events. Stages come from the backend, not simulated animation.
4. Read the illustrative example, missing-information answer, recap, and expandable practice answers.
5. Inspect Quality report and Attempts. The count is informational; all mandatory checks must pass.
6. Download approved Markdown/audit JSON, or a clearly labelled review draft.
7. Reload `/?run=<id>` or use Run history to retrieve the saved record.

References are collected from the public English Wikipedia search/text-extract APIs when a run starts. Excerpts, revision URLs, access times and CC BY-SA attribution are frozen with the run. These are automatically collected secondary references, not human-reviewed primary-source packs. If usable source text cannot be found or the service is unavailable, the run stops with a clear reference error and no invented citations. Try a more specific topic name when needed.

## Deliberate-error demonstration

Enable **Inject a factual error into the first draft**. The app first generates normally and preserves the original, then inserts a false numerical claim and an unjustified universal guarantee. The legacy RAG demonstration retains its original always-correct claim. Only the altered lesson reaches the real evaluator, without a demo flag or desired verdict. Actual failed checks drive a rewrite; the error is never reinjected.

Attempts shows the original/altered claim, reasons, required changes, paragraph differences, and the next verdict. A missed error must be reported honestly as an evaluator defect, not hidden by hardcoded rejection. A saved real backup is in submission/backup-demo/.

## Memory and improvement demonstration

Failures count once per category per independent run, not per retry. Two completed supporting runs are required. Demonstration-origin observations are visible. Human feedback starts unverified; review can verify/dismiss it, but arbitrary feedback text never enters prompts automatically.

In Memory & learning, reviewed prompt-improvement comparisons remain scoped to the RAG calibration dataset. Other subjects still generate normally. Matching-topic memory is selected separately; RAG instructions are never injected into unrelated subjects. Choose an eligible RAG category and Compare prompts. A vetted instruction creates an inactive candidate version. Baseline and candidate each generate from the same normal assignment and targeted calibration scenario, then use the fixed rubric. Up to four generations and twelve focused evaluation calls run, each with at most two technical retries. Every lesson is checked in three groups of four mandatory checks; the merged result must contain all twelve model checks plus the two code checks.

Activation requires a targeted baseline failure to become a candidate pass with no per-check regression on baseline-passing checks. Ties end NO_IMPROVEMENT and stay inactive. Active memory is selected by topic/learner, capped at four instructions, and saved with each future run. Rollback restores the original or a previously activated version. A tiny stochastic comparison is limited evidence, not proof of universal improvement.

## Tests and live calibration

Backend, from backend/:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Frontend, from frontend/, with the backend running:

```powershell
npm run typecheck
npm run build
npm run test:ui
```

Automated inference is mocked and costs no API credits. Local health/configuration requests do not infer. Playwright uses installed Edge; PLAYWRIGHT_CHANNEL=chrome selects installed Chrome. pytest and browser profiles keep temporary data on the project drive.

For real paid evaluator testing, wait for app jobs to finish, then from backend/:

```powershell
.\.venv\Scripts\python.exe -m app.cli calibrate --split calibration --out ../submission/evaluator-calibration.json
.\.venv\Scripts\python.exe -m app.cli calibrate --split holdout --out ../submission/evaluator-holdout.json
```

`--split all` combines both. Five calibration and five holdout examples have reviewed per-check labels. Only labelled checks count toward disagreements. Reports separate false overall approvals/rejections, per-check false passes/rejections, and technical errors. Holdout is excluded from improvement. Once run, call it a fixed held-out test set, not unseen data; never retune on it and still call it unseen.

CLI utilities, from backend/:

```powershell
.\.venv\Scripts\python.exe -m app.cli run --wait
.\.venv\Scripts\python.exe -m app.cli run --demo-error --wait
.\.venv\Scripts\python.exe -m app.cli export <run-id> --out ../submission/final-lesson
```

The run command uses the running API. Exports preserve actual status and cannot approve a review draft.

## Output and reviewer files

- backend/content/: primary sources, paraphrased claims, frozen rubric, versioned prompts, fixture lesson, and dataset review.
- backend/app/dataset.py: inspectable labelled mutations and calibration/holdout splits.
- backend/data/lessonloop.sqlite3: ignored history/memory database; preserve it across restarts.
- submission/final-lesson/: actual approved lesson Markdown, rejection log, audit JSON, and metadata.
- submission/backup-demo/: clearly labelled saved live deliberate-error run.
- submission/evaluator-calibration.json and prompt-improvement.json: actual evidence when those operations ran.
- submission/lesson-for-google-docs.html: clean document for Google Docs or Notion import/copy.
- docs/DESIGN.md: implemented design, safeguards, one-day trade-offs, and production work.
- docs/VIDEO_WALKTHROUGH.md: 15–20-minute face-visible script and checklist.
- VERIFICATION.md: actual results. artifacts/ holds ignored QA screenshots/downloads.

## API

Sprint 1 health, provider configuration, and manual Gemini check endpoints remain. Health/status work without keys and never call a model.

| Endpoint | Purpose |
| --- | --- |
| GET /api/workspace | Sources, rubric, models, preset, limits |
| POST /api/runs | HTTP 202, arbitrary topic input, automatic references and bounded job |
| GET /api/runs?limit=10&offset=0 | Paginated history |
| GET /api/runs/{id} | Status, drafts, checks, memory, released lesson or review draft |
| GET /api/runs/{id}/events?after=0 | Ordered event cursor |
| POST /api/runs/{id}/feedback | Unverified observation |
| POST /api/feedback/{id}/review | Human review with note |
| GET /api/memory | Instructions, failure counts, versions, experiments |
| POST /api/improvements | Bounded prompt comparison |
| GET /api/improvements/{id} | Comparison progress and evidence |
| POST /api/prompts/rollback | Restore eligible validated prompt |
| GET /api/runs/{id}/export?format=markdown | Correctly labelled lesson or review draft |
| GET /api/runs/{id}/export?format=json | Full audit, including technical failures |

Application errors use status, error_code, and an actionable sanitized message. Input validation uses FastAPI 422 for malformed input, not a subject whitelist. Busy is 409, missing settings 503, provider quota 429, and timeout 504. Malformed verdicts never authorize release.

## Troubleshooting and limits

- Backend unavailable: start it separately, check the URL, and retry explicitly.
- Credentials/model/quota: edit backend/.env, restart, and check account access/credits. Only the explicitly configured Groq quota fallback changes provider/model; the change is recorded. An earlier verification key returned a 20-request daily Flash limit; see submission/quota-blocker.json. One comparison needs twelve evaluator calls before retries, and each five-case calibration split needs fifteen. Schedule against your actual project quota; do not repeatedly retry a daily 429.
- Interrupted: the process stopped; inspect preserved history and start a new run.
- CORS: localhost:5173 and 127.0.0.1:5173 differ. Match FRONTEND_ORIGIN.
- Python encodings error: create .venv with a working interpreter; avoid deleting global installations.
- Full C drive/error 112: set TEMP, TMP, UV_CACHE_DIR, and npm_config_cache under the ignored project .cache directory before installation. No user files need deletion.
- Gemini HTTP 503: the service is temporarily busy. LessonLoop retries transient server/network failures at most twice with increasing waits and jitter (normally 4–5 then 8–9 seconds), keeping the same model and request format. Longer provider wait instructions stop the automatic retries. If retries are exhausted, use **Try again** to start a new run; the failed run remains in history. Authentication and daily quota errors are not automatically retried.
- Gemini schema/evidence errors: bounded technical retries can repair requests/responses; unresolved failures remain ERROR. Early unsuccessful development runs are preserved honestly.

This is **local development software**. It binds to loopback by default. Writes require development mode and the configured browser origin; CORS is not authentication. Public deployment still needs access control, spending limits, and durable execution.

Every generation, evaluation, connection, comparison, and calibration call consumes provider quota and can incur charges under the account plan. No inference or reference research runs on page load. Content retries are at most two; technical retries are separate and at most two per generation or focused evaluation request. Evaluation uses three focused requests per draft, each with at most two retries; a partial result cannot approve.

A human must record/upload the face-visible video and import/publish the document if a sharing link is required. No recording URL, document sharing URL, or assessment submission is invented.

Primary reference links/access dates are in the source pack. No third-party application code was copied; dependencies retain their licenses. SDK syntax follows the [Google SDK](https://github.com/googleapis/python-genai), [structured-output docs](https://ai.google.dev/gemini-api/docs/structured-output), and [LangGraph Graph API](https://docs.langchain.com/oss/python/langgraph/graph-api).

Repository: [sriram-Kannan-45/LessonLoop](https://github.com/sriram-Kannan-45/LessonLoop).

## Automatic Groq quota fallback

1. Put the Groq key only in `backend/.env` as `GROQ_API_KEY=...`; never put it in frontend variables or Git. Keep the model fields from `.env.example`, or choose Groq models your account supports.
2. Restart the backend. The studio displays **Groq quota fallback** and whether the key is configured. Configuration is not a successful live connection check. Connections tests the Gemini primary only; a primary quota failure does not test Groq access.
3. Generate normally. Gemini is always tried first unless that same model has a cached quota cooldown. On HTTP 429, the affected generation or evaluator request switches to Groq automatically. A judge quota does not disable a healthy Gemini generator.
4. Inspect live events and the provider trace for each draft. They identify the actual provider/model, including mixed Gemini/Groq evaluation groups. Audit JSON stores the same information. Run model fields remain the originally configured primary snapshots.

The same JSON/schema, source, evidence, strict-boolean and all-mandatory-check validation applies to Groq. A fallback is not approval. If Groq also fails, the run remains ERROR and saved drafts are retained. Authentication failures and non-quota Gemini failures do not switch providers. There is no provider loop.

Quota cooldowns are per Gemini model in the current backend process. The provider retry time is used when available; absent that hint, a daily quota is cached for one hour and another rate limit for one minute. Once the cooldown expires, the next request tries Gemini again. Restarting clears these in-memory cooldowns; it may make one new Gemini quota request before switching again.

The default Groq request interval is 65 seconds to reduce token-per-minute failures on its free plan. Waiting is shown as a real workflow event. Requests omit duplicate prompt schemas and use bounded completion budgets; outside usage, large prompts or daily token limits can still cause Groq 429. Change `GROQ_MIN_INTERVAL_SECONDS` only for the actual allowance of your account. Groq's strict schema rules are applied in the transport; all original Pydantic rules remain enforced locally.

A prompt comparison cannot activate if the actual generation/evaluation provider signatures differ across its arms: the result is INCOMPARABLE, not credited to the prompt. Historical Gemini-only runs remain unchanged.

Official Groq references: [Chat API](https://console.groq.com/docs/api-reference), [structured outputs](https://console.groq.com/docs/structured-outputs), [free-plan limits](https://console.groq.com/docs/rate-limits). Real evaluation failover was verified in React run 2b13bb0094e348b8935480142a81deb8: Gemini quota triggered a Groq Qwen response and the lesson passed all fourteen checks. See submission/groq-live-verification.json and submission/groq-live-lesson/. General judge quality, Groq generation fallback and complete Groq-only evaluation still need broader live validation; transport tests do not establish model accuracy.

## Dynamic topics and reference provenance

The React request sends `reference_pack_id=auto`. The run is accepted immediately, then load_context searches for the subject, retrieves bounded public excerpts and freezes the resulting pack before any draft is generated. Only the fixed Wikipedia HTTPS API is contacted: a URL typed as the topic is search text, never an arbitrary fetch target. Each retrieved note has a run-local claim ID, and citations must match those actual pairs. Disambiguation pages are excluded. Original page revisions and content hashes make the reference snapshot inspectable.

New runs use generator-topic-v2 and evaluator-topic-v3-compact-evidence, with twelve subject-neutral model checks plus two code checks. Definitions, coverage, explanation, distinctions, factual grounding, terminology, example, assumptions, missing information and practice are judged for the requested subject. Each run freezes its own rubric; a saved RAG rubric cannot approve a biology lesson. Public references are not automatically correct or complete, and an APPROVED status records the system's checks rather than a guarantee of truth.

The original RAG prompt, sources, rubric and labelled calibration remain for historical runs and explicitly requested legacy RAG workflows. Older clients that send the legacy pack ID with a new subject are upgraded to automatic topic references. History is not rewritten. Prompt improvement still needs a reviewed calibration dataset for its scope; observations from unrelated subjects cannot count as RAG support.

CLI example from backend/: `.\.venv\Scripts\python.exe -m app.cli run --topic "Photosynthesis" --wait`. The generator/evaluator continue to use the configured Gemini -> Groq quota fallback. On-demand public reference retrieval requires internet access but no additional API key. General-topic model accuracy has not been established by the old RAG calibration reports.

Reference API documentation: [Wikipedia search](https://www.mediawiki.org/wiki/API:Search), [text extracts](https://www.mediawiki.org/wiki/Extension:TextExtracts). Source excerpts retain their per-source [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) attribution; app source-code licensing does not replace that content license.

Groq accounts can enforce a separate output-token allowance. Evaluation responses are kept concise with a 900-token cap. A full lesson still needs a larger generation budget; a provider allowance that cannot accommodate it produces an explicit unapproved error.

During an active lesson, click **Cancel generation** in the status panel to stop further work. The run becomes **CANCELLED**, saved drafts remain unapproved in history, and a new lesson can be started. Requests already sent to a provider may still consume quota.

## Optional local FreeLLM router

The configured fallback chain is Gemini -> Groq -> FreeLLM. A Gemini quota response selects Groq; Groq quota, truncated output or a temporary transport/service failure can then select FreeLLM. Invalid credentials are reported rather than routed around. If Groq is disabled, a configured FreeLLM router can handle the Gemini quota fallback directly. A five-minute Groq cooldown avoids repeating the same failed call for every evaluation group. Healthy Gemini calls still use Gemini.

In ignored backend/.env, configure FREELLM_BASE_URL=http://127.0.0.1:31415/v1, FREELLM_API_KEY, FREELLM_MODEL=auto, FREELLM_EVALUATOR_MODEL=auto and FREELLM_FALLBACK_ENABLED=true. Use an ordinary URL without backslash escapes. Keep the local router running and restart the backend after editing settings. HTTPS remote routers or HTTP loopback addresses are supported; embedded URL credentials, query strings, fragments and plaintext remote URLs are rejected.

LessonLoop uses the router's chat-completions endpoint directly through HTTPX. FreeLLM controls its own upstream providers and key pool. Its reported model ID and actual response usage are preserved; auto routing does not establish independent evaluation or unlimited quota. Structured lessons, exact evidence, strict check IDs, cancellation, the three-draft limit and the all-check release gate remain enforced. A failed final router call still produces an honest unapproved error. The original failed run remains unchanged; start a new run to use the new configuration.

FREELLM_MAX_OUTPUT_TOKENS defaults to 8192 to leave room for reasoning models to finish their JSON. It can be configured between 512 and 32768. Truncated local-router output remains an error; a larger key pool cannot remove every model or output limit.
