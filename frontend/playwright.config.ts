import { defineConfig, devices } from '@playwright/test'
import { mkdirSync } from 'node:fs'
import { fileURLToPath } from 'node:url'

// Keep browser profiles on the project's drive, including when the system drive is full.
const browserTemp = fileURLToPath(new URL('../.cache/browser-tmp', import.meta.url))
mkdirSync(browserTemp, { recursive: true })
process.env.TEMP = browserTemp
process.env.TMP = browserTemp
process.env.TMPDIR = browserTemp

export default defineConfig({
  testDir: './tests',
  fullyParallel: false,
  workers: 1,
  reporter: 'list',
  use: {
    baseURL: 'http://localhost:5173',
    channel: process.env.PLAYWRIGHT_CHANNEL || 'msedge',
    screenshot: 'only-on-failure',
  },
  projects: [
    { name: 'desktop', use: { ...devices['Desktop Chrome'], viewport: { width: 1440, height: 1100 } } },
    { name: 'mobile', use: { viewport: { width: 390, height: 844 }, isMobile: true, deviceScaleFactor: 1, hasTouch: true } },
  ],
  webServer: { command: 'npm run dev', url: 'http://localhost:5173', reuseExistingServer: !process.env.CI },
})
