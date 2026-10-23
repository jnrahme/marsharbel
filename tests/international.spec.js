const {test, expect} = require('@playwright/test');
const AxeBuilder = require('@axe-core/playwright').default;
const registry = require('../locales/registry.json');
const repoRoot = require('path').resolve(__dirname, '..');
const {loadBuiltManifest, loadResolver, generatedNavEligibleRoutes} = require('../scripts/tests/same_page_contract.cjs');
const samePageManifest = loadBuiltManifest(repoRoot);
const samePageApi = loadResolver(repoRoot);
const eligibleNavRoutes = generatedNavEligibleRoutes(samePageManifest);
const languages = Object.keys(registry.locales);
const homeLanguages=languages.filter(code=>registry.locales[code].home&&registry.locales[code].capabilities?.home!==false);
const noHomeLanguages=languages.filter(code=>!homeLanguages.includes(code));
const catalogs = Object.fromEntries(languages.map(code => [code, require(`../locales/${code}/pages.json`)]));
const prayerMirror = require('../locales/ar/mirrors/prayers.json');
const prayerMirrorFrench = require('../locales/fr/mirrors/prayers.json');
const prayerMirrorSpanish = require('../locales/es/mirrors/prayers.json');
const prayerMirrorPortuguese = require('../locales/pt/mirrors/prayers.json');
const prayerMirrorItalian = require('../locales/it/mirrors/prayers.json');
const prayerMirrorGerman = require('../locales/de/mirrors/prayers.json');
const prayerMirrorPolish = require('../locales/pl/mirrors/prayers.json');
const exactFor = topic => registry.exactMirrors?.[topic === 'feastDay' ? 'feast' : topic];
const historyFor = (code, topic) => topic === 'biography' && code !== 'en' && registry.pageMirrors['history-master'].renderLocales.includes(code);
const travelFamily = {annaya: 'annaya-master', twentySecond: 'twenty-second-master'};
const travelFor = (code, topic) => code !== 'en' && travelFamily[topic] && registry.pageMirrors[travelFamily[topic]].renderLocales.includes(code) ? travelFamily[topic] : null;
const travelHeading = (code, family) => {
  const binding = require(`../locales/en/${family}-bindings.json`).bindings.find(b => b.kind === 'text' && /(^| > )h1(:nth-of-type\(\d+\))?$/.test(b.selector));
  return require(`../locales/${code}/${family}-copy.json`)[binding.key];
};
const prayerFor = (code,topic) => ({prayers:'saint-charbel-prayers-master',novena:'saint-charbel-novena-master'}[topic] && registry.pageMirrors[{prayers:'saint-charbel-prayers-master',novena:'saint-charbel-novena-master'}[topic]]?.renderLocales.includes(code)) ? {prayers:'saint-charbel-prayers-master',novena:'saint-charbel-novena-master'}[topic] : null;
const topicHeading = (code, topic) => prayerFor(code,topic) ? travelHeading(code,prayerFor(code,topic)) : travelFor(code,topic) ? travelHeading(code, travelFor(code,topic)) : historyFor(code,topic) ? require(`../locales/${code}/history-master-copy.json`)['history.hero.the-life-of-saint-charbel-makhlouf'] : (exactFor(topic)?.renderLocales || []).includes(code) ? require(`../locales/${code}/${topic === 'feastDay' ? 'feast' : topic}-exact.json`).slots['1'].text : code === 'ar' && topic === 'feastDay' ? require('../locales/ar/feast-mirror.json').slots['1'].text : topic === 'prayers' && ['ar', 'en', 'fr', 'es', 'pt', 'it', 'de', 'pl'].includes(code) ?
  ({ar: prayerMirror, fr: prayerMirrorFrench, es: prayerMirrorSpanish, pt: prayerMirrorPortuguese, it: prayerMirrorItalian, de: prayerMirrorGerman, pl: prayerMirrorPolish, en: require('../locales/en/mirrors/prayers.json')})[code]['hero.heading'] :
  catalogs[code][topic].title;
