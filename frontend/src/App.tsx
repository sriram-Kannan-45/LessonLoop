import { useCallback, useEffect, useRef, useState } from 'react'
import { ArrowRight, BookOpen, BrainCircuit, Check, ChevronLeft, ChevronRight, Clock3, Download, FileCheck2, FlaskConical, History, Layers3, LoaderCircle, MessageSquareText, RefreshCw, Send, Settings2, ShieldCheck, Sparkles, Workflow } from 'lucide-react'
import Setup from './Setup'
import { RunActivity } from './components/RunActivity'
import { LessonReader } from './components/LessonReader'
import { QualityReport } from './components/QualityReport'
import { AttemptHistory } from './components/AttemptHistory'
import { ProviderUsage } from './components/ProviderUsage'
import { MemoryPanel } from './components/MemoryPanel'
import { workspaceApi, type Event, type FrozenRun, type Memory, type Run, type RunSummary, type Workspace } from './lib/workspace'
import './workspace.css'

type View = 'studio' | 'history' | 'memory'
type ReaderTab = 'lesson' | 'quality' | 'attempts' | 'feedback'
const stageNames: Record<string, string> = { CANCELLED: 'Lesson cancelled', PROVIDER_FALLBACK: 'Switching to Groq backup', PROVIDER_WAIT: 'Waiting for the API allowance', PROVIDER_USED: 'Provider response received', RESEARCHING: 'Finding topic references', REFERENCES_READY: 'Topic references ready', QUEUED: 'Getting ready', LOADING_CONTEXT: 'Loading references', GENERATING: 'Creating your lesson', VALIDATING: 'Checking the structure', EVALUATING: 'Reviewing every checkpoint', REWRITING: 'Improving the draft', VERDICT: 'Recording the verdict', DEMO_MUTATION: 'Inserting the demonstration error', TECHNICAL_RETRY: 'Retrying a technical request', APPROVED: 'Lesson approved', NEEDS_REVIEW: 'Human review needed', ERROR: 'Run stopped', INTERRUPTED: 'Run interrupted' }

export default function App() {
  return new URLSearchParams(window.location.search).get('view') === 'connections' ? <Setup /> : <Studio />
}

