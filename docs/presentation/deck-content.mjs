// Slide copy and Tanglish presenter notes. Evidence snapshot: 15 November 2026.
export const slides = [
  { title: 'LessonLoop', kind: 'cover', subtitle: 'A lesson generator that checks its own work', time: '00:00–00:15',
    notes: 'Vanakkam. Intha project LessonLoop. Oru beginner topic kudutha, system lesson create pannum, thaniya evaluate pannum, mistakes irundha rewrite pannum. Intha video-la first seven minutes planning and architecture explain pannuren. Adutha seven minutes product demo. Kadaisi one minute current result and pending work solluren.', source: 'README.md; docs/OVERALL_GUIDE.md' },
  { title: 'The sprint plan', kind: 'rows', rows: [
    ['01–03', 'Foundation', 'Setup, reviewed RAG references, rubric and workflow'],
    ['04–06', 'Product', 'Persistent records, learning controls, API and React'],
    ['07–09', 'Evidence', 'Tests, lesson exports, documentation and demo preparation']], time:'00:15–00:45',
    notes:'First assessment requirement-a small milestones-aa split pannom. Foundation phase-la working API and quality rules. Product phase-la history, memory controls and UI. Evidence phase-la tests, approved lesson, rejection log and recording materials. Intha nine sprints logical implementation milestones. Ovvoru sprint-um formal two-week Scrum sprint nu claim pannala. Video recording innum user deliverable. Plan irukkiradhu vera, acceptance evidence irukkiradhu vera.', source:'docs/SPRINT_STATUS.md; docs/ASSESSMENT_AUDIT.md' },
  { title:'Sprints 1 to 3 built the quality loop', kind:'rows', rows:[
    ['01','Setup','Python API, health check, model configuration and ignored secrets'],
    ['02','Sources and rubric','Reviewed RAG references, claim IDs and hard pass or fail checks'],
    ['03','Workflow','Generate, validate, evaluate and rewrite with at most three drafts']], time:'00:45–01:20',
    notes:'Sprint one-la backend setup, health endpoint and environment configuration pannom. API key Git-la pogakoodadhu, athan ignored env file. Sprint two-la RAG references and fourteen mandatory checks define pannom. Sprint three-la actual LangGraph loop build pannom. Oru check fail aana reason next generation-ku pogum. Initial draft plus two rewrites mattum. Moonu draft mudinjudhu-nu automatic approval kudukka maattom.',source:'backend/app/config.py; backend/content/rag_sources.json; backend/content/rubric.json; backend/app/workflow.py; commits cd4f3a0, 2e21720, 9d1dfa2' },
  { title:'Sprints 4 to 6 made the app usable',kind:'rows',rows:[
    ['04','Persistence','SQLite keeps attempts, events, feedback and frozen versions'],
    ['05','Learning controls','Repeated failure observations, candidate comparison and rollback'],
    ['06','API and React','Studio, reader, reports, history and feedback']],time:'01:20–01:55',
    notes:'Sprint four-la data memory-la mattum irukkaama SQLite-la persist pannom. Server restart aana history survive aagum. Sprint five-la repeated failures observe panni candidate prompt compare panra controls irukku. Aana successful live improvement and reuse innum demonstrate pannala. Sprint six-la React studio, reports and feedback connect pannom. User feedback vandhadhum system blindly prompt change pannaadhu. Human verification and comparison gate irukku.',source:'backend/app/db.py; backend/app/improvements.py; frontend/src/App.tsx; docs/ASSESSMENT_AUDIT.md; commit 9d1dfa2' },
  {title:'Sprints 7 to 9 prepared the evidence',kind:'rows',rows:[
    ['07','Verification','Backend tests, browser tests and recorded model disagreements'],
    ['08','Deliverables','Approved RAG lesson, audit, rejection log and setup guide'],
    ['09','Demonstration','Running workflow, saved deliberate-error case and recording script']],time:'01:55–02:25',
    notes:'Sprint seven-la positive case mattum test pannala. Wrong check IDs, false booleans, bad evidence, provider failure and cancellation test pannom. Sprint eight-la approved English RAG lesson and audit save pannom. Sprint nine-ku script and real saved error demo ready. Actual face-visible recording and public sharing links innum pending. Recorded old evidence-a current live run maadhiri present panna koodadhu.',source:'VERIFICATION.md; submission/final-lesson/; submission/backup-demo/; docs/VIDEO_WALKTHROUGH.md; commit 0284efc' },
  {title:'How we used Agile ideas',kind:'list',items:[
    ['Small backlog items','Split the assessment into reviewable milestones'],
    ['Working increments','Add one usable capability, then test it'],
    ['Feedback changes the next task','Quota failures and confusing screens became fixes'],
    ['Completion checks','Verify the change, commit it and push it']],foot:'Agile-inspired individual workflow. Formal Scrum ceremonies and velocity were not tracked.',time:'02:25–02:55',
    notes:'Agile use pannoma-na, iterative way-la use pannom. Requirement backlog irundhuchu, small working increments ship pannom, user feedback base panni next task change pannom. Example, user-ku status theriyala, so countdown add pannom. Cancel venum-nu sonna cancellation add pannom. Daily stand-up, sprint velocity and story points track pannom-nu solla evidence illa. So accurate wording Agile-inspired individual workflow.',source:'git log; commits 3707406, 91b8987, 954bf6e' },
  {title:'The technology stack',kind:'list',items:[
    ['React, TypeScript and Vite','Lesson studio and browser interaction'],
    ['Python and FastAPI','Local API, task ownership and cancellation'],
    ['LangGraph and Pydantic','Workflow routing and strict response validation'],
    ['SQLite','Durable run history, versions and feedback'],
    ['Gemini, Groq and FreeLLM','Separate generation and evaluation calls'],
    ['pytest and Playwright','Backend checks and desktop/mobile flows']],time:'02:55–03:30',
    notes:'Frontend React and TypeScript. Backend FastAPI in Python. Pydantic required JSON shape and strict booleans validate pannum. LangGraph control flow handle pannum. SQLite persistence handle pannum. Gemini primary, Groq backup, and local FreeLLM router another fallback. HTTPX direct API transport use pannom. Tests-ku pytest and Playwright. Download-ku ReportLab PDF, python-docx Word, and native script PDF shaping-ku HarfBuzz use pannom.',source:'backend/requirements.in; frontend/package.json; backend/app/runtime.py; backend/app/services/' },
  {title:'Why LangGraph fits this workflow',kind:'list',items:[
    ['A visible loop','Failures route back to generation'],
    ['Conditional decisions','Pass, rewrite, needs review or error'],
    ['Shared state','The next step receives the draft and failed checks'],
    ['Separate steps','Test generation, validation and evaluation independently']],foot:'LangGraph runs the workflow. Our SQLite repository stores the durable history.',time:'03:30–04:00',
    notes:'Intha app straight line API call mattum illa. Evaluation result base panni path change aagum. Athukku explicit graph easy-aa explain and test panna mudiyum. LangGraph mandatory-nu illa, plain Python-layum build panna mudiyum. Aana nodes, state and conditional edges intha loop-a clear-aa represent pannudhu. Persistence automatic LangGraph magic illa. Intha implementation-la namma SQLite repository-thaan permanent history store pannudhu.',source:'backend/app/workflow.py; backend/app/db.py; docs/DESIGN.md' },
  {title:'Five LangGraph terms in plain words',kind:'terms',items:[
    ['Node','One work function, such as generate_lesson'],
    ['Edge','The route to the next work function'],
    ['State','The shared notebook for this run'],
    ['compile()','Prepare the connected graph for execution'],
    ['ainvoke()','Run it asynchronously with an initial run_id']],time:'04:00–04:50',
    notes:'Simple example: oru teacher lesson prepare panra work-a imagine pannunga. Node-na oru task function. Generate node lesson create pannum. Edge-na adutha task enna-nu sollra route. State-na common notebook: topic, lesson, failed checks, retry count ellam athula irukkum. compile-na nodes and routes connect pannina graph-a runnable-aa ready panradhu. Athu model train panradhu illa. ainvoke call pannumbodhu actual run start aagum. Await use panrom because provider calls asynchronous. Oru draft fail aana same run state-oda rewrite path-ku pogum.',source:'backend/app/workflow.py: RunState, build_graph, execute_run' },
  {title:'The lesson workflow',kind:'graph',time:'04:50–05:35',
    notes:'Inga left-lendhu follow pannunga. load_context sources, rubric, prompt and selected memory load pannum. generate_lesson first draft or rewrite produce pannum. validate_structure required sections and source mappings check pannum. evaluate_lesson separate model calls-la content judge pannum. Conditional edge route_result decide pannum. Fail and drafts remaining-na generate node-ku thirumbi pogum. All pass-na approved. Third draft-kum fail-na needs review. persist_final_result final status save pannum. Provider failure separate error path. Ovvoru draft-kum new run start panna vendam.',source:'backend/app/workflow.py: build_graph and route_result' },
  {title:'Compile and run in our code',kind:'code',code:[
    'graph.add_node("generate_lesson", generate_lesson)',
    'graph.add_edge("load_context", "generate_lesson")',
    'graph.add_conditional_edges(',
    '    "evaluate_lesson", route_result,',
    '    ["generate_lesson", "persist_final_result"])',
    'return graph.compile()',
    '',
    '# execute_run starts the compiled workflow',
    'await build_graph(repository, ai).ainvoke(',
    '    {"run_id": run_id}, {"recursion_limit": 30})'],time:'05:35–06:15',
    notes:'Ithu namma workflow file-la irukkira selected lines. add_node function-a register pannudhu. add_edge normal next step define pannudhu. add_conditional_edges evaluator result base panni rewrite or finish choose pannudhu. build_graph graph.compile return pannudhu. execute_run athoda ainvoke method-a await pannudhu. Recursion limit another guard. Content rewrite limit separate-aa two retries-nu code enforce pannudhu. compile success mattum lesson correct-nu meaning illa. Actual evaluator and Python release rule pass aaganum.',source:'backend/app/workflow.py; selected lines reformatted for readability' },
  {title:'Commits show the product growing',kind:'commits',rows:[
    ['9d1dfa2','Workflow, evaluation audits and persistent learning controls'],
    ['f4318ac','Automatic Groq fallback after Gemini quota'],
    ['8c288d7','Dynamic topics and frozen references'],
    ['385f2b3 / bae515b','FreeLLM fallback and Groq JSON-failure recovery'],
    ['d253444 / 1df29aa','Document downloads, native languages and assessment audit']],foot:'Full commit history is in the appendix. Sprint milestones do not map one-to-one to commits.',time:'06:15–06:45',
    notes:'Inga representative commits kaatturen. First big implementation workflow and persistence. Appuram real quota failure base panni Groq backup. Dynamic topics, FreeLLM router, JSON failure recovery, PDF Word downloads and native language support add pannom. Ovvoru sprint-kum exactly oru commit-nu sollala. Some commits multiple milestones cover pannudhu. Full commit list appendix-la irukku. Git history implementation evidence; model accuracy-ku test and live result evidence separate.',source:'git log through 1df29aa; https://github.com/sriram-Kannan-45/LessonLoop/commits/main' },
  {title:'Product walkthrough',kind:'demo',items:[['Lesson studio','Topic, language and live status'],['Quality report and Attempts','Evidence, failed checks and real corrections'],['History, downloads and memory','Preserved runs and honest learning status']],time:'06:45–07:00',
    notes:'Ippo app-ku switch pannuren. First assignment and language selector show pannuren. Apram actual workflow events, quality report and attempts. Saved deliberate-error case use panna, idhu saved historical live run-nu clear-aa solluven. API slow irundha waiting time full-aa video-la waste pannaama saved evidence show pannalaam. Face camera visible-aa irukkanum. Env file or service dashboard open panna vendam.',source:'frontend/src/App.tsx; real approved-run product screenshot captured locally' },
  {title:'What works and what remains',kind:'status',time:'14:00–15:00',
    notes:'Final-aa implementation and acceptance separate pannuren. Current code snapshot-la 133 backend tests and 44 browser tests pass. English fourteen checks, native language fifteen. Ten language options irukku. Tamil PDF and Word font rendering inspect pannom. Aana successful live Tamil inference test local router unreachable-nala pending. Self-improvement controls implemented, but zero active learned instructions in latest audit. Qualifying live improvement and later reuse innum pending. Public final document link and this face-visible video sharing link ready aana assessment submission complete panna mudiyum. Intha limitations-a hide pannaama explain panradhu engineering ownership-oda part.',source:'VERIFICATION.md; docs/ASSESSMENT_AUDIT.md; evidence snapshot 1df29aa, 15 November 2026' },
  {title:'Appendix  Commit history 1',kind:'history',rows:[
    ['cd4f3a0','First commit'],['2e21720','Gemini-only setup and automatic push workflow'],['9d1dfa2','Lesson workflow, audits and persistent learning controls'],['0284efc','Sprint acceptance audit and stronger evaluation controls'],['471972d','Provider outage recovery and actionable citation corrections'],['f4318ac','Automatic Gemini-quota fallback to Groq'],['d971cd1','Recorded real successful evaluation fallback to Groq'],['8c288d7','Dynamic topics with frozen public references']],time:'Optional appendix',
    notes:'Reference slide. Main seven-minute PPT portion-la intha full list read panna thevai illa. Interviewer commit details ketta use pannunga. Titles git log-lendhu summarize pannirukkom. Original assessment any model allow pannudhu. Earlier user preference Gemini-only, later explicit request base panni Groq and FreeLLM backups add pannom.',source:'git log through 1df29aa' },
  {title:'Appendix  Commit history 2',kind:'history',rows:[
    ['3707406','Persistent run status and API-wait countdown'],['954bf6e','Editable next-topic field during an active run'],['91b8987','Cancel active lesson generation'],['385f2b3','Local FreeLLM fallback for quota and output truncation'],['bae515b','FreeLLM fallback for Groq json_validate_failed'],['d253444','PDF, TXT and editable Word downloads'],['1df29aa','Assessment audit and native-language lessons']],time:'Optional appendix',
    notes:'Reference slide. Indha later changes user feedback-lendhu vandha backlog items. Status theriyala, topic type panna mudiyala, cancel venum, provider error varudhu, document formats venum, native language venum. Ippadi feedback-a small verified changes-aa convert pannom. Idhu Agile-inspired iteration-ku concrete example.',source:'git log through 1df29aa' },
];

