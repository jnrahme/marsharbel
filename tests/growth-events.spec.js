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
for (const formType of ['daily-prayer', 'submit-testimony']) {
  test(`local ${formType} counts accepted once, rejects failure and duplicate in-flight submissions`, async ({ page }) => {
    await page.route('**/testimony-client.js*', route => route.fulfill({ contentType: 'application/javascript', body: `window.Testimony={configured:true,config:{supabaseUrl:'https://local-test.invalid',supabaseAnonKey:'mock',submissionsEnabled:true},status:(el,text)=>{el.textContent=text},captcha:async()=>({token:()=> 'local-token',reset:()=>{}})};` }));
    let calls = 0; let accepted = false;
    await page.route('https://local-test.invalid/**', async route => {
      calls++;
      await new Promise(resolve => setTimeout(resolve, 100));
      await route.fulfill({ status: accepted ? 202 : 503, contentType: 'application/json', body: JSON.stringify(accepted ? { accepted: true, reference: 'local-only' } : { message: 'Unavailable' }) });
    });
    await page.goto('https://marsharbel.com/' + formType, { waitUntil: 'domcontentloaded' });
    const daily = formType === 'daily-prayer';
    if (daily) await page.locator('[name=email]').fill('local-test@example.invalid');
    else {
      await page.locator('[name=display_name]').fill('Local test');
      await page.locator('[name=story]').fill('This is local synthetic test copy for a mocked response, never a real testimony.');
      for (const name of ['age_confirmed', 'consent_publish', 'ai_consent']) await page.locator(`[name=${name}]`).check();
    }
    const button = page.locator(daily ? '#subscribe-btn' : '#submit-testimony-btn');
    await expect(button).toBeEnabled();
    await page.locator('form').evaluate(form => { form.requestSubmit(); form.requestSubmit(); });
    await expect(page.locator('#submit-status')).toContainText('temporarily unavailable');
    expect(calls).toBe(1); expect(await events(page)).toEqual([]);
    accepted = true;
    await page.locator('form').evaluate(form => { form.requestSubmit(); form.requestSubmit(); });
    await expect(page.locator('#submit-status')).toContainText(daily ? 'Almost there' : 'pending review');
    expect(calls).toBe(2);
    expect(await events(page)).toEqual([[daily ? 'daily_prayer_signup' : 'testimony_submit', {}]]);
  });
}
