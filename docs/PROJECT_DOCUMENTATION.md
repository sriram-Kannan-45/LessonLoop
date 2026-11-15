# LessonLoop Project Documentation

LessonLoop creates beginner lessons, evaluates them against mandatory checks, and revises failed drafts before release. This document explains the project, the saved Introduction to RAG lesson, and the demonstration to record for the assessment. The intended reader is the assignment reviewer; the speaking notes can also guide the presenter.

Repository: https://github.com/sriram-Kannan-45/LessonLoop

## Problem and intended learner

A fluent AI answer can contain false claims, unexplained technical words, or missing teaching steps. LessonLoop makes those issues visible through a generation and evaluation loop. Its learner is an Indian grade 12 graduate with limited English vocabulary and no assumed AI or programming background.

The submission lesson is Introduction to RAG. RAG means retrieval-augmented generation: finding relevant information in outside documents and placing it in the model input before the model writes an answer. The lesson explains what RAG is, why it helps, how it works, and why it can still make mistakes.

## Project objectives

- Create a structured lesson with objectives, explanation, a worked example, limitations, a recap, and three practice questions with answers.
- Check content and teaching quality through explicit pass or fail decisions.
- Use failed checks to request targeted revisions, with at most two rewrites.
- Preserve references, drafts, evaluation reasons, provider usage, and final status for inspection.

## Architecture and technology choices

React and TypeScript provide the lesson studio, live progress, lesson reader, quality report, attempt history, memory view, and downloads. Vite serves the frontend during local development; Tailwind supports its styling.

FastAPI exposes the backend API. LangGraph runs the actual stateful workflow and its conditional rewrite route. Pydantic validates structured lesson and evaluator responses. SQLite stores histories, feedback, prompt versions, and memory for this local single-user application.

Gemini is the primary generation and evaluation provider. Configured Groq fallback handles Gemini quota responses. An optional FreeLLM router can handle eligible later failures. Each draft records the actual reported provider and model. Fallback improves availability; it does not prove the evaluator is correct or independent.

The graph is implemented in backend/app/workflow.py. Quality validation is in backend/app/quality.py, provider orchestration is in backend/app/services/lesson_ai.py, and the interface starts in frontend/src/App.tsx.

## How the agentic workflow runs

1. The user chooses a topic, learner preset, and teaching language, then starts a run.
2. The backend freezes the sources, rubric, prompts, language, and selected memory for that run. Canonical RAG topics use the reviewed RAG reference pack; other topics retrieve public Wikipedia excerpts automatically.
3. The generator creates a structured lesson using that context.
4. Python checks the required structure and reference identifiers.
5. Separate model calls evaluate the lesson against the remaining mandatory checks. Evaluator output must satisfy local validation, including expected check IDs and valid evidence.
6. If every mandatory check passes, the run becomes APPROVED. Failed checks and requested corrections otherwise feed the next generation.
7. After the initial draft and two unsuccessful rewrites, the run becomes NEEDS_REVIEW. Technical failures produce ERROR; cancellation and interrupted execution have their own statuses. None of these statuses authorizes release.
8. The application saves the history and offers correctly labelled lesson and audit downloads.

An agentic workflow uses evaluation results to decide its next action. Here, the graph chooses whether to revise or finish. The implementation has generation and evaluation roles; the rewrite uses the generation role again. It does not require a separate model for every node.

## Quality evaluation and release

English lessons have fourteen mandatory checks: two code checks and twelve model checks. Native-language lessons add a LANGUAGE check. A count such as fourteen out of fourteen shows passed checkpoints, rather than an average quality score.

For the RAG lesson, the code checks validate complete structure and approved source identifiers. Model checks cover the RAG definition, the need for external knowledge, retrieval and generation order, document preparation, the distinction from retraining, grounded claims, explained terminology, prerequisites, the worked example, honest limitations, missing information, and coherent teaching with correct practice answers.

Every mandatory check must pass. Missing checks, malformed verdicts, and invalid evidence cannot approve a lesson. Valid evidence selection establishes which text was assessed; it does not establish that the model interpreted the text correctly.

## Demonstrating a deliberate error

Enable Inject a factual error into the first draft. The application preserves the generated original before altering the first draft. For the RAG demonstration, it inserts the claim: "RAG guarantees that the AI answer is always correct."

The evaluator receives the altered lesson without a demo label or desired verdict. It must identify the false guarantee through its normal rubric. Failed-check feedback asks the generator to correct the lesson; the error is not inserted into later drafts.

The saved live backup run d7f428ad985b4aceba7b8a17610bfeef shows this behavior. Draft one failed HONEST_LIMITATIONS because it claimed guaranteed correctness; a separate SOURCES check also failed. Draft two passed all mandatory checks. The audit and rejection log are in submission/backup-demo/.

In the video, show the altered text, the evaluator's actual reason, the required correction, and the next draft. If using the saved run, identify it as previously recorded live evidence. A new run that misses the error must be described honestly.

## Saved final lesson and observed results

The final lesson is Introduction to RAG Finding Facts for AI. Its saved run ID is b0ba902b21e64ce3a8f38a1ff446ef1d. The record shows Gemini generation, a separate Gemini evaluator, two drafts, and final status APPROVED. Its frozen source pack is rag-primary-v1.1 and its rubric is beginner-rag-v1.1.

The first draft failed TERMS_EXPLAINED and NO_PREREQUISITES because it used concepts such as weights and pipeline without sufficient explanation. The next draft added beginner explanations and passed every mandatory check. This is evidence of correction within a run.

