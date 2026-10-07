const {test,expect}=require('@playwright/test');
const registry=require('../locales/registry.json');
const contract=require('../locales/prayer-equivalence.json');
for(const family of ['saint-charbel-prayers-master','saint-charbel-novena-master'])for(const [lang,route]of Object.entries({en:registry.pageMirrors[family].english,...registry.pageMirrors[family].routes}))test(`${route} prayer selection respects gated exact twins`,async({page,baseURL})=>{
 await page.route('**/*',r=>new URL(r.request().url()).origin===new URL(baseURL).origin?r.continue():r.fulfill({status:204,body:''}));
 const response=await page.goto(route);expect(response.status()).toBe(200);
 // Browser URL is the post-redirect entry, not merely the requested path.
 await expect(page).toHaveURL(baseURL+route);
 await expect(page.locator('head link[rel=canonical]')).toHaveAttribute('href',registry.site+route);
 const active=contract.gateStatus==='approved';
 for(const code of ['en','ar','de','fr','ru','pt','it','pl','es']){
  const option=page.locator(`#sc-language-select option[value="${code}"]`);
  if(active||code===lang||code==='en')await expect(option).toBeEnabled();else await expect(option).toBeDisabled();
 }
 expect(await page.evaluate(()=>SC_LANGUAGE_SWITCH.request('zz'))).toBe(false);
 if(active){
  for(const target of ['ar','de','fr','ru','pt','it','pl','es','en']){
   const path=target==='en'?registry.pageMirrors[family].english:registry.pageMirrors[family].routes[target];
   await page.selectOption('#sc-language-select',target);await expect(page).toHaveURL(baseURL+path);await expect(page.locator('html')).toHaveAttribute('lang',target);
  }
  if(family==='saint-charbel-novena-master'){
   await page.goto(registry.pageMirrors[family].routes.ar+'#day-6');await page.selectOption('#sc-language-select','fr');await expect(page).toHaveURL(baseURL+registry.pageMirrors[family].routes.fr+'#day-6');await expect(page.locator('#day-6')).toBeInViewport();
  }
 }else{
  const before=page.url(),target=lang==='fr'?'de':'fr';expect(await page.evaluate(code=>SC_LANGUAGE_SWITCH.request(code),target)).toBe(false);expect(page.url()).toBe(before);
 }
});
