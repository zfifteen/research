/**
 * Playwright config for cross-browser determinism evidence.
 * Runs the determinism corpus across Chromium, Firefox, and WebKit.
 *
 * Usage:
 *   npx playwright test --config=playwright.determinism.config.ts
 */
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  testMatch: 'determinism-evidence.spec.ts',
  fullyParallel: false, // sequential for deterministic report generation
  retries: 0,
  workers: 1,
  reporter: [['html', { open: 'never' }], ['json', { outputFile: 'evidence/playwright-report.json' }]],
  use: {
    baseURL: 'http://localhost:4173',
    trace: 'off',
  },
  webServer: {
    command: 'npx pnpm@9 preview',
    url: 'http://localhost:4173',
    reuseExistingServer: true,
    timeout: 30000,
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
  ],
});
