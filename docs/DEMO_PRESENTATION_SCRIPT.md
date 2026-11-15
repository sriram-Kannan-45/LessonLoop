# Revised LessonLoop recording plan

This version adds the LangChain/LangGraph/LangSmith distinction, the actual project choice, fine-tuning trade-offs, reference grounding, release checks, provider reliability and the difference between history, memory and training.

## Recording route

- Slides 1–20: about 9 minutes 25 seconds of technical explanation. Follow the per-slide notes and use the optional details only if time allows.
- Product demo: 09:25–14:00, about 4 minutes 35 seconds.
- Slide 21: 14:00–15:00 closing and honest acceptance status.
- Slides 22–25: optional commit-history and interview-question appendices. Skip them in the timed main route. Using them makes an 18–20-minute explanation possible, which also fits the original assessment.

The assessment asks for a 15–20-minute face-visible video. A 15-minute main route fits both that requirement and the requested 10–15-minute recording range. Rehearse once; do not read every optional detail at full length and then rush the product evidence.

## The most important correction

Say: “I chose LangGraph directly for explicit workflow control. I use the Google SDK and HTTPX for model calls. LangChain core and the LangSmith SDK are indirect dependencies, but I did not configure LangChain create_agent or LangSmith tracing.”

Do not say all three products are the same, that LangSmith is the judge model, or that installing its SDK proves tracing is active. The project stores its own audit events in SQLite.

## The fine-tuning answer

Tanglish cue: “Fine-tuning bad-nu sollala. Intha project-ku first audited content loop and reliable evaluator venum. Reviewed training corpus and measured held-out benefit illa. Athan prompting, references and controlled rewriting first choose pannom. Future-la sufficient reviewed examples and clear benefit irundha tuning consider pannalaam. Appovum grounding and release checks thevai.”

Prompting sets instructions. References supply facts at request time. Fine-tuning adapts learned behavior through training. They can complement one another. This code does not update model weights and does not contain an embedding index/vector store.

## Before recording

1. Start backend/frontend and the configured local router. Check service availability before a live generation attempt.
2. Keep face camera visible. Keep .env, credentials, password prompts and API dashboards off screen.
3. Open saved approved RAG run b0ba902b21e64ce3a8f38a1ff446ef1d and saved deliberate-error backup d7f428ad985b4aceba7b8a17610bfeef in separate tabs.
4. The screenshot in the PPT shows a genuine saved approved run. It does not claim a new live execution.
5. Use Introduction to RAG in English for the demonstrated assessment flow. Show native language selection as an additional feature and disclose its live-validation limit.

## 09:25–10:10  Topic and live workflow

Show the topic and language selector, normal mode with deliberate error OFF, and start at most one run if capacity permits. Show actual status and events. Explain that a countdown is the next-request wait, not a guaranteed finish time. If the provider is slow, keep it running and move to clearly labelled saved evidence.

## 10:10–11:15  Approved lesson and quality report

Open the saved approved RAG run. Briefly show what it is, how it works, the invented example and missing-information answer. Open Quality report, show all fourteen mandatory checks and two real evidence excerpts. Explain that the count is not an averaged score and model mistakes remain possible.

## 11:15–12:35  Deliberate error and correction

Open the saved historical live backup and identify it as saved evidence. In Attempts show original/altered draft, the false correctness guarantee, the real failed verdict and the corrected next draft. The evaluator did not receive a demo flag or a desired verdict. A newly executing error-injection demo is optional only if quota/time permit; never invent its result.

## 12:35–13:15  Downloads and history

Show persistence and one PDF/Word download. Review drafts remain labelled NOT APPROVED and collapsed until explicit inspection. Show Cancel only if a run is active; cancellation preserves saved drafts and cannot refund already-sent provider requests.

## 13:15–14:00  Memory and limitations

Show memory observations and actual comparison outcomes. Audited active learned-instruction count is zero. Explain candidate comparison, no-regression activation and pending live reuse. Do not trigger an expensive comparison just to fill time. English reviewed-RAG learning does not automatically transfer to native languages.