function Studio() {
  const [view, setView] = useState<View>('studio')
  const [workspace, setWorkspace] = useState<Workspace | null>(null)
  const [memory, setMemory] = useState<Memory | null>(null)
  const [history, setHistory] = useState<RunSummary[]>([])
  const [total, setTotal] = useState(0)
  const [offset, setOffset] = useState(0)
  const [runId, setRunId] = useState<string | null>(new URLSearchParams(window.location.search).get('run'))
  const [run, setRun] = useState<FrozenRun | null>(null)
  const [events, setEvents] = useState<Event[]>([])
  const [topic, setTopic] = useState('Photosynthesis')
  const [demo, setDemo] = useState(false)
  const [cancelling, setCancelling] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)
  const [readerTab, setReaderTab] = useState<ReaderTab>('lesson')
  const [draftNumber, setDraftNumber] = useState<number | null>(null)
  const [pollKey, setPollKey] = useState(0)
  const submitGuard = useRef(false)

  const refresh = useCallback(async () => {
    try {
      const [info, rows, evidence] = await Promise.all([workspaceApi.workspace(), workspaceApi.history(offset), workspaceApi.memory()])
      setWorkspace(info); setHistory(rows.items); setTotal(rows.total); setMemory(evidence); setError('')
    } catch (err) { setError(err instanceof Error ? err.message : 'Could not load the workspace.') }
    finally { setLoading(false) }
  }, [offset])
  useEffect(() => { void refresh() }, [refresh])
  useEffect(() => {
    if (!runId) return
    let cancelled = false
    let timer: ReturnType<typeof setTimeout>
    let cursor = 0
    const collected: Event[] = []
    setEvents([]); setDraftNumber(null)
    async function poll() {
      try {
        const [current, updates] = await Promise.all([workspaceApi.run(runId!), workspaceApi.events(runId!, cursor)])
        if (cancelled) return
        cursor = updates.next_cursor; collected.push(...updates.events)
        setRun(current); setEvents([...collected]); setError('')
        if (current.status === 'RUNNING') timer = setTimeout(poll, 1500)
        else await refresh()
      } catch (err) { if (!cancelled) setError(err instanceof Error ? err.message : 'Could not retrieve this run. Refresh to retry.') }
    }
    void poll()
    return () => { cancelled = true; clearTimeout(timer) }
  }, [runId, pollKey, refresh])

  function openRun(id: string) {
    setRun(null); setRunId(id); setView('studio'); setReaderTab('lesson')
    window.history.replaceState(null, '', `/?run=${id}`)
  }
  async function generate(event: React.FormEvent) {
    event.preventDefault()
    await startLesson(topic, demo)
  }
  async function startLesson(requestedTopic: string, requestedDemo: boolean) {
    if (submitGuard.current) return
    submitGuard.current = true; setSubmitting(true); setError('')
    setTopic(requestedTopic); setDemo(requestedDemo)
    try { const created = await workspaceApi.create(requestedTopic, requestedDemo); openRun(created.id); setWorkspace(current => current ? { ...current, busy: true } : current) }
    catch (err) { setError(err instanceof Error ? err.message : 'Could not start the lesson.') }
    finally { submitGuard.current = false; setSubmitting(false) }
  }
  async function cancelLesson() {
    if (!run || cancelling) return
    setCancelling(true)
    try {
      setRun(await workspaceApi.cancel(run.id))
      setPollKey(key => key + 1)
      await refresh()
    } catch (err) { setError(err instanceof Error ? err.message : 'Could not cancel the run. Try again.') }
    finally { setCancelling(false) }
  }
  const attempt = run?.attempts.find(item => item.number === draftNumber) || run?.attempts.at(-1)
  const active = run?.status === 'RUNNING'
  const busy = submitting || active || workspace?.busy
  const temporaryFailure = run?.error && (['TIMEOUT', 'SERVICE_UNAVAILABLE', 'PROVIDER_SERVER_ERROR', 'CONNECTION_ERROR'].includes(run.error.code) || run.error.diagnostics?.provider_http_status === 503)
  const providerMessage = run?.error?.diagnostics?.provider_http_status === 503 ? `${run?.error?.diagnostics?.provider === 'groq' ? 'Groq' : 'Gemini'} is temporarily busy or unavailable (HTTP 503). Please wait a moment, then try again.` : run?.error?.message
  const passed = attempt?.evaluation?.filter(check => check.passed).length || 0
  const draftLabel = run?.attempt_count ? `Draft ${run.attempt_count} of 3` : active ? 'Preparing draft 1 of 3' : 'No saved draft'

  return <div className="product-shell">
    <header className="product-header"><div className="product-header-inner"><a className="brand" href="/"><span className="brand-mark"><Workflow size={23} /></span><span>LessonLoop<span className="brand-dot">.</span></span></a><nav aria-label="Workspace navigation">{([{ id: 'studio', label: 'Lesson studio', icon: Sparkles }, { id: 'history', label: 'Run history', icon: History }, { id: 'memory', label: 'Memory & learning', icon: BrainCircuit }] as const).map(item => <button key={item.id} className={view === item.id ? 'selected' : ''} aria-current={view === item.id ? 'page' : undefined} onClick={() => setView(item.id)}><item.icon size={15} />{item.label}</button>)}</nav><a className="connections-link" href="/?view=connections"><Settings2 size={16} /><span>Connections</span></a></div></header>
    <main className="product-main">
      {error && <div className="error-banner" role="alert"><span>{error}</span><button onClick={() => { void refresh(); setPollKey(key => key + 1) }}><RefreshCw size={14} />Retry</button></div>}
      {view === 'studio' && <><div className="view-heading studio-intro"><div><span className="reader-kicker"><span className="small-square" />YOUR SELF-EVALUATING LESSON WORKSPACE</span><h1>Made to teach.<br className="mobile-break" /> Checked to make sense<span>.</span></h1><p>From a first draft to a lesson a beginner can follow. Every checkpoint matters.</p></div><span className="workspace-badge"><span className={`status-dot ${workspace ? 'green' : 'gray'}`} />{loading ? 'Connecting' : workspace ? 'Local workspace' : 'Backend unavailable'}</span></div>
      <div className="studio-layout"><aside className="create-column"><form className="panel create-panel" onSubmit={generate}><div className="panel-heading"><span className="tiny-icon"><Sparkles size={18} /></span><h2>Create a lesson</h2></div><label htmlFor="topic">What would you like to learn?</label><input id="topic" value={topic} onChange={event => setTopic(event.target.value)} minLength={3} maxLength={160} required /><p className="field-help">Enter any subject, such as photosynthesis, Python programming, or world history. References are collected for your topic.</p>{busy && <p className="field-help">You can type your next topic now. Generate becomes available when the current run finishes.</p>}<label htmlFor="learner">Who is it for?</label><select id="learner" defaultValue="india_beginner"><option value="india_beginner">India · Grade 12 · Beginner</option></select><div className="learner-note"><BookOpen size={16} /><p>Simple English. No specialist background assumed. Respectful, step-by-step learning.</p></div><label htmlFor="reference-pack">Topic references</label><select id="reference-pack" defaultValue="auto"><option value="auto">Collect automatically for this topic</option></select><p className="field-help">Public reference excerpts are saved with each run. They are automatically collected, not human-reviewed.</p><div className="model-labels"><div><span>GENERATOR · PRIMARY</span><code>{workspace?.generator_model || 'Loading model'}</code></div><div><span>EVALUATOR · PRIMARY</span><code>{workspace?.evaluator_model || 'Loading model'}</code></div></div><p className="provider-caveat">Gemini is primary. Separate calls can still share mistakes.</p>{workspace?.fallback && <div className="fallback-config"><strong>Groq quota fallback</strong><span>{!workspace.fallback.enabled ? 'Disabled' : workspace.fallback.configured ? 'Configured for Gemini quota fallback' : 'Add GROQ_API_KEY in backend/.env'}</span><code>{workspace.fallback.generator_model}</code></div>}{workspace?.demo_enabled && <label className="demo-option"><input type="checkbox" checked={demo} onChange={event => setDemo(event.target.checked)} disabled={Boolean(busy)} /><span>Inject a factual error into the first draft<small>Development demonstration · real evaluator verdict</small></span></label>}<button className="primary-button generate-button" type="submit" disabled={Boolean(busy) || !workspace?.configured}>{busy ? <LoaderCircle size={17} className="spin" /> : <Sparkles size={17} />}{submitting ? 'Starting…' : active ? 'Lesson in progress' : 'Generate lesson'}{!busy && <ArrowRight size={16} />}</button><p className="cost-note">Uses provider quota · up to 3 content drafts</p>{workspace && !workspace.configured && <a href="/?view=connections" className="configure-notice">Add your Gemini key in Connections to begin.</a>}</form>
      <div className="guardrail-note"><ShieldCheck size={17} /><p><strong>A firm release rule</strong>Every mandatory check must pass. After two rewrites, unresolved lessons stay in review.</p></div><div className="recent-mini"><div><h3>Recent runs</h3><button onClick={() => setView('history')}>View all<ArrowRight size={12} /></button></div>{history.length ? history.slice(0, 3).map(item => <button key={item.id} onClick={() => openRun(item.id)}><span>{item.topic}<small>{new Date(item.started_at).toLocaleString()}</small></span><span className={`mini-dot ${item.status.toLowerCase()}`} /></button>) : <p>Your lesson history will appear here.</p>}</div></aside>
      <div className="run-column">{!runId ? <div className="panel welcome-panel"><div className="welcome-illustration"><span><Layers3 size={42} strokeWidth={1.3} /></span><i><ShieldCheck size={21} /></i></div><span className="reader-kicker">A LITTLE CARE GOES A LONG WAY</span><h2>A lesson worth understanding.</h2><p>Choose a topic and start the loop.<br />We’ll create, check, and improve it before release.</p><div className="loop-explainer"><div><span>01</span><strong>Create</strong><small>Grounded in topic references</small></div><ArrowRight size={17} /><div><span>02</span><strong>Evaluate</strong><small>Every mandatory checkpoint</small></div><ArrowRight size={17} /><div><span>03</span><strong>Improve</strong><small>Specific feedback, up to 2 retries</small></div></div><div className="welcome-bottom"><Check size={14} />Your drafts, verdicts, and corrections are saved locally.</div></div> : !run ? <div className="panel loading-panel" role="status"><LoaderCircle className="spin" />Loading your run…</div> : <>
        <RunActivity run={run} events={events} onCancel={() => void cancelLesson()} cancelling={cancelling} stage={stageNames[run.stage] || run.stage.replaceAll('_', ' ')} /><section className="panel run-progress" aria-live="polite"><div className="run-progress-top"><div><span className="reader-kicker">{run.demo_error ? 'DELIBERATE-ERROR DEMONSTRATION' : 'YOUR LESSON RUN'}</span><h2>{stageNames[run.stage] || run.stage.replaceAll('_', ' ')}</h2></div><span className={`status-pill ${run.status.toLowerCase()}`}>{active && <LoaderCircle size={12} className="spin" />}{run.status.replaceAll('_', ' ')}</span></div><div className="run-facts"><span><Clock3 size={13} />{new Date(run.started_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span><span>{draftLabel}</span><span>{run.selected_memory.length} memory {run.selected_memory.length === 1 ? 'instruction' : 'instructions'} used</span><code>{run.id.slice(0, 8)}</code></div>{attempt && <ProviderUsage attempt={attempt} />}{run.error && <div className="inline-error" role="alert"><p>{providerMessage}</p>{temporaryFailure && <div className="failure-recovery"><button className="secondary-button" type="button" disabled={Boolean(busy) || !workspace?.configured} onClick={() => { void startLesson(run.topic, Boolean(run.demo_error)) }}><RefreshCw size={14} />Try again</button><span>Starts a new run. This run stays in your history.</span></div>}</div>}{run.status === 'NEEDS_REVIEW' && <div className="review-warning">No lesson was released. Unresolved checks remain after the maximum two rewrites.</div>}<details className="event-log"><summary>Live workflow events <span>{events.length} recorded</span></summary><ol>{events.map(item => <li key={item.sequence}><time>{new Date(item.created_at).toLocaleTimeString()}</time><span>{item.message}</span></li>)}</ol></details></section>
        {attempt && <section className="panel reader-panel"><div className="reader-toolbar"><div role="tablist" aria-label="Run details">{([{ id: 'lesson', text: 'Lesson', icon: BookOpen }, { id: 'quality', text: 'Quality report', icon: FileCheck2 }, { id: 'attempts', text: 'Attempts', icon: History }, { id: 'feedback', text: 'Feedback', icon: MessageSquareText }] as const).map(tab => <button key={tab.id} role="tab" aria-selected={readerTab === tab.id} onClick={() => setReaderTab(tab.id)}><tab.icon size={14} />{tab.text}</button>)}</div><label className="draft-select">Draft<select aria-label="Select draft" value={attempt.number} onChange={event => setDraftNumber(Number(event.target.value))}>{run.attempts.map(item => <option key={item.id} value={item.number}>{item.number}</option>)}</select></label></div>
          {readerTab === 'lesson' && <LessonReader lesson={attempt.draft} sources={run.source_snapshot?.sources || workspace?.source_pack.sources || []} approved={run.status === 'APPROVED' && attempt.status === 'APPROVED'} />}
          {readerTab === 'quality' && <QualityReport attempt={attempt} rubric={run.rubric_snapshot?.checks || workspace?.rubric.checks || []} sources={run.source_snapshot?.sources || workspace?.source_pack.sources || []} />}
          {readerTab === 'attempts' && <AttemptHistory run={run} onSelect={number => { setDraftNumber(number); setReaderTab('lesson') }} />}
          {readerTab === 'feedback' && <FeedbackPanel run={run} refresh={() => setPollKey(key => key + 1)} />}
          <div className="reader-footer"><span><ShieldCheck size={14} />{passed} / {workspace?.rubric.checks.length || 14} checks passed on this draft</span><div><a href={workspaceApi.exportUrl(run.id, 'markdown')}><Download size={13} />{run.status === 'APPROVED' ? 'Approved lesson' : 'Review draft'}</a><a href={workspaceApi.exportUrl(run.id, 'json')}><Download size={13} />Audit JSON</a></div></div></section>}
        {!attempt && active && <div className="panel working-panel"><LoaderCircle className="spin" size={25} /><h3>Building your first draft</h3><p>The model is working from the references saved for your topic. Progress above comes from real backend events.</p></div>}
        {!attempt && !active && <div className="panel working-panel"><h3>No draft was released</h3><p>The run stopped before a usable draft was saved. Its events and error remain in history.</p><a className="secondary-button" href={workspaceApi.exportUrl(run.id, 'json')}><Download size={13} />Download audit JSON</a></div>}
        <div className="run-metadata"><span>References: {run.source_pack_version}</span><span>Rubric: {run.rubric_version}</span><span>Prompt: {run.generator_prompt_version}</span>{run.selected_memory.map(item => <span key={item.id}>Memory: {item.id.slice(0, 8)} · {item.category}</span>)}</div>
      </>}</div></div></>}
      {view === 'history' && <div className="history-page"><div className="view-heading"><span className="reader-kicker">EVERY ATTEMPT COUNTS</span><h1>Your lesson history<span>.</span></h1><p>Completed lessons and unfinished drafts survive server restarts.</p></div><section className="panel workspace-panel"><div className="panel-heading"><h2>Saved runs</h2><span className="version-tag">{total} total</span></div>{!history.length ? <div className="empty-state"><History size={30} /><h3>A fresh start</h3><p>Create your first lesson in the studio. Its full history will be saved here.</p><button className="secondary-button" onClick={() => setView('studio')}>Open lesson studio</button></div> : <div className="history-table"><div className="history-row history-labels"><span>LESSON</span><span>STATUS</span><span>DRAFTS</span><span>STARTED</span></div>{history.map(item => <button className="history-row" key={item.id} onClick={() => openRun(item.id)}><span><strong>{item.topic}</strong><small>{item.id.slice(0, 8)}</small></span><span className={`status-pill ${item.status.toLowerCase()}`}>{item.status.replaceAll('_', ' ')}</span><span>{item.attempt_count} / 3</span><span>{new Date(item.started_at).toLocaleString()}</span></button>)}</div>}<div className="pagination"><span>{total ? offset + 1 : 0}–{Math.min(offset + 10, total)} of {total}</span><button aria-label="Previous history page" disabled={offset === 0} onClick={() => setOffset(value => Math.max(0, value - 10))}><ChevronLeft size={17} /></button><button aria-label="Next history page" disabled={offset + 10 >= total} onClick={() => setOffset(value => value + 10)}><ChevronRight size={17} /></button></div></section></div>}
      {view === 'memory' && <MemoryPanel memory={memory} workspace={workspace} refresh={refresh} />}
      <footer className="product-footer"><p>LessonLoop · Generate. Evaluate. Improve.</p><span>Gemini primary · Groq quota backup · Local history · All-checks release rule</span></footer>
    </main>
  </div>
}

function FeedbackPanel({ run, refresh }: { run: Run; refresh: () => void }) {
  const [category, setCategory] = useState('confusing_language')
  const [message, setMessage] = useState('')
  const [note, setNote] = useState('')
  const [status, setStatus] = useState('')
  const [busy, setBusy] = useState(false)
  async function submit(event: React.FormEvent) {
    event.preventDefault(); setBusy(true); setStatus('')
    try { const result = await workspaceApi.feedback(run.id, category, message); setStatus(result.message); setMessage(''); refresh() }
    catch (err) { setStatus(err instanceof Error ? err.message : 'Feedback could not be saved.') }
    finally { setBusy(false) }
  }
  async function review(id: string, action: string) {
    setBusy(true)
    try { await workspaceApi.reviewFeedback(id, action, note); setStatus('Review saved. Only a vetted instruction that passes a comparison can become active memory.'); setNote(''); refresh() }
    catch (err) { setStatus(err instanceof Error ? err.message : 'Review could not be saved.') }
    finally { setBusy(false) }
  }
  return <div className="feedback-panel"><h2>Help the next lesson</h2><p className="muted">Feedback is saved as an unverified observation. It never changes active prompts automatically.</p><form onSubmit={submit}><label htmlFor="feedback-category">What should we look at?</label><select id="feedback-category" value={category} onChange={event => setCategory(event.target.value)}><option value="confusing_language">Confusing language</option><option value="factual_issue">A factual issue</option><option value="missing_example">A missing example</option><option value="correction">A correction</option></select><label htmlFor="feedback-message">Your feedback</label><textarea id="feedback-message" minLength={5} maxLength={2000} required value={message} onChange={event => setMessage(event.target.value)} placeholder="Tell us which part needs attention and why." /><button className="primary-button" disabled={busy}><Send size={14} />Save feedback</button></form>{status && <p role="status" className="inline-notice">{status}</p>}{run.feedback.map(item => <article className="feedback-item" key={item.id}><div><strong>{item.category.replaceAll('_', ' ')}</strong><span className="status-pill">{item.status}</span></div><p>{item.message}</p>{item.review_note && <p>Review: {item.review_note}</p>}{item.status === 'unverified' && <div><label htmlFor={`review-${item.id}`}>Human review note (at least 10 characters)</label><input id={`review-${item.id}`} value={note} onChange={event => setNote(event.target.value)} maxLength={1000} /><div className="review-actions"><button className="secondary-button" disabled={busy || note.trim().length < 10} onClick={() => review(item.id, 'verified')}>Verified observation</button><button className="secondary-button" disabled={busy || note.trim().length < 10} onClick={() => review(item.id, 'dismissed')}>Dismiss</button></div></div>}</article>)}</div>
}
