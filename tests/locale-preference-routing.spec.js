const {test, expect} = require('@playwright/test');
const registry = require('../locales/registry.json');

for (const [route, lang, heading] of [
  ['/ar/qannoubine-monastery', 'ar', require('../locales/ar/mirrors/qannoubine-monastery.json')['hero.heading1']],
  ['/ar/qozhaya-monastery', 'ar', require('../locales/ar/mirrors/qozhaya-monastery.json')['hero.heading1']],
  ['/fr/vallee-qadisha', 'fr', require('../locales/fr/mirrors/qadisha.json')['hero.heading1']],
]) {
  test(`${route} remains in its authored language with a conflicting saved preference`, async ({page}) => {
    await page.addInitScript(() => localStorage.setItem('sc_lang_pref', 'ar'));
    await page.goto(route);
    await expect(page.locator('html')).toHaveAttribute('lang', lang);
    await expect(page.locator('html')).toHaveAttribute('dir', lang === 'ar' ? 'rtl' : 'ltr');
    await expect(page.locator('#sc-language-select')).toHaveValue(lang);
    await expect(page).toHaveURL(new RegExp(`${route.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}$`));
    if (heading) await expect(page.locator('h1')).toHaveText(heading);
    expect(await page.evaluate(() => localStorage.getItem('sc_lang_pref'))).toBe('ar');
  });
}

test('a saved choice redirects an English URL to its published twin, but explicit English wins', async ({page}) => {
  await page.goto('/qannoubine-monastery?lang=en');
  await page.locator('#sc-language-select').selectOption('ar');
  await expect(page).toHaveURL(/\/ar\/qannoubine-monastery$/);
  await expect(page.locator('html')).toHaveAttribute('dir', 'rtl');
  expect(await page.evaluate(() => localStorage.getItem('sc_lang_pref'))).toBe('ar');
  await page.goto('/qannoubine-monastery');
  await expect(page).toHaveURL(/\/ar\/qannoubine-monastery$/);
  await page.goto('/qannoubine-monastery?lang=en');
  await expect(page).toHaveURL(/\/qannoubine-monastery\?lang=en$/);
  await expect(page.locator('html')).toHaveAttribute('lang', 'en');
  await expect(page.locator('html')).toHaveAttribute('dir', 'ltr');
  await expect(page.locator('#sc-language-select')).toHaveValue('en');
  expect(await page.evaluate(() => localStorage.getItem('sc_lang_pref'))).toBe('ar');
});

test('an explicit published language query on English URL lands on its canonical twin', async ({page}) => {
  await page.goto('/qozhaya-monastery?lang=ar&ref=test#visiting');
  await expect(page).toHaveURL(/\/ar\/qozhaya-monastery\?ref=test#visiting$/);
  await expect(page.locator('html')).toHaveAttribute('dir', 'rtl');
  await expect(page.locator('#sc-language-select')).toHaveValue('ar');
});

test('unpublished locale query remains runtime fallback, with no fabricated indexed twin', async ({page}) => {
  await page.goto('/miracles/nohad-el-shami?lang=fr');
  await expect(page.locator('#sc-language-select')).toHaveValue('fr');
  await expect(page.locator('html')).toHaveAttribute('lang', 'fr');
  await expect(page.locator('link[rel="canonical"]')).toHaveAttribute('href', registry.site+'/miracles/nohad-el-shami');
});

for (const route of ['/news', '/bekaa-kafra']) {
  test(`${route} leaves English copy and LTR on legacy route despite an Arabic preference`, async ({page}) => {
    await page.addInitScript(() => localStorage.setItem('sc_lang_pref', 'ar'));
    await page.goto(route);
    await expect(page.locator('html')).toHaveAttribute('lang', 'en');
    await expect(page.locator('html')).toHaveAttribute('dir', 'ltr');
    await expect(page.locator('#sc-language-select')).toHaveValue('en');
    expect(await page.evaluate(() => localStorage.getItem('sc_lang_pref'))).toBe('ar');
  });
}

test('the English homepage with a saved Arabic choice opens its authored Arabic hub', async ({page}) => {
  await page.addInitScript(() => localStorage.setItem('sc_lang_pref', 'ar'));
  await page.goto('/');
  await expect(page).toHaveURL(/\/ar\/$/);
  await expect(page.locator('html')).toHaveAttribute('dir', 'rtl');
});

test('a story with a published Arabic twin follows the preference', async ({page}) => {
  await page.addInitScript(() => localStorage.setItem('sc_lang_pref', 'ar'));
  await page.goto('/miracles/nohad-el-shami');
  await expect(page).toHaveURL(/\/ar\/miracles\/nohad-el-shami$/);
  await expect(page.locator('html')).toHaveAttribute('dir', 'rtl');
});

test('a stray language query never changes an authored localized URL', async ({page}) => {
  await page.goto('/ar/qannoubine-monastery?lang=he');
  await expect(page.locator('html')).toHaveAttribute('lang', 'ar');
  await expect(page.locator('html')).toHaveAttribute('dir', 'rtl');
  await expect(page.locator('#sc-language-select')).toHaveValue('ar');
  await expect(page.locator('h1')).toHaveText(require('../locales/ar/mirrors/qannoubine-monastery.json')['hero.heading1']);
});

test('an explicit English prayer master URL stays on the full master', async ({page}) => {
  await page.addInitScript(() => localStorage.setItem('sc_lang_pref', 'ar'));
  await page.goto('/saint-charbel-prayers?lang=en');
  await expect(page).toHaveURL(/\/saint-charbel-prayers\?lang=en$/);
  await expect(page.locator('html')).toHaveAttribute('lang', 'en');
  await expect(page.locator('#sc-language-select')).toHaveValue('en');
});
