const {test,expect}=require('@playwright/test');
const {default:AxeBuilder}=require('@axe-core/playwright');
const fs=require('node:fs');
const routes=[];
for(const lang of ['ar','fr','es','pt','it','de','pl']){
  for(const file of fs.readdirSync(lang).filter(f=>f.endsWith('.html'))){
    const html=fs.readFileSync(`${lang}/${file}`,'utf8');
    if(!/<body[^>]*class="[^"]*travel-page/.test(html)||!html.includes('enc-language'))continue;
    const canonical=html.match(/<link\s+rel="canonical"\s+href="https:\/\/marsharbel.com([^"]+)"/);
    if(canonical)routes.push(canonical[1]);
  }
}
for(const route of routes)test(`${route}: open Legacy discloses English destinations visibly`,async({page,baseURL},info)=>{
  await page.setViewportSize({width:info.project.name==='phone'?390:1440,height:900});
  await page.route('**/*',r=>new URL(r.request().url()).origin===new URL(baseURL).origin?r.continue():r.fulfill({status:204,body:''}));
  await page.goto(route,{waitUntil:'domcontentloaded'});
  const parent=page.locator('header .nav-parent[href="/saint-charbel-encyclopedia"]');
  if(await page.evaluate(()=>matchMedia('(hover: none)').matches||innerWidth<=820))await parent.click();else await parent.hover();
  const group=page.locator('header .nav-group').filter({has:page.locator('.nav-parent[href="/saint-charbel-encyclopedia"]')});
  const qualifiers=group.locator('.enc-language');
  await expect(qualifiers).toHaveCount(2);
  for(const qualifier of await qualifiers.all()){
    await expect(qualifier).toBeVisible();
    expect((await qualifier.innerText()).trim()).not.toBe('');
    const style=await qualifier.evaluate(el=>{const s=getComputedStyle(el);return{color:s.color,opacity:Number(s.opacity)}});
    expect(style.color).toBe('rgb(243, 237, 227)');
    expect(style.opacity).toBeGreaterThanOrEqual(.8);
  }
  const contrast=await new AxeBuilder({page}).include('header .enc-language').withRules(['color-contrast']).analyze();
  expect(contrast.violations).toEqual([]);
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
  if(route==='/ar/travel')await page.screenshot({path:info.outputPath('legacy-english-disclosure.png')});
});
