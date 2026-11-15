# LessonLoop technical interview explanations

Use these answers alongside the revised PowerPoint. The app uses LangGraph directly; do not describe a LangChain agent API or LangSmith tracing integration that the project has not configured.

## LangChain, LangGraph and LangSmith

**LangChain** provides higher-level agent abstractions and model/tool integrations. **LangGraph** gives explicit workflow control using shared state, nodes and edges. **LangSmith** provides tracing, debugging and evaluation tools. They have different responsibilities and can work together. LangGraph does not require the higher-level LangChain agent API. See the official [LangChain overview](https://docs.langchain.com/oss/python/langchain/overview), [LangGraph overview](https://docs.langchain.com/oss/python/langgraph/overview), and [LangSmith observability guide](https://docs.langchain.com/langsmith/observability).

In this repository `langgraph` is a direct requirement. Application code calls the Google SDK and HTTPX directly. The lockfile includes `langchain-core` and the LangSmith SDK as dependencies, but no `create_agent` usage or explicit LangSmith tracing setup appears in the project. Installed packages alone do not establish configured product behavior.

Tanglish: “LangChain agent building abstractions. LangGraph workflow traffic control. LangSmith observation and debugging. Namma direct-aa choose pannadhu LangGraph. Actual LLM requests SDK/HTTPX-la pogudhu. Local audit SQLite-la irukku.”

## Why LangGraph rather than only a Python loop

A Python loop could implement this small workflow. We chose an explicit graph to make state transitions, rewrite routing and separate work functions visible and testable. `generate_lesson`, `validate_structure`, `evaluate_lesson` and `persist_final_result` have different responsibilities. `route_result` chooses a rewrite or final persistence. LangGraph does not make the evaluator automatically correct. SQLite persistence and release rules are our own application responsibilities.

Tanglish: “Plain Python mudiyadhu-nu sollala. Graph structure-la each step and conditional route clear-aa kaatta mudiyudhu. Athan select pannom.”

## Node, edge, state, compile and run

- Node: a work function that reads state and returns updates.
- Edge: the next route, either fixed or conditional.
- State: the run's shared data, such as topic, current lesson, failed checks and retry count.
- `compile()`: prepares a runnable graph. It does not train an LLM or approve content.
- `ainvoke()`: asynchronously executes the compiled workflow with an initial run ID.

In our implementation `build_graph` returns `graph.compile()`. `execute_run` awaits `build_graph(...).ainvoke(...)`. The three-draft content limit and graph recursion guard are different protections.

## Why we did not fine-tune first

Our immediate objective was a grounded, inspectable generation/evaluation/rewrite system. We do not have a curated corpus of reviewed training lessons and measured held-out evidence that tuning would improve this application. Prompt/rubric versions and reference snapshots let us inspect and revise teaching behavior without launching a training job.

Supervised tuning adapts learned behavior using labelled examples; it requires data preparation and evaluation. Google documents these concepts in its [supervised tuning overview](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/tuning/supervised-tuning) and [data preparation guide](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/tuning/supervised-tuning/prepare-data). This is not a claim that fine-tuning is unsuitable for education. It could become useful for a measured recurring behavior problem after we collect reviewed examples and establish a reliable evaluation baseline.

Tanglish: “Fine-tuning bad illa. First namma defect enna, baseline quality enna-nu measure pannanum. Training examples and holdout benefit illaama tune pannina improvement prove panna mudiyadhu.”

## Prompting versus references versus fine-tuning

Prompting gives instructions. Reference context supplies supporting facts at request time. Fine-tuning adapts the model through training. These methods can complement each other. Fine-tuning does not eliminate the need for sources, citation checks, quality gates or regression evaluation.

Our code uses reviewed RAG source notes or bounded Wikipedia excerpts. It does not update model weights. The [Google RAG overview](https://docs.cloud.google.com/gemini-enterprise-agent-platform/build/rag-engine/rag-overview) explains context augmentation; it is background reading, not a claim that LessonLoop uses Google's RAG Engine.

## Why there is no vector database

This assessment builds a lesson generator, with Introduction to RAG as its submission topic. The current grounding implementation uses reviewed notes and public article retrieval, not an embedding index. SQLite stores structured audit/history records. It is not being used as a vector store.

A future document-question-answering feature would need document ingestion, chunking, embeddings, an appropriate retrieval store and retrieval-quality tests. Do not claim those components exist in the current app.

## Why SQLite and when another database would help

The local app supports one server process and one active workflow. SQLite makes local setup and durable audit records straightforward. Multi-user or multi-process deployment would require revisiting database concurrency, authentication, durable background jobs and operations; PostgreSQL is a possible option, not an implemented migration.

## Why Pydantic plus an LLM evaluator

Pydantic validates structure and strict types. Python also checks source/claim mappings, expected check IDs and exact evidence provenance. The model judges whether the teaching is accurate, clear and appropriate. Shape-correct JSON is insufficient evidence of educational quality. Every mandatory verdict must pass, and a final partial response cannot approve a lesson.

The model judge can miss errors. Historical disagreements are documented. English has fourteen mandatory checks; native-language lessons add LANGUAGE as a fifteenth. Native language support does not establish independently reviewed fluency in every supported language.

## Why provider fallback does not mean unlimited availability

Gemini is primary. Its quota failure can select Groq. Eligible Groq capacity, output-truncation, explicit JSON-validation and transient failures can select the configured FreeLLM router. Model identity and usage are recorded as reported. Credentials/configuration failures remain distinguishable. If the final route fails, the run stays unapproved.

Content rewrites address failed teaching checks and stop after three drafts total. Technical retries address request/output failures and have their own bounds. Neither is a loop that keeps spending requests until some judge finally passes a lesson.

## Why history and prompt memory are not fine-tuning

History records what happened. Reusable memory contains selected teaching instructions with provenance. Controlled comparisons must establish benefit without regressions before activation. They change prompt instructions, not model parameters. The latest audited live database has zero active learned instructions. Successful live improvement and later reuse remain pending; mocked activation tests do not replace that evidence.

## What LangSmith could add later

LangSmith could provide richer trace inspection, evaluation workflows and production monitoring. The app currently provides local run events, usage and audit JSON. A future integration would need deliberate instrumentation, handling of sensitive content and a retention policy. Do not call the current local logging implementation “LangSmith tracing.”

## Claims to avoid in the recording

- “All three libraries do the same thing.”
- “We use LangChain create_agent,” or “LangSmith monitors this app,” without an implemented configuration.
- “We trained a model” when only prompts changed.
- “We implemented a vector database RAG pipeline.”
- “The two model calls guarantee independent or error-free evaluation.”
- “All sprints have complete live acceptance,” or “learning activated,” when current evidence says otherwise.
- “FreeLLM has no limits,” or “the final failed response is approved anyway.”

Use the actual implementation and evidence. A clear, justified scope decision is stronger than claiming an unimplemented feature.
