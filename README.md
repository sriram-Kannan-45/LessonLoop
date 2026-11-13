# LessonLoop

**Generate. Evaluate. Improve.** LessonLoop will use Gemini to generate and evaluate beginner lessons, then improve failed lessons through LangGraph.

Sprint 1 builds the connection foundation: a React setup dashboard, a FastAPI backend, safe configuration, and small manual provider checks. Lesson generation is intentionally a later sprint.

## What is ready

- Responsive React + TypeScript + Vite + Tailwind dashboard.
- Backend health and provider configuration checks that do not call a model.
- A manual Gemini connection test using the official async Google Gen AI SDK.
- Explicit timeouts, no automatic provider retries, sanitized errors, and a local backend environment file.
- Backend tests and desktop/mobile browser tests that do not spend API credits.
- LangGraph installed for the future lesson workflow; no database or workflow is implemented yet.

**Gemini is the only AI provider.** Its real connection was verified with `gemini-3.5-flash-lite`. See `VERIFICATION.md` for actual results. Lesson generation and evaluation will both use Gemini in later sprints.

## Prerequisites

- Windows PowerShell, Git, and a working Python 3.11+ installation.
- Node.js 20.19+ or 22.12+ and npm. This workspace was tested with Node 24.14.0 and npm 11.18.0.
- A Gemini API key with access to the selected text model. Enter credentials locally, never in chat.
- Microsoft Edge for the optional browser tests, or another Playwright-supported browser.

## 1. Install the backend

Open PowerShell in the project root, for example `D:\LessonLoop`:

```powershell
py -3.12 -m venv backend\.venv
.\backend\.venv\Scripts\python.exe -m pip install -r backend\requirements-dev.txt
```

If you already have a working virtual environment, keep it. Activation is optional; the commands here call its Python directly, so PowerShell execution-policy restrictions on `Activate.ps1` do not matter. If you prefer activation, use `.\backend\.venv\Scripts\Activate.ps1` from the project root.

**Python issue on this machine:** Python 3.12.6 at `C:\Users\user\AppData\Local\Programs\Python\Python312\python.exe` still fails to import `encodings`; its standard library is incomplete. Python 3.11.16 installed by uv works. The local virtual environment has already been created with that interpreter. No global installation was changed. To recreate it on this machine, use the already installed uv:

```powershell
uv venv --python 3.11 backend\.venv
uv pip install --python backend\.venv\Scripts\python.exe -r backend\requirements-dev.txt
```

The application does not need uv after installation. Production-only Python dependencies are pinned in `backend/requirements.txt`; `requirements-dev.txt` also includes pytest and HTTPX. The `.in` files record the intended direct dependency ranges.

## 2. Install the frontend

```powershell
cd frontend
npm ci
cd ..
```

Use `npm ci` to install the exact versions from `package-lock.json`.

## 3. Add environment files and credentials

Templates were copied into ignored local `.env` files during setup. On a fresh checkout, run these commands from the project root. They preserve existing files:

```powershell
if (-not (Test-Path backend\.env)) { Copy-Item backend\.env.example backend\.env }
if (-not (Test-Path frontend\.env)) { Copy-Item frontend\.env.example frontend\.env }
```

Open **`backend/.env` in your editor**. Enter your key beside `GEMINI_API_KEY=`. Keep the key in the backend only. Do not commit them or paste them into chat.

The example selects `gemini-3.5-flash-lite`. The model ID is configurable; access depends on your account. The app sends exactly the model you select and does not fall back to another model. These small smoke checks request at most 64 output tokens. If you select a model with substantial internal reasoning, this limit may leave no usable text; choose a suitable short-text model for this sprint.

Model and SDK syntax were checked against the official documentation:

