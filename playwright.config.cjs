const { defineConfig, devices } = require('@playwright/test');
const port = Number(process.env.PORT || 4173);
const baseURL = process.env.BASE_URL || `http://127.0.0.1:${port}`;

module.exports = defineConfig({
  testDir: './tests',
  timeout: 30_000,
  expect: { timeout: 5_000 },
  fullyParallel: true,
  forbidOnly: Boolean(process.env.CI),
  retries: process.env.CI ? 1 : 0,
  workers: process.env.CI ? 2 : undefined,
  reporter: process.env.CI ? [['line'], ['html', { open: 'never' }]] : 'list',
  use: {
    baseURL,
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure'
  },
  webServer: {
    command: `node scripts/dev-server.mjs --port=${port}`,
    url: baseURL,
    reuseExistingServer: !process.env.CI
  },
  projects: [
    { name: 'small-phone', use: { ...devices['iPhone SE'], browserName: 'chromium' } },
    { name: 'phone', use: { ...devices['iPhone 13'], browserName: 'chromium' } },
    { name: 'tablet', use: { ...devices['iPad (gen 7)'], browserName: 'chromium' } },
    { name: 'laptop', use: { viewport: { width: 1366, height: 768 } } },
    { name: 'wide-desktop', use: { viewport: { width: 1920, height: 1080 } } }
  ]
});
