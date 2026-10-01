// Staged WCAG 2.2 AA sweep over every public sitemap URL. Batches are added
// one locale group at a time; the hand-picked keyboard gate lives in
// accessibility-gate.spec.js. Phone only, offline, any axe violation fails.
const fs = require('fs');
const path = require('path');
const { test, expect } = require('@playwright/test');
const AxeBuilder = require('@axe-core/playwright').default;

const LOCALES = ['ar', 'de', 'en', 'es', 'fr', 'it', 'pl', 'pt'];
const BATCHES = ['root']; // add 'ar', 'fr', 'es', ... as each group is cleaned
const sitemap = fs.readFileSync(path.join(__dirname, '..', 'sitemap.xml'), 'utf8');
const urls = [...sitemap.matchAll(/<loc>https:\/\/marsharbel\.com([^<]*)<\/loc>/g)].map(m => m[1] || '/');
const group = url => LOCALES.find(code => url === `/${code}` || url.startsWith(`/${code}/`)) || 'root';
const gatePages = fs.readFileSync(path.join(__dirname, 'accessibility-gate.spec.js'), 'utf8');
const covered = url => gatePages.includes(`'${url}'`);

for (const url of urls.filter(u => BATCHES.includes(group(u)) && !covered(u))) {
  test(`axe ${url}`, async ({ page }, info) => {
    test.skip(info.project.name !== 'phone', 'phone project covers the sweep');
    await page.route(u => !['127.0.0.1', 'localhost'].includes(new URL(u).hostname), route => route.abort());
    await page.emulateMedia({ reducedMotion: 'reduce' });
    const response = await page.goto(url, { waitUntil: 'load' });
    expect(response?.ok(), `HTTP failure for ${url}`).toBeTruthy();
    await page.waitForTimeout(300);
    const results = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa', 'best-practice'])
      .analyze();
    expect(results.violations.map(v => `${v.id} (${v.impact}): ${v.nodes.slice(0, 3).map(n => n.target.join(' ')).join(' | ')}`),
      `Accessibility violations on ${url}`).toEqual([]);
  });
}
