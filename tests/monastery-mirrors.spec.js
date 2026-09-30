const {test, expect} = require('./qa-test.cjs');
const catalogs = {
  qannoubine: require('../locales/ar/mirrors/qannoubine-monastery.json'),
  qozhaya: require('../locales/ar/mirrors/qozhaya-monastery.json')
};

for (const name of Object.keys(catalogs)) {
  const slug = `${name}-monastery`;
  for (const code of ['en', 'ar']) {
    const route = code === 'en' ? `/${slug}` : `/ar/${slug}`;
    test(`${route} preserves the monastery structure, images, FAQ and SEO`, async ({page}) => {
      const errors = [];
      page.on('pageerror', e => errors.push(e.message));
      await page.goto(route);
      await expect(page.locator('html')).toHaveAttribute('lang', code);
      await expect(page.locator('html')).toHaveAttribute('dir', code === 'ar' ? 'rtl' : 'ltr');
      await expect(page.locator('main > section')).toHaveCount(10);
      await expect(page.locator('main img')).toHaveCount(2);
      await expect(page.locator('main h3')).toHaveCount(6);
      await expect(page.locator('#sc-language-select')).toHaveCount(1);
      const sibling = name === 'qannoubine' ? 'qozhaya' : 'qannoubine';
      const localizedPrefix = code === 'ar' ? '/ar' : '';
      for (const destination of [`${localizedPrefix}/qadisha-valley`, `${localizedPrefix}/${sibling}-monastery`]) {
        await expect(page.locator(`header .nav-sub a[href="${destination}"]`)).toHaveCount(1);
      }
      await expect(page.locator('link[rel="canonical"]')).toHaveAttribute('href', `https://marsharbel.com${route}`);
      for (const language of ['en', 'ar', 'x-default']) {
        await expect(page.locator(`link[rel="alternate"][hreflang="${language}"]`)).toHaveCount(1);
      }
      const schemas = await page.locator('script[type="application/ld+json"]').allTextContents();
      expect(schemas.map(JSON.parse).map(schema => schema['@type'])).toEqual(['WebPage', 'FAQPage', 'TouristAttraction']);
      expect(JSON.parse(schemas[1]).mainEntity).toHaveLength(6);
      if (code === 'ar') {
        await expect(page.locator('h1')).toHaveText(catalogs[name]['hero.heading1']);
        for (let n = 1; n <= 6; n++) {
          await expect(page.locator('main h3').nth(n-1)).toHaveText(catalogs[name][`faq.question${n}`]);
          expect(JSON.parse(schemas[1]).mainEntity[n-1].acceptedAnswer.text).toBe(catalogs[name][`faq.text${n}`]);
        }
        await expect(page.locator(`main a[href="/ar/${name === 'qannoubine' ? 'qozhaya' : 'qannoubine'}-monastery"]`).first()).toBeVisible();
        await expect(page.locator('main a[href="/ar/qadisha-valley"]').first()).toBeVisible();
      }
      if (name === 'qozhaya') await expect(page.locator('main section li strong')).toHaveCount(6);
      for (const image of await page.locator('main img').all()) {
        await image.scrollIntoViewIfNeeded();
        await expect.poll(() => image.evaluate(el => el.complete && el.naturalWidth > 0)).toBe(true);
      }
      const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
      expect(overflow).toBeLessThanOrEqual(1);
      expect(errors).toEqual([]);
    });
  }
  test(`${slug} switches between English and Arabic while preserving route`, async ({page}) => {
    await page.goto(`/${slug}?lang=en`);
    await page.locator('#sc-language-select').selectOption('ar');
    await expect(page).toHaveURL(new RegExp(`/ar/${slug}$`));
    await expect(page.locator('h1')).toHaveText(catalogs[name]['hero.heading1']);
    await page.locator('#sc-language-select').selectOption('en');
    await expect(page).toHaveURL(new RegExp(`/${slug}$`));
  });
}
