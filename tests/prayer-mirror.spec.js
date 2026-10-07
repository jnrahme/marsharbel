const {test, expect} = require('@playwright/test');

for (const [route, code] of [['/saint-charbel-prayers','en'], ['/en/prayers','en'], ['/ar/prayers','ar'], ['/fr/prieres','fr'], ['/es/oraciones','es'], ['/pt/oracoes','pt'], ['/it/preghiere','it'], ['/de/gebete','de'], ['/pl/modlitwy','pl'],['/ru/molitvy','ru']]) {
  test(`${route} prayers mirror stays readable and complete`, async ({page}) => {
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    await page.goto(route);
    await expect(page.locator('html')).toHaveAttribute('lang', code);
    await expect(page.locator('main > section')).toHaveCount(8);
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

// Existing authored routes are tested directly; resemblance is not a twin review.
for(const [route,code]of [['/en/prayers','en'],['/ar/prayers','ar'],['/fr/prieres','fr'],['/es/oraciones','es'],['/pt/oracoes','pt'],['/it/preghiere','it'],['/de/gebete','de'],['/pl/modlitwy','pl'],['/ru/molitvy','ru']]) {
  test(`${route} keeps authored prayer copy and refuses pending twins`,async({page})=>{
    await page.addInitScript(()=>localStorage.setItem('sc_lang_pref','en'));
    await page.goto(route+'?lang=ar');
    const family='saint-charbel-prayers-master';
    const binding=require(`../locales/en/${family}-bindings.json`).bindings.find(b=>b.kind==='text'&&/(^| > )h1(:nth-of-type\(\d+\))?$/.test(b.selector));
    const heading=['ar','de','fr','ru','pt','it','pl'].includes(code)?require(`../locales/${code}/${family}-copy.json`)[binding.key]:require(`../locales/${code}/mirrors/prayers.json`)['hero.heading'];
    await expect(page.locator('h1')).toHaveText(heading);
    await expect(page.locator('html')).toHaveAttribute('lang',code);
    await expect(page.locator('#sc-language-select')).toHaveValue(code);
    const other=code==='fr'?'ar':'fr';
    if(['ar','fr','de','ru','pt','it','pl'].includes(code)){
      await expect(page.locator(`#sc-language-select option[value="${other}"]`)).toBeEnabled();
      await page.selectOption('#sc-language-select',other);
      const target=require('../locales/registry.json').pageMirrors['saint-charbel-prayers-master'].routes[other];
      await expect(page).toHaveURL(new RegExp(target+'$'));await expect(page.locator('html')).toHaveAttribute('lang',other);
      await page.goto(route);
      await expect(page.locator('#sc-language-select option[value="ru"]')).toBeEnabled();
      await expect(page.locator('#sc-language-select option[value="pt"]')).toBeEnabled();
      await expect(page.locator('#sc-language-select option[value="pl"]')).toBeEnabled();
      await expect(page.locator('#sc-language-select option[value="it"]')).toBeEnabled();
      for(const pending of ['es'])await expect(page.locator(`#sc-language-select option[value="${pending}"]`)).toBeDisabled();
    }else await expect(page.locator(`#sc-language-select option[value="${other}"]`)).toBeDisabled();
    const pending=['ar','fr','de','ru','pt','it','pl'].includes(code)?'es':'ru';
    await expect(page.locator(`#sc-language-select option[value="${pending}"]`)).toBeDisabled();
    const before=await page.evaluate(()=>({url:location.href,main:document.querySelector('main').innerHTML,lang:document.documentElement.lang}));
    expect(await page.evaluate(lang=>SC_LANGUAGE_SWITCH.request(lang),pending)).toBe(false);
    expect(await page.evaluate(()=>({url:location.href,main:document.querySelector('main').innerHTML,lang:document.documentElement.lang}))).toEqual(before);
    await page.reload();await expect(page.locator('h1')).toHaveText(heading);
  });
}