## 14:00–15:00  Closing on slide 21

State what the current tests establish, the limits of model judging and pending live learning/Tamil checks. Public Google Doc/Notion and video sharing links are still submission deliverables. Do not present local artifacts as public sharing links or claim the assessment form was submitted.


# Slide speaker notes

## Slide 1  LessonLoop

Timing: 00:00–00:15

Vanakkam. Intha project LessonLoop. Oru beginner topic kudutha lesson create panni, evaluate panni, mistakes irundha rewrite pannum. First technical decisions and workflow explain pannuren. Apram product evidence show pannuren. Closing-la actual completion boundary solluren.

Sources: README.md; docs/OVERALL_GUIDE.md

## Slide 2  The sprint plan

Timing: 00:15–00:40

First assessment requirement-a small milestones-aa split pannom. Foundation phase-la working API and quality rules. Product phase-la history, memory controls and UI. Evidence phase-la tests, approved lesson, rejection log and recording materials. Intha nine sprints logical implementation milestones. Ovvoru sprint-um formal two-week Scrum sprint nu claim pannala. Video recording innum user deliverable. Plan irukkiradhu vera, acceptance evidence irukkiradhu vera.

Sources: docs/SPRINT_STATUS.md; docs/ASSESSMENT_AUDIT.md

## Slide 3  Sprints 1 to 3 built the quality loop

Timing: 00:40–01:05

Sprint one-la backend setup, health endpoint and environment configuration pannom. API key Git-la pogakoodadhu, athan ignored env file. Sprint two-la RAG references and fourteen mandatory checks define pannom. Sprint three-la actual LangGraph loop build pannom. Oru check fail aana reason next generation-ku pogum. Initial draft plus two rewrites mattum. Moonu draft mudinjudhu-nu automatic approval kudukka maattom.

Sources: backend/app/config.py; backend/content/rag_sources.json; backend/content/rubric.json; backend/app/workflow.py; commits cd4f3a0, 2e21720, 9d1dfa2

## Slide 4  Sprints 4 to 6 made the app usable

Timing: 01:05–01:30

Sprint four-la data memory-la mattum irukkaama SQLite-la persist pannom. Server restart aana history survive aagum. Sprint five-la repeated failures observe panni candidate prompt compare panra controls irukku. Aana successful live improvement and reuse innum demonstrate pannala. Sprint six-la React studio, reports and feedback connect pannom. User feedback vandhadhum system blindly prompt change pannaadhu. Human verification and comparison gate irukku.

Sources: backend/app/db.py; backend/app/improvements.py; frontend/src/App.tsx; docs/ASSESSMENT_AUDIT.md; commit 9d1dfa2

## Slide 5  Sprints 7 to 9 prepared the evidence

Timing: 01:30–01:50

Sprint seven-la positive case mattum test pannala. Wrong check IDs, false booleans, bad evidence, provider failure and cancellation test pannom. Sprint eight-la approved English RAG lesson and audit save pannom. Sprint nine-ku script and real saved error demo ready. Actual face-visible recording and public sharing links innum pending. Recorded old evidence-a current live run maadhiri present panna koodadhu.

Sources: VERIFICATION.md; submission/final-lesson/; submission/backup-demo/; docs/VIDEO_WALKTHROUGH.md; commit 0284efc

## Slide 6  How we used Agile ideas

Timing: 01:50–02:10

Agile use pannoma-na, iterative way-la use pannom. Requirement backlog irundhuchu, small working increments ship pannom, user feedback base panni next task change pannom. Example, user-ku status theriyala, so countdown add pannom. Cancel venum-nu sonna cancellation add pannom. Daily stand-up, sprint velocity and story points track pannom-nu solla evidence illa. So accurate wording Agile-inspired individual workflow.

Sources: git log; commits 3707406, 91b8987, 954bf6e

## Slide 7  The technology stack

Timing: 02:10–02:35

