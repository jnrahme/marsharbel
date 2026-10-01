// WCAG 2.2 AA gate. Any axe violation (any impact) fails. Runs once on a phone
// and once on a desktop project; the other projects add no new coverage.
const { test, expect } = require('@playwright/test');
const AxeBuilder = require('@axe-core/playwright').default;

const pages = ['/', '/story', '/history', '/stories', '/saints', '/prayer-library', '/saint-charbel-prayers',
  '/saint-charbel-novena', '/litany-of-saint-charbel', '/saint-charbel-prayer-for-healing', '/saint-charbel-feast-day',
  '/rosary-intro', '/mystery-meditation', '/gallery', '/news', '/videos', '/miracles/', '/testimonies', '/submit-testimony',
  '/visit-annaya', '/st-rafqa', '/pio-story', '/privacy-policy', '/terms-of-service', '/accessibility',
  '/ar/', '/ar/prayers', '/ar/novena', '/fr/', '/es/'];
const rtl = path => path.startsWith('/ar/');

for (const path of pages) {
  test(`a11y gate ${path}`, async ({ page }, info) => {
    test.skip(!['phone', 'laptop'].includes(info.project.name), 'phone and laptop cover the gate');
    // Keep the gate offline so it never reaches analytics or third-party hosts.
    await page.route(url => !['127.0.0.1', 'localhost'].includes(new URL(url).hostname), route => route.abort());
    // Scroll-reveal fades are mid-transition when axe samples colors; reduced motion shows final colors.
    await page.emulateMedia({ reducedMotion: 'reduce' });
    const response = await page.goto(path, { waitUntil: 'load' });
    await page.waitForTimeout(300);
    expect(response?.ok(), `HTTP failure for ${path}`).toBeTruthy();

    const results = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa', 'best-practice'])
      .exclude('iframe[src*="youtube"]')
      .analyze();
    expect(results.violations.map(v => `${v.id} (${v.impact}): ${v.nodes.slice(0, 3).map(n => n.target.join(' ')).join(' | ')}`),
      `Accessibility violations on ${path}`).toEqual([]);

    const basics = await page.evaluate(() => ({
      lang: document.documentElement.lang,
      dir: getComputedStyle(document.documentElement).direction,
      mains: document.querySelectorAll('main').length,
      blocksZoom: /user-scalable\s*=\s*(no|0)|maximum-scale\s*=\s*1(\.0)?(?![\d.])/.test(document.querySelector('meta[name=viewport]')?.content || '')
    }));
    expect(basics.lang, `lang on ${path}`).toBeTruthy();
    expect(basics.dir, `direction on ${path}`).toBe(rtl(path) ? 'rtl' : 'ltr');
    expect(basics.mains, `main landmark on ${path}`).toBe(1);
    expect(basics.blocksZoom, `zoom blocked on ${path}`).toBe(false);

    // First keyboard stop is the skip link and it moves to the main region.
    await page.keyboard.press('Tab');
    await page.waitForTimeout(250);
    const first = await page.evaluate(() => {
      const el = document.activeElement;
      return { cls: el.className, href: el.getAttribute('href'), box: el.getBoundingClientRect().toJSON() };
    });
    expect(first.cls, `first Tab stop on ${path}`).toContain('skip-link');
    expect(first.box.top, `skip link visible on focus on ${path}`).toBeGreaterThanOrEqual(0);
    await page.keyboard.press('Enter');
    expect(await page.evaluate(() => location.hash), `skip link target on ${path}`).toBe(first.href);
    expect(await page.locator(first.href).count(), `skip target exists on ${path}`).toBe(1);
    // Focus must really move to the target, not only the URL hash.
    const moved = await page.evaluate(href => document.activeElement === document.querySelector(href), first.href);
    expect(moved, `focus moved to skip target on ${path}`).toBe(true);
    // The next Tab lands inside main, not back in the navigation.
    await page.keyboard.press('Tab');
    const next = await page.evaluate(href => {
      const el = document.activeElement;
      return { inMain: !!el.closest(href), tag: el.tagName, cls: String(el.className) };
    }, first.href);
    expect(next.inMain, `next Tab after skip stays inside main on ${path} (landed on ${next.tag}.${next.cls})`).toBe(true);
    // Content must not sit under the sticky header after the jump.
    await page.waitForTimeout(150);
    const clearance = await page.evaluate(href => {
      const header = document.querySelector('header');
      const bottom = header && ['sticky', 'fixed'].includes(getComputedStyle(header).position) ? header.getBoundingClientRect().bottom : 0;
      const heading = document.querySelector(`${href} h1, ${href} h2`);
      return { bottom, top: heading ? heading.getBoundingClientRect().top : null };
    }, first.href);
    if (clearance.top !== null && clearance.top > -1) {
      expect(clearance.top, `first heading hidden under sticky header on ${path}`).toBeGreaterThanOrEqual(clearance.bottom - 1);
    }
  });
}

test('every checkbox and radio is at least 24px (WCAG 2.5.8)', async ({ page }, info) => {
  test.skip(info.project.name !== 'phone');
  await page.route(url => !['127.0.0.1', 'localhost'].includes(new URL(url).hostname), route => route.abort());
  await page.goto('/submit-testimony');
  const small = await page.evaluate(() => [...document.querySelectorAll('input[type=checkbox],input[type=radio]')]
    .map(el => el.getBoundingClientRect()).filter(r => r.width && (r.width < 24 || r.height < 24)).length);
  expect(small).toBe(0);
});

test('reduced motion stops running animations', async ({ browser }, info) => {
  test.skip(info.project.name !== 'laptop');
  const context = await browser.newContext({ reducedMotion: 'reduce', baseURL: info.project.use.baseURL });
  await context.route(url => !['127.0.0.1', 'localhost'].includes(new URL(url).hostname), route => route.abort());
  for (const path of ['/', '/fr/', '/ar/']) {
    const page = await context.newPage();
    await page.goto(path, { waitUntil: 'load' });
    await page.waitForTimeout(400);
    const running = await page.evaluate(() => document.getAnimations()
      .filter(a => a.playState === 'running' && a.effect.getComputedTiming().iterations === Infinity).length);
    expect(running, `infinite animations under reduced motion on ${path}`).toBe(0);
    await page.close();
  }
  await context.close();
});
