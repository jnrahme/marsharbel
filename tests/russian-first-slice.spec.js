const {test,expect}=require('@playwright/test');
const {default:AxeBuilder}=require('@axe-core/playwright');
const registry=require('../locales/registry.json');
const expectedLocales=['en','ar','fr','es','pt','it','de','pl','ru','hi','th'];
async function assertOptions(page){
 expect(Object.keys(registry.locales)).toEqual(expectedLocales);
 await expect(page.locator('#sc-language-select option')).toHaveCount(expectedLocales.length);
 expect(await page.locator('#sc-language-select option').evaluateAll(nodes=>nodes.map(n=>n.value))).toEqual(expectedLocales);
}
test.beforeEach(async({page})=>{await page.addInitScript(()=>window.__SC_QA_TRAFFIC__=true);await page.route('**/*',route=>{const u=new URL(route.request().url());return ['127.0.0.1','localhost'].includes(u.hostname)?route.continue():route.abort()})});
for(const route of ['/ru/','/ru/biography'])test(`${route}: Cyrillic, loaded assets, usable links and no horizontal overflow`,async({page})=>{
 const errors=[],bad=[];page.on('pageerror',e=>errors.push(e.message));page.on('response',r=>{if(new URL(r.url()).hostname==='127.0.0.1'&&r.status()>=400)bad.push(r.url())});await page.goto(route,{waitUntil:'domcontentloaded'});await expect(page.locator('html')).toHaveAttribute('lang','ru');await expect(page.locator('h1')).toContainText('Шарбел');if(route==='/ru/biography')await expect(page.locator('h1')).toContainText('Махлуф');if(route==='/ru/biography'){for(const region of await page.locator('.history-table-wrap').all()){await expect(region).toHaveAttribute('tabindex','0');await expect(region).toHaveAttribute('role','region');await expect(region).toHaveAttribute('aria-label',/по горизонтали/);await region.focus();await expect(region).toBeFocused();}}await assertOptions(page);await expect(page.locator('#sc-language-select')).toHaveValue('ru');
 await page.evaluate(async()=>{for(let y=0;y<document.body.scrollHeight;y+=700){window.scrollTo(0,y);await new Promise(r=>setTimeout(r,15))}});await expect.poll(()=>page.evaluate(()=>[...document.querySelectorAll('main img')].every(i=>i.complete&&i.naturalWidth>0))).toBe(true);expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);expect(errors).toEqual([]);expect(bad).toEqual([]);const a11y=await new AxeBuilder({page}).analyze();expect(a11y.violations).toEqual([]);
 if(route==='/ru/'){await page.locator('main a[href="/ru/biography"]').first().click();await expect(page).toHaveURL(/\/ru\/biography$/)}else{await page.evaluate(()=>window.scrollTo(0,0));const before=page.url();await expect(page.locator('#sc-language-select option[value="de"]')).toBeEnabled();await page.selectOption('#sc-language-select','en');await expect(page).toHaveURL(/\/history$/);await expect(page.locator('html')).toHaveAttribute('lang','en')}
});

for(const route of ['/ru/annaya','/ru/molitvy','/ru/novena'])test(`${route}: all eleven choices and page-specific HI/TH refusal`,async({page})=>{
 await page.goto(route);await assertOptions(page);
 for(const code of ['hi','th']){
  const option=page.locator(`#sc-language-select option[value="${code}"]`);
  await expect(option).toBeDisabled();await expect(option).toContainText(registry.locales[code].nativeName);
  await expect(option).toContainText(require('../locales/same-page-copy.json').ru.suffix);
  const before=await page.evaluate(()=>({url:location.href,main:document.querySelector('main').innerHTML,lang:document.documentElement.lang}));
  expect(await page.evaluate(c=>window.SC_LANGUAGE_SWITCH.request(c),code)).toBe(false);
  expect(await page.evaluate(()=>({url:location.href,main:document.querySelector('main').innerHTML,lang:document.documentElement.lang}))).toEqual(before);
  await expect(page.locator('#sc-language-status')).toHaveText(require('../locales/same-page-copy.json').ru.unavailable);
  if(route==='/ru/annaya')await expect(page.locator(`footer a[hreflang="${code}"]`).first()).toHaveAttribute('href',registry.locales[code].home);
 }
 await expect(page.locator('#sc-language-select option[value="en"]')).toBeEnabled();
});