Frontend React and TypeScript. Backend FastAPI in Python. Pydantic required JSON shape and strict booleans validate pannum. LangGraph control flow handle pannum. SQLite persistence handle pannum. Gemini primary, Groq backup, and local FreeLLM router another fallback. HTTPX direct API transport use pannom. Tests-ku pytest and Playwright. Download-ku ReportLab PDF, python-docx Word, and native script PDF shaping-ku HarfBuzz use pannom.

Sources: backend/requirements.in; frontend/package.json; backend/app/runtime.py; backend/app/services/

## Slide 8  LangChain, LangGraph and LangSmith

Timing: 02:35–03:20

Moonu names same maadhiri irundhaalum responsibilities different. LangChain models, tools and agent loop compose panna higher-level framework. LangGraph exact work order, shared state and branch control panna runtime. LangSmith traces, debugging and evaluations observe panna platform. Ivanga competitors mattum illa; serndhum use pannalaam. Namma project-la LangGraph direct-aa use pannom. LangChain agent API and LangSmith tracing use pannom-nu claim panna koodadhu.

Sources: https://docs.langchain.com/oss/python/langchain/overview; https://docs.langchain.com/oss/python/langgraph/overview; https://docs.langchain.com/langsmith/observability; backend/requirements.in; backend/app/workflow.py

## Slide 9  What this project actually uses

Timing: 03:20–03:50

Interview-la correct-aa ipdi sollunga: naan LangGraph select panninen because explicit evaluation and rewrite control venum. LLM calls Google SDK and HTTPX-la irukku. Full LangChain create_agent use pannala. Requirements lock-la langchain-core and langsmith irukkiradhu indirect dependency. Installed package irukkaradhu product feature configured-nu proof illa. Namma local events and audit traceability irukku; adhu LangSmith service integration illa.

Sources: backend/requirements.in; backend/requirements.txt; backend/app/services/lesson_ai.py; backend/app/workflow.py; backend/app/db.py

## Slide 10  Why LangGraph fits this workflow

Timing: 03:50–04:15

Intha app straight line API call mattum illa. Evaluation result base panni path change aagum. Athukku explicit graph easy-aa explain and test panna mudiyum. LangGraph mandatory-nu illa, plain Python-layum build panna mudiyum. Aana nodes, state and conditional edges intha loop-a clear-aa represent pannudhu. Persistence automatic LangGraph magic illa. Intha implementation-la namma SQLite repository-thaan permanent history store pannudhu.

Sources: backend/app/workflow.py; backend/app/db.py; docs/DESIGN.md

## Slide 11  Five LangGraph terms in plain words

Timing: 04:15–04:55

Simple example: oru teacher lesson prepare panra work-a imagine pannunga. Node-na oru task function. Generate node lesson create pannum. Edge-na adutha task enna-nu sollra route. State-na common notebook: topic, lesson, failed checks, retry count ellam athula irukkum. compile-na nodes and routes connect pannina graph-a runnable-aa ready panradhu. Athu model train panradhu illa. ainvoke call pannumbodhu actual run start aagum. Await use panrom because provider calls asynchronous. Oru draft fail aana same run state-oda rewrite path-ku pogum.

Sources: backend/app/workflow.py: RunState, build_graph, execute_run

## Slide 12  The lesson workflow

Timing: 04:55–05:30

Inga left-lendhu follow pannunga. load_context sources, rubric, prompt and selected memory load pannum. generate_lesson first draft or rewrite produce pannum. validate_structure required sections and source mappings check pannum. evaluate_lesson separate model calls-la content judge pannum. Conditional edge route_result decide pannum. Fail and drafts remaining-na generate node-ku thirumbi pogum. All pass-na approved. Third draft-kum fail-na needs review. persist_final_result final status save pannum. Provider failure separate error path. Ovvoru draft-kum new run start panna vendam.

Sources: backend/app/workflow.py: build_graph and route_result

## Slide 13  Compile and run in our code

Timing: 05:30–06:00

