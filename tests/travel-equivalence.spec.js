const{test,expect}=require('@playwright/test');
const registry=require('../locales/registry.json');
for(const family of ['annaya-master','twenty-second-master','pilgrimage-master'])for(const[lang,route]of Object.entries(registry.pageMirrors[family].routes))test(`${family} ${lang} has9 available choices and switches to reviewed FR then EN`,async({page})=>{
 await page.goto(route);
 await expect(page.locator('#sc-language-select')).toHaveCount(1);
 for(const code of Object.keys(registry.locales))await expect(page.locator(`#sc-language-select option[value="${code}"]`)).toBeEnabled();
 const target=lang==='fr'?'ar':'fr';await page.selectOption('#sc-language-select',target);await expect(page).toHaveURL(new RegExp(registry.pageMirrors[family].routes[target]+'$'));await expect(page.locator('html')).toHaveAttribute('lang',target);
 await page.selectOption('#sc-language-select','en');await expect(page).toHaveURL(new RegExp(registry.pageMirrors[family].english+'$'));await expect(page.locator('html')).toHaveAttribute('lang','en');
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
});
test('genuinely pending Russian prayer translation remains disabled',async({page})=>{await page.goto('/saint-charbel-prayers');await expect(page.locator('#sc-language-select option[value="ru"]')).toBeDisabled();});