const routeFor = (code, topic) => prayerFor(code,topic) ? registry.pageMirrors[prayerFor(code,topic)].routes[code] : travelFor(code,topic) ? registry.pageMirrors[travelFor(code,topic)].routes[code] : (exactFor(topic)?.renderLocales || []).includes(code) ? exactFor(topic).routes[code] : topic ? `/${code}/${registry.locales[code].slugs[topic]}` : registry.locales[code].home;
const topicLanguages = topic => topic ? languages.filter(code => (registry.topics[topic].locales || languages).includes(code)) : languages;
// Discovery clusters depend on this page's identity, not merely its topic.
const clusterFor = (language, topic) => {
  if(!topic)return Object.fromEntries(homeLanguages.map(code=>[code,registry.locales[code].home]));
  if(topic==='prayers') return language==='en' ? {en:'/en/prayers'} : Object.fromEntries(Object.entries(registry.pageMirrors['saint-charbel-prayers-master'].discoveryRoutes).filter(([k])=>k!=='x-default'));
  if(topic==='novena') return prayerFor(language,topic) ? Object.fromEntries(Object.entries(registry.pageMirrors['saint-charbel-novena-master'].discoveryRoutes).filter(([k])=>k!=='x-default')) : Object.fromEntries(['en','es','pt','it','pl'].filter(c=>!registry.pageMirrors['saint-charbel-novena-master'].renderLocales.includes(c)).map(c=>[c,routeFor(c,topic)]));
  if (travelFor(language, topic)) {const cfg=registry.pageMirrors[travelFor(language,topic)];return Object.fromEntries(Object.entries(cfg.discoveryRoutes||{en:registry.topics[topic].relatedEnglish,...cfg.routes}).filter(([code])=>code!=='x-default'));}
  if (travelFamily[topic] && language === 'en') return {en: routeFor('en', topic)};
  if (topic === 'biography') return language === 'en' ? {en:'/en/biography'} : {en:'/history',...registry.pageMirrors['history-master'].routes};
  const exact = exactFor(topic), route = routeFor(language, topic);
  if (exact && Object.values(exact.routes).includes(route)) return exact.routes;
  const codes = topicLanguages(topic).filter(code => !(exact?.renderLocales || []).includes(code));
  const cluster = Object.fromEntries(codes.map(code => [code, routeFor(code, topic)]));
  if (!exact) cluster[registry.defaultLocale] ||= registry.topics[topic]?.relatedEnglish || registry.locales[registry.defaultLocale].home;
  return cluster;
};

