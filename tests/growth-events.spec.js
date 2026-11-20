const { test, expect } = require('@playwright/test');
const fs = require('node:fs/promises');
const path = require('node:path');
const ROOT = path.resolve(__dirname, '..');
// Isolated local bytes at the production hostname, never a production form or
// GA request. This checks browser wiring, not GA4 receipt/DebugView.
test.beforeEach(async ({ context }) => {
  await context.route('**/*', async route => {
    const url = new URL(route.request().url());
    if (url.hostname !== 'marsharbel.com') return route.fulfill({ status: 200, contentType: 'application/javascript', body: '' });
    if (route.request().method() !== 'GET') throw new Error('Unexpected external effect in local growth test');
    let name = decodeURIComponent(url.pathname).replace(/^\/+/, '') || 'index.html';
    if (!path.extname(name)) name += '.html';
    const file = path.resolve(ROOT, name);
    if (!file.startsWith(ROOT + path.sep)) return route.abort();
    try {
      const body = await fs.readFile(file);
      const ext = path.extname(file);
      const type = { '.html': 'text/html', '.js': 'application/javascript', '.css': 'text/css', '.json': 'application/json', '.svg': 'image/svg+xml', '.jpg': 'image/jpeg', '.png': 'image/png', '.woff2': 'font/woff2' }[ext] || 'application/octet-stream';
      await route.fulfill({ body, contentType: type });
    } catch { await route.fulfill({ status: 404, body: '' }); }
  });
});
const events = page => page.evaluate(() => Array.from(window.dataLayer || []).filter(row => row[0] === 'event').map(row => [row[1], row[2]]));
test('local browser sends one sanitized native/copy event only after success', async ({ page }, info) => {
  await page.addInitScript(() => {
    Object.defineProperty(navigator, 'share', { value: async () => { if (window.shareFails) throw new DOMException('Cancelled', 'AbortError'); } });
    Object.defineProperty(navigator, 'clipboard', { value: { writeText: async () => {} } });
  });
  await page.goto('https://marsharbel.com/saint-charbel-prayers', { waitUntil: 'domcontentloaded' });
  await page.locator('.share-trigger').first().click();
  await page.locator('.share-native-row').first().click();
  await expect.poll(() => events(page)).toEqual([['share', { method: 'native' }]]);
  await page.evaluate(() => { window.shareFails = true; });
  await page.locator('.share-trigger').first().click();
  await page.locator('.share-native-row').first().click();
  await expect.poll(() => events(page)).toEqual([['share', { method: 'native' }]]);
  await page.locator('.share-trigger').first().click();
  await page.locator('.share-copy').first().click();
  await expect.poll(() => events(page)).toEqual([['share', { method: 'native' }], ['share', { method: 'copy' }]]);
  await page.screenshot({ path: 'output/playwright/g02-local-' + info.project.name + '.png' });
});
test('QA browser suppresses growth clicks without changing visible sharing', async ({ page }) => {
  await page.addInitScript(() => { window.__MARSHARBEL_QA__ = true; Object.defineProperty(navigator, 'clipboard', { value: { writeText: async () => {} } }); });
  await page.goto('https://marsharbel.com/saint-charbel-prayers', { waitUntil: 'domcontentloaded' });
  await page.locator('.share-trigger').first().click(); await page.locator('.share-copy').first().click();
  await expect(page.locator('.share-status').first()).toContainText('copied');
  expect(await events(page)).toEqual([]);
});
