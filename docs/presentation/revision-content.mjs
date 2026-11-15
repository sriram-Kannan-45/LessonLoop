// Expanded engineering explanation. Preserve the original deck source for reference.
import { slides as original } from './deck-content.mjs';
const lc='https://docs.langchain.com/oss/python/langchain/overview';
const lg='https://docs.langchain.com/oss/python/langgraph/overview';
const ls='https://docs.langchain.com/langsmith/observability';
const ft='https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/tuning/supervised-tuning';
const data='https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/tuning/supervised-tuning/prepare-data';
const rag='https://docs.cloud.google.com/gemini-enterprise-agent-platform/build/rag-engine/rag-overview';

const ecosystem={title:'LangChain, LangGraph and LangSmith',kind:'rows',rows:[
  ['Build','LangChain','Higher-level agent abstractions and model/tool integrations'],
  ['Route','LangGraph','Explicit state, nodes, edges and workflow execution'],
  ['Observe','LangSmith','Tracing, debugging and evaluation tooling']],
  notes:'Moonu names same maadhiri irundhaalum responsibilities different. LangChain models, tools and agent loop compose panna higher-level framework. LangGraph exact work order, shared state and branch control panna runtime. LangSmith traces, debugging and evaluations observe panna platform. Ivanga competitors mattum illa; serndhum use pannalaam. Namma project-la LangGraph direct-aa use pannom. LangChain agent API and LangSmith tracing use pannom-nu claim panna koodadhu.',source:`${lc}; ${lg}; ${ls}; backend/requirements.in; backend/app/workflow.py`};

const actual={title:'What this project actually uses',kind:'list',items:[
  ['LangGraph directly','StateGraph defines the controlled lesson workflow'],
  ['Provider APIs directly','Google SDK and HTTPX call the configured models'],
  ['Local observability','SQLite events, attempts and usage power the UI'],
  ['Dependency distinction','langchain-core and LangSmith SDK arrive transitively']],foot:'The project does not configure LangChain create_agent or LangSmith tracing.',
  notes:'Interview-la correct-aa ipdi sollunga: naan LangGraph select panninen because explicit evaluation and rewrite control venum. LLM calls Google SDK and HTTPX-la irukku. Full LangChain create_agent use pannala. Requirements lock-la langchain-core and langsmith irukkiradhu indirect dependency. Installed package irukkaradhu product feature configured-nu proof illa. Namma local events and audit traceability irukku; adhu LangSmith service integration illa.',source:'backend/requirements.in; backend/requirements.txt; backend/app/services/lesson_ai.py; backend/app/workflow.py; backend/app/db.py'};

const strategies={title:'Prompts, references and fine-tuning',kind:'rows',rows:[
  ['Guide','Prompting','Instructions define the audience, lesson structure and checks'],
  ['Ground','References','Supply supporting facts in the model input at request time'],
  ['Adapt','Fine-tuning','Training changes learned behavior using example data']],
  notes:'Oru student analogy use pannalaam. Prompt-na teacher instructions. References-na open-book material. Fine-tuning-na examples use panni training moolama model behavior adapt panradhu. Indha app instructions and frozen reference excerpts kudukkudhu. Model weights-a update pannaadhu. Retrieval and fine-tuning together use panna mudiyum. Fine-tuning pannina citation checking or evaluator thevai illa-nu artham illa.',source:`${ft}; ${data}; ${rag}; backend/app/services/lesson_ai.py; backend/content/prompts.json`};

const noTuning={title:'Why fine-tuning is not the first step',kind:'list',items:[
  ['Project objective','Demonstrate an auditable content-quality loop'],
  ['Training evidence','We do not have a curated lesson-training corpus'],
  ['Changing factual content','Frozen references keep factual inputs inspectable'],
  ['Iteration and validation','Test prompt/rubric changes before adding a training job']],foot:'Fine-tuning remains an option after a measured baseline and reviewed training data.',
  notes:'Fine-tuning bad-nu sollala. Indha assessment objective workflow and evaluator ownership. Namma kitte reviewed training lessons corpus and proven holdout benefit illa. Adhukkulla training panna quality improve aagum-nu assume panna mudiyadhu. Sources and rules change aana prompts/reference snapshots inspect panna easy. Dataset preparation, training and evaluation extra work. First baseline defects understand pannitu, reliable labels collect panni, benefit measure pannina apram tuning consider pannalaam. Tuning failure-free factual accuracy guarantee pannaadhu.',source:`Project decision based on docs/ASSESSMENT_AUDIT.md and backend/dataset.py; tuning concepts: ${ft}; ${data}`};

const quality={title:'How the release gate works',kind:'list',items:[
  ['Python validates structure','Required sections, strict booleans and source mappings'],
  ['The model judges teaching','Accuracy, jargon, examples, flow and missing information'],
  ['Evidence must exist','Check IDs and selected lesson fields must match'],
  ['Every mandatory check passes','14 checks for English, 15 for native languages']],foot:'Separate calls can share mistakes. Calibration and human review still matter.',
  notes:'Valid JSON vandhaa lesson correct-nu solla mudiyadhu. Pydantic shape and strict booleans validate pannum. Python source IDs and exact evidence check pannum. Model actual teaching content judge pannum. English-ku fourteen, native language-ku language check serthu fifteen. Oru mandatory fail-na release illa. Same provider different role calls independent human judgement illa. Historical false passes irundhadhai calibration documentation-la preserve pannirukkom.',source:'backend/app/quality.py; backend/app/lesson_schemas.py; backend/app/languages.py; VERIFICATION.md'};

