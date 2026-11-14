import { test, expect, type Page } from '@playwright/test'
import { readFileSync } from 'node:fs'

const lesson = JSON.parse(readFileSync(new URL('../../backend/content/example_lesson.json', import.meta.url), 'utf8'))
const source = JSON.parse(readFileSync(new URL('../../backend/content/rag_sources.json', import.meta.url), 'utf8'))
const rubric = JSON.parse(readFileSync(new URL('../../backend/content/rubric.json', import.meta.url), 'utf8'))
const checks = rubric.checks.map((item: { id: string }) => ({ check_id: item.id, passed: true, evidence: lesson.title, reason: 'Mocked browser-test judgment.', required_change: '', claim_ids: [], missing_content: false }))
const workspace = { source_pack: source, rubric, learner_profile: 'India grade 12 beginner', generator_model: 'mocked-gemini', evaluator_model: 'mocked-gemini', provider_note: 'Gemini only', configured: true, busy: false, active_prompt_version: 'generator-v1', improvement_categories: ['TERMS_EXPLAINED'], demo_enabled: true }
const emptyMemory = { instructions: [], failure_categories: [], prompt_versions: [{ version: 'generator-v1', active: 1, memory_ids: [], instructions: 'Test prompt' }], experiments: [], active_prompt_version: 'generator-v1' }
function makeRun(status = 'APPROVED', drafts = 1, demo = false) {
  return { id: 'browser-test-run', topic: 'Introduction to RAG', learner_profile: 'india_beginner', status, stage: status, started_at: '2026-11-13T10:00:00Z', finished_at: '2026-11-13T10:01:00Z', source_pack_version: source.version, rubric_version: rubric.version, generator_prompt_version: 'generator-v1', evaluator_prompt_version: 'evaluator-v1', generator_model: 'mocked-gemini', evaluator_model: 'mocked-gemini', attempt_count: drafts, selected_memory: [], retry_count: drafts - 1, demo_error: Number(demo), error: status === 'ERROR' ? { code: 'TIMEOUT', message: 'The provider timed out. No lesson was approved.' } : null, feedback: [], final_lesson: status === 'APPROVED' ? lesson : null, review_draft: status === 'APPROVED' ? null : lesson,
    attempts: Array.from({ length: drafts }, (_, i) => ({ id: i + 1, number: i + 1, created_at: '2026-11-13T10:00:00Z', draft: demo && i === 0 ? { ...lesson, limitations: 'RAG guarantees that the AI answer is always correct.' } : lesson, original_draft: demo && i === 0 ? lesson : null, evaluation: checks.map((check: { check_id: string }) => (i < drafts - 1 || status === 'NEEDS_REVIEW') && check.check_id === 'HONEST_LIMITATIONS' ? { ...check, passed: false, evidence: 'RAG guarantees that the AI answer is always correct.', reason: 'A false promise of correctness.', required_change: 'Explain that RAG can still make mistakes.' } : check), status: i === drafts - 1 && status === 'APPROVED' ? 'APPROVED' : 'REJECTED', diagnostics: { word_count: 900, sentences_over_25_words: 2, note: 'Diagnostics only' }, generation_usage: {}, evaluator_usage: {} })) }
}

async function mocks(page: Page, selected = makeRun()) {
  await page.route('**/api/**', async route => {
    const url = new URL(route.request().url())
    const path = url.pathname
    if (path.endsWith('/workspace')) return route.fulfill({ json: workspace })
    if (path.endsWith('/memory')) return route.fulfill({ json: emptyMemory })
    if (path === '/api/runs' && route.request().method() === 'GET') return route.fulfill({ json: { items: [selected], total: 1, limit: 10, offset: 0 } })
    if (path === '/api/runs' && route.request().method() === 'POST') return route.fulfill({ status: 202, json: { id: selected.id, status: 'RUNNING' } })
    if (path.endsWith('/events')) return route.fulfill({ json: { events: [{ sequence: 1, stage: selected.status, message: 'Mocked event from backend fixture.', created_at: selected.started_at, details: {} }], next_cursor: 1 } })
    if (path.endsWith('/export')) return route.fulfill({ contentType: 'text/markdown', headers: { 'Content-Disposition': 'attachment; filename="lesson.md"' }, body: '# Lesson\n\n' + (selected.status === 'APPROVED' ? 'Approved lesson' : 'Review draft — NOT APPROVED') })
    if (path.endsWith('/feedback')) return route.fulfill({ status: 201, json: { id: 'feedback-1', status: 'unverified', message: 'Saved as an unverified observation.' } })
    if (path === '/api/runs/' + selected.id) return route.fulfill({ json: selected })
    return route.abort()
  })
}

