const {test,expect}=require('@playwright/test');
const registry=require('../locales/registry.json');
const homes=registry.homePublicationLocales.map(c=>[c,registry.locales[c].home]);
for(const [code,home] of homes){
 test(`MB16 home ${code} offers all published homes`,async({page})=>{
  await page.goto(home);await expect(page.locator('html')).toHaveAttribute('lang',code);
  for(const [target,path] of homes){
   await expect(page.locator(`#sc-language-select option[value="${target}"]`)).toBeEnabled();
   const result=await page.evaluate(c=>window.SC_SAME_PAGE.resolve(window.SC_SAME_PAGE_MANIFEST,location.href,c,document.documentElement.lang),target);
   expect(new URL(result.href).pathname).toBe(path);
  }
  await page.selectOption('#sc-language-select',code==='en'?'zh-Hans':'en');
  await expect(page).toHaveURL(new RegExp(code==='en'?'/zh-Hans/$':'/$'));
  await expect(page.locator('html')).toHaveAttribute('lang',code==='en'?'zh-Hans':'en');
 });
}
for(const source of ['/saint-charbel-movie','/saint-charbel-oil'])for(const [code,home] of homes.filter(([c])=>c!=='en')){
 test(`MB16 ${source} ${code} navigates to published home`,async({page})=>{
  await page.goto(source);await expect(page.locator(`#sc-language-select option[value="${code}"]`)).toBeEnabled();
  await page.selectOption('#sc-language-select',code);await expect(page).toHaveURL(new RegExp(home+'$'));
  await expect(page.locator('html')).toHaveAttribute('lang',code);
 });
}
for(const route of ['/saint-charbel-prayers','/fr/prieres','/es/oraciones','/ru/molitvy','/ar/prayers']){
 test(`MB16 prayer twin ${route}`,async({page})=>{
  await page.goto(route);await page.selectOption('#sc-language-select',route==='/fr/prieres'?'ar':'fr');
  await expect(page).toHaveURL(route==='/fr/prieres'?/\/ar\/prayers$/:/\/fr\/prieres$/);
 });
}
test('MB16 Chinese home is distinct from Chinese travel',async({page})=>{
 await page.goto('/zh-Hans/');const title=await page.locator('h1').innerText();
 await page.goto('/zh-Hans/travel');expect(await page.locator('h1').innerText()).not.toBe(title);
 await page.selectOption('#sc-language-select','en');await expect(page).toHaveURL(/\/travel$/);
});
