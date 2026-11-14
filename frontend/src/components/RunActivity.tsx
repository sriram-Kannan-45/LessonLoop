import { useEffect, useState } from 'react'
import { LoaderCircle } from 'lucide-react'
import type { Event, Run } from '../lib/workspace'

export function RunActivity({ run, events, stage }: { run: Run; events: Event[]; stage: string }) {
  const [now, setNow] = useState(Date.now())
  const active = run.status === 'RUNNING'
  useEffect(() => {
    setNow(Date.now())
    if (!active) return
    const timer = setInterval(() => setNow(Date.now()), 1000)
    return () => clearInterval(timer)
  }, [active, run.id])
  const latest = [...events].reverse().find(event => event.stage === run.stage)
  const wait = latest?.stage === 'PROVIDER_WAIT' && typeof latest.details.wait_seconds === 'number' ? latest : null
  const seconds = wait ? Math.max(0, Math.ceil((Date.parse(wait.created_at) + Number(wait.details.wait_seconds) * 1000 - now) / 1000)) : 0
  const elapsed = Math.max(0, Math.floor(((active ? now : Date.parse(run.finished_at || run.started_at)) - Date.parse(run.started_at)) / 1000))
  return <div className="run-activity" aria-label="Current run status">
    <div><strong>{active && <LoaderCircle size={15} className="spin" />}{stage}</strong><span>{run.status.replaceAll('_', ' ')} · Draft {Math.max(1, run.attempt_count)} of 3</span></div>
    {active ? <>
      <p>{wait ? 'Groq API allowance wait. Checking continues automatically. You can return to this run through Run history.' : latest?.message || 'The run is active. New drafts and results will appear automatically.'}</p>
      <small role="timer" aria-live="off">Elapsed {Math.floor(elapsed / 60)}m {elapsed % 60}s{wait && (seconds > 0 ? ` · Next request in about ${seconds}s` : ' · Waiting for the provider response')}</small>
      <p>The visible lesson is a saved draft. Wait for Approved, Needs review, or Error before treating the run as finished.</p>
      {Boolean(run.demo_error) && <p><b>Error demonstration is ON.</b> Draft 1 contains an intentional false statement. Turn off “Inject a factual error” for your next normal lesson.</p>}
    </> : <p>{run.status === 'APPROVED' ? 'Finished. Every mandatory check passed; you can read and download the lesson.' : run.status === 'NEEDS_REVIEW' ? 'Finished. Some checks still failed after three drafts. Open Quality report to see the remaining issues.' : 'Stopped. See the error details and saved drafts below.'}</p>}
  </div>
}