test('creates a lesson, reads practice answers, quality report, and downloads an approved export', async ({ page }, testInfo) => {
  await mocks(page)
  let submitted = 0
  page.on('request', request => { if (request.method() === 'POST' && request.url().endsWith('/runs')) submitted++ })
  await page.goto('/')
  await expect(page.getByRole('heading', { name: 'A lesson worth understanding.' })).toBeVisible()
  expect(submitted).toBe(0)
  await page.getByRole('button', { name: 'Generate lesson' }).click()
  await expect(page.getByRole('heading', { name: lesson.title, exact: true })).toBeVisible()
  expect(submitted).toBe(1)
  await page.getByText('2. Does looking up a new notice automatically retrain the language model?').click()
  await expect(page.getByText(lesson.practice_questions[1].answer, { exact: true })).toBeVisible()
  await page.getByRole('tab', { name: 'Quality report' }).click()
  await expect(page.getByRole('heading', { name: 'Draft 1 quality report' })).toBeVisible()
  await expect(page.getByText('PASS', { exact: true })).toHaveCount(14)
  const downloadPromise = page.waitForEvent('download')
  await page.getByRole('link', { name: 'Approved lesson', exact: true }).click()
  const download = await downloadPromise
  await download.saveAs(`../artifacts/download-${testInfo.project.name}.md`)
  expect(readFileSync((await download.path())!, 'utf8')).toContain('Approved lesson')
  await page.getByRole('tab', { name: 'Lesson', exact: true }).click()
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true)
  await page.screenshot({ path: `../artifacts/product-reader-${testInfo.project.name}.png`, fullPage: true })
})

test('error injection is inspectable and actual next-verdict results are shown', async ({ page }) => {
  const run = makeRun('APPROVED', 2, true)
  await mocks(page, run)
  await page.goto('/?run=browser-test-run')
  await expect(page.getByText('DELIBERATE-ERROR DEMONSTRATION', { exact: true })).toBeVisible()
  await page.getByRole('tab', { name: 'Attempts' }).click()
  await expect(page.getByText('A false promise of correctness.', { exact: true })).toBeVisible()
  await expect(page.getByText('Next evaluation: PASS — targeted check passed')).toBeVisible()
  await page.getByText('Development error injection audit', { exact: true }).click()
  await expect(page.getByRole('heading', { name: 'Altered limitation' })).toBeVisible()
  await page.getByText('Compare actual changes with draft 2', { exact: true }).click()
  await expect(page.getByRole('heading', { name: 'Added or changed' })).toBeVisible()
})

test('needs-review drafts are clearly labelled and cannot download as approved', async ({ page }) => {
  await mocks(page, makeRun('NEEDS_REVIEW', 3))
  await page.goto('/?run=browser-test-run')
  await expect(page.getByText('No lesson was released.', { exact: false })).toBeVisible()
  await expect(page.getByText('REVIEW DRAFT · This draft has not passed every mandatory check.')).toBeVisible()
  await expect(page.getByRole('link', { name: 'Approved lesson', exact: true })).toHaveCount(0)
  await expect(page.getByRole('link', { name: 'Review draft', exact: true })).toBeVisible()
})

test('provider failure stays unapproved and history is retrievable after refresh', async ({ page }) => {
  await mocks(page, makeRun('ERROR', 0))
  await page.goto('/?run=browser-test-run')
  await expect(page.getByText('The provider timed out. No lesson was approved.')).toBeVisible()
  await page.reload()
  await expect(page.getByText('The provider timed out. No lesson was approved.')).toBeVisible()
  await page.getByRole('button', { name: 'Run history', exact: true }).click()
  await expect(page.getByRole('heading', { name: 'Your lesson history.' })).toBeVisible()
  await expect(page.getByText('browser-', { exact: true })).toBeVisible()
})

