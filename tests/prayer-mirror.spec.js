const {test, expect} = require('@playwright/test');

for (const [route, code] of [['/saint-charbel-prayers','en'], ['/en/prayers','en'], ['/ar/prayers','ar'], ['/fr/prieres','fr'], ['/es/oraciones','es'], ['/pt/oracoes','pt'], ['/it/preghiere','it'], ['/de/gebete','de'], ['/pl/modlitwy','pl']]) {
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
for(const [route,code]of [['/en/prayers','en'],['/ar/prayers','ar'],['/fr/prieres','fr'],['/es/oraciones','es'],['/pt/oracoes','pt'],['/it/preghiere','it'],['/de/gebete','de'],['/pl/modlitwy','pl']]) {
  test(`${route} keeps authored prayer copy and refuses pending twins`,async({page})=>{
    await page.addInitScript(()=>localStorage.setItem('sc_lang_pref','en'));
    await page.goto(route+'?lang=ar');
    const heading=require(`../locales/${code}/mirrors/prayers.json`)['hero.heading'];
    await expect(page.locator('h1')).toHaveText(heading);
    await expect(page.locator('html')).toHaveAttribute('lang',code);
    await expect(page.locator('#sc-language-select')).toHaveValue(code);
    const other=code==='en'?'ar':'en';
    await expect(page.locator(`#sc-language-select option[value="${other}"]`)).toBeDisabled();
    const before=await page.evaluate(()=>({url:location.href,main:document.querySelector('main').innerHTML,lang:document.documentElement.lang}));
    expect(await page.evaluate(lang=>SC_LANGUAGE_SWITCH.request(lang),other)).toBe(false);
    expect(await page.evaluate(()=>({url:location.href,main:document.querySelector('main').innerHTML,lang:document.documentElement.lang}))).toEqual(before);
    await page.reload();await expect(page.locator('h1')).toHaveText(heading);
  });
}
