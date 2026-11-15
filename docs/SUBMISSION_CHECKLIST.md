# Submission checklist

## Repository

Real repository: https://github.com/sriram-Kannan-45/LessonLoop

The project workflow requires a verified push after completed updates. Check VERIFICATION.md and the latest commit before sharing. Real environment files, SQLite files, caches, dependencies, screenshots, and local logs are ignored.

## Approved lesson and audit

- Current final normal run: `b0ba902b21e64ce3a8f38a1ff446ef1d`, **APPROVED**, two drafts, 14/14 final checks. The earlier browser-started v3 run is preserved in submission/earlier-approved-v3/.
- Frozen references: rag-primary-v1.1. Frozen rubric: beginner-rag-v1.1.
- Actual Markdown: submission/final-lesson/lesson-approved.md.
- Actual rejection log: submission/final-lesson/rejection-log.md.
- Actual audit: submission/final-lesson/audit.json.
- Metadata: submission/final-lesson/run-metadata.json.
- Clean document: submission/lesson-for-google-docs.html. It is generated from the approved run, with escaped text and no fabricated approval edits.

“Approved” means the system's recorded checks passed, not a claim that the evaluator cannot miss an error. See the evaluator disagreements before presenting the system as reliable for real scholarship or career decisions.

## Deliberate-error backup

Saved live run: `d7f428ad985b4aceba7b8a17610bfeef`, **APPROVED** after two drafts. Draft 1 contains the injected false guarantee and was rejected by the real evaluator. The complete original/altered draft, actual failures, correction, and next verdict are in submission/backup-demo/. Label it aloud as a saved live backup when using it in a recording.

## Evaluation and persistent learning

- submission/evaluator-v2-first-report.json preserves the first live calibration/holdout results, including a false overall approval.
- submission/evaluator-calibration.json records the v3 combined report with disclosed held-out-set reuse.
- submission/evaluator-v4-calibration.json and submission/evaluator-calibration-v5.json preserve earlier calibration-only tests. Do not present it as unseen holdout validation.
- submission/model-trial.json records the unverified stronger-Gemini trial; the actual app model was not silently changed.
- submission/prompt-improvement-v4.json records a completed real baseline/candidate comparison with **NO_IMPROVEMENT**. There were no per-check regressions, but no targeted benefit either, so the candidate stayed inactive.
- submission/prompt-improvement-v6.json records the later Flash comparison stopped by the actual HTTP 429 daily quota. submission/quota-blocker.json records the limit (20/day), provider retry delay and estimated reset.
- submission/memory-evidence.json records persistent supporting runs, proposals, versions, and outcomes. There are **zero active learned instructions**. Mocked tests demonstrate activation, reuse, persistence, and rollback; live activation/reuse has not been observed.

This is an honest limitation, not permission to bypass the activation gate. Two genuine independent terminology failures are now saved. Once the quota resets or the project has sufficient quota, run the new paired-normal-and-targeted-v2 comparison, activate only if the actual criteria are met, restart the backend and start a later run to inspect its selected memory. Current evaluator dataset validation is also pending quota; historical reports are not relabelled as current validation. Do not weaken the rubric or fabricate a passing experiment.

## Human document publishing step

The connected account now contains the [final lesson Google Doc](https://docs.google.com/document/d/1vqeoeXSbl528_docxgoOnrb-bH9iX53mdWm55m5W3gA/edit?usp=drivesdk) and [project documentation Google Doc](https://docs.google.com/document/d/1tv5o62u8IJGClQYiLw922xzgVXsnO9TKpyFwFGLmAss/edit?usp=drivesdk). Sharing is currently restricted; verify reviewer access before submitting. Final Word copies are in docs/submission/. See docs/SUBMISSION_LINKS.md for the current link index.

## Human video step

The user supplied this [Loom recording](https://www.loom.com/share/15677d43e06540a29ead22df2c266097). Its duration, face visibility, playback access, and contents have not been independently verified. Check it against docs/VIDEO_WALKTHROUGH.md and the assessment's 15–20-minute requirement, including the end-to-end run, deliberate-error rejection, and face-visible explanation.

## Before submitting

- Follow README.md to start the app and check local health.
- Run backend tests and frontend checks, or show the recorded verified results.
- Read docs/DESIGN.md for the actual local-process, same-provider, and dataset limitations.
- Do not claim independent OpenAI evaluation: the current routing uses Gemini primary and an explicitly authorized Groq quota backup.
- Do not claim learned memory improved a live run while all candidates remain inactive.
- Review the lesson yourself for overlooked clarity/factual issues before using it as teaching material.
- Verify GitHub, document, and video links. The app's localhost URL is not a public deployment URL.
- The assessment form has not been submitted; the user must submit it or explicitly authorize that action.

## Dynamic-topic support

The current studio accepts arbitrary subject names, collects topic-specific public Wikipedia references, and uses a generic fourteen-check beginner rubric. Inspect reference relevance and attribution in each run. No human review of automatically collected references is claimed. Historical RAG lesson artifacts above remain unchanged. See submission/topics-live-verification.json for actual new-topic integration outcomes; broad subject accuracy and topic-specific learning activation are not claimed.