for (const [language, config] of Object.entries(registry.locales)) {
  const topics = Object.keys(registry.topics).filter(topic => topicLanguages(topic).includes(language));
  const resources = language === registry.defaultLocale || !homeLanguages.includes(language) ? topics : [null, ...topics];
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
        if (topic === 'rosary' && ['en', 'ar', 'fr', 'es', 'pt', 'it', 'de', 'pl'].includes(language)) {
          // A1 certified rosary-guide family: all 8 twins are live, so the next-locale
          // link must be an active exact link to the certified twin route; locales
          // outside the certified family stay fail-closed.
          const next = published[(published.indexOf(language) + 1) % published.length];
          const target = page.locator(`header nav a[hreflang="${next}"]`).first();
          await expect(target).not.toHaveAttribute('aria-disabled', 'true');
          await expect(target).toHaveAttribute('href', registry.site + routeFor(next, topic));
          for (const off of ['ru', 'hi', 'th']) {
            const unavailable = page.locator(`header nav a[hreflang="${off}"]`).first();
            await expect(unavailable).toHaveAttribute('aria-disabled', 'true');
            await expect(unavailable).not.toHaveAttribute('href', /.+/);
          }
        } else if (topic && topic !== 'biography' && !travelFor(language, topic) && !prayerFor(language,topic) && !(exactFor(topic)?.renderLocales || []).includes(language) && published.length > 1 && !(['en', 'ar', 'fr', 'es', 'pt', 'it', 'de', 'pl'].includes(language) && topic === 'prayers') && !(language === 'ar' && topic === 'feastDay')) {
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
      if(["ar","de","fr","ru","pt","it","pl","es"].includes(language)){await expect(page.locator(`#sc-language-select option[value="${language}"]`)).toBeEnabled();}else await expect(page.locator(`#sc-language-select option[value="${language}"]`)).toBeDisabled();
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
    await expect(page.locator('.locale-navigation')).toHaveCount(0);
    // PR3: eligible same-page families carry exactly one marked generated
    // no-JS fallback nav. With JS ready the select is the only VISIBLE control;
    // the fallback stays in the DOM (hidden) as the crawlable/no-JS layer.
    // Fallback presence, eligibility and exact twin link targets stay asserted.
    const localeNavs = page.locator('nav.locale-nav');
    const localeNavCount = await localeNavs.count();
    expect(localeNavCount).toBeLessThanOrEqual(1);
    const normalizedRoute = route.replace(/\/$/, '') || '/';
    if (localeNavCount === 1) {
      const fallback = localeNavs.first();
      await expect(fallback).toHaveAttribute('data-i18n-generated', '');
      await expect(fallback).toBeHidden();
      expect(eligibleNavRoutes.has(normalizedRoute)).toBe(true);
      const anchors = await fallback.locator('a[hreflang]').all();
      expect(anchors.map(() => 0).length).toBe(samePageManifest.languages.length);
      // Live layer: the switcher rewrites anchors against the live URL (preview
      // origin, ?lang=en view). The DOM contract is resolver output for THAT
      // SAME input - page.url() - never a fabricated production origin.
      for (const anchor of anchors) {
        const code = await anchor.getAttribute('hreflang');
        const resolution = samePageApi.resolve(samePageManifest, page.url(), code, 'en');
        if (resolution.available) {
          expect(await anchor.getAttribute('href')).toBe(resolution.href);
        } else {
          expect(await anchor.getAttribute('href')).toBeNull();
          expect(await anchor.getAttribute('aria-disabled')).toBe('true');
        }
      }
      // Committed-bytes layer: the served no-JS fallback must keep exact
      // production twin hrefs resolved from the canonical site URL.
      const staticHtml = await (await page.request.get(normalizedRoute)).text();
      const staticNav = staticHtml.match(/<nav\b[^>]*\bclass="[^"]*\blocale-nav\b[^"]*"[^>]*>[\s\S]*?<\/nav>/);
      expect(staticNav, 'committed page carries the generated locale nav').not.toBeNull();
      for (const m of staticNav[0].matchAll(/<a\b[^>]*\bhreflang="([^"]+)"[^>]*>/g)) {
        const code = m[1];
        const href = (m[0].match(/\bhref="([^"]*)"/) || [])[1] || null;
        const resolution = samePageApi.resolve(samePageManifest, 'https://marsharbel.com' + normalizedRoute, code, 'en');
        if (resolution.available) expect(href).toBe(resolution.href);
        else expect(href).toBeNull();
      }
    } else {
      expect(eligibleNavRoutes.has(normalizedRoute)).toBe(false);
    }
    // P0: a crawlable locale bar may exist - at most one per page, one
    // canonical link per locale, and never parameter (?lang=) URLs. English
    // pages used to forbid footer locale links entirely; the bar is the
    // crawlable path that replaced runtime-only switching.
    const localeBarCount = await page.locator('nav.footer-locales').count();
    expect(localeBarCount).toBeLessThanOrEqual(1);
    for (const code of homeLanguages) {
      await expect(page.locator(`nav.footer-locales a[hreflang="${code}"]`)).toHaveCount(localeBarCount);
    }
    for(const code of noHomeLanguages)await expect(page.locator(`nav.footer-locales a[hreflang="${code}"]`)).toHaveCount(0);
    const footerHtml = ((await (await page.request.get(route)).text()).match(/<nav[^>]*footer-locales[\s\S]*?<\/nav>/) || [''])[0];
    expect(footerHtml).not.toContain('?lang=');
    for (const code of languages) {
      await expect(page.locator(`#sc-language-select option[value="${code}"]`)).toHaveCount(1);
    }
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  });
}

test('Arabic prayer mirror keeps authored copy and always offers its English source', async ({page}) => {
  await page.goto('/ar/prayers');
  await expect(page.locator('h1')).toHaveText(travelHeading('ar','saint-charbel-prayers-master'));
  await expect(page.locator('html')).toHaveAttribute('lang', 'ar');
  await expect(page.locator('main > section')).toHaveCount(8);
  // The ar Oct-22 devotion-guidance aside reuses card styling; count only
  // the fourteen authored prayer cards inside the prayer grids.
  await expect(page.locator('.prayer-grid .prayer-card')).toHaveCount(14);
  await expect(page.locator('main img[src="/media/annaya/charbel-historic-photo.webp"]')).toHaveCount(1);
  await page.reload();
  await expect(page.locator('h1')).toHaveText(travelHeading('ar','saint-charbel-prayers-master'));
  await expect(page.locator('#sc-language-select option[value="en"]')).toBeEnabled();
  await expect(page).toHaveURL(/\/ar\/prayers$/);
  await expect(page.locator('h1')).toHaveText(travelHeading('ar','saint-charbel-prayers-master'));
});