test('a temporary Gemini outage can be retried explicitly without changing failed history', async ({ page }) => {
  const failed = { ...makeRun('ERROR', 0, true), error: { code: 'PROVIDER_FAILURE', message: 'The provider request failed.', diagnostics: { provider_http_status: 503 } } }
  await mocks(page, failed)
  let posts = 0
  await page.route('**/api/runs', async route => {
    if (route.request().method() !== 'POST') return route.fallback()
    posts++
    expect(route.request().postDataJSON()).toMatchObject({ topic: failed.topic, demo_error: true })
    return route.fulfill({ status: 202, json: { id: 'recovered-run', status: 'RUNNING' } })
  })
  await page.route('**/api/runs/recovered-run', route => route.fulfill({ json: { ...makeRun(), id: 'recovered-run' } }))
  await page.goto('/?run=browser-test-run')
  await expect(page.getByRole('alert')).toContainText('Gemini is temporarily busy or unavailable (HTTP 503)')
  expect(posts).toBe(0)
  await page.getByRole('button', { name: 'Try again', exact: true }).click()
  await expect(page).toHaveURL(/run=recovered-run/)
  await expect(page.getByRole('heading', { name: 'Lesson approved' })).toBeVisible()
  expect(posts).toBe(1)
  await expect(page.getByLabel('Inject a factual error into the first draft')).toBeChecked()
  await page.goto('/?run=browser-test-run')
  await expect(page.getByRole('alert')).toContainText('HTTP 503')
  expect(posts).toBe(1)
})


test('quota fallback shows backup readiness and the actual saved providers', async ({ page }, testInfo) => {
  const fallbackRun = { ...makeRun(), attempts: makeRun().attempts.map(attempt => ({ ...attempt,
    generation_usage: { provider: 'gemini', model: 'mocked-generator', fallback: false },
    evaluator_usage: { group_usage: [{ provider: 'groq', model: 'qwen/qwen3.8-27b', fallback: true }] } })) }
  await mocks(page, fallbackRun)
  await page.route('**/api/workspace', route => route.fulfill({ json: { ...workspace,
    fallback: { provider: 'groq', enabled: true, configured: true, generator_model: 'qwen/qwen3.8-27b', evaluator_model: 'qwen/qwen3.8-27b', min_interval_seconds: 65 } } }))
  await page.goto('/?run=browser-test-run')
  await expect(page.getByText('Configured for Gemini quota fallback', { exact: true })).toBeVisible()
  const trace = page.getByLabel('Actual providers for draft 1')
  await expect(trace).toContainText('Generated by gemini · mocked-generator')
  await expect(trace).toContainText('Evaluated by groq · qwen/qwen3.8-27b')
  await expect(trace).toContainText('Groq quota fallback used')
  await page.getByRole('tab', { name: 'Attempts', exact: true }).click()
  await expect(page.getByLabel('Actual providers for draft 1')).toHaveCount(2)
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true)
  await page.screenshot({ path: `../artifacts/groq-fallback-${testInfo.project.name}.png`, fullPage: true })
})


test('a missing backup key is visible without blocking healthy Gemini use', async ({ page }) => {
  await mocks(page)
  await page.route('**/api/workspace', route => route.fulfill({ json: { ...workspace,
    fallback: { provider: 'groq', enabled: true, configured: false, generator_model: 'qwen/qwen3.8-27b', evaluator_model: 'qwen/qwen3.8-27b', min_interval_seconds: 65 } } }))
  await page.goto('/')
  await expect(page.getByText('Add GROQ_API_KEY in backend/.env', { exact: true })).toBeVisible()
  await expect(page.getByRole('button', { name: 'Generate lesson', exact: true })).toBeEnabled()
})


test('feedback stays unverified and memory has honest empty states', async ({ page }) => {
  await mocks(page)
  await page.goto('/?run=browser-test-run')
  await page.getByRole('tab', { name: 'Feedback' }).click()
  await page.getByLabel('Your feedback', { exact: true }).fill('Please explain the word index more clearly.')
  await page.getByRole('button', { name: 'Save feedback' }).click()
  await expect(page.getByText('Saved as an unverified observation.', { exact: true })).toBeVisible()
  await page.getByRole('button', { name: 'Memory & learning', exact: true }).click()
  await expect(page.getByText('No reusable instructions have been validated yet.')).toBeVisible()
  await expect(page.getByRole('button', { name: 'Compare prompts' })).toBeDisabled()
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true)
})

test('reference failures are actionable without a subject whitelist', async ({ page }) => {
  const failed = { ...makeRun('ERROR', 0), error: { code: 'REFERENCES_UNAVAILABLE', message: 'Topic references could not be retrieved. Check your connection and try again.' } }
  await mocks(page, failed)
  await page.goto('/')
  await page.getByLabel('What would you like to learn?').fill('Organic chemistry')
  await expect(page.getByLabel('Topic references')).toHaveValue('auto')
  await page.getByRole('button', { name: 'Generate lesson' }).click()
  await expect(page.getByRole('alert')).toContainText('Topic references could not be retrieved.')
})


