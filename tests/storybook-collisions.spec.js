const { test, expect } = require('@playwright/test');
// Permanent gate: no two reader hero/control elements may overlap (the sticky dock may sit over page content while scrolling, so dock-vs-settings is not compared), at standard widths, 100% and 200% text, English and Arabic.
const widths = [390, 768, 820, 1100, 1280, 1920];
const sel = ['.story-hero .kicker', '.story-hero .story-shelf-link', '.story-hero h1', '.story-hero p', '.storybook>details.story-settings>summary', '#story-prev', '#story-read', '#story-next'];
for (const lang of ['', '?lang=ar']) for (const zoom of ['100%', '200%']) for (const w of widths) {
  test(`reader elements do not collide at ${w} ${zoom} ${lang || 'en'}`, async ({ page }, info) => {
    test.skip(info.project.name !== 'laptop');
    await page.setViewportSize({ width: w, height: 900 });
    await page.route(/google-analytics\.com/, r => r.fulfill({ status: 204 }));
    await page.goto('/charbel-story-v2' + lang);
    await page.addStyleTag({ content: `html{font-size:${zoom}}` });
    await expect(page.locator('#story-step')).toContainText(/\d/);
    const hits = await page.evaluate(list => {
      const els = list.map(s => [s, document.querySelector(s)]).filter(([, e]) => e && e.getClientRects().length && getComputedStyle(e).visibility !== 'hidden');
      const out = [];
      for (let i = 0; i < els.length; i++) for (let j = i + 1; j < els.length; j++) {
        const a = els[i][1].getBoundingClientRect(), b = els[j][1].getBoundingClientRect();
        const ox = Math.min(a.right, b.right) - Math.max(a.left, b.left), oy = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top);
        if (ox > 1 && oy > 1 && !(/^#story-/.test(els[i][0]) !== /^#story-/.test(els[j][0]) && /summary/.test(els[i][0] + els[j][0]))) out.push(els[i][0] + ' x ' + els[j][0]);
      }
      return out;
    }, sel);
    expect(hits).toEqual([]);
  });
}