The lesson includes an explicitly invented Asha College book-grant notice. It demonstrates retrieving the application deadline and saying that the grant amount is missing from the passage. The invented notice is a teaching example, not real scholarship guidance.

The approved lesson, rejection log, audit JSON, and run metadata are preserved in submission/final-lesson/. The companion final-lesson Word document reproduces that saved lesson, with formatting changes only. Its approval is the application's historical verdict, not a guarantee of factual perfection or a new evaluation.

## Memory and current limitations

SQLite preserves recurring failure observations, reviewed feedback, prompt versions, comparisons, and selected-memory snapshots. Prompt comparisons require explicit initiation. Candidate activation requires a targeted improvement without regression, and eligible prompts can be rolled back.

The assessment audit records no demonstrated qualifying live prompt activation followed by later reuse. Describe that capability as implemented with live acceptance still pending. Correction within a run does not establish learning across future runs. Broad evaluator accuracy and native-language teaching quality also need more review.

The local runner uses one backend worker and one active task slot. Saved drafts survive a restart, but unfinished work becomes interrupted rather than automatically resuming. Public hosting would require authentication, durable execution, spending controls, and additional operational work.

## Setup and running the application

Use Python 3.11 or later, a supported Node.js version from the README, npm, Git, and provider access. From the repository root in PowerShell:

```powershell
py -3.11 -m venv backend\.venv
.\backend\.venv\Scripts\python.exe -m pip install -r backend\requirements-dev.txt
cd frontend
npm ci
cd ..
if (-not (Test-Path backend\.env)) { Copy-Item backend\.env.example backend\.env }
if (-not (Test-Path frontend\.env)) { Copy-Item frontend\.env.example frontend\.env }
```

Edit backend/.env locally with the provider settings from backend/.env.example. Keep API keys in the backend file. Frontend variables are public. Do not show environment files while recording. Restart the backend after changing its settings.

Start the backend from the repository root in one terminal:

```powershell
cd backend
.\.venv\Scripts\python.exe -m app.main
```

Start the frontend from the repository root in a second terminal:

```powershell
cd frontend
npm run dev
```

Open http://localhost:5173. Use this exact origin with the default configuration. The backend API documentation is available at http://127.0.0.1:8000/docs. The README provides interpreter recovery, provider configuration, troubleshooting, and the authoritative setup details.

For application validation, run the backend pytest suite and the frontend typecheck, build, and UI tests using the README commands. Automated inference tests use mocks; passing them does not establish live model accuracy. Consult VERIFICATION.md for recorded live outcomes and known disagreements.

## Recording plan for an eighteen minute video

### Minutes zero to two introduce the project

Show the studio with your face visible. Say: "LessonLoop creates a beginner lesson, checks it, and revises it when mandatory checks fail. My submission topic is Introduction to RAG. The intended learner has completed grade twelve and does not need prior programming knowledge."

### Minutes two to five explain the lesson topic

Open the final lesson. Say: "RAG stands for retrieval-augmented generation. Think of an open-book exam. The system searches useful documents, adds the relevant passage to the model input, and then writes an answer. Looking up documents does not itself retrain the model."

Use the invented college notice: "The passage gives a deadline of fifteen July, so the answer can use that deadline. It does not give the grant amount, so the system should say that information is missing. RAG can still make mistakes when sources are outdated, retrieval is weak, or the model adds unsupported details."

### Minutes five to nine show a normal run

Enter Introduction to RAG, select English, leave error injection off, and start generation. Show actual progress events, the finished status, the lesson, the quality report, and attempt history. Explain a rewrite only if one occurs. If the provider fails, describe the status and clearly identify any saved evidence you open.

### Minutes nine to thirteen demonstrate the deliberate error

Start a run with error injection enabled. Show the false correctness guarantee, evaluator rejection, required changes, and the corrected next draft. Explain that the evaluator decides through the normal checks. Keep the saved live backup available if provider availability prevents a fresh demonstration.

### Minutes thirteen to sixteen explain the implementation

Show the LangGraph nodes and conditional edge in workflow.py. Explain that the next action depends on the verdict. Show the two-rewrite limit, the strict release rule, and the stored history. Describe memory as a separate capability and state its actual acceptance limits.

### Minutes sixteen to eighteen show the outputs

Open the approved lesson document, repository README, and audit export. Explain the distinction between mock tests and live evidence. End by showing the verified repository and document sharing links. Keep your face visible during the walkthrough and check the audio before the full recording.

## Submission documents and links

The assessment's Document link should open the final lesson content in Google Docs or Notion. This project explanation supports the walkthrough and can be shared separately. Upload the companion final-lesson Word document into Google Docs, or copy its content into Notion, then check the resulting document and its sharing access.

Submit the actual repository link, accessible final-lesson document link, and uploaded fifteen to twenty minute face-visible Loom link. A local Word file does not create a hosted document URL. Public document publication, video recording, and assessment-form submission remain separate completion steps.

## Project evidence

- README.md contains setup, run commands, provider configuration, and feature details.
- docs/ASSESSMENT_AUDIT.md separates implementation from pending assessment acceptance.
- VERIFICATION.md records actual tests, live results, and known evaluator limitations.
- submission/final-lesson/ contains the saved approved lesson and its evaluation history.
- submission/backup-demo/ contains the saved deliberate-error rejection and correction.
- docs/VIDEO_WALKTHROUGH.md contains the longer recording checklist and demonstration notes.