export const demoScript = `# LessonLoop recording plan

Target: 15 minutes total. Slides 1–13 take about 7 minutes, product walkthrough takes 7 minutes, and slide 14 closes in 1 minute. Slides 15–16 are optional reference appendices. This meets the lower end of the assessment's original 15–20-minute requirement. If speaking fast, slow down on the actual product evidence rather than adding unsupported claims.

## Before recording

- Start backend, frontend and the configured local FreeLLM router. Open the app and test only when needed.
- Keep face camera visible. Keep .env, passwords and API dashboards off screen.
- Open the approved RAG run b0ba902b21e64ce3a8f38a1ff446ef1d and the saved deliberate-error backup d7f428ad985b4aceba7b8a17610bfeef in separate tabs.
- Keep docs/ASSESSMENT_AUDIT.md open for the honest final status. Read the notes once before recording.
- Do not call a saved run a currently executing run. Do not claim that a failed comparison activated learning.

## 07:00–08:00  Assignment

Show Introduction to RAG. English is the demonstrated historical assessment language. Show Tamil and the other language options, then explain that each language has a frozen run assignment and an additional mandatory language check. Use normal mode with Inject a factual error OFF.

Tanglish cue: Ithu topic search answer mattum illa. Generate click pannina oru run start aagum. Same run-kulla draft, checking and rewrite nadakkum.

## 08:00–09:30  Running workflow

If provider capacity is available, start one normal run and show real events. Explain source loading, generation, evaluation, API wait and cancellation. The countdown is for the next request, not the final completion time. A cancelled request already sent may still use provider quota. If execution is slow, keep it running and show the labelled saved approved run rather than making another request.

Tanglish cue: Inga current stage actual backend events-lendhu varudhu. UI timer approval decide pannaadhu. Python release rule-thaan final decision edukudhu.

## 09:30–11:00  Approved lesson and evidence

Open the saved approved RAG run. Read the definition, process, invented example and missing-information answer briefly. Open Quality report and two evidence excerpts. Show all fourteen mandatory checks. Open Attempts and inspect one actual failed check and the next draft's correction.

Tanglish cue: 14 out of 14 oru average mark illa. Ella mandatory check-um pass aaganum. Model judge thappu panna chance irukku, athan evidence and calibration reports preserve pannirukkom.

## 11:00–12:30  Deliberate error

Open the saved historical live backup d7f428ad985b4aceba7b8a17610bfeef. Say explicitly that it is a saved live run. In Attempts expand the original/altered draft audit, show the false correctness guarantee, the evaluator's actual rejection and the corrected second draft. A fresh deliberate-error run is optional only if quota and recording time permit; its verdict must not be invented.

Tanglish cue: Idhu hardcoded FAIL demo illa. False sentence insert pannom, aana evaluator-ku demo flag kudukkala. Actual result and evidence inga save aagirukku.

## 12:30–13:15  History and downloads

Show persistent history and one clearly labelled review draft. Unapproved drafts require explicit inspection. Download one PDF or Word document. Explain that all formats preserve approval status and references. Do not export a review draft and call it an approved final lesson.

## 13:15–14:00  Memory

Open Memory & learning. Show observations, comparison outcomes and current active instruction count. The audited count is zero. Explain that comparisons must demonstrate improvement without regressions before activation. Do not launch a multi-call comparison just to fill recording time. English reviewed-RAG calibration excludes native-language observations and instructions.

Tanglish cue: History ellame save pannum. Reusable memory-na validated instruction mattum. Store pannadhu mattum self-learning prove pannaadhu. Qualifying live improvement and later reuse innum pending.

## 14:00–15:00  Return to slide 14

Explain current verification and pending submission items. Point to the repo, audit and overall guide. The required public Google Doc/Notion and video sharing links must still be published and checked before form submission.
`;
