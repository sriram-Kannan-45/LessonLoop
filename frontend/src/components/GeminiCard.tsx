import { useEffect, useRef, useState } from 'react'
import { ArrowUpRight, Check, CircleAlert, Clock3, LoaderCircle, PlugZap, Sparkles } from 'lucide-react'
import { api, ApiError, type CheckSuccess, type ProviderStatus } from '../lib/api'

type Props = {
  configuration: ProviderStatus | undefined
  backendConnected: boolean
  onVerified: (verified: boolean) => void
}

export function GeminiCard({ configuration, backendConnected, onVerified }: Props) {
  const [busy, setBusy] = useState(false)
  const [result, setResult] = useState<CheckSuccess | null>(null)
  const [error, setError] = useState<string | null>(null)
  const inFlight = useRef(false)
  const configured = configuration?.configured === true

  useEffect(() => {
    setResult(null)
    setError(null)
    onVerified(false)
  }, [configuration?.configured, configuration?.model, onVerified])

  async function check() {
    if (inFlight.current) return
    inFlight.current = true
    setBusy(true)
    setError(null)
    setResult(null)
    onVerified(false)
    try {
      const response = await api.check()
      setResult(response)
      onVerified(true)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Something went wrong. Please retry.')
    } finally {
      inFlight.current = false
      setBusy(false)
    }
  }

  const status = busy ? 'Testing connection' : error ? 'Check failed' : result ? 'Connection verified' : !backendConnected ? 'Status unavailable' : configured ? 'Ready to test' : 'Not configured'

  return (
    <article className="provider-card panel" aria-labelledby="gemini-title">
      <div className="provider-top">
        <div className="provider-icon gemini" aria-hidden="true"><Sparkles size={27} /></div>
        <span className="eyebrow">POWERED BY GEMINI</span>
      </div>
      <h3 id="gemini-title">Gemini</h3>
      <p className="provider-role">Lesson generator & evaluator</p>
      <p className="provider-description">One AI provider for creating clear lessons and reviewing their quality.</p>
      <div className="model-row"><span>MODEL</span><code>{configuration?.model || 'Not selected'}</code></div>
      <div className="provider-status" role="status" aria-live="polite">
        <span className={`status-dot ${result ? 'green' : busy ? 'indigo' : error ? 'red' : 'gray'}`} />
        <span>{status}</span>
        {configured && !result && !busy && !error && <span className="unverified">Unverified</span>}
      </div>
      <div className={`result-box ${error ? 'error' : result ? 'success' : ''}`} aria-live="polite">
        {busy ? <><LoaderCircle className="spin" size={17} /><p>Sending a small test request…</p></> : error ? <><CircleAlert size={17} /><p>{error}</p></> : result ? <><Check size={17} /><div><p>{result.message}</p><span className="result-meta"><Clock3 size={12} />{result.latency_ms.toLocaleString()} ms · {new Date(result.checked_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span></div></> : <><PlugZap size={17} /><p>{!backendConnected ? 'Connect the backend to view provider settings.' : configured ? 'Configuration found. Run a test to verify access.' : <>Add your API key to <code>backend/.env</code> to get started.</>}</p></>}
      </div>
      <button className="provider-button" onClick={check} disabled={busy || !configured || !backendConnected} aria-label="Test Gemini connection">
        {busy ? <><LoaderCircle size={16} className="spin" />Testing connection…</> : <>{result || error ? 'Test again' : 'Test connection'}<ArrowUpRight size={17} /></>}
      </button>
      <p className="request-note">Runs one small request · API usage may apply</p>
    </article>
  )
}
