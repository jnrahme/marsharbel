const {test,expect}=require('@playwright/test');
const registry=require('../locales/registry.json');
const homes=registry.homePublicationLocales;
const history=registry.pageMirrors['history-master'];
const prayers=registry.pageMirrors['saint-charbel-prayers-master'];
const locales=Object.keys(registry.locales);
for(const lang of locales){
 const routes=[];
 if(homes.includes(lang)) routes.push(['home',registry.locales[lang].home]);
 if(lang==='en')routes.push(['saint',history.english],['prayer',prayers.english]);
 else {
  if(history.renderLocales.includes(lang))routes.push(['saint',history.routes[lang]]);
  if(prayers.renderLocales.includes(lang))routes.push(['prayer',prayers.routes[lang]]);
 }
 for(const [kind,route]of routes)test(`growth regression ${lang} ${kind} ${route}`,async({page})=>{
  const response=await page.goto(route,{waitUntil:'domcontentloaded'});
  expect(response.status()).toBe(200);
  await expect(page.locator('html')).toHaveAttribute('lang',lang);
  await expect(page.locator('main h1').first()).toBeVisible();
  await expect(page.locator('#sc-language-select')).toBeVisible();
  const enabled=await page.locator('#sc-language-select option:not([disabled])').evaluateAll(nodes=>nodes.map(n=>n.value));
  expect(enabled).toContain(lang);
  if(lang!=='en'){
   expect(enabled).toContain('en');
   await page.selectOption('#sc-language-select','en');
   await expect(page.locator('html')).toHaveAttribute('lang','en');
   await expect(page.locator('main h1').first()).toBeVisible();
  }
 });
}
