const {test, expect} = require('@playwright/test');
const AxeBuilder = require('@axe-core/playwright').default;
const registry = require('../locales/registry.json');
const languages = Object.keys(registry.locales);
const catalogs = Object.fromEntries(languages.map(code => [code, require(`../locales/${code}/pages.json`)]));
const prayerMirror = require('../locales/ar/mirrors/prayers.json');
const prayerMirrorFrench = require('../locales/fr/mirrors/prayers.json');
const prayerMirrorSpanish = require('../locales/es/mirrors/prayers.json');
const prayerMirrorPortuguese = require('../locales/pt/mirrors/prayers.json');
const prayerMirrorItalian = require('../locales/it/mirrors/prayers.json');
const prayerMirrorGerman = require('../locales/de/mirrors/prayers.json');
const prayerMirrorPolish = require('../locales/pl/mirrors/prayers.json');
const exactFor = topic => registry.exactMirrors?.[topic === 'feastDay' ? 'feast' : topic];
const topicHeading = (code, topic) => (exactFor(topic)?.renderLocales || []).includes(code) ? require(`../locales/${code}/${topic === 'feastDay' ? 'feast' : topic}-exact.json`).slots['1'].text : code === 'ar' && topic === 'feastDay' ? require('../locales/ar/feast-mirror.json').slots['1'].text : topic === 'prayers' && ['ar', 'en', 'fr', 'es', 'pt', 'it', 'de', 'pl'].includes(code) ?
  ({ar: prayerMirror, fr: prayerMirrorFrench, es: prayerMirrorSpanish, pt: prayerMirrorPortuguese, it: prayerMirrorItalian, de: prayerMirrorGerman, pl: prayerMirrorPolish, en: require('../locales/en/mirrors/prayers.json')})[code]['hero.heading'] :
  catalogs[code][topic].title;
const routeFor = (code, topic) => (exactFor(topic)?.renderLocales || []).includes(code) ? exactFor(topic).routes[code] : topic ? `/${code}/${registry.locales[code].slugs[topic]}` : registry.locales[code].home;
const topicLanguages = topic => topic ? languages.filter(code => (registry.topics[topic].locales || languages).includes(code)) : languages;
// Discovery clusters depend on this page's identity, not merely its topic.
const clusterFor = (language, topic) => {
  const exact = exactFor(topic), route = routeFor(language, topic);
  if (exact && Object.values(exact.routes).includes(route)) return exact.routes;
  const codes = topicLanguages(topic).filter(code => !(exact?.renderLocales || []).includes(code));
  const cluster = Object.fromEntries(codes.map(code => [code, routeFor(code, topic)]));
  if (!exact) cluster[registry.defaultLocale] ||= registry.topics[topic]?.relatedEnglish || registry.locales[registry.defaultLocale].home;
  return cluster;
};

for (const [language, config] of Object.entries(registry.locales)) {
  const topics = Object.keys(registry.topics).filter(topic => topicLanguages(topic).includes(language));
  const resources = language === registry.defaultLocale ? topics : [null, ...topics];
  for (const topic of resources) {
    const route = routeFor(language, topic);
    test(`${route} reads and switches language without JavaScript`, async ({browser, baseURL}, testInfo) => {
      const context = await browser.newContext({...testInfo.project.use, javaScriptEnabled:false, baseURL});
      try {
        const page = await context.newPage();
        await page.route('**/*', r => new URL(r.request().url()).origin === new URL(baseURL).origin ? r.continue() : r.abort());
        const response = await page.goto(route);
        expect(response.status()).toBe(200);
        await expect(page.locator('h1')).toBeVisible();
        if (topic) await expect(page.locator('h1')).toHaveText(topicHeading(language, topic));
        await expect(page.locator('html')).toHaveAttribute('dir', config.direction);
        await expect(page.locator('html')).toHaveAttribute('lang', language);
        expect((await page.locator('main').innerText()).length).toBeGreaterThan(700);
        expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
        const cluster = clusterFor(language, topic);
        await expect(page.locator('link[hreflang]')).toHaveCount(Object.keys(cluster).length + 1);
        await expect(page.locator('link[hreflang="x-default"]')).toHaveAttribute('href', registry.site + (cluster[registry.defaultLocale] || Object.values(cluster)[0]));
        for (const [code, path] of Object.entries(cluster)) {
          await expect(page.locator(`link[hreflang="${code}"]`)).toHaveAttribute('href', registry.site + path);
        }
        const anchors = await page.locator('a[href^="#"]').evaluateAll(nodes => nodes.map(node => node.getAttribute('href')));
        for (const anchor of anchors) await expect(page.locator(anchor)).toHaveCount(1);
        const published = topicLanguages(topic);
        if (topic && !(exactFor(topic)?.renderLocales || []).includes(language) && published.length > 1 && !(['en', 'ar', 'fr', 'es', 'pt', 'it', 'de', 'pl'].includes(language) && topic === 'prayers') && !(language === 'ar' && topic === 'feastDay')) {
          const next = published[(published.indexOf(language) + 1) % published.length];
          // Same-page switching is fail-closed: every unpublished twin stays an unavailable, non-navigating link.
          const target = page.locator(`header nav a[hreflang="${next}"]`).first();
          if (next === 'en') {
            await expect(target).not.toHaveAttribute('aria-disabled', 'true');
            await expect(target).toHaveAttribute('href', /.+/);
          } else {
            await expect(target).toHaveAttribute('aria-disabled', 'true');
            await expect(target).not.toHaveAttribute('href', /.+/);
          }
        }
      } finally {
        await context.close();
      }
    });
  }
  if (topicLanguages("prayers").includes(language)) test(`${language} prayer guide accessibility`,async({page}) => {
    await page.goto(routeFor(language,'prayers'));
    const results = await new AxeBuilder({page}).analyze();
    expect(results.violations.filter(v => ['serious','critical'].includes(v.impact))).toEqual([]);
  });
  if (language !== registry.defaultLocale) {
    test(`language selector keeps ${language} reading guide unavailable until published`,async({page}) => {
      // Same-page switching is fail-closed: an unpublished twin is a disabled option, never a navigation.
      await page.goto('/saint-charbel-prayers?lang=en');
      await expect(page.locator(`#sc-language-select option[value="${language}"]`)).toBeDisabled();
      await expect(page).toHaveURL(/\/saint-charbel-prayers\?lang=en$/);
    });
  }
}


