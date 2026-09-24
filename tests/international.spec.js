const {test, expect} = require('@playwright/test');
const AxeBuilder = require('@axe-core/playwright').default;
const registry = require('../locales/registry.json');
const languages = Object.keys(registry.locales);
const catalogs = Object.fromEntries(languages.map(code => [code, require(`../locales/${code}/pages.json`)]));
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
        if (topic) await expect(page.locator('h1')).toHaveText(catalogs[language][topic].title);
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
        if (topic && published.length > 1) {
          const next = published[(published.indexOf(language) + 1) % published.length];
          await page.locator('header nav').getByRole('link',{name:registry.locales[next].nativeName,exact:true}).click();
          await expect(page.locator('html')).toHaveAttribute('lang',next);
          await expect(page.locator('h1')).toHaveText(catalogs[next][topic].title);
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
      await expect(page.locator('h1')).toHaveText(catalogs[language].prayers.title);
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
