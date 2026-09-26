const {test, expect} = require('@playwright/test');
const catalog = require('../locales/fr/mirrors/qadisha.json');

for (const route of ['/qadisha-valley', '/ar/qadisha-valley', '/fr/vallee-qadisha']) {
  test(`${route} retains Qadisha content and the single language selector`, async ({page}) => {
    const errors = [];
    page.on('pageerror', e => errors.push(e.message));
    await page.goto(route);
    await expect(page.locator('main > section')).toHaveCount(9);
    await expect(page.locator('main img')).toHaveCount(4);
    await expect(page.locator('main h3')).toHaveCount(10);
    await expect(page.locator('#sc-language-select')).toHaveCount(1);
    await expect(page.locator('header .nav-sub a[href*="qadisha"]')).toHaveCount(1);
    for (const image of await page.locator('main img').all()) {
      await image.scrollIntoViewIfNeeded();
      expect(await image.evaluate(el => el.complete && el.naturalWidth > 0)).toBe(true);
    }
    expect(await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth)).toBeLessThanOrEqual(1);
    expect(errors).toEqual([]);
  });
}

test('French Qadisha persists in French, switches to English master and back', async ({page}) => {
  await page.goto('/qadisha-valley?lang=en');
  await page.locator('#sc-language-select').selectOption('fr');
  await expect(page).toHaveURL(/\/fr\/vallee-qadisha$/);
  await expect(page.locator('h1')).toHaveText(catalog['hero.heading1']);
  await page.goto('/fr/vallee-qadisha?lang=en');
  await expect(page.locator('h1')).toHaveText(catalog['hero.heading1']);
  await page.locator('#sc-language-select').selectOption('en');
  await expect(page).toHaveURL(/\/qadisha-valley$/);
  await page.locator('#sc-language-select').selectOption('fr');
  await expect(page).toHaveURL(/\/fr\/vallee-qadisha$/);
});

test('French Qadisha links to real localized guides and preserves unpublished English routes', async ({page}) => {
  await page.goto('/fr/vallee-qadisha');
  await expect(page.locator('main a[href="/fr/annaya"]')).toHaveCount(2);
  await expect(page.locator('main a[href^="/saint-charbel-trail"]')).toHaveCount(3);
  await page.locator('main .btn[href="/fr/annaya"]').click();
  await expect(page).toHaveURL(/\/fr\/annaya$/);
});
