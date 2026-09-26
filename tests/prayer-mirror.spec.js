const {test, expect} = require('@playwright/test');

for (const [route, code] of [['/saint-charbel-prayers','en'], ['/en/prayers','en'], ['/ar/prayers','ar'], ['/fr/prieres','fr'], ['/es/oraciones','es'], ['/pt/oracoes','pt'], ['/it/preghiere','it'], ['/de/gebete','de'], ['/pl/modlitwy','pl']]) {
  test(`${route} prayers mirror stays readable and complete`, async ({page}) => {
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

test('English guide mirror switches to Arabic authored mirror', async ({page}) => {
  await page.goto('/en/prayers');
  await expect(page.locator('h1')).toHaveText('Saint Charbel Prayer Library');
  await page.locator('#sc-language-select').selectOption('ar');
  await expect(page).toHaveURL(/\/ar\/prayers$/);
  await expect(page.locator('h1')).toHaveText('مكتبة صلوات مار شربل');
});

test('French mirror uses the authored locale and switches to English', async ({page}) => {
  await page.goto('/saint-charbel-prayers?lang=en');
  await page.locator('#sc-language-select').selectOption('fr');
  await expect(page).toHaveURL(/\/fr\/prieres$/);
  await expect(page.locator('h1')).toHaveText('Bibliothèque de prières de saint Charbel');
  await page.reload();
  await expect(page.locator('h1')).toHaveText('Bibliothèque de prières de saint Charbel');
  await page.locator('#sc-language-select').selectOption('en');
  await expect(page).toHaveURL(/\/saint-charbel-prayers$/);
});

test('French prayer mirror keeps its native text with an English preference', async ({page}) => {
  await page.goto('/saint-charbel-prayers?lang=en');
  await page.locator('#sc-language-select').selectOption('fr');
  await expect(page).toHaveURL(/\/fr\/prieres$/);
  await page.goto('/fr/prieres?lang=en');
  await expect(page.locator('h1')).toHaveText('Bibliothèque de prières de saint Charbel');
  await expect(page.locator('html')).toHaveAttribute('lang', 'fr');
});

test('Spanish mirror stays authored through reload and returns to English master', async ({page}) => {
  await page.goto('/saint-charbel-prayers?lang=en');
  await page.locator('#sc-language-select').selectOption('es');
  await expect(page).toHaveURL(/\/es\/oraciones$/);
  await expect(page.locator('h1')).toHaveText('Biblioteca de oraciones a san Chárbel');
  await page.reload();
  await expect(page.locator('h1')).toHaveText('Biblioteca de oraciones a san Chárbel');
  await page.locator('#sc-language-select').selectOption('en');
  await expect(page).toHaveURL(/\/saint-charbel-prayers$/);
  await page.goto('/es/oraciones?lang=en');
  await expect(page.locator('html')).toHaveAttribute('lang','es');
  await expect(page.locator('h1')).toHaveText('Biblioteca de oraciones a san Chárbel');
});

test('Portuguese mirror stays authored through reload and returns to English master', async ({page}) => {
  await page.goto('/saint-charbel-prayers?lang=en');
  await page.locator('#sc-language-select').selectOption('pt');
  await expect(page).toHaveURL(/\/pt\/oracoes$/);
  await expect(page.locator('h1')).toHaveText('Biblioteca de orações a São Charbel');
  await page.reload();
  await expect(page.locator('h1')).toHaveText('Biblioteca de orações a São Charbel');
  await page.locator('#sc-language-select').selectOption('en');
  await expect(page).toHaveURL(/\/saint-charbel-prayers$/);
  await page.goto('/pt/oracoes?lang=en');
  await expect(page.locator('html')).toHaveAttribute('lang','pt');
  await expect(page.locator('h1')).toHaveText('Biblioteca de orações a São Charbel');
});

test('Italian mirror stays authored through reload and returns to English master', async ({page}) => {
  await page.goto('/saint-charbel-prayers?lang=en');
  await page.locator('#sc-language-select').selectOption('it');
  await expect(page).toHaveURL(/\/it\/preghiere$/);
  await expect(page.locator('h1')).toHaveText('Raccolta di preghiere a san Charbel');
  await page.reload();
  await expect(page.locator('h1')).toHaveText('Raccolta di preghiere a san Charbel');
  await page.locator('#sc-language-select').selectOption('en');
  await expect(page).toHaveURL(/\/saint-charbel-prayers$/);
  await page.goto('/it/preghiere?lang=en');
  await expect(page.locator('html')).toHaveAttribute('lang','it');
  await expect(page.locator('h1')).toHaveText('Raccolta di preghiere a san Charbel');
});

test('German mirror stays authored through reload and returns to English master', async ({page}) => {
  await page.goto('/saint-charbel-prayers?lang=en');
  await page.locator('#sc-language-select').selectOption('de');
  await expect(page).toHaveURL(/\/de\/gebete$/);
  await expect(page.locator('h1')).toHaveText('Gebete zum heiligen Charbel');
  await page.reload();
  await expect(page.locator('h1')).toHaveText('Gebete zum heiligen Charbel');
  await page.locator('#sc-language-select').selectOption('en');
  await expect(page).toHaveURL(/\/saint-charbel-prayers$/);
  await page.goto('/de/gebete?lang=en');
  await expect(page.locator('html')).toHaveAttribute('lang','de');
  await expect(page.locator('h1')).toHaveText('Gebete zum heiligen Charbel');
});

test('Polish mirror stays authored through reload and returns to English master', async ({page}) => {
  await page.goto('/saint-charbel-prayers?lang=en');
  await page.locator('#sc-language-select').selectOption('pl');
  await expect(page).toHaveURL(/\/pl\/modlitwy$/);
  await expect(page.locator('h1')).toHaveText('Modlitwy do świętego Szarbela');
  await page.reload();
  await expect(page.locator('h1')).toHaveText('Modlitwy do świętego Szarbela');
  await page.locator('#sc-language-select').selectOption('en');
  await expect(page).toHaveURL(/\/saint-charbel-prayers$/);
  await page.goto('/pl/modlitwy?lang=en');
  await expect(page.locator('html')).toHaveAttribute('lang','pl');
  await expect(page.locator('h1')).toHaveText('Modlitwy do świętego Szarbela');
});
