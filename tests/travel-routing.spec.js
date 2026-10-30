const{test,expect}=require('@playwright/test');
const{default:AxeBuilder}=require('@axe-core/playwright');
const fs=require('node:fs');const config=JSON.parse(fs.readFileSync('locales/travel-routes.json'));const registry=JSON.parse(fs.readFileSync('locales/registry.json'));
const routes=new Set(['/travel',...config.destinations]);for(const name of ['travel','qadisha','qannoubine','qozhaya'])for(const route of Object.values(registry.authoredMirrors[name].routes))routes.add(route);
for(const route of routes)test(`${route} has a real body, working resources, full-page accessibility and route landmarks`,async({page,request})=>{
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.emulateMedia({reducedMotion:'reduce'});
 const response=await page.goto(route);expect(response.status()).toBe(200);
 await page.evaluate(async()=>{for(const image of document.images){image.loading='eager';await image.decode()}});
 await expect(page.locator('main')).toHaveCount(1);await expect(page.locator('h1')).not.toBeEmpty();
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy();expect(errors).toEqual([]);
 const axe=await new AxeBuilder({page}).analyze();expect(axe.violations).toEqual([]);
 await expect(page.locator('.travel-breadcrumb')).toBeVisible();
 const code=await page.locator('html').getAttribute('lang');const hub=code==='en'?'/travel':`/${code}/travel`;
 expect(await page.locator('.nav-parent[href$="travel"]').evaluate(a=>new URL(a.href).pathname)).toBe(hub);
 const menu=page.locator('.nav-sub a').filter({hasText:code==='en'?'Travel':JSON.parse(fs.readFileSync(`locales/${code}/travel.json`)).hubLabel});expect(await menu.count()).toBeGreaterThan(0);
 const links=await page.locator('main a[href],link[hreflang]').evaluateAll(es=>es.map(e=>e.href).filter(u=>u.startsWith(location.origin)&&!u.includes('#')));
 for(const url of new Set(links)){const r=await request.get(url);expect(r.ok(),`${route}: ${url}`).toBeTruthy();if((r.headers()['content-type']||'').includes('text/html'))expect(await r.text()).toContain('<main');}
});
for(const alias of Object.keys(config.englishAliases))test(`${alias} redirects to its canonical root page`,async({request})=>{
 const r=await request.get(alias,{maxRedirects:0});expect(r.status()).toBe(301);expect(r.headers().location).toBe(config.englishAliases[alias]);
});
for(const route of ['/ar/','/ar/annaya'])test(`${route} has a direct localized Travel route and preserves its language control`,async({page})=>{
 await page.goto(route);
 const registry=require('../locales/registry.json');
 const migratedHome=(route==='/ar/'&&registry.homepageMirrors?.renderLocales.includes('ar'))||(route==='/ar/annaya'&&registry.pageMirrors?.['annaya-master']?.renderLocales.includes('ar'));
 if(migratedHome){
  const parent=page.locator('header a.nav-parent[href="/ar/travel"]');
  await parent.click();
  if(await page.evaluate(()=>innerWidth<=820||matchMedia('(hover: none)').matches))await page.locator('header .nav-sub a[href="/ar/travel"]').click();
 }
 else await page.locator('.travel-hub-return').click();await expect(page).toHaveURL(/\/ar\/travel$/);await expect(page.locator('html')).toHaveAttribute('lang','ar');
});
