# Submission checklist

## Repository

Real repository: https://github.com/sriram-Kannan-45/LessonLoop

The project workflow requires a verified push after completed updates. Check VERIFICATION.md and the latest commit before sharing. Real environment files, SQLite files, caches, dependencies, screenshots, and local logs are ignored.

## Approved lesson and audit

- Final normal browser run: `a791fca8f9004ca1828c59ef1b63794e`, **APPROVED**, one draft, 14/14 checks.
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
- submission/evaluator-v4-calibration.json records the current evidence protocol's calibration-only test. Do not present it as unseen holdout validation.
- submission/model-trial.json records the unverified stronger-Gemini trial; the actual app model was not silently changed.
- submission/prompt-improvement-v4.json records a completed real baseline/candidate comparison with **NO_IMPROVEMENT**. There were no per-check regressions, but no targeted benefit either, so the candidate stayed inactive.
- submission/memory-evidence.json records persistent supporting runs, proposals, versions, and outcomes. There are **zero active learned instructions**. Mocked tests demonstrate activation, reuse, persistence, and rollback; live activation/reuse has not been observed.

This is an honest limitation, not permission to bypass the activation gate. For more evidence, collect genuine repeated failures, run a new bounded comparison, and activate only if the actual criteria are met. Do not weaken the rubric or fabricate a passing experiment.

## Human document publishing step

No connected document session was available. The clean HTML and Markdown are ready locally. Open the HTML in a browser, copy its rendered content into a Google Doc or Notion page, check the headings and reference links, and choose the required sharing access. Verify the resulting link before adding it to the assessment. No published document URL is claimed yet.

## Human video step

Use docs/VIDEO_WALKTHROUGH.md to record a face-visible 15–20-minute walkthrough. Hide the environment file and account details. Include actual live results and the recorded evaluator/memory limitations. Upload the recording, test its sharing link while signed out, and add the real video URL. No recording/upload is claimed in this repository.

## Before submitting

- Follow README.md to start the app and check local health.
- Run backend tests and frontend checks, or show the recorded verified results.
- Read docs/DESIGN.md for the actual local-process, same-provider, and dataset limitations.
- Do not claim independent OpenAI evaluation: the user chose Gemini only.
- Do not claim learned memory improved a live run while all candidates remain inactive.
- Review the lesson yourself for overlooked clarity/factual issues before using it as teaching material.
- Verify GitHub, document, and video links. The app's localhost URL is not a public deployment URL.
- The assessment form has not been submitted; the user must submit it or explicitly authorize that action.
