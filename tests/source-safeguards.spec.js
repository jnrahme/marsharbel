const{test,expect}=require('@playwright/test');
const registry=require('../locales/registry.json');
const key='saint-charbel-novena.when-to-pray-it.the-feast-falls-on-the-third-sunday-of-july-in-the-maronite';
for(const code of Object.keys(registry.locales))test(`${code} source-first safeguards stay readable`,async({page,baseURL},info)=>{
 await page.route('**/*',r=>new URL(r.request().url()).origin===new URL(baseURL).origin?r.continue():r.fulfill({status:204,body:''}));
 const home=require(`../locales/${code}/home-copy.json`);
 await page.goto(registry.locales[code].home);
 await expect(page.locator('.home-portrait img')).toHaveAttribute('alt',home['home.accessibility.an-artistic-rendition-of-saint-charbel-in-a-black']);
 await page.locator('#monthly-prayer details').evaluateAll(es=>es.forEach(e=>e.open=true));
 await expect(page.locator('.monthly-prayer-context')).toContainText(home['home.monthly-prayer.why-the-22nd-this-monthly-devotion-recalls-nouhad-el']);
 await page.locator('.monthly-prayer-context').scrollIntoViewIfNeeded();await page.screenshot({path:info.outputPath(code+'-home-safeguard.png')});
 const route=code==='en'?registry.pageMirrors['saint-charbel-novena-master'].english:registry.pageMirrors['saint-charbel-novena-master'].routes[code];
 await page.goto(route);
 const copy=require(`../locales/${code}/saint-charbel-novena-master-copy.json`);
 await expect(page.locator('main')).toContainText(copy[key]);
 await page.locator('main > section').nth(3).scrollIntoViewIfNeeded();
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
 await page.screenshot({path:info.outputPath(code+'-calendar.png')});
});