test('English directory hub selector routes Arabic to its published twin, other locales stay unpublished', async ({page}) => {
  await page.goto('/miracles/?lang=en');
  await expect(page.locator('link[rel="canonical"]')).toHaveAttribute('href', registry.site + '/miracles/');
  // #769 published /ar/miracles/: the ar option is enabled and routes to the twin.
  await expect(page.locator('#sc-language-select option[value="ar"]')).toBeEnabled();
  expect(await page.evaluate(c=>SC_LANGUAGE_SWITCH.request(c),'ar')).toBe(true);
  await expect(page).toHaveURL(/\/ar\/miracles\/$/);
  await expect(page.locator('html')).toHaveAttribute('lang','ar');
  await expect(page.locator('html')).toHaveAttribute('dir','rtl');
  // Control: fr has no /miracles/ twin in the registry and stays unpublished.
  await page.goto('/miracles/?lang=en');
  await expect(page.locator('#sc-language-select option[value="fr"]')).toBeDisabled();
  const before=page.url();
  expect(await page.evaluate(c=>SC_LANGUAGE_SWITCH.request(c),'fr')).toBe(false);
  await expect(page).toHaveURL(before);
});

test('unpublished locale on a miracle story stays unavailable with no machine fallback', async ({page}) => {
  await page.goto('/miracles/nohad-el-shami?lang=en');
  await expect(page.locator('#sc-language-select option[value="fr"]')).toBeDisabled();
  await expect(page).toHaveURL(/\/miracles\/nohad-el-shami\?lang=en$/);
  await expect(page.locator('link[rel="canonical"]')).toHaveAttribute('href', registry.site + '/miracles/nohad-el-shami');
});

for (const [source,target] of [['/ar/annaya','/visit-annaya'],['/ar/biography','/history'],['/ar/22nd-of-the-month','/22nd-of-the-month']]) {
  test(`${source} always offers its English source`, async ({page}) => {
    await page.goto(source);
    await expect(page.locator('#sc-language-select option[value="en"]')).toBeEnabled();
    if(source !== '/ar/annaya' || true){
      await expect(page.locator('head link[hreflang="en"]')).toHaveAttribute('href',registry.site+target);
      await expect(page.locator('footer nav.footer-locales a[hreflang=en]')).toHaveAttribute('href','/');
    } else await expect(page.locator('header nav a[hreflang="en"]')).toHaveAttribute('href', /.+/);
    await page.selectOption('#sc-language-select','en');
    await expect(page).toHaveURL(new RegExp(target+'$'));
    await expect(page.locator('html')).toHaveAttribute('lang','en');
  });
}

for(const code of homeLanguages) test(`${code} homepage offers every shipped homepage`,async({page})=>{
  await page.goto(registry.locales[code].home);
  for(const lang of homeLanguages) await expect(page.locator(`#sc-language-select option[value="${lang}"]`)).toBeEnabled();
  for(const lang of noHomeLanguages){await expect(page.locator(`#sc-language-select option[value="${lang}"]`)).toBeDisabled();const before=page.url();expect(await page.evaluate(c=>SC_LANGUAGE_SWITCH.request(c),lang)).toBe(false);await expect(page).toHaveURL(before);}
  const next=code==='fr'?'ar':'fr';
  await page.selectOption('#sc-language-select',next);
  await expect(page).toHaveURL(new RegExp(registry.locales[next].home+'$'));
  await expect(page.locator('html')).toHaveAttribute('lang',next);
});
// Keyed masters use crawlable footer homepage links, not the legacy header menu.
for (const [route,code] of [['/pt/novena','pt'],['/it/novena','it'],['/ru/novena','ru'],['/pl/nowenna','pl'],['/es/novena','es']]) test(`${route} keeps keyed prayer and language fallback readable without JavaScript`, async ({browser, baseURL}, testInfo) => {
  const context = await browser.newContext({...testInfo.project.use, baseURL, javaScriptEnabled:false});
  try {
    const page = await context.newPage();
    await page.goto(route);
    await expect(page.locator('html')).toHaveAttribute('lang',code);
    await expect(page.locator('h1')).toBeVisible();
    for (let day=1;day<=9;day++) await expect(page.locator(`#day-${day}`)).toHaveCount(1);
    await page.locator('a[href="#day-9"]').first().click();
    await expect(page.locator('#day-9')).toBeInViewport();
    const fallback = page.locator('nav.footer-locales');
    await expect(fallback).toHaveCount(1);
    await fallback.scrollIntoViewIfNeeded();
    await expect(fallback).toBeVisible();
    for (const lang of homeLanguages) {
      const link = fallback.locator(`a[hreflang="${lang}"]`);
      await expect(link).toBeVisible();
      await expect(link).toHaveAttribute('href',registry.locales[lang].home);
      expect((await link.innerText()).trim()).not.toBe('');
    }
    for(const lang of noHomeLanguages)await expect(fallback.locator(`a[hreflang="${lang}"]`)).toHaveCount(0);
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
    await page.screenshot({path:testInfo.outputPath(code+'-keyed-nojs-footer.png')});
    await fallback.locator('a[hreflang="en"]').click();
    await expect(page).toHaveURL(baseURL+registry.locales.en.home);
    await expect(page.locator('html')).toHaveAttribute('lang','en');
  } finally { await context.close(); }
});

