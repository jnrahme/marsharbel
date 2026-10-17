const{test,expect}=require('@playwright/test');
const registry=require('../locales/registry.json');
const reviewed=require('../locales/travel-equivalence.json').groups;
for(const family of ['annaya-master','twenty-second-master','pilgrimage-master'])for(const[lang,route]of Object.entries(registry.pageMirrors[family].routes).filter(([lang])=>Object.hasOwn(reviewed[family].variants,lang)))test(`${family} ${lang} retains reviewed choices and refuses unlocalized HI/TH and switches to reviewed FR then EN`,async({page})=>{
 await page.goto(route);
 await expect(page.locator('#sc-language-select')).toHaveCount(1);
 for(const code of Object.keys(registry.locales)){
  const option=page.locator(`#sc-language-select option[value="${code}"]`);
  if(code==='en'||Object.hasOwn(reviewed[family].variants,code))await expect(option).toBeEnabled();
  else {await expect(option).toBeDisabled();const before=page.url();await page.evaluate(c=>window.SC_LANGUAGE_SWITCH.request(c),code);expect(page.url()).toBe(before);}
 }
 const target=lang==='fr'?'ar':'fr';await page.selectOption('#sc-language-select',target);await expect(page).toHaveURL(new RegExp(registry.pageMirrors[family].routes[target]+'$'));await expect(page.locator('html')).toHaveAttribute('lang',target);
 await page.selectOption('#sc-language-select','en');await expect(page).toHaveURL(new RegExp(registry.pageMirrors[family].english+'$'));await expect(page.locator('html')).toHaveAttribute('lang','en');
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
});
test('published Polish prayer translation navigates to its keyed twin',async({page})=>{await page.goto('/saint-charbel-prayers');await expect(page.locator('#sc-language-select option[value="pl"]')).toBeEnabled();await page.selectOption('#sc-language-select','pl');await expect(page).toHaveURL(/\/pl\/modlitwy$/);await expect(page.locator('html')).toHaveAttribute('lang','pl');});

for(const [family,cfg] of Object.entries(registry.pageMirrors).filter(([_,cfg])=>cfg.renderLocales?.includes('zh-Hans') && cfg.routes?.['zh-Hans'])) {
 test(`partial ZH selector shows its actual language: ${family}`,async({page})=>{
  await page.goto(cfg.routes['zh-Hans']);
  const select=page.locator('#sc-language-select');
  await expect(select).toHaveValue('zh-Hans');
  await expect(select.locator('option:checked')).toHaveText('简体中文');
  await expect(select.locator('option[value="zh-Hans"]')).toBeEnabled();
  expect(await page.evaluate(()=>window.SC_SAME_PAGE_MANIFEST.publishedHomes['zh-Hans'])).toBeUndefined();
 });
}
