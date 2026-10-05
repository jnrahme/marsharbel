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
      await expect.poll(() => image.evaluate(el => el.complete && el.naturalWidth > 0)).toBe(true);
    }
    const sizes = await page.evaluate(() => ({scroll: document.documentElement.scrollWidth, viewport: document.documentElement.clientWidth}));
    expect(sizes.scroll).toBeLessThanOrEqual(sizes.viewport + 1);
    expect(errors).toEqual([]);
  });
}

test('ar Qadisha keeps authored language and offers English while refusing pending non-English', async ({page}) => {
  await page.goto('/ar/qadisha-valley?lang=en');
  await expect(page.locator('h1')).toHaveText(catalog['hero.heading1']);
  await expect(page.locator('html')).toHaveAttribute('lang','ar');
  await expect(page.locator('#sc-language-select option[value="en"]')).toBeEnabled();
  const before=await page.evaluate(()=>({url:location.href,main:document.querySelector('main').innerHTML,lang:document.documentElement.lang}));
  expect(await page.evaluate(()=>SC_LANGUAGE_SWITCH.request('de'))).toBe(false);
  expect(await page.evaluate(()=>({url:location.href,main:document.querySelector('main').innerHTML,lang:document.documentElement.lang}))).toEqual(before);
  await page.reload();await expect(page.locator('h1')).toHaveText(catalog['hero.heading1']);
  await page.selectOption('#sc-language-select','en');await expect(page).toHaveURL(/\/qadisha-valley$/);await expect(page.locator('html')).toHaveAttribute('lang','en');
});

test('Arabic Qadisha has functioning nav and local authored links', async ({page}) => {
  await page.goto('/ar/qadisha-valley');
  const travel = page.locator('header .nav-group').last().locator('.nav-sub');
  for (const destination of ['/ar/qannoubine-monastery', '/ar/qozhaya-monastery', '/ar/qadisha-valley']) {
    await expect(travel.locator(`a[href="${destination}"]`)).toHaveCount(1);
  }
  await expect(page.locator('main a[href="/ar/annaya"]')).toHaveCount(2);
  await page.locator('main .btn[href="/ar/annaya"]').click();
  await expect(page).toHaveURL(/\/ar\/annaya$/);
});
