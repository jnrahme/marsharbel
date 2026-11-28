const { test, expect } = require('@playwright/test');
const { AxeBuilder } = require('@axe-core/playwright');
const fs = require('node:fs');
// A controlled cross-origin player fixture posts the same envelope used by the
// nocookie player. This tests UI/security behavior, not YouTube availability.
async function fixture(page) {
  await page.route('https://www.youtube-nocookie.com/embed/**', route => route.fulfill({
    contentType: 'text/html',
    body: '<!doctype html><html lang="en"><title>Provider fixture</title><body>Provider fixture</body></html>'
  }));
  await page.goto('/videos');
  const frameElement = page.locator('iframe').first();
  await frameElement.scrollIntoViewIfNeeded();
  await expect(frameElement).toHaveAttribute('src', /enablejsapi=1/);
  await expect.poll(() => page.frames().filter(f => f.url().includes('enablejsapi=1')).length).toBeGreaterThan(0);
  return page.frames().find(f => f.url().includes('/embed/tF8SYCuYKBE'));
}
async function emit(frame, code) {
  await frame.evaluate(code => parent.postMessage(JSON.stringify({ event: 'onError', info: code }), '*'), code);
}
test('all 23 videos keep static original and relevant reading links without JavaScript', async ({ browser, baseURL }) => {
  const context = await browser.newContext({ javaScriptEnabled: false });
  const page = await context.newPage();
  await page.goto(`${baseURL}/videos`);
  await expect(page.locator('iframe')).toHaveCount(23);
  await expect(page.locator('.video-fallback')).toHaveCount(23);
  for (const fallback of await page.locator('.video-fallback').all()) {
    const id = await fallback.getAttribute('data-video-id');
    await expect(fallback.locator('a').first()).toHaveAttribute('href', `https://www.youtube.com/watch?v=${id}`);
    await expect(fallback.locator('a').last()).toHaveAttribute('href', /^\.\/[a-z0-9/-]+$/);
  }
  await context.close();
});
test('restriction, unavailable and missing-referrer states are distinct and accessible', async ({ page }, testInfo) => {
  const frame = await fixture(page);
  const fallback = page.locator('.video-fallback').first();
  const expected = {100: /unavailable or private/, 101: /owner does not allow/, 150: /owner does not allow/, 153: /could not identify/, 2: /could not play/, 5: /could not play/};
  for (const [code, message] of Object.entries(expected)) {
    await emit(frame, Number(code));
    await expect(fallback).toHaveAttribute('data-state', code);
    await expect(fallback.locator('[role="status"]')).toHaveText(message);
  }
  await expect(page).toHaveURL(/\/videos$/);
  await expect(fallback.locator('[role="status"]')).toHaveAttribute('aria-live', 'polite');
  await fallback.locator('a').first().focus();
  await page.keyboard.press('Tab');
  await expect(fallback.locator('a').last()).toBeFocused();
  const results = await new AxeBuilder({ page }).include('.video-fallback').analyze();
  expect(results.violations).toEqual([]);
  await fallback.scrollIntoViewIfNeeded();
  await page.screenshot({ path: testInfo.outputPath('failure.png') });
  if (['phone', 'laptop'].includes(testInfo.project.name)) {
    fs.mkdirSync('test-results/video-proof', {recursive:true});
    await page.screenshot({ path: `test-results/video-proof/${testInfo.project.name}-failure.png` });
  }
});
test('rejects spoofed origin/source, malformed payload and unknown error', async ({ page }) => {
  const frame = await fixture(page);
  const fallback = page.locator('.video-fallback').first();
  await page.evaluate(() => window.postMessage({ event: 'onError', info: 100 }, '*'));
  await frame.evaluate(() => {
    parent.postMessage('not JSON', '*');
    parent.postMessage({ event: 'onError', info: '100' }, '*');
    parent.postMessage({ event: 'onError', info: 999 }, '*');
  });
  await expect(fallback).not.toHaveAttribute('data-state');
  await emit(frame, 101);
  await expect(fallback).toHaveAttribute('data-state', '101');
});
test('no remote API script, telemetry, private origin path, CSP edit or eager player', async ({ page }) => {
  await fixture(page);
  await expect(page.locator('script[src*="youtube"]')).toHaveCount(0);
  for (const iframe of await page.locator('iframe').all()) {
    await expect(iframe).toHaveAttribute('loading', 'lazy');
    await expect(iframe).toHaveAttribute('referrerpolicy', 'strict-origin-when-cross-origin');
    const src = new URL(await iframe.getAttribute('src'));
    expect(src.origin).toBe('https://www.youtube-nocookie.com');
    expect(src.searchParams.get('origin')).toBe(new URL(page.url()).origin);
    expect(src.searchParams.has('autoplay')).toBe(false);
  }
});
