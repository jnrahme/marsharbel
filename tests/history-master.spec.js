const { test, expect } = require('@playwright/test');
const routes = require('../locales/registry.json').pageMirrors['history-master'].routes;
for (const [lang, route] of Object.entries(routes)) {
  test(`${lang} full history has complete joins, English access and decoded images`, async ({ page }) => {
    test.setTimeout(60000);
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    await page.goto(route);
    const selector = page.locator('#sc-language-select');
    await expect(selector).toHaveCount(1);
    await expect(selector.locator('option[value="en"]')).toBeEnabled();
    await expect(page.locator('main')).toBeVisible();
    for (const region of await page.locator('.history-table-wrap').all()) {
      await expect(region).toHaveAttribute('tabindex','0');
      await expect(region).toHaveAttribute('role','region');
      await expect(region).toHaveAttribute('aria-label',/.+/);
      await region.focus();
      await expect(region).toBeFocused();
    }
    const result = await page.evaluate(async () => {
      const initialHeight = document.documentElement.scrollHeight;
      for (let y = 0; y < initialHeight; y += 800) {
        scrollTo(0, y);
        await new Promise(resolve => setTimeout(resolve, 25));
      }
      await Promise.all(Array.from(document.images).map(image => image.decode().catch(() => {})));
      const paragraph = document.querySelector('#visit p');
      const wordJoins = Array.from(paragraph.querySelectorAll('a')).filter(link => {
        const next = link.nextSibling?.textContent || '';
        return /^\p{L}/u.test(next);
      });
      return {
        overflow: document.documentElement.scrollWidth > innerWidth,
        broken: Array.from(document.images).filter(image => !image.naturalWidth).map(image => image.src),
        badJoins: wordJoins.map(link => link.textContent),
        links: Array.from(paragraph.querySelectorAll('a')).map(link => link.textContent.trim()),
        heading: document.querySelector('#visit h2').textContent,
      };
    });
    expect(result.overflow).toBe(false);
    expect(result.broken).toEqual([]);
    expect(result.badJoins).toEqual([]);
    expect(result.links).toHaveLength(3);
    expect(result.links.every(Boolean)).toBe(true);
    if (lang === 'ru') expect(result.heading).toBe('Посещение Аннайи');
    expect(errors).toEqual([]);
  });
}