// PR3 generated fallback: native closed details disclosure. Works no-JS (and on
// failed/slow script), keyboard-operable, exact twin links; hidden only after
// the enhanced select is actually ready (no residual summary).
for (const route of ['/saint-charbel-novena', '/es/novena']) {
  test(`${route} generated fallback disclosure works without JavaScript`, async ({browser, baseURL}, testInfo) => {
    const context = await browser.newContext({...testInfo.project.use, baseURL, javaScriptEnabled:false});
    try {
      const page = await context.newPage();
      await page.goto(route);
      const wrapper = page.locator('[data-locale-fallback]');
      await expect(wrapper).toHaveCount(1);
      await expect(wrapper).not.toHaveAttribute('open', '');
      const summary = wrapper.locator('summary');
      await expect(summary).toBeVisible();
      expect((await summary.boundingBox()).height).toBeGreaterThanOrEqual(44);
      // Closed by default: the exact nav stays in the DOM for crawlers, hidden visually.
      await expect(wrapper.locator('nav.locale-nav[data-i18n-generated]')).toBeHidden();
      await summary.focus();
      await page.keyboard.press('Enter');
      await expect(wrapper).toHaveAttribute('open', '');
      const nav = wrapper.locator('nav.locale-nav[data-i18n-generated]');
      await expect(nav).toBeVisible();
      // Exact twin link targets inside the disclosure.
      await expect(nav.locator('a[hreflang="en"]')).toHaveAttribute('href', 'https://marsharbel.com/saint-charbel-novena');
      await page.keyboard.press('Enter');
      await expect(wrapper).not.toHaveAttribute('open', '');
    } finally { await context.close(); }
  });

  test(`${route} hides the fallback only after the enhanced select is ready`, async ({page}) => {
    await page.goto(route);
    await expect(page.locator('#sc-language-select')).toBeVisible();
    // JSready: single visible control, no residual summary or wrapper.
    await expect(page.locator('[data-locale-fallback]')).toBeHidden();
    await expect(page.locator('[data-locale-fallback] summary')).toBeHidden();
    await expect(page.locator('.lang-switcher')).toHaveCount(1);
  });

  test(`${route} keeps the disclosure when the switcher script fails`, async ({browser, baseURL}, testInfo) => {
    const context = await browser.newContext({...testInfo.project.use, baseURL});
    try {
      await context.route('**/same-page-switcher.js', route_ => route_.abort());
      const page = await context.newPage();
      await page.goto(route);
      await expect(page.locator('#sc-language-select')).toHaveCount(0);
      const wrapper = page.locator('[data-locale-fallback]');
      await expect(wrapper).toBeVisible();
      await wrapper.locator('summary').click();
      await expect(wrapper.locator('nav.locale-nav[data-i18n-generated]')).toBeVisible();
      // Keyed prayer still reachable with the disclosure present.
      await page.locator('a[href="#day-9"]').first().click();
      await expect(page.locator('#day-9')).toBeInViewport();
    } finally { await context.close(); }
  });
}

