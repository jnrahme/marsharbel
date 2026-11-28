const{test,expect}=require('@playwright/test');
const{default:AxeBuilder}=require('@axe-core/playwright');
for(const route of ['/de/biografie','/de/novene','/de/gedenktag','/de/miracles/'])test(`${route}: complete German page, honest language control and localized chrome`,async({page,baseURL},info)=>{
 await page.setViewportSize({width:info.project.name==='phone'?390:1440,height:900});
 await page.route('**/*',r=>new URL(r.request().url()).origin===new URL(baseURL).origin?r.continue():r.fulfill({status:204,body:''}));
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto(route,{waitUntil:'domcontentloaded'});await page.emulateMedia({reducedMotion:'reduce'});
 await expect(page.locator('html')).toHaveAttribute('lang','de');await expect(page.locator('#sc-language-select')).toHaveValue('de');
 await expect(page.locator('#sc-language-select option[value=en]')).toBeEnabled();
 if(route==='/de/miracles/')expect(await page.locator('.hero h1').evaluate(el=>{const node=el.firstChild;return [...node.textContent.matchAll(/\S+/g)].every(m=>{const r=document.createRange();r.setStart(node,m.index);r.setEnd(node,m.index+m[0].length);return r.getClientRects().length===1;});})).toBe(true);
 const original=await page.evaluate(()=>({url:location.href,main:document.querySelector('main').innerHTML,lang:document.documentElement.lang}));
 if(['/de/biografie','/de/novene'].includes(route)){await expect(page.locator('#sc-language-select option[value=fr]')).toBeEnabled();} else expect(await page.evaluate(()=>SC_LANGUAGE_SWITCH.request('fr'))).toBe(false);
 expect(await page.evaluate(()=>({url:location.href,main:document.querySelector('main').innerHTML,lang:document.documentElement.lang}))).toEqual(original);
 expect(await page.locator('main').innerText()).not.toContain('not available');
 for(const img of await page.locator('main img').all()){await img.scrollIntoViewIfNeeded();await expect.poll(()=>img.evaluate(e=>e.complete&&e.naturalWidth>0)).toBe(true);}
 if(route==='/de/novene'){const trigger=page.locator('.share-trigger').first();await expect(trigger).toContainText('Teilen');await trigger.click();const panel=page.locator('#'+await trigger.getAttribute('aria-controls'));await expect(panel).toBeVisible();await page.keyboard.press('Escape');await expect(panel).toBeHidden();}else await expect(page.locator('script[src*="share.js"]')).toHaveCount(0);
 if(route==='/de/novene'){await expect(page.locator('footer')).toContainText(require('../locales/de/saint-charbel-novena-master-copy.json')['saint-charbel-novena.footer.saint-charbel-novena-author-please-pray-for-the-person-who-m']);}else await expect(page.locator('footer a[href="/privacy-policy"]')).toHaveText('Datenschutzerklärung (Englisch)');
 if(route==='/de/novene')for(let i=1;i<=9;i++){await page.locator(`#nine-days nav a[href="#day-${i}"]`).click();await expect(page.locator(`#day-${i}`)).toBeInViewport();}
 await page.evaluate(async()=>{for(let y=0;y<document.body.scrollHeight;y+=700){scrollTo(0,y);await new Promise(r=>setTimeout(r,20));}scrollTo(0,0);});
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);expect(errors).toEqual([]);
 const axe=await new AxeBuilder({page}).analyze();expect(axe.violations).toEqual([]);
 await page.screenshot({path:info.outputPath('german-hero.png')});
 let n=0;for(const section of await page.locator('main > section').all()){await section.scrollIntoViewIfNeeded();await page.screenshot({path:info.outputPath('section-'+(++n)+'.png')});}
 const retainedHash=new URL(page.url()).hash;const english=await page.locator('link[rel=alternate][hreflang=en]').getAttribute('href');await page.selectOption('#sc-language-select','en');await expect(page).toHaveURL(baseURL+new URL(english).pathname+retainedHash);await expect(page.locator('html')).toHaveAttribute('lang','en');
});