Ithu namma workflow file-la irukkira selected lines. add_node function-a register pannudhu. add_edge normal next step define pannudhu. add_conditional_edges evaluator result base panni rewrite or finish choose pannudhu. build_graph graph.compile return pannudhu. execute_run athoda ainvoke method-a await pannudhu. Recursion limit another guard. Content rewrite limit separate-aa two retries-nu code enforce pannudhu. compile success mattum lesson correct-nu meaning illa. Actual evaluator and Python release rule pass aaganum.

Sources: backend/app/workflow.py; selected lines reformatted for readability

## Slide 14  Prompts, references and fine-tuning

Timing: 06:00–06:45

Oru student analogy use pannalaam. Prompt-na teacher instructions. References-na open-book material. Fine-tuning-na examples use panni training moolama model behavior adapt panradhu. Indha app instructions and frozen reference excerpts kudukkudhu. Model weights-a update pannaadhu. Retrieval and fine-tuning together use panna mudiyum. Fine-tuning pannina citation checking or evaluator thevai illa-nu artham illa.

Sources: https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/tuning/supervised-tuning; https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/tuning/supervised-tuning/prepare-data; https://docs.cloud.google.com/gemini-enterprise-agent-platform/build/rag-engine/rag-overview; backend/app/services/lesson_ai.py; backend/content/prompts.json

## Slide 15  Why fine-tuning is not the first step

Timing: 06:45–07:30

Fine-tuning bad-nu sollala. Indha assessment objective workflow and evaluator ownership. Namma kitte reviewed training lessons corpus and proven holdout benefit illa. Adhukkulla training panna quality improve aagum-nu assume panna mudiyadhu. Sources and rules change aana prompts/reference snapshots inspect panna easy. Dataset preparation, training and evaluation extra work. First baseline defects understand pannitu, reliable labels collect panni, benefit measure pannina apram tuning consider pannalaam. Tuning failure-free factual accuracy guarantee pannaadhu.

Sources: Project decision based on docs/ASSESSMENT_AUDIT.md and backend/dataset.py; tuning concepts: https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/tuning/supervised-tuning; https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/tuning/supervised-tuning/prepare-data

## Slide 16  How the release gate works

Timing: 07:30–08:00

Valid JSON vandhaa lesson correct-nu solla mudiyadhu. Pydantic shape and strict booleans validate pannum. Python source IDs and exact evidence check pannum. Model actual teaching content judge pannum. English-ku fourteen, native language-ku language check serthu fifteen. Oru mandatory fail-na release illa. Same provider different role calls independent human judgement illa. Historical false passes irundhadhai calibration documentation-la preserve pannirukkom.

Sources: backend/app/quality.py; backend/app/lesson_schemas.py; backend/app/languages.py; VERIFICATION.md

## Slide 17  Provider fallback and stopping rules

Timing: 08:00–08:25

Gemini primary. Quota vandhaa Groq backup. Groq quota, output cut-off, explicit json_validate_failed or eligible temporary error vandhaa configured FreeLLM route use pannalaam. Authentication error-a silently bypass panna maattom. FreeLLM auto upstream model choose pannalaam; router report panna model name usage-la store pannom. Ella providers-um fail aana honest ERROR. Repeated unlimited retries or fake approval pannaadhu. Cancel local task-a stop pannum, already sent request quota consume pannirukkalaam.

Sources: backend/app/services/lesson_ai.py; backend/app/services/groq.py; backend/app/services/freellm.py; backend/app/runtime.py

## Slide 18  History, memory and model training

Timing: 08:25–08:55

History save pannradhu, reusable memory, fine-tuning moonum same illa. History-la ella records-um irukkum. Validated memory-la proven teaching instructions mattum select aaganum. Repeated failures observe pannitu candidate compare panni benefit and no-regression demonstrate panna thaan activate. Current audited count zero active instructions. Prompt text sharpen pannradhu weights update panradhu illa. Successful live improvement and later reuse pending-nu clear-aa sollanum.

Sources: backend/app/db.py; backend/app/improvements.py; docs/ASSESSMENT_AUDIT.md

## Slide 19  Commits show the product growing

Timing: 08:55–09:15

