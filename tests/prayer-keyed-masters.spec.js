const {test,expect}=require('@playwright/test');
const AxeBuilder=require('@axe-core/playwright').default;
const registry=require('../locales/registry.json');
for(const family of ['saint-charbel-prayers-master','saint-charbel-novena-master'])for(const [lang,route]of Object.entries(registry.pageMirrors[family].routes))for(const width of [320,390,1280])test(`${route} full keyed master ${width}px`,async({page,baseURL},info)=>{
 await page.setViewportSize({width,height:900});await page.emulateMedia({reducedMotion:'reduce'});
 await page.route('**/*',r=>new URL(r.request().url()).origin===new URL(baseURL).origin?r.continue():r.fulfill({status:204,body:''}));
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 const response=await page.goto(route);expect(response.status()).toBe(200);
 await expect(page.locator('html')).toHaveAttribute('lang',lang);await expect(page.locator('html')).toHaveAttribute('dir',registry.locales[lang].direction);
 await expect(page.locator('#sc-language-select')).toHaveValue(lang);
 const binding=require(`../locales/en/${family}-bindings.json`).bindings.find(b=>b.kind==='text'&&/(^| > )h1(:nth-of-type\(\d+\))?$/.test(b.selector));
 await expect(page.locator('h1')).toHaveText(require(`../locales/${lang}/${family}-copy.json`)[binding.key]);
 for(const [code,path]of Object.entries(registry.pageMirrors[family].discoveryRoutes))await expect(page.locator(`head link[hreflang="${code}"]`)).toHaveAttribute('href',registry.site+path);
 for(const a of await page.locator('main a[href^="#"]').all()){const target=await a.getAttribute('href');await expect(page.locator(target)).toHaveCount(1);await a.click();await expect(page.locator(target)).toBeInViewport();}
 for(const image of await page.locator('main img').all()){await image.scrollIntoViewIfNeeded();await expect.poll(()=>image.evaluate(e=>e.complete&&e.naturalWidth>0)).toBe(true);}
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);expect(errors).toEqual([]);
 expect((await new AxeBuilder({page}).analyze()).violations).toEqual([]);
 // Tile the full page to stay below mobile compositor surface limits.
 const height=await page.evaluate(()=>document.documentElement.scrollHeight);
 for(let y=0,n=0;y<height;y+=800){await page.evaluate(y=>scrollTo(0,y),y);await page.screenshot({path:info.outputPath(`page-tile-${n++}.png`)});}
 await page.evaluate(()=>scrollTo(0,0));
 await expect(page.locator('#sc-language-select option[value=en]')).toBeEnabled();const anchor=new URL(page.url()).hash;await page.selectOption('#sc-language-select','en');await expect(page).toHaveURL(baseURL+registry.pageMirrors[family].english+anchor);await expect(page.locator('html')).toHaveAttribute('lang','en');
});
