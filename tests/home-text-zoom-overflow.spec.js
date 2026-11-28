// WCAG 1.4.4 / 1.4.10: at 200% text size the home intro, news, letter and monthly-prayer blocks
// must stay inside their own box and the page must not scroll sideways.
const { test, expect } = require('@playwright/test');

for (const path of ['/', '/de/', '/ar/']) {
  for (const width of [390, 768, 1100, 1280]) {
    test(`home blocks at 200% text ${path} ${width}px`, async ({ page }, info) => {
      test.skip(info.project.name !== 'laptop', 'sizes are set inside the test');
      await page.route(url => !['127.0.0.1', 'localhost'].includes(new URL(url).hostname), route => route.abort());
      await page.setViewportSize({ width, height: 800 });
      await page.goto(path, { waitUntil: 'load' });
      await page.addStyleTag({ content: 'html{font-size:200% !important}' });
      await page.waitForTimeout(300);
      const m = await page.evaluate(() => {
        const out = [];
        for (const c of document.querySelectorAll('.monthly-prayer,.home-intro-band,.home-news,.home-letter')) {
          const cb = c.getBoundingClientRect();
          for (const e of c.querySelectorAll('*')) {
            const b = e.getBoundingClientRect();
            if (b.width && getComputedStyle(e).position !== 'absolute' && (b.right > cb.right + 1 || b.left < cb.left - 1)) {
              out.push(`${c.className.split(' ')[0]} > ${e.className || e.tagName}`);
            }
          }
        }
        return { out, iw: innerWidth, sw: document.documentElement.scrollWidth };
      });
      expect(m.out, 'items past their block edge').toEqual([]);
      expect(m.sw, 'page scrolls sideways').toBeLessThanOrEqual(m.iw + 1);
    });
  }
}
