import { useEffect, useState } from 'react'
import { FlaskConical, History, LoaderCircle, RotateCcw } from 'lucide-react'
import { workspaceApi, type Experiment, type Memory, type Workspace } from '../lib/workspace'

export function MemoryPanel({ memory, workspace, refresh }: { memory: Memory | null; workspace: Workspace | null; refresh: () => Promise<void> }) {
  const [category, setCategory] = useState('TERMS_EXPLAINED')
  const [experiment, setExperiment] = useState<Experiment | null>(null)
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const supports = memory?.failure_categories.find(item => item.category === category)?.independent_runs || 0
  useEffect(() => {
    if (!selectedId) return
    let stopped = false
    let timer: ReturnType<typeof setTimeout>
    async function poll() {
      try {
        const data = await workspaceApi.experiment(selectedId!)
        if (stopped) return
        setExperiment(data)
        if (data.status === 'RUNNING') timer = setTimeout(poll, 1800)
        else { setBusy(false); await refresh() }
      } catch (err) { if (!stopped) { setError(err instanceof Error ? err.message : 'Could not load the comparison.'); setBusy(false) } }
    }
    void poll()
    return () => { stopped = true; clearTimeout(timer) }
  }, [selectedId, refresh])
  async function start() {
    setBusy(true); setError('')
    try { const result = await workspaceApi.improve(category); setSelectedId(result.id) }
    catch (err) { setError(err instanceof Error ? err.message : 'Could not start the comparison.'); setBusy(false) }
  }
  async function rollback(version: string) {
    setBusy(true); setError('')
    try { await workspaceApi.rollback(version); await refresh() }
    catch (err) { setError(err instanceof Error ? err.message : 'Could not roll back.') }
    finally { setBusy(false) }
  }
  return <div className="memory-page"><div className="view-heading"><span className="reader-kicker">LEARNING ACROSS RUNS</span><h1>Better instructions need evidence<span>.</span></h1><p>History records what happened. Validated memory changes what the next lesson receives.</p></div>
    {error && <div className="error-banner" role="alert">{error}</div>}
    <div className="memory-grid"><section className="panel workspace-panel"><div className="panel-heading"><History size={18} /><h2>Repeated failure patterns</h2></div><p className="muted">At least two independent completed runs are needed. Three attempts in one run count once. Reviewed human feedback can support a category.</p>
      {!memory?.failure_categories.length ? <p className="empty-note">No failure observations yet. Run a lesson to begin collecting evidence.</p> : memory.failure_categories.map(item => <div className="category-row" key={item.category}><code>{item.category}</code><span>{item.independent_runs} independent {item.independent_runs === 1 ? 'run' : 'runs'}</span></div>)}
    </section><section className="panel workspace-panel"><div className="panel-heading"><FlaskConical size={18} /><h2>Test a prompt improvement</h2></div><p className="muted">Compare the current prompt with a candidate on the same normal assignment and targeted calibration scenario and fixed rubric. This makes four generations and {4 * (workspace?.evaluation_groups ?? 3)} focused evaluation calls, plus at most {workspace?.technical_retries ?? 2} technical retries per call.</p><label htmlFor="improvement-category">Target failure category</label><select id="improvement-category" value={category} onChange={e => setCategory(e.target.value)}>{workspace?.improvement_categories.map(item => <option key={item}>{item}</option>)}</select><p className="field-help">{supports} supporting independent runs · 2 required</p><button className="primary-button" onClick={start} disabled={busy || workspace?.busy || !workspace?.configured || supports < 2}>{busy ? <LoaderCircle className="spin" size={15} /> : <FlaskConical size={15} />}Compare prompts</button><p className="field-help">Activation needs a targeted improvement over baseline and no failed check that previously passed. No benefit means no activation.</p></section></div>
    <section className="panel workspace-panel"><div className="panel-heading"><h2>Reusable instructions</h2><span className="version-tag">{memory?.active_prompt_version || 'Loading'}</span></div><p className="muted">At most four relevant, validated instructions are loaded. Arbitrary feedback never enters active prompts.</p>{!memory?.instructions.length ? <p className="empty-note">No reusable instructions have been validated yet.</p> : memory.instructions.map(item => <article className="memory-instruction" key={item.id}><div><code>{item.category}</code><span className={`status-pill ${item.status}`}>{item.status.replaceAll('_', ' ')}</span></div><p>{item.instruction}</p><small>{item.origin}</small><p className="field-help">Supporting runs: {item.supporting_runs.map(id => <a key={id} href={`/?run=${id}`}>{id.slice(0, 8)} </a>)}</p></article>)}</section>
    <section className="panel workspace-panel"><h2>Comparison evidence</h2><div className="experiment-list">{!memory?.experiments.length && !experiment ? <p className="empty-note">A completed comparison will show both drafts, every verdict, and any regressions here.</p> : memory?.experiments.map(item => <button key={item.id} onClick={() => setSelectedId(item.id)} className="experiment-button"><span>{item.category}<small>{item.id.slice(0, 8)}</small></span><span className={`status-pill ${item.status.toLowerCase()}`}>{item.status.replaceAll('_', ' ')}</span></button>)}</div>
      {experiment && <div className="experiment-evidence"><h3>{experiment.status.replaceAll('_', ' ')} · {experiment.stage.replaceAll('_', ' ')}</h3><p className="muted">{experiment.baseline_prompt_version} → {experiment.candidate_prompt_version}</p>{experiment.error && <p role="alert">{experiment.error.message}</p>}{experiment.results.map(row => <details key={row.case_id}><summary>{row.case_id}</summary>{row.provider_comparison_valid === false && <p className="diagnostic-note">Providers or models differed across arms. This comparison cannot activate a candidate.</p>}<div className="comparison-arms">{(['baseline', 'candidate'] as const).map(arm => <div key={arm}><h4>{arm}</h4>{row[arm] ? <><p>{row[arm]!.approved ? 'Every check passed' : 'Not approved'}</p>{row[arm]!.checks.map(check => <p className={check.passed ? 'text-pass' : 'text-fail'} key={check.check_id}>{check.passed ? 'PASS' : 'FAIL'} · {check.check_id}<small>{check.reason}</small></p>)}<details><summary>Generated draft</summary><pre>{JSON.stringify(row[arm]!.draft, null, 2)}</pre></details></> : <p>Not completed</p>}</div>)}</div></details>)}<p className="diagnostic-note">A tiny comparison is limited evidence, not proof that a prompt works for every learner or topic.</p></div>}
    </section>
    <section className="panel workspace-panel"><h2>Prompt versions and rollback</h2>{memory?.prompt_versions.map(prompt => { const validated = prompt.version === 'generator-v1' || memory.experiments.some(item => item.candidate_prompt_version === prompt.version && item.status === 'ACTIVATED'); return <div className="prompt-row" key={prompt.version}><div><code>{prompt.version}</code><small>{prompt.active ? 'Current active version' : validated ? 'Previously validated version' : 'Inactive candidate'}</small></div>{!prompt.active && validated && <button className="secondary-button" disabled={busy || workspace?.busy} onClick={() => rollback(prompt.version)}><RotateCcw size={13} />Restore version</button>}</div> })}</section>
  </div>
}
