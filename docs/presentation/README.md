# Presentation source

This source builds an editable 16-slide PowerPoint for the LessonLoop recording. Slides 1–13 support about seven minutes of explanation, slide 14 closes after the product demo, and slides 15–16 hold the full implementation commit history as optional reference.

`deck-content.mjs` contains the slide copy, timing, source references and Tanglish speaker notes. `build-deck.mjs` lays out native editable text and the requested workflow diagram using the bundled Codex Artifact Tool. The application itself does not depend on the presentation runtime.

The generated PPTX/PDF, application screenshot and render evidence live in ignored `artifacts/presentation/` and `.cache/presentation-build/`. The repository workflow excludes generated artifacts from Git. The companion recording script is tracked at `docs/DEMO_PRESENTATION_SCRIPT.md`.

## Rebuild in the authoring environment

Use the runtime locations returned by `load_workspace_dependencies`. Set `RUNTIME_NODE_MODULES`, `RUNTIME_PYTHON` and `PRESENTATIONS_SKILL_DIR`. Optionally set `LESSONLOOP_WORKSPACE` if the checkout is outside D:/LessonLoop. Set `DECK_OUTPUT` to a fresh filename, because finalization intentionally refuses to overwrite a previous deliverable.

Before first authoring, run the skill's artifact-start marker as documented in its implementation guide. Supply a screenshot of a genuine approved run as `artifacts/presentation/product.png`. Never include credentials or private provider dashboards. Then run this builder with the supplied runtime Node executable.

The finalizer checks package structure, canvas dimensions, fonts and importability. Render and inspect every slide before handoff. In this Windows environment the optional Artifact Tool PDF exporter failed to resolve a bundled Helvetica module; native Microsoft PowerPoint produced the PDF preview instead. Native PowerPoint also rendered the PPTX for inspection. The workflow's return arrow uses explicit editable connector segments to preserve its path in PowerPoint.

The presentation describes an Agile-inspired individual workflow, not invented Scrum ceremonies. It distinguishes implementation from live learning acceptance and does not claim that a recording or public document URL already exists. Evidence uses the application snapshot through commit 1df29aa on 15 November 2026.
