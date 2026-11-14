import { BookOpen, ExternalLink } from 'lucide-react'
import type { Lesson, Source } from '../lib/workspace'

export function LessonReader({ lesson, sources, approved }: { lesson: Lesson; sources: Source[]; approved: boolean }) {
  if (!lesson.learning_objectives || !lesson.worked_example || !lesson.practice_questions) return <div className="empty-state"><h3>Incomplete review draft</h3><p>This draft failed structure validation. Inspect its raw content in the audit report.</p><pre>{JSON.stringify(lesson, null, 2)}</pre></div>
  const example = lesson.worked_example
  return <article className="lesson-reader">
    {!approved && <div className="review-warning">REVIEW DRAFT · This draft has not passed every mandatory check.</div>}
    <div className="reader-kicker"><BookOpen size={15} />BEGINNER LESSON</div><h2>{lesson.title}</h2>
    <section className="objectives"><h3>What you will learn</h3><ul>{lesson.learning_objectives.map((item, i) => <li key={i}>{item}</li>)}</ul></section>
    <section><h3>Before you start</h3><p>{lesson.prerequisites}</p></section>
    <section><h3>What it is</h3><p>{lesson.what_it_is}</p></section>
    <section><h3>Why it matters</h3><p>{lesson.why_it_matters}</p></section>
    <section><h3>How it works</h3><ol className="process-steps">{lesson.how_it_works.map((item, i) => <li key={i}><span>{String(i + 1).padStart(2, '0')}</span><p>{item}</p></li>)}</ol></section>
    <section className="worked-example"><span className="reader-kicker">LET’S TRY AN EXAMPLE</span><h3>A question, a source, an answer</h3><p>{example.context}</p><h4>Your question</h4><p>{example.learner_question}</p><h4>The source passage</h4><blockquote>{example.source_passage}</blockquote><h4>What is retrieved and added</h4><p>{example.retrieved_information}</p><h4>The supported answer</h4><p>{example.supported_answer}</p><h4>When the information is missing</h4><p>{example.missing_information_question}</p><p>{example.missing_information_answer}</p></section>
    <section><h3>What to be careful about</h3><p>{lesson.limitations}</p></section>
    <section className="recap-box"><h3>A quick recap</h3><ul>{lesson.recap.map((item, i) => <li key={i}>{item}</li>)}</ul></section>
    <section><h3>Check your understanding</h3>{lesson.practice_questions.map((item, i) => <details className="practice" key={i}><summary>{i + 1}. {item.question}<span>Show answer</span></summary><p>{item.answer}</p></details>)}</section>
    <section className="reader-sources"><h3>Where these ideas come from</h3>{lesson.source_references.map(ref => { const source = sources.find(item => item.id === ref.source_id); return source ? <a key={source.id} href={source.url} target="_blank" rel="noreferrer">{source.title}<ExternalLink size={13} /></a> : <p key={ref.source_id}>Unknown source: {ref.source_id}</p> })}</section>
  </article>
}
