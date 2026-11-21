const{test,expect}=require('@playwright/test');const AxeBuilder=require('@axe-core/playwright').default;const registry=require('../locales/registry.json');
for(const route of ['/ar/','/fr/'])for(const js of [true,false])test(`${route} native section navigation JS=${js}`,async({browser,baseURL},info)=>{
 const c=await browser.newContext({javaScriptEnabled:js,viewport:{width:info.project.name==='phone'?390:1440,height:900}});const p=await c.newPage();await p.route('**/*',r=>new URL(r.request().url()).origin===new URL(baseURL).origin?r.continue():r.abort());await p.goto(baseURL+route,{waitUntil:'domcontentloaded'});// Mirrored homes reuse the English header and its single app selector.
 // Native section links already exist in the English footer; a guide-only
 // header nav would violate mirror parity and duplicate language controls.
 const mirrored=registry.homepageMirrors?.renderLocales.includes(route.split('/')[1]);
 const nav=p.locator(mirrored?'footer nav.footer-locales':'header nav.locale-nav[data-locale-section-navigation]');await expect(nav).toHaveCount(1);
 for(const[code,cfg]of Object.entries(registry.locales).filter(([,cfg])=>cfg.capabilities?.home!==false&&cfg.home)){const a=nav.locator(`a[hreflang="${code}"]`);await expect(a).toHaveText(cfg.nativeName);await expect(a).toHaveAttribute('href',cfg.home);await expect(a).not.toHaveAttribute('aria-disabled');await expect(a).not.toHaveAttribute('data-language-switch');}
 for(const[code,cfg]of Object.entries(registry.locales).filter(([,cfg])=>cfg.capabilities?.home===false||!cfg.home))await expect(nav.locator(`a[hreflang="${code}"]`)).toHaveCount(0);
 await expect(nav.locator('.sc-language-helper,.sc-unavailable-suffix')).toHaveCount(0);
 if(js){const before=await p.evaluate(()=>({url:location.href,main:document.querySelector('main').innerHTML,lang:document.documentElement.lang}));await expect(p.locator('#sc-language-select option[value=de]')).toBeEnabled();expect((await new AxeBuilder({page:p}).include('header').analyze()).violations).toEqual([]);expect(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);await p.screenshot({path:info.outputPath('home-navigation.png')});expect(await p.evaluate(()=>SC_LANGUAGE_SWITCH.request('de'))).toBe(true);await expect(p).toHaveURL(baseURL+'/de/');}
 await c.close();
});
