# Sprint 1 verification

Verified on 13 November 2026 on Windows. The application now uses Gemini only for the connection foundation and planned lesson generation/evaluation. Automated checks and real provider results are recorded separately below.

## Results

| Check | Outcome |
| --- | --- |
| Backend tests | **26 passed**. No external provider requests. |
| Frontend type check | **Passed** (`tsc --noEmit`). |
| Frontend production build | **Passed** (`vite build`). |
| Browser tests | **12 passed** across installed Edge desktop (1440 px) and mobile (390 px) viewports. |
| Visual review | Desktop and mobile screenshots inspected. Real local configuration, mocked success results, and backend downtime/retry states verified. |
| Real local backend health | **HTTP 200**, correct LessonLoop/development response. |
| Real local configuration endpoint | **HTTP 200**, contains only the configured Gemini provider and its selected model ID; no keys are returned. |
| Real local frontend | **HTTP 200**, opens and reaches the backend. No browser page errors in the live-backend test. |
| Real Gemini request | **Success**, `gemini-3.5-flash-lite`, **1,576 ms**. Actual text: `LessonLoop connection OK.` Checked at `2026-11-13T16:48:29.573393Z` (10:18:29 PM IST). |
| Secret hygiene | Local backend/frontend `.env` files and generated folders confirmed ignored. No real environment files tracked. Candidate source scan found no provider key prefixes. |

Browser success screenshots deliberately contain **mocked** text and test model IDs. They demonstrate UI behavior, not real Gemini connectivity. The `live-*` screenshots show the actual local backend configuration without inference.

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
| LangGraph | 1.2.21 |
| pytest / HTTPX | 9.2.0 / 0.28.1 |
| React / React DOM | 19.3.1 / 19.3.1 |
| Vite / TypeScript | 7.3.8 / 5.9.3 |
| Tailwind CSS | 4.3.5 |
| Playwright | 1.65.0 |

Exact transitive dependencies are in the two backend requirements files and `frontend/package-lock.json`.

## Current acceptance status

The Gemini-only Sprint 1 foundation is complete: the frontend runs, backend health/configuration work, the real Gemini request succeeds, and credentials stay on the backend. Lesson generation and evaluation remain later-sprint work and will both use Gemini.

The secondary SDK, client code, settings, environment template entries, dashboard card, and dependency pins have been removed. Its entries were also removed from the ignored local backend environment file, with Gemini settings preserved. Automated tests assert that the removed provider name is rejected and its card is absent.

After removal, one real Gemini request was made through the running backend endpoint, returning HTTP 200 and the actual text recorded above. Sanitized machine-readable results are saved locally in the ignored `artifacts/provider-checks.json` file. No automatic provider requests were added.
