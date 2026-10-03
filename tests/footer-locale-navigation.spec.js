const{test,expect}=require('@playwright/test');
const{default:AxeBuilder}=require('@axe-core/playwright');
for(const route of ['/','/history','/saint-charbel-novena','/miracles/'])for(const js of [true,false])test(`${route} footer section navigation, JS=${js}`,async({browser,baseURL},info)=>{
 const context=await browser.newContext({javaScriptEnabled:js,viewport:{width:info.project.name==='phone'?390:1440,height:900}});
 const page=await context.newPage();await page.route('**/*',r=>new URL(r.request().url()).origin===new URL(baseURL).origin?r.continue():r.abort());
 await page.goto(baseURL+route,{waitUntil:'domcontentloaded'});
 const nav=page.locator('nav.footer-locales');await expect(nav).toHaveCount(1);
 const names={en:'English',ar:'العربية',fr:'Français',es:'Español',pt:'Português',it:'Italiano',de:'Deutsch',pl:'Polski'};
 const homes={en:'/',ar:'/ar/',fr:'/fr/',es:'/es/',pt:'/pt/',it:'/it/',de:'/de/',pl:'/pl/'};
 for(const [lang,home]of Object.entries(homes)){
  const a=nav.locator(`a[hreflang="${lang}"]`);await expect(a).toHaveAttribute('href',home);await expect(a).toHaveText(names[lang]);await expect(a).not.toHaveAttribute('aria-disabled','true');await expect(a).not.toHaveAttribute('tabindex','-1');await expect(a).not.toHaveAttribute('data-language-switch');
 }
 await expect(nav.locator('.sc-unavailable-suffix,.sc-language-helper')).toHaveCount(0);
 if(js){await nav.scrollIntoViewIfNeeded();const before=page.url();expect(await page.evaluate(()=>SC_LANGUAGE_SWITCH.request('fr'))).toBe(false);expect(page.url()).toBe(before);await expect(nav.locator('a[hreflang=fr]')).toHaveAttribute('href','/fr/');expect((await new AxeBuilder({page}).include('nav.footer-locales').analyze()).violations).toEqual([]);expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);await page.screenshot({path:info.outputPath('footer.png')});await nav.locator('a[hreflang=fr]').click();await expect(page).toHaveURL(baseURL+'/fr/');await expect(page.locator('html')).toHaveAttribute('lang','fr');}
 await context.close();
});
