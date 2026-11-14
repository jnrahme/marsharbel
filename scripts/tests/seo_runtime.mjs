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
  let page = await context.newPage();
  for (const canonical of urls) {
    await page.close(); page = await context.newPage();
    const response = await page.goto(base + new URL(canonical).pathname, { waitUntil: 'load' });
    assert.equal(response.status(), 200, canonical);
    assert.equal(await page.locator('link[rel="canonical"]').getAttribute('href'), canonical);
    assert.equal(await page.locator('meta[property="og:url"]').getAttribute('content'), canonical);
    assert.ok(!(await page.locator('meta[name="robots"]').getAttribute('content')).includes('noindex'));
  }
  // Authored AR pages (#769): head-integrity invariant. An entity-escaped comment or
  // any stray text node in <head> triggers the HTML5 head-closing rule and the
  // canonical/og/hreflang tags silently parse into <body> (translate.js then injects
  // a duplicate canonical). Assert head ancestry in the LIVE DOM, not just counts.
  for (const path of ['/ar/rosary', '/ar/miracles/', '/ar/miracles/nohad-el-shami', '/ar/miracles/dafne-gutierrez', '/ar/miracles/raymond-nader']) {
    await page.close(); page = await context.newPage();
    const response = await page.goto(base + path, { waitUntil: 'load' });
    assert.equal(response.status(), 200, path);
    const audit = await page.evaluate(() => {
      const inHead = (el) => el && el.closest('head') !== null;
      const headText = [...document.head.childNodes]
        .filter((n) => n.nodeType === Node.TEXT_NODE)
        .map((n) => n.textContent).join('').trim();
      return {
        headText,
        canonicals: [...document.querySelectorAll('link[rel="canonical"]')].map((el) => ({ inHead: inHead(el), href: el.getAttribute('href') })),
        alternates: [...document.querySelectorAll('link[rel="alternate"][hreflang]')].map((el) => inHead(el)),
        robots: inHead(document.querySelector('meta[name="robots"]')),
        title: inHead(document.querySelector('title')),
      };
    });
    assert.equal(audit.headText, '', `${path}: stray text node in <head>`);
    assert.equal(audit.canonicals.length, 1, `${path}: expected exactly one canonical, got ${JSON.stringify(audit.canonicals)}`);
    assert.ok(audit.canonicals[0].inHead, `${path}: canonical outside <head>`);
    assert.ok(audit.alternates.length > 0 && audit.alternates.every(Boolean), `${path}: hreflang alternates missing from <head>`);
    assert.ok(audit.robots, `${path}: robots meta outside <head>`);
    assert.ok(audit.title, `${path}: title outside <head>`);
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
  for (const [path, lang, dir] of [['/', 'en', null], ['/fr/', 'fr', 'ltr'], ['/ar/', 'ar', 'rtl']]) {
    await staticPage.goto(base + path, { waitUntil: 'load' });
    assert.equal(await staticPage.locator('html').getAttribute('lang'), lang);
    if (dir) assert.equal(await staticPage.locator('html').getAttribute('dir'), dir);
    for (const [alternate, target] of [['en', '/'], ['fr', '/fr/'], ['ar', '/ar/'], ['x-default', '/']]) {
      assert.equal(await staticPage.locator(`link[hreflang="${alternate}"]`).getAttribute('href'), `https://marsharbel.com${target}`);
    }
    assert.ok((await staticPage.locator('main').innerText()).length > 700, 'Localized content is available without JavaScript');
  }
  await page.goto(base + '/', { waitUntil: 'load' });
  assert.equal(await page.locator('#sc-language-select option[value="fr"]').isDisabled(), false);
  assert.equal(await page.evaluate(() => SC_LANGUAGE_SWITCH.request('fr')), true);
  await page.waitForURL(base + '/fr/');
  assert.equal(await page.locator('html').getAttribute('lang'), 'fr');
  assert.equal(await page.locator('link[rel=canonical]').getAttribute('href'), 'https://marsharbel.com/fr/');
  assert.equal(await page.locator('#sc-language-select').inputValue(), 'fr');
  await noJs.close();
  console.log(`SEO runtime passed: ${urls.length} public pages, 7 noindex pages, and tracking parameters.`);
} finally {
  await browser.close();
}