- [Gemini 3.5 Flash-Lite](https://aistudio.google.com/docs/models/gemini-3.5-flash-lite) and [Google Gen AI Python SDK](https://github.com/googleapis/python-genai).
- [Pydantic settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/), [Vite](https://vite.dev/guide/), and [Tailwind Vite integration](https://tailwindcss.com/docs/installation/using-vite).

`backend/.env` is resolved relative to the backend source, regardless of the current working directory. Process environment variables override file values. Blank or whitespace-only keys and model IDs mean missing configuration. Restart the backend after editing its environment file.

The only frontend setting is `VITE_API_BASE_URL=http://127.0.0.1:8000`. All `VITE_*` values are public. Never put a provider key there. Restart Vite after editing frontend environment settings.

## 4. Run in two terminals

In the first terminal, from the project root:

```powershell
cd backend
.\.venv\Scripts\python.exe -m app.main
```

In the second terminal, from the project root:

```powershell
cd frontend
npm run dev
```

Open **[http://localhost:5173](http://localhost:5173)**. The frontend checks backend health and configuration on load. It never runs a paid model check automatically.

- Backend: [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)
- Configuration: [http://127.0.0.1:8000/api/providers/status](http://127.0.0.1:8000/api/providers/status)
- Interactive API docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

Use the **Test connection** button on the Gemini card after adding credentials and restarting the backend. A successful card displays the actual returned text, the requested model, elapsed milliseconds, and your local check time. The API timestamp is UTC. Each click makes one small external request and **can incur API charges**.

“Configured” only means a key and model are present. “Connection verified” requires an actual successful provider request. Results and the checklist live in the current page session and reset on reload. There is no persistent storage in Sprint 1.

The backend binds to `127.0.0.1` by default. Its launcher reads `BACKEND_HOST` and `BACKEND_PORT` from settings. Update `VITE_API_BASE_URL` if you change the backend port. CORS allows exactly `FRONTEND_ORIGIN`, normally `http://localhost:5173`. Keep that spelling when opening the frontend; `127.0.0.1:5173` is a different origin.

## 5. Verify

Backend checks, from `backend/`:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Frontend checks, from `frontend/`:

```powershell
npm run typecheck
npm run build
npm run test:ui
```

Browser tests use the installed Microsoft Edge by default. They start Vite if needed. Keep the backend running for the two real local health/configuration browser tests. All provider inference is mocked in automated tests; no API keys or credits are required. To use installed Chrome, set `$env:PLAYWRIGHT_CHANNEL='chrome'` first. On another OS, install a supported Playwright browser with `npx playwright install chromium` and set `$env:PLAYWRIGHT_CHANNEL='chromium'`.

Tests cover missing settings, unsupported providers, returned model/text/UTC metadata, timeouts, invalid credentials, quota, model access, network failure, empty text, secret redaction, SDK request serialization, explicit CORS, and disabling paid diagnostics outside development. Browser tests cover loading, missing credentials, downtime/retry, manually triggered results, duplicate prevention, and mobile overflow.

See [VERIFICATION.md](VERIFICATION.md) for the recorded outcomes and resolved major dependency versions. All resolved Python dependencies and frontend dependencies are recorded in the lock files.

## Troubleshooting

| Symptom | Next action |
| --- | --- |
| `ModuleNotFoundError: No module named 'encodings'` | Check `py -0p` and test an interpreter with `-c "import encodings"`. Use a working interpreter to create the project virtual environment. See this machine's uv workaround above. Do not delete installations or change global Python variables just to start this project. |
| `ENOSPC` or Windows error 112 | The target drive is full. This machine's C: drive was full; project caches and temporary files were directed to D:. See commands below. No user files were deleted. |
| PowerShell blocks activation | Use `.\.venv\Scripts\python.exe` directly; activation is unnecessary. If npm's PowerShell wrapper is blocked, use `npm.cmd`. |
| Backend unavailable | Start the backend in its own terminal, check the URL, and click **Check backend**. |
| Browser reports a CORS/network error | Open `http://localhost:5173`; match `FRONTEND_ORIGIN` exactly and restart the backend. |
| Provider not configured | Add both the key and model in `backend/.env`, save, and restart the backend. An empty setting is missing. |
| Invalid credentials | Replace the key locally in `backend/.env`, confirm it belongs to that provider, and restart. |
| Model unavailable / access denied | Check the exact model ID and your account/project permissions. A 403 can indicate key restrictions as well as model access. The app will not substitute a model. |
| Rate limit / quota | Check provider billing, credits, and project quotas before retrying. |
| Timeout / provider failure | Check your network and provider status; retry manually. The timeout is configurable from 0 to 120 seconds, exclusive of 0, and defaults to 30. |
| No usable text | The provider returned no text or exhausted the output budget. Check the text model selection and retry only when needed. |
| Port is occupied | Stop the old server with Ctrl+C, or update the port and matching URL/origin settings. Vite uses a strict port to avoid silent CORS mismatches. |

If C: has no space, run this **in each setup/test terminal from the project root** before installation or browser tests. It changes only that terminal session:

```powershell
$taskCache = Join-Path (Get-Location) '.cache'
$env:TEMP = Join-Path $taskCache 'tmp'
$env:TMP = $env:TEMP
$env:UV_CACHE_DIR = Join-Path $taskCache 'uv'
$env:npm_config_cache = Join-Path $taskCache 'npm'
New-Item -ItemType Directory -Force -Path $env:TEMP | Out-Null
```

## API and development limits

| Endpoint | Behavior |
| --- | --- |
| `GET /api/health` | Liveness only; works without credentials. |
| `GET /api/providers/status` | Key/model presence only; never exposes keys or calls a provider. |
| `POST /api/providers/gemini/check` | One small Gemini request. |

Provider errors use `{ provider, status: "error", error_code, message }` without raw exceptions. Unsupported provider names return FastAPI's 422 validation response. Missing configuration returns 503, rejected credentials 401, access/model failures 403/404, quota 429, timeout 504, and other unusable/provider failures 502.

This unauthenticated diagnostic interface is **only for local development**. Provider checks are disabled when `APP_ENV` is not `development`; cross-site origins are also rejected before inference. CORS is not authentication. Do not bind this to a public interface or deploy it publicly without protecting the endpoints, enforcing access control, and adding spending/rate limits.

Real environment files, caches, virtual environments, node modules, build output, local databases, logs, and screenshots are ignored by Git. `.env.example` templates are tracked. You can check safely with `git check-ignore backend/.env frontend/.env` without printing file contents.

## Later sprints

Gemini-powered beginner RAG lesson generation and pass/fail evaluation, LangGraph rewrite routing, SQLite history, persistent memory, prompt improvement, and exports. No lesson-generation button, authentication, vector database, Docker, or deployment service is included in this sprint.
