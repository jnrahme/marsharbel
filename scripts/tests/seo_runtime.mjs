import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { chromium } from 'playwright';

const base = process.env.BASE_URL || 'http://127.0.0.1:4188';
const sitemap = await readFile(new URL('../../sitemap.xml', import.meta.url), 'utf8');
const urls = [...sitemap.matchAll(/<loc>(.*?)<\/loc>/g)].map(match => match[1]);
const browser = await chromium.launch({ headless: true });
try {
  const context = await browser.newContext({ serviceWorkers: 'block' });
  // These tests assert our metadata, independently of third-party availability.
  await context.route('**/*', route => new URL(route.request().url()).origin === new URL(base).origin
    ? route.continue() : route.abort());
  const page = await context.newPage();
  for (const canonical of urls) {
    const response = await page.goto(base + new URL(canonical).pathname, { waitUntil: 'load' });
    assert.equal(response.status(), 200, canonical);
    assert.equal(await page.locator('link[rel="canonical"]').getAttribute('href'), canonical);
    assert.equal(await page.locator('meta[property="og:url"]').getAttribute('content'), canonical);
    assert.ok(!(await page.locator('meta[name="robots"]').getAttribute('content')).includes('noindex'));
  }
  for (const path of ['/shop', '/shop-mockup', '/voice-lab', '/submit-testimony', '/testimony-review', '/souvenirs', '/account']) {
    await page.goto(base + path, { waitUntil: 'load' });
    assert.match(await page.locator('meta[name="robots"]').getAttribute('content'), /noindex/, path);
  }
  await page.goto(base + '/history?utm_source=test#timeline', { waitUntil: 'load' });
  assert.equal(await page.locator('link[rel="canonical"]').getAttribute('href'), 'https://marsharbel.com/history');
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto(base + '/', { waitUntil: 'load' });
  for (const dimensions of await page.locator('.promo-card img').evaluateAll(images => images.map(image => {
    const rect = image.getBoundingClientRect();
    return { width: rect.width, height: rect.height };
  }))) {
    assert.ok(Math.abs(dimensions.width / dimensions.height - 16 / 9) < 0.02, 'Promo previews retain their responsive aspect ratio');
  }
  const noJs = await browser.newContext({ javaScriptEnabled: false });
  const staticPage = await noJs.newPage();
  await staticPage.goto(base + '/', { waitUntil: 'load' });
  assert.equal(await staticPage.locator('h1').evaluate(el => getComputedStyle(el).opacity), '1');
  assert.ok(await staticPage.locator('h1').isVisible());
  for (const [path, lang, dir] of [['/', 'en', null], ['/fr', 'fr', 'ltr'], ['/ar', 'ar', 'rtl']]) {
    await staticPage.goto(base + path, { waitUntil: 'load' });
    assert.equal(await staticPage.locator('html').getAttribute('lang'), lang);
    if (dir) assert.equal(await staticPage.locator('html').getAttribute('dir'), dir);
    for (const [alternate, target] of [['en', '/'], ['fr', '/fr'], ['ar', '/ar'], ['x-default', '/']]) {
      assert.equal(await staticPage.locator(`link[hreflang="${alternate}"]`).getAttribute('href'), `https://marsharbel.com${target}`);
    }
    assert.ok((await staticPage.locator('main').innerText()).length > 700, 'Localized content is available without JavaScript');
  }
  await page.goto(base + '/', { waitUntil: 'load' });
  await page.locator('#sc-language-select').selectOption('fr');
  await page.waitForURL(base + '/fr');
  await page.getByRole('link', { name: 'English', exact: true }).click();
  await page.waitForURL(base + '/?lang=en');
  assert.equal(await page.locator('#sc-language-select').inputValue(), 'en');
  await noJs.close();
  console.log(`SEO runtime passed: ${urls.length} public pages, 7 noindex pages, and tracking parameters.`);
} finally {
  await browser.close();
}
