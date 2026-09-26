const {test, expect} = require('@playwright/test');
const AxeBuilder = require('@axe-core/playwright').default;
const registry = require('../locales/registry.json');
const languages = Object.keys(registry.locales);
const catalogs = Object.fromEntries(languages.map(code => [code, require(`../locales/${code}/pages.json`)]));
const prayerMirror = require('../locales/ar/mirrors/prayers.json');
const prayerMirrorFrench = require('../locales/fr/mirrors/prayers.json');
const topicHeading = (code, topic) => topic === 'prayers' && ['ar','en','fr'].includes(code) ?
  ({ar:prayerMirror,fr:prayerMirrorFrench,en:require('../locales/en/mirrors/prayers.json')})[code]['hero.heading'] :
  catalogs[code][topic].title;
const routeFor = (code, topic) => topic ? `/${code}/${registry.locales[code].slugs[topic]}` : registry.locales[code].home;
const topicLanguages = topic => topic ? languages.filter(code => (registry.topics[topic].locales || languages).includes(code)) : languages;
const alternateFor = (code, topic) => topicLanguages(topic).includes(code) ? routeFor(code, topic) : registry.topics[topic].relatedEnglish;

for (const [language, config] of Object.entries(registry.locales)) {
  const topics = Object.keys(registry.topics).filter(topic => topicLanguages(topic).includes(language));
  const resources = language === registry.defaultLocale ? topics : [null, ...topics];
  for (const topic of resources) {
    const route = routeFor(language, topic);
    test(`${route} reads and switches language without JavaScript`, async ({browser, baseURL}, testInfo) => {
      const context = await browser.newContext({...testInfo.project.use, javaScriptEnabled:false, baseURL});
      try {
        const page = await context.newPage();
        const response = await page.goto(route);
        expect(response.status()).toBe(200);
        await expect(page.locator('h1')).toBeVisible();
        if (topic) await expect(page.locator('h1')).toHaveText(topicHeading(language, topic));
        await expect(page.locator('html')).toHaveAttribute('dir', config.direction);
        await expect(page.locator('html')).toHaveAttribute('lang', language);
        expect((await page.locator('main').innerText()).length).toBeGreaterThan(700);
        expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
        const cluster = [...new Set([registry.defaultLocale, ...topicLanguages(topic)])];
        await expect(page.locator('link[hreflang]')).toHaveCount(cluster.length + 1);
        for (const code of cluster) {
          await expect(page.locator(`link[hreflang="${code}"]`)).toHaveAttribute('href', registry.site + alternateFor(code, topic));
        }
        const anchors = await page.locator('a[href^="#"]').evaluateAll(nodes => nodes.map(node => node.getAttribute('href')));
        for (const anchor of anchors) await expect(page.locator(anchor)).toHaveCount(1);
        const published = topicLanguages(topic);
        if (topic && published.length > 1 && !(['en','ar','fr'].includes(language) && topic === 'prayers')) {
          const next = published[(published.indexOf(language) + 1) % published.length];
          await page.locator('header nav').getByRole('link',{name:registry.locales[next].nativeName,exact:true}).click();
          await expect(page.locator('html')).toHaveAttribute('lang',next);
          await expect(page.locator('h1')).toHaveText(topicHeading(next, topic));
        }
      } finally {
        await context.close();
      }
    });
  }
  test(`${language} prayer guide accessibility`,async({page}) => {
    await page.goto(routeFor(language,'prayers'));
    const results = await new AxeBuilder({page}).analyze();
    expect(results.violations.filter(v => ['serious','critical'].includes(v.impact))).toEqual([]);
  });
  if (language !== registry.defaultLocale) {
    test(`legacy language selector opens ${language} reading guide`,async({page}) => {
      await page.goto('/saint-charbel-prayers?lang=en');
      await page.locator('#sc-language-select').selectOption(language);
      await expect(page).toHaveURL(new RegExp(routeFor(language,'prayers')+'$'));
      await expect(page.locator('h1')).toHaveText(topicHeading(language, 'prayers'));
    });
  }
}


test('existing pages keep one top language selector without duplicate menus', async ({page}) => {
  for (const route of ['/', ...Object.values(registry.topics).map(topic => topic.relatedEnglish)]) {
    await page.goto(route + '?lang=en');
    await expect(page.locator('#sc-language-select')).toHaveCount(1);
    await expect(page.locator('#sc-language-select')).toBeVisible();
    await expect(page.locator('.lang-switcher')).toHaveCount(1);
    await expect(page.locator('.locale-navigation, .locale-nav')).toHaveCount(0);
    await expect(page.locator('footer a[lang], main nav a[lang]')).toHaveCount(0);
    for (const code of languages) {
      await expect(page.locator(`#sc-language-select option[value="${code}"]`)).toHaveCount(1);
    }
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  }
});

test('Arabic prayer mirror keeps authored copy and round-trips to English', async ({page}) => {
  await page.goto('/ar/prayers');
  await expect(page.locator('h1')).toHaveText(prayerMirror['hero.heading']);
  await expect(page.locator('html')).toHaveAttribute('lang', 'ar');
  await expect(page.locator('main > section')).toHaveCount(7);
  await expect(page.locator('.prayer-card')).toHaveCount(14);
  await expect(page.locator('main img[src="/media/annaya/charbel-historic-photo.webp"]')).toHaveCount(1);
  await page.reload();
  await expect(page.locator('h1')).toHaveText(prayerMirror['hero.heading']);
  await page.locator('#sc-language-select').selectOption('en');
  await expect(page).toHaveURL(/\/saint-charbel-prayers$/);
  await page.locator('#sc-language-select').selectOption('ar');
  await expect(page).toHaveURL(/\/ar\/prayers$/);
  await expect(page.locator('h1')).toHaveText(prayerMirror['hero.heading']);
});

test('English directory hub selector reaches the authored Arabic hub', async ({page}) => {
  await page.goto('/miracles/?lang=en');
  await page.locator('#sc-language-select').selectOption('ar');
  await expect(page).toHaveURL(/\/ar\/miracles\/$/);
  await expect(page.locator('h1')).toHaveText(catalogs.ar.miracles.title);
  await expect(page.locator('link[rel="canonical"]')).toHaveAttribute('href', registry.site + '/ar/miracles/');
});

test('unpublished locale on a miracle story stays as a runtime fallback', async ({page}) => {
  await page.goto('/miracles/nohad-el-shami?lang=en');
  await page.locator('#sc-language-select').selectOption('fr');
  await expect(page).toHaveURL(/\/miracles\/nohad-el-shami\?lang=fr$/);
  await expect(page.locator('link[rel="canonical"]')).toHaveAttribute('href', registry.site + '/miracles/nohad-el-shami');
});
