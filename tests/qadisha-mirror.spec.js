const {test, expect} = require('@playwright/test');
const catalog = require('../locales/ar/mirrors/qadisha.json');

for (const route of ['/qadisha-valley', '/ar/qadisha-valley']) {
  test(`${route} keeps the reviewed sections and images`, async ({page}) => {
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    await page.goto(route);
    await expect(page.locator('main > section')).toHaveCount(9);
    await expect(page.locator('main img')).toHaveCount(4);
    await expect(page.locator('#sc-language-select')).toHaveCount(1);
    await expect(page.locator('main h3')).toHaveCount(10);
    for (const image of await page.locator('main img').all()) {
      await image.scrollIntoViewIfNeeded();
      expect(await image.evaluate(el => el.complete && el.naturalWidth > 0)).toBe(true);
    }
    const sizes = await page.evaluate(() => ({scroll: document.documentElement.scrollWidth, viewport: document.documentElement.clientWidth}));
    expect(sizes.scroll).toBeLessThanOrEqual(sizes.viewport + 1);
    expect(errors).toEqual([]);
  });
}

test('Arabic Qadisha persists in Arabic, switches to English master, and returns', async ({page}) => {
  await page.goto('/qadisha-valley?lang=en');
  await page.locator('#sc-language-select').selectOption('ar');
  await expect(page).toHaveURL(/\/ar\/qadisha-valley$/);
  await expect(page.locator('html')).toHaveAttribute('dir', 'rtl');
  await expect(page.locator('h1')).toHaveText(catalog['hero.heading1']);
  await page.goto('/ar/qadisha-valley?lang=en');
  await expect(page.locator('h1')).toHaveText(catalog['hero.heading1']);
  await page.locator('#sc-language-select').selectOption('en');
  await expect(page).toHaveURL(/\/qadisha-valley$/);
  await expect(page.locator('h1')).toHaveText("The Qadisha Valley, Lebanon's Holy Valley");
});

test('Arabic Qadisha has functioning nav and local authored links', async ({page}) => {
  await page.goto('/ar/qadisha-valley');
  await expect(page.locator('header .nav-group').last().locator('.nav-sub a')).toHaveCount(6);
  await expect(page.locator('main a[href="/ar/annaya"]')).toHaveCount(2);
  await page.locator('main .btn[href="/ar/annaya"]').click();
  await expect(page).toHaveURL(/\/ar\/annaya$/);
});
