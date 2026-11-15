# LessonLoop LinkedIn Post

I built LessonLoop, an agentic GenAI application that creates beginner-friendly lessons and evaluates them before release.

The workflow: Generate → Evaluate → Revise.

Using LangGraph, I connected lesson generation, structure validation, and separate LLM evaluation calls through shared state and conditional routing. Every mandatory check must pass before a lesson is approved. Failed checks drive up to two rewrites; unresolved drafts remain marked for review.

For the deliberate-error demo, I inserted the false claim: “RAG guarantees that AI answers are always correct.” The evaluator rejected it, and the next draft corrected the statement.

The project includes:

- 14 mandatory checks for English lessons, covering structure, sources, accuracy, clarity, and practice questions.
- Reference-grounded generation with source snapshots.
- Saved drafts, evaluation evidence, and rejection reasons for inspecting each revision.
- A React interface with workflow progress, lesson history, and document exports.

Tech stack: Python, FastAPI, LangGraph, Gemini, React, TypeScript, and SQLite.

An LLM evaluator can still miss mistakes. Approval records the checks that passed, rather than guaranteeing perfect accuracy.

I’d welcome feedback from people building agentic AI systems or technical learning experiences.

GitHub: https://github.com/sriram-Kannan-45/LessonLoop

Demo: https://www.loom.com/share/15677d43e06540a29ead22df2c266097

#GenerativeAI #LangGraph #AgenticAI #Python #AIEngineering #EdTech
