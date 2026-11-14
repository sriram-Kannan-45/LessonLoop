import { Check, CircleAlert } from 'lucide-react'
import type { Attempt, RubricCheck, Source } from '../lib/workspace'

export function QualityReport({ attempt, rubric, sources }: { attempt: Attempt; rubric: RubricCheck[]; sources: Source[] }) {
  const checks = attempt.evaluation || []
  const count = checks.filter(check => check.passed).length
  return <div className="quality-report"><div className="report-summary"><div><h2>Draft {attempt.number} quality report</h2><p>Every mandatory check must pass. This count is informational.</p></div><strong>{count}<span> / {rubric.length}</span></strong></div>
    {!checks.length && <div className="inline-notice">Evaluation has not completed for this draft. It is not approved.</div>}
    {rubric.map(definition => { const check = checks.find(item => item.check_id === definition.id); return <details className={`check-detail ${check ? check.passed ? 'passed' : 'failed' : ''}`} key={definition.id} open={check?.passed === false}>
      <summary><span className="check-symbol">{check?.passed ? <Check size={15} /> : <CircleAlert size={15} />}</span><span><strong>{definition.name}</strong><small>{definition.id} · {definition.evaluator === 'code' ? 'Python validation' : 'Gemini evaluation'}</small></span><b>{check ? check.passed ? 'PASS' : 'FAIL' : 'PENDING'}</b></summary>
      <div className="check-body"><p><strong>Passing condition:</strong> {definition.pass}</p>{check && <><p>{check.reason}</p>{check.evidence_path && <p className="claim-list">Exact text selected from: {check.evidence_path}</p>}{check.evidence ? <blockquote>{check.evidence}</blockquote> : <p className="muted">Missing content; no quotation was invented.</p>}{check.required_change && <p className="requested-change"><strong>Requested correction:</strong> {check.required_change}</p>}{check.claim_ids.length > 0 && <p className="claim-list">Supporting claims: {check.claim_ids.join(', ')}</p>}</>}</div>
    </details> })}
    <p className="diagnostic-note">{attempt.diagnostics.word_count} words · {attempt.diagnostics.sentences_over_25_words} sentences over 25 words. Diagnostics do not decide educational quality.</p>
    <details className="reference-details"><summary>Inspect approved references</summary>{sources.map(source => <div key={source.id}><h4><a href={source.url} target="_blank" rel="noreferrer">{source.id} · {source.title}</a></h4>{source.notes.map(note => <p key={note.id}>{note.text} <small>({note.claim_ids.join(', ')})</small></p>)}</div>)}</details>
  </div>
}