Inga representative commits kaatturen. First big implementation workflow and persistence. Appuram real quota failure base panni Groq backup. Dynamic topics, FreeLLM router, JSON failure recovery, PDF Word downloads and native language support add pannom. Ovvoru sprint-kum exactly oru commit-nu sollala. Some commits multiple milestones cover pannudhu. Full commit list appendix-la irukku. Git history implementation evidence; model accuracy-ku test and live result evidence separate.

Sources: git log through 1df29aa; https://github.com/sriram-Kannan-45/LessonLoop/commits/main

## Slide 20  Product walkthrough

Timing: 09:15–09:25

Ippo app-ku switch pannuren. First assignment and language selector show pannuren. Apram actual workflow events, quality report and attempts. Saved deliberate-error case use panna, idhu saved historical live run-nu clear-aa solluven. API slow irundha waiting time full-aa video-la waste pannaama saved evidence show pannalaam. Face camera visible-aa irukkanum. Env file or service dashboard open panna vendam.

Sources: frontend/src/App.tsx; real approved-run product screenshot captured locally

## Slide 21  What works and what remains

Timing: 14:00–15:00

Final-aa implementation and acceptance separate pannuren. Current code snapshot-la 133 backend tests and 44 browser tests pass. English fourteen checks, native language fifteen. Ten language options irukku. Tamil PDF and Word font rendering inspect pannom. Aana successful live Tamil inference test local router unreachable-nala pending. Self-improvement controls implemented, but zero active learned instructions in latest audit. Qualifying live improvement and later reuse innum pending. Public final document link and this face-visible video sharing link ready aana assessment submission complete panna mudiyum. Intha limitations-a hide pannaama explain panradhu engineering ownership-oda part.

Sources: VERIFICATION.md; docs/ASSESSMENT_AUDIT.md; evidence snapshot 1df29aa, 15 November 2026

## Slide 22  Appendix  Commit history 1

Timing: Optional appendix

Reference slide. Main seven-minute PPT portion-la intha full list read panna thevai illa. Interviewer commit details ketta use pannunga. Titles git log-lendhu summarize pannirukkom. Original assessment any model allow pannudhu. Earlier user preference Gemini-only, later explicit request base panni Groq and FreeLLM backups add pannom.

Sources: git log through 1df29aa

## Slide 23  Appendix  Commit history 2

Timing: Optional appendix

Reference slide. Indha later changes user feedback-lendhu vandha backlog items. Status theriyala, topic type panna mudiyala, cancel venum, provider error varudhu, document formats venum, native language venum. Ippadi feedback-a small verified changes-aa convert pannom. Idhu Agile-inspired iteration-ku concrete example.

Sources: git log through 1df29aa

## Slide 24  Appendix  Storage and retrieval choices

Timing: Optional appendix

SQLite history database-a vector database-nu describe panna koodadhu. Intha app single local workflow-ku simple setup choose pannom. Multi-user deployment grow aana PostgreSQL and job infrastructure evaluate pannalaam. Current grounding reviewed notes and Wikipedia excerpts. Semantic embedding search or full document-QA product implement pannala. Andha requirement vandhaa document ingestion, chunks, embedding index and retrieval evaluation add panna vendum. RAG topic teach pannradhu and full RAG search product build pannradhu separate scope.

Sources: backend/app/db.py; backend/app/topics.py; backend/content/rag_sources.json; docs/DESIGN.md

## Slide 25  Appendix  When fine-tuning makes sense

Timing: Optional appendix

Future-la tune panna eppo? Repeated style or teaching behavior defect reliable-aa measure pannirukkanum. Reviewed examples and separate evaluation data venum. Tuning support irukkira model, budget and measurable improvement venum. Current one small authored calibration set-a large production training corpus-nu claim panna koodadhu. Facts supply panra references and final quality gate tuned model-kum continue aaganum.

Sources: https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/tuning/supervised-tuning; https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/tuning/supervised-tuning/prepare-data; project decisions: backend/dataset.py; docs/ASSESSMENT_AUDIT.md