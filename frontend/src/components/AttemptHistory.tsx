import type { Run } from '../lib/workspace'
import { lessonText } from '../lib/text'

export function AttemptHistory({ run, onSelect }: { run: Run; onSelect: (number: number) => void }) {
  return <div className="attempt-history"><h2>Every draft has a history</h2><p className="muted">Earlier drafts and evaluator verdicts are preserved. Changes are checked against the next evaluation.</p>{run.attempts.map((attempt, index) => {
    const next = run.attempts[index + 1]
    const failures = attempt.evaluation?.filter(check => !check.passed) || []
    const before = lessonText(attempt.draft).split('\n').filter(Boolean)
    const after = next ? lessonText(next.draft).split('\n').filter(Boolean) : []
    const removed = before.filter(line => !after.includes(line))
    const added = after.filter(line => !before.includes(line))
    return <section className="attempt-block" key={attempt.id}><div className="attempt-block-title"><h3>Draft {attempt.number}</h3><span className={`status-pill ${attempt.status.toLowerCase()}`}>{attempt.status.replaceAll('_', ' ')}</span><button onClick={() => onSelect(attempt.number)}>Read this draft</button></div>
      {failures.length ? failures.map(check => <div className="failure-row" key={check.check_id}><strong>{check.check_id}</strong><p>{check.reason}</p><p>Requested: {check.required_change}</p>{next && <span className="next-verdict">Next evaluation: {next.evaluation?.find(item => item.check_id === check.check_id)?.passed === true ? 'PASS — targeted check passed' : next.evaluation ? 'Still failed or not evaluated' : 'Pending'}</span>}</div>) : <p>{attempt.evaluation ? 'No failed checks on this draft.' : 'Evaluation not completed.'}</p>}
      {attempt.original_draft && <details><summary>Development error injection audit</summary><p>The generated original is retained. The altered draft went to the evaluator without a demo label.</p><div className="draft-diff"><div><h4>Original limitation</h4><p>{attempt.original_draft.limitations}</p></div><div><h4>Altered limitation</h4><p>{attempt.draft.limitations}</p></div></div></details>}
      {next && <details><summary>Compare actual changes with draft {next.number}</summary><div className="draft-diff"><div><h4>Removed or changed</h4>{removed.map((line, i) => <p key={i}>{line}</p>)}</div><div><h4>Added or changed</h4>{added.map((line, i) => <p key={i}>{line}</p>)}</div></div><p className="muted">Paragraph comparison. A textual change alone does not establish correctness.</p></details>}
    </section>
  })}</div>
}
