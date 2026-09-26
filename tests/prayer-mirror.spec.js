const {test, expect} = require('@playwright/test');

for (const [route, code] of [['/saint-charbel-prayers','en'], ['/ar/prayers','ar']]) {
  test(`${code} prayers mirror stays readable and complete`, async ({page}) => {
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    await page.goto(route);
    await expect(page.locator('html')).toHaveAttribute('lang', code);
    await expect(page.locator('main > section')).toHaveCount(7);
    await expect(page.locator('.prayer-card')).toHaveCount(14);
    await expect(page.locator('#sc-language-select')).toHaveCount(1);
    const layout = await page.evaluate(() => ({
      width: document.documentElement.scrollWidth,
      viewport: document.documentElement.clientWidth,
      image: document.querySelector('.hero-figure img'),
      title: document.querySelector('h1').textContent,
    }));
    expect(layout.width).toBeLessThanOrEqual(layout.viewport + 1);
    expect(await page.locator('.hero-figure img').evaluate(image => image.complete && image.naturalWidth > 0)).toBe(true);
    expect(errors).toEqual([]);
  });
}

test('Arabic mirror resists stale English preference and preserves authored copy', async ({page}) => {
  await page.goto('/saint-charbel-prayers?lang=en');
  await page.locator('#sc-language-select').selectOption('ar');
  await expect(page).toHaveURL(/\/ar\/prayers$/);
  await expect(page.locator('h1')).toHaveText('مكتبة صلوات مار شربل');
  await page.reload();
  await expect(page.locator('h1')).toHaveText('مكتبة صلوات مار شربل');
  await page.goto('/ar/prayers?lang=en');
  await expect(page.locator('h1')).toHaveText('مكتبة صلوات مار شربل');
  await expect(page.locator('html')).toHaveAttribute('lang','ar');
});
