import { useEffect, useRef, useState } from 'react'
import { ArrowUpRight, Check, CircleAlert, Clock3, LoaderCircle, PlugZap, Sparkles } from 'lucide-react'
import { api, ApiError, type CheckSuccess, type Provider, type ProviderStatus } from '../lib/api'

type Props = {
  provider: Provider
  configuration: ProviderStatus | undefined
  backendConnected: boolean
  onVerified: (provider: Provider, verified: boolean) => void
}

export function ProviderCard({ provider, configuration, backendConnected, onVerified }: Props) {
  const [busy, setBusy] = useState(false)
  const [result, setResult] = useState<CheckSuccess | null>(null)
  const [error, setError] = useState<string | null>(null)
  const inFlight = useRef(false)
  const gemini = provider === 'gemini'
  const name = gemini ? 'Gemini' : 'OpenAI'
  const configured = configuration?.configured === true

  useEffect(() => {
    setResult(null)
    setError(null)
    onVerified(provider, false)
  }, [configuration?.configured, configuration?.model, onVerified, provider])

  async function check() {
    if (inFlight.current) return
    inFlight.current = true
    setBusy(true)
    setError(null)
    setResult(null)
    onVerified(provider, false)
    try {
      const response = await api.check(provider)
      setResult(response)
      onVerified(provider, true)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Something went wrong. Please retry.')
    } finally {
      inFlight.current = false
      setBusy(false)
    }
  }

  const status = busy ? 'Testing connection' : error ? 'Check failed' : result ? 'Connection verified' : !backendConnected ? 'Status unavailable' : configured ? 'Ready to test' : 'Not configured'

  return (
    <article className="provider-card panel" aria-labelledby={`${provider}-title`}>
      <div className="provider-top">
        <div className={`provider-icon ${provider}`} aria-hidden="true">{gemini ? <Sparkles size={27} /> : <span className="openai-mark">✳</span>}</div>
        <span className="eyebrow">{gemini ? '01 / GENERATE' : '02 / EVALUATE'}</span>
      </div>
      <h3 id={`${provider}-title`}>{name}</h3>
      <p className="provider-role">{gemini ? 'Lesson generator' : 'Lesson evaluator'}</p>
      <p className="provider-description">{gemini ? 'Turns a topic into a clear, beginner-friendly lesson.' : 'Reviews each lesson for clarity, accuracy, and quality.'}</p>
      <div className="model-row"><span>MODEL</span><code>{configuration?.model || 'Not selected'}</code></div>
      <div className="provider-status" role="status" aria-live="polite">
        <span className={`status-dot ${result ? 'green' : busy ? 'indigo' : error ? 'red' : 'gray'}`} />
        <span>{status}</span>
        {configured && !result && !busy && !error && <span className="unverified">Unverified</span>}
      </div>
      <div className={`result-box ${error ? 'error' : result ? 'success' : ''}`} aria-live="polite">
        {busy ? <><LoaderCircle className="spin" size={17} /><p>Sending a small test request…</p></> : error ? <><CircleAlert size={17} /><p>{error}</p></> : result ? <><Check size={17} /><div><p>{result.message}</p><span className="result-meta"><Clock3 size={12} />{result.latency_ms.toLocaleString()} ms · {new Date(result.checked_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span></div></> : <><PlugZap size={17} /><p>{!backendConnected ? 'Connect the backend to view provider settings.' : configured ? 'Configuration found. Run a test to verify access.' : <>Add your API key to <code>backend/.env</code> to get started.</>}</p></>}
      </div>
      <button className="provider-button" onClick={check} disabled={busy || !configured || !backendConnected} aria-label={`Test ${name} connection`}>
        {busy ? <><LoaderCircle size={16} className="spin" />Testing connection…</> : <>{result || error ? 'Test again' : 'Test connection'}<ArrowUpRight size={17} /></>}
      </button>
      <p className="request-note">Runs one small request · API usage may apply</p>
    </article>
  )
}
