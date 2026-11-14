# LessonLoop face-visible walkthrough

Target length: 18 to 20 minutes. A human must record with their own face visible. This repository supplies the script and backup evidence; it does not contain a fabricated recording or video URL.

## Pre-recording checklist

- Run backend and frontend in separate terminals using the README commands.
- Open the app at http://localhost:5173 and verify the selected Gemini model labels.
- Keep `.env`, API dashboards, private account details, and browser password prompts off screen.
- Check the camera and microphone. Place the camera bubble where it does not cover status labels.
- Confirm the approved normal run and saved deliberate-error backup exist in `submission/`.
- Open `submission/evaluator-calibration.json`, `submission/prompt-improvement.json`, `docs/DESIGN.md`, and backend source in separate tabs.
- Read VERIFICATION.md for the actual recorded results. Say `NO_IMPROVEMENT`, errors, or disagreement counts exactly as recorded; do not imply a failed candidate activated.
- Do not repeatedly generate paid runs just to make a recording smoother. Use the clearly labelled saved backup if a provider is slow.
- Confirm the real GitHub URL and final document path. A video link is pending until you record and upload it.

## 0 to 2 minutes — Problem and learner

App action: show Lesson studio and the learner summary.

Speaker notes: “Our learner has finished grade 12 in India, studied outside English-medium education, and is starting an AI career. A fluent AI answer may still use unexplained jargon or invent a fact. LessonLoop creates a lesson and checks specific requirements before releasing it. I chose Gemini only; generation and evaluation are separate calls, which can still share mistakes.”

## 2 to 6 minutes — Normal end-to-end run

App actions:

1. Keep Introduction to RAG and the reviewed RAG reference pack selected.
2. Leave the deliberate-error option unchecked.
3. Click Generate lesson once. Open Live workflow events.
4. Explain each actual backend stage as it appears. Do not narrate a stage that has not occurred.
5. Once complete, show the lesson, illustrative notice, missing-information answer, recap, and expandable practice answers.
6. Open Quality report. Explain that 14/14 is a count of hard checkpoints, not an averaged score.
7. Download the approved Markdown and JSON audit if the run is approved. If it is not approved, show the honest status and open the saved approved normal run instead.

Files: `submission/final-lesson/lesson-approved.md`, `audit.json`, and `run-metadata.json`.

## 6 to 10 minutes — Deliberate factual error

App actions:

1. Start a new run with “Inject a factual error into the first draft” enabled, or open the clearly labelled saved backup run from VERIFICATION.md.
2. Open Attempts. Expand Development error injection audit on draft 1.
3. Show the generated original and the altered claim: “RAG guarantees that the AI answer is always correct.”
4. Show the real evaluator's failed checks, evidence, and requested correction. It received no demo label or desired verdict.
5. Compare actual adjacent draft changes. Show whether the targeted checks passed in the next real evaluation.
6. Explain that an evaluator could miss an error; such a result is a defect to investigate, not a reason to hardcode a rejection.

Backup files: `submission/backup-demo/` contains the actual preserved rejection log and audit. Identify it aloud as a saved live run, not a newly executing request.

## 10 to 14 minutes — State, graph, rubric, and sources

Files/screens:

- `backend/app/workflow.py`: StateGraph nodes, conditional edge, MAX_RETRIES usage.
- `backend/app/lesson_schemas.py`: structured lesson and evaluator fields.
- `backend/app/quality.py`: expected IDs, evidence checks, and `releasable`.
- `backend/content/rubric.json`: all checks mandatory with passing/failing evidence conditions.
- `backend/content/rag_sources.json`: reviewed primary sources, claims, notes, access dates.
- Quality report → Inspect approved references.

Speaker notes: “Python enforces release and stopping rules. Initial generation plus two retries is three drafts. Reaching the limit never means approval. Source IDs are checked in code, but whether a claim follows a source still needs evaluation. We test the evaluator too.”

## 14 to 17 minutes — Persistent learning and evidence

App actions:

1. Open Run history and refresh the page to retrieve stored runs.
2. Open Memory & learning. Show independent-run counts and their supporting run IDs.
3. Explain which observations came from deliberate-error demonstrations.
4. Open the recorded baseline/candidate comparison. Show both drafts and per-check verdicts.
5. State its actual result. If no improvement was observed, explain why it correctly stayed inactive. Show mocked activation/persistence tests as tests, not live model evidence.
6. If an instruction was actually activated, open the subsequent live run and show its selected memory IDs and prompt version. Otherwise identify live reuse as unobserved rather than inventing it.
7. Show Feedback: a new observation starts unverified. Demonstrate review with an honest human note only if you personally checked the claim.

Files: `backend/app/improvements.py`, `tests/test_workflow.py`, `submission/prompt-improvement.json`, and `submission/memory-evidence.json` when present.

## 17 to 20 minutes — Tests, limitations, outputs, repository

Show `python -m pytest -q`, `npm run build`, and browser results already recorded; avoid spending the recording waiting for every test.

Open the evaluator calibration/holdout report. Explain false passes, false rejections, per-check disagreements, and technical failures separately. Ten authored examples cannot prove general evaluator accuracy.

Explain local-only task execution and restart interruption, one reviewed topic, same-provider bias, and the lack of public-deployment security. Show the final approved lesson, rejection log, audit, clean document version, and real GitHub repository.

Close with the actual remaining human steps: record and upload this video, publish/import the lesson document if required, and supply those real links. Do not claim the assessment form has been submitted.

## After recording

1. Watch the entire recording and verify face visibility, readable text, accurate claims, and hidden secrets.
2. Upload to your chosen recording host and check sharing permissions from a signed-out browser.
3. Import/copy the clean lesson document into Google Docs or Notion and verify its sharing link.
4. Put the real video and document URLs in the submission checklist. Never substitute the local app URL as a public demo URL.
5. Submit the assessment form yourself unless you explicitly authorize a submission action.
