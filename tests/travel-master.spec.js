const { test, expect } = require('@playwright/test');
const mirrors = require('../locales/registry.json').pageMirrors;
const families = ['annaya-master', 'twenty-second-master', 'pilgrimage-master'];
for (const family of families) {
  for (const [lang, route] of Object.entries(mirrors[family].routes)) {
    test(`${family} ${lang} renders cleanly with English access and no overflow`, async ({ page }) => {
      test.setTimeout(60000);
      const errors = [];
      page.on('pageerror', error => errors.push(error.message));
      await page.goto(route);
      const selector = page.locator('#sc-language-select');
      await expect(selector).toHaveCount(1);
      await expect(selector.locator('option[value="en"]')).toBeEnabled();
      await expect(page.locator('main')).toBeVisible();
      const result = await page.evaluate(async () => {
        const height = document.documentElement.scrollHeight;
        for (let y = 0; y < height; y += 800) { scrollTo(0, y); await new Promise(r => setTimeout(r, 25)); }
        await Promise.all(Array.from(document.images).map(i => i.decode().catch(() => {})));
        const glued = Array.from(document.querySelectorAll('main a')).filter(a => {
          const before = a.previousSibling && a.previousSibling.textContent || '';
          const after = a.nextSibling && a.nextSibling.textContent || '';
          return /\p{L}$/u.test(before) && /^\p{L}/u.test(a.textContent) || /\p{L}$/u.test(a.textContent) && /^\p{L}/u.test(after);
        }).map(a => a.textContent);
        return {
          lang: document.documentElement.lang,
          dir: document.documentElement.dir,
          overflow: document.documentElement.scrollWidth > innerWidth,
          broken: Array.from(document.images).filter(i => !i.naturalWidth).map(i => i.src),
          glued,
          h1: document.querySelectorAll('h1').length,
        };
      });
      expect(result.lang).toBe(lang);
      expect(result.dir).toBe(lang === 'ar' ? 'rtl' : 'ltr');
      expect(result.overflow).toBe(false);
      expect(result.broken).toEqual([]);
      expect(result.h1).toBe(1);
      expect(result.glued).toEqual([]);
      expect(errors).toEqual([]);
    });
  }
}
