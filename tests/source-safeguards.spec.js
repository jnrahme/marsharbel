const{test,expect}=require('@playwright/test');
const registry=require('../locales/registry.json');
const key='saint-charbel-novena.when-to-pray-it.the-feast-falls-on-the-third-sunday-of-july-in-the-maronite';
const novena=registry.pageMirrors['saint-charbel-novena-master'];
const supportedNovenaLocales=new Set(['en',...(novena.renderLocales||Object.keys(novena.routes||{}))]);
for(const code of Object.keys(registry.locales))test(`${code} source-first safeguards stay readable`,async({page,baseURL},info)=>{
 await page.route('**/*',r=>new URL(r.request().url()).origin===new URL(baseURL).origin?r.continue():r.fulfill({status:204,body:''}));
 const home=require(`../locales/${code}/home-copy.json`);
 await page.goto(registry.locales[code].home);
 await expect(page.locator('.home-portrait img')).toHaveAttribute('alt',home['home.accessibility.an-artistic-rendition-of-saint-charbel-in-a-black']);
 await page.locator('#monthly-prayer details').evaluateAll(es=>es.forEach(e=>e.open=true));
 await expect(page.locator('.monthly-prayer-context')).toContainText(home['home.monthly-prayer.why-the-22nd-this-monthly-devotion-recalls-nouhad-el']);
 await page.locator('.monthly-prayer-context').scrollIntoViewIfNeeded();await page.screenshot({path:info.outputPath(code+'-home-safeguard.png')});
 if(supportedNovenaLocales.has(code)){
  const route=code==='en'?novena.english:novena.routes[code];
  await page.goto(route);
  const copy=require(`../locales/${code}/saint-charbel-novena-master-copy.json`);
  await expect(page.locator('main')).toContainText(copy[key]);
  await page.locator('main > section').nth(3).scrollIntoViewIfNeeded();
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
  await page.screenshot({path:info.outputPath(code+'-calendar.png')});
 }else{
  // Limited-launch locale (home/history only): the registry must honestly advertise
  // no localized novena route, and the English master must carry the visit.
  expect(registry.limitedLaunchLocales).toContain(code);
  expect(novena.routes[code]).toBeUndefined();
  expect(novena.discoveryRoutes[code]).toBeUndefined();
  const response=await page.goto(novena.english);
  expect(response.ok()).toBe(true);
  await expect(page.locator('html')).toHaveAttribute('lang','en');
  const english=require('../locales/en/saint-charbel-novena-master-copy.json');
  await expect(page.locator('main')).toContainText(english[key]);
  await expect(page.locator('main')).not.toContainText('saint-charbel-novena.');
  await page.locator('main > section').nth(3).scrollIntoViewIfNeeded();
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
  await page.screenshot({path:info.outputPath(code+'-calendar-english-fallback.png')});
 }
});
