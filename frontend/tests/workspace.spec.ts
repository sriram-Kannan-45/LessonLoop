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

test('backend outage and unsupported-topic errors are actionable', async ({ page }) => {
  await mocks(page)
  await page.route('**/api/runs', route => route.fulfill({ status: 422, json: { status: 'error', error_code: 'UNSUPPORTED_TOPIC', message: 'Choose RAG or add a reviewed reference pack.' } }))
  await page.goto('/')
  await page.getByLabel('What would you like to learn?').fill('Organic chemistry')
  await page.getByRole('button', { name: 'Generate lesson' }).click()
  await expect(page.getByRole('alert')).toContainText('Choose RAG or add a reviewed reference pack.')
})
