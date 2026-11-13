import { test, expect, type Page } from '@playwright/test'

const health = { status: 'ok', app: 'LessonLoop', environment: 'development' }
const configured = {
  gemini: { configured: true, model: 'gemini-test-model' },
}

async function mockSetup(page: Page, options: { configured?: boolean; slow?: boolean } = {}) {
  await page.route('**/api/health', async route => {
    if (options.slow) await new Promise(resolve => setTimeout(resolve, 500))
    await route.fulfill({ json: health })
  })
  await page.route('**/api/providers/status', route => route.fulfill({ json: options.configured ? configured : {
    gemini: { configured: false, model: 'gemini-test-model' },
  } }))
}

test('loads safely, never calls paid checks automatically, and fits the viewport', async ({ page }, testInfo) => {
  let paidCalls = 0
  await page.route('**/api/providers/*/check', route => { paidCalls++; return route.abort() })
  await mockSetup(page, { slow: true })
  await page.goto('/')
  await expect(page.getByRole('status').filter({ hasText: 'Checking' })).toBeVisible()
  await expect(page.getByRole('status').filter({ hasText: 'Connected' })).toBeVisible()
  await expect(page.getByText('Not configured', { exact: true })).toHaveCount(1)
  await expect(page.getByRole('button', { name: 'Test Gemini connection' })).toBeDisabled()
  await expect(page.getByRole('heading', { name: 'OpenAI', exact: true })).toHaveCount(0)
  expect(paidCalls).toBe(0)
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true)
  await page.screenshot({ path: `../artifacts/setup-${testInfo.project.name}.png`, fullPage: true })
})

test('backend outage is actionable and can be retried', async ({ page }, testInfo) => {
  await page.route('**/api/**', route => route.abort())
  await page.goto('/')
  await expect(page.getByText('Unavailable', { exact: true })).toBeVisible()
  await expect(page.getByRole('alert')).toContainText('Start it in a separate terminal')
  await expect(page.getByRole('button', { name: 'Test Gemini connection' })).toBeDisabled()
  await page.screenshot({ path: `../artifacts/unavailable-${testInfo.project.name}.png`, fullPage: true })
  await page.unroute('**/api/**')
  await mockSetup(page)
  await page.getByRole('button', { name: 'Check backend' }).click()
  await expect(page.getByRole('status').filter({ hasText: 'Connected' })).toBeVisible()
})

test('configured and verified are separate; manual checks show real response fields', async ({ page }, testInfo) => {
  await mockSetup(page, { configured: true })
  let calls = 0
  await page.route('**/api/providers/*/check', async route => {
    calls++
    const provider = 'gemini'
    await new Promise(resolve => setTimeout(resolve, 350))
    await route.fulfill({ json: { provider, status: 'success', model: `${provider}-test-model`, message: `${provider} mocked connection OK.`, latency_ms: 250, checked_at: '2026-11-13T10:00:00Z' } })
  })
  await page.goto('/')
  await expect(page.getByText('Ready to test', { exact: true })).toHaveCount(1)
  expect(calls).toBe(0)
  const geminiButton = page.getByRole('button', { name: 'Test Gemini connection' })
  await geminiButton.click()
  await expect(geminiButton).toBeDisabled()
  await expect(page.getByText('gemini mocked connection OK.')).toBeVisible()
  await expect(page.getByText(/250 ms/)).toBeVisible()
  await expect(page.getByRole('progressbar')).toHaveAttribute('aria-valuenow', '2')
  expect(calls).toBe(1)
  await page.screenshot({ path: `../artifacts/results-${testInfo.project.name}.png`, fullPage: true })
})

test('a failed provider check shows the backend message and allows retry', async ({ page }) => {
  await mockSetup(page, { configured: true })
  await page.route('**/api/providers/gemini/check', route => route.fulfill({ status: 429, json: {
    provider: 'gemini', status: 'error', error_code: 'RATE_LIMIT_OR_QUOTA', message: 'Check your API quota and billing before retrying.',
  } }))
  await page.goto('/')
  const button = page.getByRole('button', { name: 'Test Gemini connection' })
  await button.click()
  await expect(page.getByText('Check failed', { exact: true })).toBeVisible()
  await expect(page.getByText('Check your API quota and billing before retrying.')).toBeVisible()
  await expect(button).toBeEnabled()
  await expect(button).toHaveText('Test again')
})

test('the real local backend serves health and configuration without inference', async ({ page, request }, testInfo) => {
  const response = await request.get('http://127.0.0.1:8000/api/health')
  expect(response.ok()).toBe(true)
  expect(await response.json()).toMatchObject(health)
  const status = await request.get('http://127.0.0.1:8000/api/providers/status')
  expect(Object.keys(await status.json())).toEqual(['gemini'])
  const failures: string[] = []
  page.on('pageerror', error => failures.push(error.message))
  await page.goto('/')
  await expect(page.getByRole('status').filter({ hasText: 'Connected' })).toBeVisible()
  expect(failures).toEqual([])
  await page.screenshot({ path: `../artifacts/live-${testInfo.project.name}.png`, fullPage: true })
})

test('changing provider configuration clears the old verification', async ({ page }) => {
  await mockSetup(page, { configured: true })
  await page.route('**/api/providers/gemini/check', route => route.fulfill({ json: {
    provider: 'gemini', status: 'success', model: 'gemini-test-model', message: 'Verified old model.', latency_ms: 150, checked_at: '2026-11-13T10:00:00Z',
  } }))
  await page.goto('/')
  await page.getByRole('button', { name: 'Test Gemini connection' }).click()
  await expect(page.getByText('Verified old model.')).toBeVisible()
  await page.route('**/api/providers/status', route => route.fulfill({ json: {
    ...configured, gemini: { configured: true, model: 'new-model' },
  } }))
  await page.getByRole('button', { name: 'Check backend' }).click()
  await expect(page.getByText('new-model', { exact: true })).toBeVisible()
  await expect(page.getByText('Verified old model.')).toHaveCount(0)
  await expect(page.getByRole('progressbar')).toHaveAttribute('aria-valuenow', '1')
})