for (const topic of ['Photosynthesis', 'Python programming']) {
  test(`creates ${topic} with automatic references and reads its own saved rubric`, async ({ page }) => {
    const dynamicLesson = { ...lesson, title: `Introduction to ${topic}` }
    const definitions = [{ id: 'STRUCTURE', name: 'Complete lesson structure', evaluator: 'code', pass: 'All sections present.' },
      { id: 'SOURCES', name: 'Topic references', evaluator: 'code', pass: 'References match.' },
      { id: 'TOPIC_DEFINITION', name: `Accurate introduction to ${topic}`, evaluator: 'model', pass: 'The subject is explained correctly.' }]
    const dynamicSource = { id: 'S1', title: `${topic} reference`, url: 'https://en.wikipedia.org/wiki/Test', accessed_at: '2026-11-14', notes: [{ id: 'N1', text: `Authored ${topic} browser-test reference.`, claim_ids: ['T01'] }] }
    const run = { ...makeRun(), topic, final_lesson: dynamicLesson,
      source_snapshot: { id: 'auto', sources: [dynamicSource] }, rubric_snapshot: { version: 'mocked-topic-rubric', checks: definitions },
      attempts: makeRun().attempts.map(attempt => ({ ...attempt, draft: dynamicLesson, evaluation: definitions.map(item => ({ ...checks[0], check_id: item.id, evidence: dynamicLesson.title })) })) }
    await mocks(page, run)
    await page.route('**/api/runs', async route => {
      if (route.request().method() !== 'POST') return route.fallback()
      expect(route.request().postDataJSON()).toMatchObject({ topic, reference_pack_id: 'auto' })
      return route.fulfill({ status: 202, json: { id: run.id, status: 'RUNNING' } })
    })
    await page.goto('/')
    await page.getByLabel('What would you like to learn?').fill(topic)
    await page.getByRole('button', { name: 'Generate lesson' }).click()
    await expect(page.getByRole('heading', { name: dynamicLesson.title, exact: true })).toBeVisible()
    await page.getByRole('tab', { name: 'Quality report', exact: true }).click()
    await expect(page.getByText(`Accurate introduction to ${topic}`, { exact: true })).toBeVisible()
    await expect(page.getByText('Correct RAG definition', { exact: true })).toHaveCount(0)
    await page.getByText('Inspect lesson references', { exact: true }).click()
    await expect(page.getByRole('link', { name: `S1 · ${topic} reference` })).toBeVisible()
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true)
  })
}


test('keeps API wait, draft status and demonstration warning visible until the run finishes', async ({ page }) => {
  const run = makeRun('RUNNING', 2, true)
  run.stage = 'PROVIDER_WAIT'
  run.started_at = new Date().toISOString()
  await mocks(page, run)
  const created = new Date().toISOString()
  await page.route('**/api/runs/*/events*', route => route.fulfill({ json: { events: [{ sequence: 2, stage: 'PROVIDER_WAIT', message: 'Waiting for allowance.', created_at: created, details: { wait_seconds: 65 } }], next_cursor: 2 } }))
  await page.goto('/?run=browser-test-run')
  const activity = page.getByLabel('Current run status')
  await expect(activity).toContainText('RUNNING · Draft 2 of 3')
  const topic = page.getByLabel('What would you like to learn?')
  await expect(topic).toBeEditable()
  await topic.fill('Performance testing')
  await expect(topic).toHaveValue('Performance testing')
  await expect(page.getByRole('button', { name: 'Lesson in progress', exact: true })).toBeDisabled()
  await expect(activity).toContainText('Groq API allowance wait')
  await expect(activity).toContainText('Error demonstration is ON')
  const timer = activity.getByRole('timer')
  await expect(timer).toContainText('Next request in about')
  const first = await timer.textContent()
  await expect.poll(() => timer.textContent()).not.toBe(first)
  await page.locator('.lesson-reader').scrollIntoViewIfNeeded()
  await expect(activity).toBeInViewport()
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true)
  run.status = 'APPROVED'; run.stage = 'APPROVED'
  await expect(activity).toContainText('Finished. Every mandatory check passed')
  await expect(timer).toHaveCount(0)
})