const fallback={title:'Provider fallback and stopping rules',kind:'list',items:[
  ['Gemini primary','Generation and evaluation use separate calls'],
  ['Groq backup','A Gemini quota response can switch the affected call'],
  ['FreeLLM router','Eligible Groq capacity and JSON/output failures can continue'],
  ['Explicit final failure','No provider loop or approval from an incomplete response']],foot:'Actual provider/model usage is recorded. A larger key pool does not remove all limits.',
  notes:'Gemini primary. Quota vandhaa Groq backup. Groq quota, output cut-off, explicit json_validate_failed or eligible temporary error vandhaa configured FreeLLM route use pannalaam. Authentication error-a silently bypass panna maattom. FreeLLM auto upstream model choose pannalaam; router report panna model name usage-la store pannom. Ella providers-um fail aana honest ERROR. Repeated unlimited retries or fake approval pannaadhu. Cancel local task-a stop pannum, already sent request quota consume pannirukkalaam.',source:'backend/app/services/lesson_ai.py; backend/app/services/groq.py; backend/app/services/freellm.py; backend/app/runtime.py'};

const memory={title:'History, memory and model training',kind:'rows',rows:[
  ['Record','History','Every attempt, check result and provider event'],
  ['Reuse','Validated memory','Only selected teaching instructions with provenance'],
  ['Train','Fine-tuning','A separate model-training activity, absent here']],
  notes:'History save pannradhu, reusable memory, fine-tuning moonum same illa. History-la ella records-um irukkum. Validated memory-la proven teaching instructions mattum select aaganum. Repeated failures observe pannitu candidate compare panni benefit and no-regression demonstrate panna thaan activate. Current audited count zero active instructions. Prompt text sharpen pannradhu weights update panradhu illa. Successful live improvement and later reuse pending-nu clear-aa sollanum.',source:'backend/app/db.py; backend/app/improvements.py; docs/ASSESSMENT_AUDIT.md'};

const storage={title:'Appendix  Storage and retrieval choices',kind:'list',items:[
  ['SQLite now','One local process, structured audit records and simple setup'],
  ['PostgreSQL later','Consider for multiple users, processes and concurrent writes'],
  ['Current reference retrieval','Reviewed RAG notes or bounded Wikipedia search/excerpts'],
  ['Vector retrieval later','Needs document ingestion, embeddings and retrieval-quality tests']],foot:'This is a lesson generator about RAG. It has no embedding index or vector database.',
  notes:'SQLite history database-a vector database-nu describe panna koodadhu. Intha app single local workflow-ku simple setup choose pannom. Multi-user deployment grow aana PostgreSQL and job infrastructure evaluate pannalaam. Current grounding reviewed notes and Wikipedia excerpts. Semantic embedding search or full document-QA product implement pannala. Andha requirement vandhaa document ingestion, chunks, embedding index and retrieval evaluation add panna vendum. RAG topic teach pannradhu and full RAG search product build pannradhu separate scope.',source:'backend/app/db.py; backend/app/topics.py; backend/content/rag_sources.json; docs/DESIGN.md', time:'Optional appendix'};

const future={title:'Appendix  When fine-tuning makes sense',kind:'list',items:[
  ['A recurring measured defect','Prompt/reference changes do not adequately resolve it'],
  ['Reviewed examples','Representative lessons and desired outputs with reliable labels'],
  ['Separate evaluation data','Compare the tuned model with the existing baseline'],
  ['Operational fit','Model support, training budget and measurable benefit']],foot:'A tuned model would still need grounding, release checks and regression testing.',
  notes:'Future-la tune panna eppo? Repeated style or teaching behavior defect reliable-aa measure pannirukkanum. Reviewed examples and separate evaluation data venum. Tuning support irukkira model, budget and measurable improvement venum. Current one small authored calibration set-a large production training corpus-nu claim panna koodadhu. Facts supply panra references and final quality gate tuned model-kum continue aaganum.',source:`${ft}; ${data}; project decisions: backend/dataset.py; docs/ASSESSMENT_AUDIT.md`,time:'Optional appendix'};

const main=[...original.slice(0,7),ecosystem,actual,original[7],original[8],original[9],original[10],strategies,noTuning,quality,fallback,memory,original[11],original[12]];
const seconds=[15,25,25,25,20,20,25,45,30,25,40,35,30,45,45,30,25,30,20,10];
let elapsed=0;
const clock=n=>`${String(Math.floor(n/60)).padStart(2,'0')}:${String(n%60).padStart(2,'0')}`;
export const slides=main.map((s,i)=>{const start=elapsed;elapsed+=seconds[i];return {...s,time:`${clock(start)}–${clock(elapsed)}`};});
slides[0].notes='Vanakkam. Intha project LessonLoop. Oru beginner topic kudutha lesson create panni, evaluate panni, mistakes irundha rewrite pannum. First technical decisions and workflow explain pannuren. Apram product evidence show pannuren. Closing-la actual completion boundary solluren.';
slides.push({...original[13],time:'14:00–15:00'},original[14],original[15],storage,future);

export const demoScript=`# Revised LessonLoop recording plan

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
`;
