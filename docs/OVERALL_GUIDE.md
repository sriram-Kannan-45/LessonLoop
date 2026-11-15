# LessonLoop overall guide

LessonLoop prepares a beginner lesson, checks it and rewrites it when checks fail. One click on Generate starts one run; drafts 1, 2 and 3 are attempts within that same run. The system decides release automatically. Approval records the checks that passed; it is not a guarantee that a model cannot make a mistake.

For the requirement-by-requirement result and pending submission items, read [ASSESSMENT_AUDIT.md](ASSESSMENT_AUDIT.md). Read [LANGUAGES.md](LANGUAGES.md) for native-language behavior and limitations.

## Start the application

PowerShell terminal one:

```powershell
cd D:\LessonLoop\backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

PowerShell terminal two:

```powershell
cd D:\LessonLoop\frontend
npm run dev
```

Open http://localhost:5173. Keep the local FreeLLM router running at its configured address if you want that fallback. Stop either server with Ctrl+C. Installation and pinned dependencies are documented in the root README; Python backend packages must be updated after pulling this change.

## Prepare a normal lesson

1. Enter the topic. For the assessment use exactly **Introduction to RAG**.
2. Select Lesson language. Choose English for the original assessment example, or Tamil/another supported language for native-language teaching.
3. Leave **Inject a factual error** unchecked for a normal lesson. It is a demonstration switch that deliberately corrupts the first draft.
4. Click Generate once. References are frozen, then generation and evaluation begin. RAG uses the reviewed pack; other subjects use automatically collected public references.
5. Wait for the final status. You may see a draft while checking is in progress, but opening it requires Inspect unapproved draft. It is not a released lesson.
6. Read an approved lesson, try the practice questions before opening their answers, and download the desired format.

The topic field remains editable so you can prepare your next topic. The language selector is locked during active work to avoid confusing the current assignment. Editing a field does not change an already saved run.

## Understand progress and final states

The sticky panel shows the current stage, saved draft count, elapsed time and any Groq allowance wait. The countdown is for the next request, not the whole run. Provider requests and reference retrieval require an internet connection; the local router must also be reachable.

| State | Meaning | Next action |
| --- | --- | --- |
| RUNNING | Generating, checking, revising or waiting | Wait, inspect events, or cancel. Do not repeatedly click Generate. |
| APPROVED | All mandatory checks passed | Read and download; inspect sources and report if needed. |
| NEEDS_REVIEW | Three drafts used and failures remain | Open Quality report. The draft is not approved. |
| ERROR | Technical or provider failure | Read the exact error, fix capacity/configuration and start a new run. Old history stays unchanged. |
| CANCELLED | User stopped this workflow | Saved drafts remain unapproved. A new run can start. |
| INTERRUPTED | Server stopped before completion | Inspect preserved drafts; start a new run after restart. |

Cancel generation stops further local workflow work and awaits cancellation. A request already sent to a provider may still consume quota.

## Reports, drafts and feedback

- **Quality report:** each checkpoint, exact evidence, explanation and requested correction. Native-language runs have one additional language check.
- **Attempts:** compare actual successive drafts and inspect demonstration mutation when enabled. A requested change is not proof it was made; check the next draft and verdict.
- **Feedback:** record confusing language, factual concerns or missing examples. New feedback is unverified. It does not instantly rewrite the current lesson or activate a prompt instruction.
- **Run history:** reopen completed, failed and cancelled runs with their frozen language, sources, rubric, prompts, provider usage and memory selections.
- **Memory & learning:** inspect observations, candidate comparisons and rollback. Current reviewed calibration is English RAG. Other languages do not borrow English learned instructions or count toward that calibration.

## Download formats

Use the links below the lesson: PDF, TXT, Word (.docx), Markdown and Audit JSON. Downloads use saved content and do not make a new model request. A review export is explicitly labelled NOT APPROVED. Word is editable; TXT is UTF-8; the audit contains full technical history.

Native-script PDFs need shaping support and a matching font. Windows Nirmala UI is supported. On another operating system set the process environment variable LESSONLOOP_PDF_FONT with a suitable script-covering TrueType font, or use DOCX/TXT. A missing font produces an explicit export error instead of unreadable boxes. Reference quotations and source titles may remain English even in a Tamil lesson; explanations should be in the selected teaching language. The interface and technical reports currently remain English.

## Architecture and provider routing

React calls a local FastAPI API. A LangGraph workflow loads frozen context, generates a structured lesson, validates structure and citations, evaluates mandatory checks in separate model calls, and either releases, rewrites, or stops. SQLite stores snapshots, attempts, events and verified-feedback provenance. Generation and evaluation are separate calls; shared model mistakes remain possible.

Gemini is primary. A Gemini quota response selects Groq when configured. Eligible Groq quota, output truncation, explicit json_validate_failed and transient service failures can select FreeLLM. The local router manages its own upstream keys/models. Actual router-reported identities are saved, not presented as independently verified upstream identities. Credential errors and unrelated invalid requests stay explicit. See README for full configuration, cooldowns and retry limits.

Secrets live only in ignored backend/.env. Keep that file, service dashboards, databases and credentials out of the assessment video. Do not paste API keys into topics or feedback. The API is intended for a single local development process and one active workflow, not an authenticated multi-user production deployment.

## Language and API example

```json
{
  "topic": "Introduction to RAG",
  "language": "ta",
  "reference_pack_id": "rag-primary-v1",
  "demo_error": false
}
```

POST this to `/api/runs`. Responses and history identify the run; `/api/runs/{id}/events` exposes progress, `/cancel` stops it, and `/export?format=pdf|txt|docx|markdown|json` downloads saved output. Supported language codes and the migration policy are in LANGUAGES.md. Omitted language means English for older clients.

## Assessment demonstration

Use the approved English RAG artifact and saved deliberate-error backup described in VERIFICATION.md. Follow VIDEO_WALKTHROUGH.md for the 15–20-minute presentation. Show actual failures, corrections, provider switches and memory status. Do not call a failed comparison an improvement. The public document/video links and final form submission remain external completion items.

## Checks and troubleshooting

```powershell
cd D:\LessonLoop\backend
.\.venv\Scripts\python.exe -m pytest -q
cd ..\frontend
npm run build
npm run test:ui
```

Browser tests require both local servers to be reachable. Do not restart the backend while testing its health endpoint or while a user run is active. A 409 busy response means wait or cancel the existing run. An unreachable FreeLLM service is not an exhausted key pool; start/check the configured local router. Increasing output budgets can help truncation but cannot guarantee provider availability. All final provider failures remain unapproved.
