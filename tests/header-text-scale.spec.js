// WCAG 1.4.4 / 1.4.10: at 200% text size the desktop header must wrap instead of running past the viewport,
// the page must not scroll sideways, and an opened dropdown must stay inside the viewport.
const { test, expect } = require('@playwright/test');

for (const path of ['/', '/story', '/prayer-library']) {
  for (const width of [900, 1100, 1280]) {
    test(`header at 200% text ${path} ${width}px`, async ({ page }, info) => {
      test.skip(info.project.name !== 'laptop', 'sizes are set inside the test');
      await page.route(url => !['127.0.0.1', 'localhost'].includes(new URL(url).hostname), route => route.abort());
      await page.setViewportSize({ width, height: 700 });
      await page.goto(path, { waitUntil: 'load' });
      await page.addStyleTag({ content: 'html{font-size:200% !important}' });
      await page.waitForTimeout(300);
      const m = await page.evaluate(() => ({
        iw: innerWidth, sw: document.documentElement.scrollWidth,
        clipped: [...document.querySelectorAll('header .links > a, header .links > .nav-group > a, header .brand')]
          .filter(e => e.getBoundingClientRect().width > 0 && e.getBoundingClientRect().right > innerWidth + 1).map(e => e.textContent.trim())
      }));
      expect(m.clipped, 'header items past the right edge').toEqual([]);
      expect(m.sw, 'page scrolls sideways').toBeLessThanOrEqual(m.iw + 1);
      const groups = page.locator('header .links .nav-group');
      const last = groups.nth((await groups.count()) - 1);
      await last.locator('> a').first().focus();
      await page.waitForTimeout(250);
      const sub = await last.locator('.nav-sub').boundingBox();
      expect(sub.x, 'dropdown left edge').toBeGreaterThanOrEqual(0);
      expect(sub.x + sub.width, 'dropdown right edge').toBeLessThanOrEqual(width + 1);
    });
  }
}

test('tall dropdown at 200% text scrolls inside the viewport and every item is reachable', async ({ page }, info) => {
  test.skip(info.project.name !== 'laptop', 'sizes are set inside the test');
  await page.route(url => !['127.0.0.1', 'localhost'].includes(new URL(url).hostname), route => route.abort());
  await page.setViewportSize({ width: 1280, height: 800 });
  await page.goto('/story', { waitUntil: 'load' });
  await page.addStyleTag({ content: 'html{font-size:200% !important}' });
  await page.waitForTimeout(300);
  const groups = page.locator('header .links .nav-group');
  let tallest = null;
  for (let i = 0; i < await groups.count(); i++) {
    const n = await groups.nth(i).locator('.nav-sub a').count();
    if (!tallest || n > tallest.n) tallest = { i, n };
  }
  const group = groups.nth(tallest.i);
  await group.locator('> a').first().focus();
  await page.waitForTimeout(250);
  const sub = group.locator('.nav-sub');
  const box = await sub.boundingBox();
  expect(box.y + box.height, 'dropdown bottom edge inside the viewport').toBeLessThanOrEqual(800 + 1);
  const lastLink = sub.locator('a').last();
  await lastLink.scrollIntoViewIfNeeded();
  const link = await lastLink.boundingBox();
  const frame = await sub.boundingBox();
  expect(link.y, 'last item reachable (top)').toBeGreaterThanOrEqual(frame.y - 1);
  expect(link.y + link.height, 'last item reachable (bottom)').toBeLessThanOrEqual(frame.y + frame.height + 1);
  expect(await sub.evaluate(el => el.scrollHeight > el.clientHeight && getComputedStyle(el).overflowY), 'dropdown scrolls').toBe('auto');
});