// Layout-shift measurement of the no-JS to JS handoff: real PerformanceObserver
// LayoutShift entries + session-window CLS, fast and delayed/failed switcher,
// control availability asserted throughout. Metrics are attached for design
// adjudication - no self-selected pixel threshold gates this test.
for (const scenario of [{name:'fast'},{name:'delayed-switcher',delayMs:2000},{name:'failed-switcher',fail:true}]) {
  test(`fallback handoff layout shift measured (${scenario.name})`, async ({browser, baseURL}, testInfo) => {
    test.skip(testInfo.project.name !== 'phone', 'measurement matrix runs on the phone project');
    const context = await browser.newContext({...testInfo.project.use, baseURL});
    try {
      await context.addInitScript(() => {
        window.__shifts = [];
        new PerformanceObserver(list => {
          for (const e of list.getEntries()) window.__shifts.push({value:e.value, hadRecentInput:e.hadRecentInput, time:e.startTime, sources:(e.sources||[]).map(s => s && s.node ? s.node.tagName : null)});
        }).observe({type:'layout-shift', buffered:true});
      });
      if (scenario.fail) await context.route('**/same-page-switcher.js', route_ => route_.abort());
      else if (scenario.delayMs) await context.route('**/same-page-switcher.js', async route_ => { await new Promise(res => setTimeout(res, scenario.delayMs)); route_.continue(); });
      const page = await context.newPage();
      await page.goto('/saint-charbel-novena', {waitUntil: scenario.fail ? 'load' : 'domcontentloaded'});
      const wrapper = page.locator('[data-locale-fallback]');
      if (scenario.fail) {
        // Failed script: the disclosure stays continuously functional.
        await expect(wrapper).toBeVisible();
        await wrapper.locator('summary').click();
        await expect(wrapper.locator('nav.locale-nav[data-i18n-generated]')).toBeVisible();
        await expect(wrapper.locator('a[hreflang="en"]')).toHaveAttribute('href', 'https://marsharbel.com/saint-charbel-novena');
        await expect(page.locator('#sc-language-select')).toHaveCount(0);
        await page.waitForTimeout(1500);
      } else {
        // The disclosure is usable until the enhanced select is ready, then hidden.
        await expect(page.locator('#sc-language-select')).toBeVisible();
        await expect(wrapper).toBeHidden();
        await page.waitForTimeout(600);
      }
      const shifts = await page.evaluate(() => window.__shifts);
      // Session-window CLS: new window on >1s gap or >5s span; report the max window.
      const nonInput = shifts.filter(s => !s.hadRecentInput);
      let sessionMax = 0, cur = 0, winStart = null, lastT = null;
      for (const s of nonInput) {
        if (winStart === null || s.time - lastT > 1000 || s.time - winStart > 5000) { sessionMax = Math.max(sessionMax, cur); cur = 0; winStart = s.time; }
        cur += s.value; lastT = s.time;
      }
      sessionMax = Math.max(sessionMax, cur);
      testInfo.attach('layout-shift-' + scenario.name, {body: JSON.stringify({scenario: scenario.name, viewport: '390x844', sessionWindowCLS: Number(sessionMax.toFixed(5)), totalNonInputCLS: Number(nonInput.reduce((a,s) => a + s.value, 0).toFixed(5)), entries: shifts}, null, 1)});
    } finally { await context.close(); }
  });
}

// Smallest supported phone: intrinsic option widths must not push RTL or LTR chrome out.
for (const route of ['/ar/annaya', '/pt/annaya', '/it/annaya', '/en/annaya', '/']) {
  test(`${route} language control fits inside its header at 320px`, async ({page}) => {
    await page.setViewportSize({width:320,height:800});
    await page.goto(route);
    await expect(page.locator('#sc-language-select')).toBeVisible();
    const layout = await page.evaluate(() => {
      const host = document.querySelector('#sc-language-switcher');
      const parent = host.parentElement.getBoundingClientRect();
      return {width:document.documentElement.scrollWidth, viewport:innerWidth, parent:{left:parent.left,right:parent.right}, boxes:[host,document.querySelector('#sc-language-select')].map(node => {const box=node.getBoundingClientRect();return {left:box.left,right:box.right};})};
    });
    expect(layout.width).toBeLessThanOrEqual(layout.viewport);
    for (const box of layout.boxes) {
      expect(box.left).toBeGreaterThanOrEqual(layout.parent.left - 1);
      expect(box.right).toBeLessThanOrEqual(layout.parent.right + 1);
    }
  });
}
