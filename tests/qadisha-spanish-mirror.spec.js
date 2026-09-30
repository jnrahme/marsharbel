const {test, expect} = require('./qa-test.cjs');
const catalog = require('../locales/es/mirrors/qadisha.json');

for (const route of ['/qadisha-valley', '/ar/qadisha-valley', '/fr/vallee-qadisha', '/es/valle-qadisha']) {
  test(`${route} retains the same visible structure, images and reciprocal cluster`, async ({page}) => {
    const errors = [];
    page.on('pageerror', e => errors.push(e.message));
    await page.goto(route);
    await expect(page.locator('main > section')).toHaveCount(9);
    await expect(page.locator('main img')).toHaveCount(4);
    await expect(page.locator('main h3')).toHaveCount(10);
    await expect(page.locator('#sc-language-select')).toHaveCount(1);
    await expect(page.locator('link[rel="alternate"][hreflang="es"]')).toHaveAttribute('href', 'https://marsharbel.com/es/valle-qadisha');
    for (const image of await page.locator('main img').all()) {
      await image.scrollIntoViewIfNeeded();
      await expect.poll(() => image.evaluate(el => el.complete && el.naturalWidth > 0)).toBe(true);
    }
    expect(await page.evaluate(() => document.documentElement.scrollWidth-document.documentElement.clientWidth)).toBeLessThanOrEqual(1);
    expect(errors).toEqual([]);
  });
}

test('Spanish Qadisha switches from English and back without runtime translation', async ({page}) => {
  await page.goto('/qadisha-valley?lang=en');
  await page.locator('#sc-language-select').selectOption('es');
  await expect(page).toHaveURL(/\/es\/valle-qadisha$/);
  await expect(page.locator('h1')).toHaveText(catalog['hero.heading1']);
  await expect(page.locator('html')).toHaveAttribute('lang', 'es');
  await page.locator('#sc-language-select').selectOption('en');
  await expect(page).toHaveURL(/\/qadisha-valley$/);
});

test('Spanish Qadisha links to real Spanish guides and English-only places', async ({page}) => {
  await page.goto('/es/valle-qadisha');
  await expect(page.locator('main a[href="/es/annaya"]')).toHaveCount(2);
  await expect(page.locator('header .nav-sub a[href^="/es/monasterio-qannoubine"]')).toHaveCount(1);
  await expect(page.locator('header .nav-sub a[href^="/es/monasterio-qozhaya"]')).toHaveCount(1);
  await expect(page.locator('main a[href^="/saint-charbel-trail"]')).toHaveCount(3);
  await page.locator('main .btn[href="/es/annaya"]').click();
  await expect(page).toHaveURL(/\/es\/annaya$/);
});
