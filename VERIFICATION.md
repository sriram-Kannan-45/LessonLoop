# Sprint 1 verification

Verified on 13 November 2026 on Windows. This is an implementation/verification record, not a claim that provider account access has been validated.

## Results

| Check | Outcome |
| --- | --- |
| Backend tests | **29 passed**. No external provider requests. |
| Frontend type check | **Passed** (`tsc --noEmit`). |
| Frontend production build | **Passed** (`vite build`). |
| Browser tests | **12 passed** across installed Edge desktop (1440 px) and mobile (390 px) viewports. |
| Visual review | Desktop and mobile screenshots inspected. Real local configuration, mocked success results, and backend downtime/retry states verified. |
| Real local backend health | **HTTP 200**, correct LessonLoop/development response. |
| Real local configuration endpoint | **HTTP 200**, both providers unconfigured, selected model IDs visible, no keys. |
| Real local frontend | **HTTP 200**, opens and reaches the backend. No browser page errors in the live-backend test. |
| Real Gemini request | **Pending credentials; not attempted.** Requested model will be `gemini-3.5-flash-lite`; latency is not available. |
| Real OpenAI request | **Pending credentials; not attempted.** Requested model will be `gpt-4.1-mini`; latency is not available. |
| Secret hygiene | Local backend/frontend `.env` files and generated folders confirmed ignored. No real environment files tracked. Candidate source scan found no provider key prefixes. |

Browser success screenshots deliberately contain **mocked** text and test model IDs. They demonstrate UI behavior, not real Gemini/OpenAI connectivity. The `live-*` screenshots show the actual local backend configuration without inference.

Screenshots are generated in the ignored `artifacts/` directory: `live-desktop.png`, `live-mobile.png`, `results-desktop.png`, `results-mobile.png`, `unavailable-desktop.png`, and `unavailable-mobile.png`.

## Environment issues handled

- The workspace began empty with no applicable AGENTS.md files or existing Git repository. A local repository was initialized; no user files were replaced.
- Python 3.12.6 still fails with missing `encodings`. The existing uv-managed Python **3.11.16** works and was used for `backend/.venv`. Global installations and variables were left alone.
- C: had **zero free space**. Dependency cache and temporary files were redirected to ignored project-local folders on D:, which had ample space. No user files were deleted. pytest and Playwright are configured to keep their temporary artifacts on the project drive.
- The interactive browser-control tool could not initialize because C: was full. Installed Microsoft Edge was successfully tested through Playwright instead; no browser download was needed.

## Resolved versions

| Component | Version |
| --- | --- |
| Python | 3.11.16 |
| Node.js / npm | 24.14.0 / 11.18.0 |
| FastAPI / Uvicorn | 0.162.6 / 0.54.0 |
| pydantic-settings | 2.16.3 |
| google-genai | 2.34.0 |
| openai | 2.54.0 |
| LangGraph | 1.2.21 |
| pytest / HTTPX | 9.2.0 / 0.28.1 |
| React / React DOM | 19.3.1 / 19.3.1 |
| Vite / TypeScript | 7.3.8 / 5.9.3 |
| Tailwind CSS | 4.3.5 |
| Playwright | 1.65.0 |

Exact transitive dependencies are in the two backend requirements files and `frontend/package-lock.json`.

## Remaining acceptance criteria

The local foundation is implemented and verified. **Sprint 1 is not fully accepted until both real provider checks succeed.**

1. Enter the Gemini and OpenAI keys locally in the ignored `backend/.env`. Do not put them in frontend files or chat.
2. Start/restart the backend and start the frontend using the README commands.
3. Open `http://localhost:5173` and click **Test connection** once for each provider. These requests can incur charges.
4. Confirm actual response text, requested model, latency, and timestamp. Resolve any credential, model-access, or quota error the dashboard reports.