for (const route of ['/', ...new Set(Object.values(registry.topics).map(topic => topic.relatedEnglish))]) {
  test(`${route} keeps one top language selector without duplicate menus`, async ({page}) => {
    await page.goto(route + '?lang=en');
    await expect(page.locator('#sc-language-select')).toHaveCount(1);
    await expect(page.locator('#sc-language-select')).toBeVisible();
    await expect(page.locator('.lang-switcher')).toHaveCount(1);
    await expect(page.locator('.locale-navigation, .locale-nav')).toHaveCount(0);
    // P0: a crawlable locale bar may exist - at most one per page, one
    // canonical link per locale, and never parameter (?lang=) URLs. English
    // pages used to forbid footer locale links entirely; the bar is the
    // crawlable path that replaced runtime-only switching.
    const localeBarCount = await page.locator('nav.footer-locales').count();
    expect(localeBarCount).toBeLessThanOrEqual(1);
    for (const code of languages) {
      await expect(page.locator(`nav.footer-locales a[hreflang="${code}"]`)).toHaveCount(localeBarCount);
    }
    const footerHtml = ((await (await page.request.get(route)).text()).match(/<nav[^>]*footer-locales[\s\S]*?<\/nav>/) || [''])[0];
    expect(footerHtml).not.toContain('?lang=');
    for (const code of languages) {
      await expect(page.locator(`#sc-language-select option[value="${code}"]`)).toHaveCount(1);
    }
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  });
}

test('Arabic prayer mirror keeps authored copy and keeps English unavailable until published', async ({page}) => {
  await page.goto('/ar/prayers');
  await expect(page.locator('h1')).toHaveText(prayerMirror['hero.heading']);
  await expect(page.locator('html')).toHaveAttribute('lang', 'ar');
  await expect(page.locator('main > section')).toHaveCount(8);
  // The ar Oct-22 devotion-guidance aside reuses card styling; count only
  // the fourteen authored prayer cards inside the prayer grids.
  await expect(page.locator('.prayer-grid .prayer-card')).toHaveCount(14);
  await expect(page.locator('main img[src="/media/annaya/charbel-historic-photo.webp"]')).toHaveCount(1);
  await page.reload();
  await expect(page.locator('h1')).toHaveText(prayerMirror['hero.heading']);
  await expect(page.locator('#sc-language-select option[value="en"]')).toBeDisabled();
  await expect(page).toHaveURL(/\/ar\/prayers$/);
  await expect(page.locator('h1')).toHaveText(prayerMirror['hero.heading']);
});

test('English directory hub selector keeps the Arabic hub unavailable until published', async ({page}) => {
  await page.goto('/miracles/?lang=en');
  await expect(page.locator('#sc-language-select option[value="ar"]')).toBeDisabled();
  await expect(page).toHaveURL(/\/miracles\/\?lang=en$/);
  await expect(page.locator('link[rel="canonical"]')).toHaveAttribute('href', registry.site + '/miracles/');
});

test('unpublished locale on a miracle story stays unavailable with no machine fallback', async ({page}) => {
  await page.goto('/miracles/nohad-el-shami?lang=en');
  await expect(page.locator('#sc-language-select option[value="fr"]')).toBeDisabled();
  await expect(page).toHaveURL(/\/miracles\/nohad-el-shami\?lang=en$/);
  await expect(page.locator('link[rel="canonical"]')).toHaveAttribute('href', registry.site + '/miracles/nohad-el-shami');
});

for (const [source,target] of [['/ar/annaya','/en/annaya'],['/ar/biography','/en/biography'],['/ar/22nd-of-the-month','/22nd-of-the-month']]) {
  test(`${source} always offers its English source`, async ({page}) => {
    await page.goto(source);
    await expect(page.locator('#sc-language-select option[value="en"]')).toBeEnabled();
    await expect(page.locator('header nav a[hreflang="en"]')).toHaveAttribute('href', /.+/);
    await page.selectOption('#sc-language-select','en');
    await expect(page).toHaveURL(new RegExp(target+'$'));
    await expect(page.locator('html')).toHaveAttribute('lang','en');
  });
}
