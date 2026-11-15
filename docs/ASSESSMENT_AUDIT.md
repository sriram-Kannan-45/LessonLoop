# Assessment audit

Audited 15 November 2026 against the assessment text supplied by the user. **The core product is implemented; the submission is not yet fully complete.** Implementation, live observations and external deliverables are different kinds of evidence.

| Requirement | Finding | Evidence and completion boundary |
| --- | --- | --- |
| Agentic generate → evaluate → regenerate | Implemented | `backend/app/workflow.py` is a compiled LangGraph with conditional rewrite routing. |
| Submission topic Introduction to RAG | Implemented | Canonical RAG topics use the reviewed primary-source pack and RAG rubric. Other topics remain supported with automatic references. Historical approved RAG lesson: `submission/final-lesson/`. |
| Beginner from an Indian non-English-medium school | Implemented as instructions and checks | Fixed learner profile, standalone structure, terminology/prerequisite checks and practice answers. Representative learner comprehension is not independently established. |
| What it is, why it matters, how it works | Implemented | Required lesson schema and content checks. |
| Hard pass/fail rubric, no averaged score | Implemented | English has 14 mandatory checks. Native-language lessons have 15 including LANGUAGE. Strict booleans, exact IDs and evidence validation; every check must pass. |
| Accuracy and grounding | Implemented with limitations | Frozen references/claim mappings and separate semantic evaluation. Reviewed RAG primary sources differ from automatically collected Wikipedia references. Historical evaluator disagreements are preserved in VERIFICATION.md. |
| Learner sees a released lesson only after the gate | Implemented in default reader | Approved lessons display normally. Unapproved content is collapsed behind an explicit Inspect unapproved draft action for debugging/review; downloads remain labelled NOT APPROVED. |
| Feedback drives at most 1–2 regenerations | Implemented | Initial draft plus at most two rewrites. Failed checks and requested changes feed the next generation. Exhaustion gives NEEDS_REVIEW, never approval. Technical retries are separate and bounded. |
| Passing lesson plus rejection log | Implemented; historical live evidence exists | `submission/final-lesson/lesson-approved.md`, `rejection-log.md`, audit snapshots, and adjacent draft comparisons in Attempts. Requested corrections and actual drafts remain distinguishable. |
| Planning, architecture and trade-offs | Implemented documentation | OVERALL_GUIDE.md, DESIGN.md, README.md and VERIFICATION.md. |
| Persistent memory from logs and feedback | Implemented | SQLite histories, independent failure observations, feedback verification, prompt versions and selected-memory snapshots survive restart. Human feedback is not automatically trusted. |
| Self-evolving prompts from repeated failures | Partially accepted | Observations and comparison/activation/rollback code exist. Comparisons are explicitly triggered. Latest inspected database has zero active learned instructions, four ERROR comparisons and one NO_IMPROVEMENT comparison. A qualifying live improvement plus later reuse is still unobserved. Do not claim demonstrated self-improvement. |
| Evaluator calibration | Historical evidence; current acceptance pending | Historical false passes/disagreements are documented. Current broad model/language accuracy and a current-protocol dataset rerun are not established. Earlier user instruction left those live checks pending. |
| GitHub workflow and setup README | Implemented | Repository: https://github.com/sriram-Kannan-45/LessonLoop. Push synchronization is verified after each completed change. No credentials are committed. |
| Public Google Doc or Notion final-lesson link | Pending external deliverable | Local approved lesson, clean HTML and Word/PDF exports exist. A local file is not a public document sharing link. Import the approved English RAG lesson, inspect it, then publish with appropriate sharing access. |
| Loom video 15–20 minutes, face visible | Pending external deliverable | VIDEO_WALKTHROUGH.md provides a script; `submission/backup-demo/` preserves a real deliberate-error rejection and correction. A face-visible recording and sharing URL have not been created or verified. |
| Submit through the supplied form | Not submitted | No form submission is claimed. Use the current form link in the assessment after the three deliverable links are ready. |
| Native teaching language selection (new request) | Implemented; live acceptance limited | Ten options, frozen per run, language-specific prompts and LANGUAGE gate, Unicode downloads. Tamil PDF shaping was visually checked with an authored font sample. The attempted real Tamil FreeLLM diagnostic stopped on connection failure; it is not a successful live Tamil lesson. |

## Evidence that is already available

- Approved normal RAG run `b0ba902b21e64ce3a8f38a1ff446ef1d` and a second independent RAG correction run are recorded in VERIFICATION.md.
- Deliberate-error backup `d7f428ad985b4aceba7b8a17610bfeef` preserves the actual generated original, inserted false guarantee, real rejection and corrected next draft.
- Historical comparisons were not activated when they failed or showed no improvement. This is correct gating behavior, not proof of successful learning.
- New local-router diagnostics explicitly identify controlled Gemini/Groq failures rather than claiming those failures occurred naturally.

## Work remaining before claiming the full assessment is complete

Later submission-link update: the connected account now contains the [final lesson](https://docs.google.com/document/d/1vqeoeXSbl528_docxgoOnrb-bH9iX53mdWm55m5W3gA/edit?usp=drivesdk) and [project documentation](https://docs.google.com/document/d/1tv5o62u8IJGClQYiLw922xzgVXsnO9TKpyFwFGLmAss/edit?usp=drivesdk) Google Docs, and the user supplied a [Loom recording](https://www.loom.com/share/15677d43e06540a29ead22df2c266097). These links supersede the earlier absence of document/video URLs. Restricted document sharing and recording compliance still require verification; the original product-learning and calibration findings remain unchanged. See docs/SUBMISSION_LINKS.md.

1. With sufficient provider capacity, complete the reviewed English RAG comparison protocol. Activate only on the actual improvement/no-regression rules, then demonstrate a later run selecting that instruction. A NO_IMPROVEMENT outcome must stay inactive.
2. Complete the current evaluator dataset run and inspect disagreements; obtain language-specific review before making broad native-language quality claims.
3. Publish the final approved English Introduction to RAG lesson as a Google Doc or Notion page and verify its sharing link.
4. Record and upload the 15–20-minute face-visible workflow video, including the deliberate-error case and honest learning results.
5. Submit the verified repository, document and video links. No automated assessment submission was performed during this audit.
