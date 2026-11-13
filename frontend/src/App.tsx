import { useCallback, useEffect, useRef, useState } from 'react'
import { ArrowRight, ArrowUpRight, Check, Code2, FileText, Info, Layers3, LoaderCircle, LockKeyhole, RefreshCw, Server, Terminal, Workflow } from 'lucide-react'
import { ProviderCard } from './components/ProviderCard'
import { api, ApiError, API_BASE_URL, type Health, type Provider, type ProvidersStatus } from './lib/api'

export default function App() {
  const [health, setHealth] = useState<Health | null>(null)
  const [providers, setProviders] = useState<ProvidersStatus>()
  const [checking, setChecking] = useState(true)
  const [backendError, setBackendError] = useState<string | null>(null)
  const [verified, setVerified] = useState<Record<Provider, boolean>>({ gemini: false, openai: false })
  const checkingRef = useRef(false)

  const checkBackend = useCallback(async () => {
    if (checkingRef.current) return
    checkingRef.current = true
    setChecking(true)
    setBackendError(null)
    try {
      const [healthResponse, statusResponse] = await Promise.all([api.health(), api.status()])
      setHealth(healthResponse)
      setProviders(statusResponse)
    } catch (error) {
      setHealth(null)
      setProviders(undefined)
      setBackendError(error instanceof ApiError ? error.message : 'Unable to check the backend.')
    } finally {
      checkingRef.current = false
      setChecking(false)
    }
  }, [])

  useEffect(() => { void checkBackend() }, [checkBackend])
  const onVerified = useCallback((provider: Provider, value: boolean) => {
    setVerified(current => ({ ...current, [provider]: value }))
  }, [])
  const completed = Number(Boolean(health)) + Number(verified.gemini) + Number(verified.openai)

  return (
    <div className="app-shell">
      <header className="site-header">
        <div className="header-inner">
          <a className="brand" href="/" aria-label="LessonLoop home"><span className="brand-mark"><Workflow size={23} strokeWidth={2.2} /></span><span>LessonLoop<span className="brand-dot">.</span></span></a>
          <div className="header-right"><span className="local-badge"><span className="status-dot green" />Local development</span><span className="version">v0.1.0</span></div>
        </div>
      </header>

      <main>
        <div className="page-intro">
          <div><div className="sprint-label"><span />Sprint 1 · Connection setup</div><h1>A good lesson starts<br className="mobile-break" /> with a connection<span>.</span></h1><p className="intro-copy">Generate. Evaluate. Improve.<br className="mobile-break" /> Let’s connect the tools behind your next lesson.</p></div>
          <div className="intro-decoration" aria-hidden="true"><div className="orbit-ring" /><div className="orbit-center"><Layers3 size={30} strokeWidth={1.5} /></div><span className="orbit-small one"><Sparkle /></span><span className="orbit-small two"><Check size={17} /></span><span className="orbit-dot" /></div>
        </div>

        <div className="workspace-grid">
          <div className="connections-column">
            <section className="backend-card panel" aria-labelledby="backend-heading">
              <div className="backend-top"><div className="backend-title"><span className="server-icon"><Server size={21} /></span><div><h2 id="backend-heading">Your backend</h2><p>The foundation for everything that follows.</p></div></div><span className={`badge ${checking ? 'neutral' : health ? 'connected' : 'failed'}`} role="status">{checking ? <LoaderCircle size={13} className="spin" /> : health ? <span className="status-dot green" /> : <span className="status-dot red" />}{checking ? 'Checking' : health ? 'Connected' : 'Unavailable'}</span></div>
              <div className="backend-bottom"><div className="endpoint"><code>{API_BASE_URL}</code><span className="endpoint-tag">FastAPI</span></div><button className="quiet-button" disabled={checking} onClick={checkBackend}><RefreshCw size={14} className={checking ? 'spin' : ''} />Check backend</button></div>
              {backendError && <p className="backend-error" role="alert">{backendError}</p>}
            </section>

            <div className="section-heading"><div><h2>Connect your AI providers</h2><p>Two models. One continuous learning loop.</p></div><span className="section-count">{Number(verified.gemini) + Number(verified.openai)} / 2 verified</span></div>
            <div className="providers-grid">
              <ProviderCard provider="gemini" configuration={providers?.gemini} backendConnected={Boolean(health)} onVerified={onVerified} />
              <ProviderCard provider="openai" configuration={providers?.openai} backendConnected={Boolean(health)} onVerified={onVerified} />
            </div>
            <div className="privacy-note"><LockKeyhole size={15} /><p>Your keys stay on the backend. They’re never sent to this browser.</p></div>
          </div>

          <aside className="setup-sidebar">
            <section className="progress-card panel" aria-labelledby="setup-heading"><div className="sidebar-eyebrow">YOUR WORKSPACE</div><div className="progress-title"><h2 id="setup-heading">Setup checklist</h2><span>{completed}<span> / 3</span></span></div><div className="progress-track" role="progressbar" aria-label="Setup progress" aria-valuemin={0} aria-valuemax={3} aria-valuenow={completed}><span style={{ width: `${completed / 3 * 100}%` }} /></div><ol className="checklist">{[['Backend is running', Boolean(health)], ['Gemini connection verified', verified.gemini], ['OpenAI connection verified', verified.openai]].map(([label, done], index) => <li key={String(label)} className={done ? 'done' : ''}><span className="checklist-number">{done ? <Check size={13} strokeWidth={2.5} /> : `0${index + 1}`}</span><span>{label}</span></li>)}</ol><p className="checklist-note">{completed === 3 ? 'All connections verified. Your foundation is ready.' : 'Small steps toward better lessons.'}</p></section>

            <section className="quickstart-card" aria-labelledby="quickstart-heading"><span className="quickstart-icon"><Terminal size={19} /></span><h2 id="quickstart-heading">First time here?</h2><p>Add your provider credentials to the backend environment file.</p><div className="file-path"><FileText size={14} /><code>backend/.env</code></div><p className="quickstart-detail">Save the file, restart the backend, then test each connection.</p><a href={`${API_BASE_URL}/docs`} target="_blank" rel="noreferrer" className="docs-link">Explore the API<ArrowUpRight size={15} /></a></section>
            <div className="manual-note"><Info size={15} /><p>Provider tests run only when you click. Configuration alone doesn’t verify access.</p></div>
          </aside>
        </div>

        <section className="milestone" aria-labelledby="milestone-heading"><div className="milestone-icon"><Workflow size={22} /></div><div className="milestone-copy"><span className="eyebrow">THE NEXT CHAPTER</span><h2 id="milestone-heading">From connection to creation</h2><p>Next: generate a beginner RAG lesson and evaluate it against a pass/fail rubric.</p></div><span className="up-next">Sprint 2<ArrowRight size={15} /></span></section>
        <footer><p>LessonLoop <span>·</span> Built for learning, designed to improve.</p><span className="footer-meta"><Code2 size={14} />Development workspace</span></footer>
      </main>
    </div>
  )
}

function Sparkle() { return <span style={{ fontSize: 23 }}>✦</span> }
