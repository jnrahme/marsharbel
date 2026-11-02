const {test,expect}=require('@playwright/test');
const AxeBuilder=require('@axe-core/playwright').default;
const fs=require('fs');
const manifest=JSON.parse(fs.readFileSync('locales/saint-of-day.json','utf8'));
const dates=Object.keys(manifest.entries).sort();
function shift(date,days){const d=new Date(date+'T12:00:00-04:00');d.setDate(d.getDate()+days);return d.toISOString().slice(0,10);}
function label(date){const[y,m,dd]=date.split('-');return `${dd}.${m}.${y}`;}
const clocks=[];
if(dates.length){
 clocks.push([shift(dates[0],-1),null]);
 for(const d of dates)clocks.push([d,d]);
 clocks.push([shift(dates[dates.length-1],1),null]);
}
for(const path of ['/','/ar/','/hi/','/th/'])for(const [date,active] of clocks){
 test(`saint date and axe ${path} ${date}`,async({page},info)=>{
  test.skip(!['phone','laptop'].includes(info.project.name));
  await page.route(url=>!['127.0.0.1','localhost'].includes(new URL(url).hostname),r=>r.abort());
  await page.emulateMedia({reducedMotion:'reduce'});
  await page.clock.setFixedTime(new Date(`${date}T12:00:00-04:00`));
  await page.goto(path,{waitUntil:'load'});
  const card=page.locator('#saint-of-the-day');
  await expect(card).toHaveCount(active?1:0);
  if(active){
   await expect(card).toBeVisible();await expect(card.locator('time[data-saint-generated-date="dateLabel"]')).toHaveText(label(active));
   if(manifest.entries[active].bookUrl){
    await expect(card.locator('.home-saint-pair > a')).toHaveCount(2);
   }else{
    await expect(card.locator('.home-saint-pair')).toHaveCount(0);
    await expect(card.locator('a.home-saint-info')).toHaveCount(1);
    await expect(card.locator('img')).toHaveCount(0);
   }
  }
  const results=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa','best-practice']).exclude('iframe[src*="youtube"]').analyze();
  expect(results.violations.map(v=>({id:v.id,nodes:v.nodes.map(n=>n.target)}))).toEqual([]);
 });
}
test('saint no-JS remains absent',async({browser},info)=>{
 test.skip(info.project.name!=='laptop');
 const context=await browser.newContext({javaScriptEnabled:false});const page=await context.newPage();
 await page.goto('/');await expect(page.locator('#saint-of-the-day')).toHaveCount(0);await context.close();
});

// No-book units: single-column info card holds at 390px with 200% text, no sideways scroll, axe clean.
for(const d of dates.filter(d=>!manifest.entries[d].bookUrl))for(const path of ['/','/ar/']){
 test(`saint no-book 390px 200% ${path} ${d}`,async({page},info)=>{
  test.skip(info.project.name!=='laptop');
  await page.route(url=>!['127.0.0.1','localhost'].includes(new URL(url).hostname),r=>r.abort());
  await page.clock.setFixedTime(new Date(`${d}T12:00:00-04:00`));
  await page.goto(path,{waitUntil:'load'});
  await page.setViewportSize({width:390,height:800});
  await page.addStyleTag({content:'html{font-size:200% !important}'});
  await page.waitForTimeout(300);
  const card=page.locator('#saint-of-the-day');
  await expect(card).toBeVisible();
  await expect(card.locator('img')).toHaveCount(0);
  const bad=await page.evaluate(()=>{
   const out=[];
   if(document.documentElement.scrollWidth>window.innerWidth+1)out.push('page sideways scroll');
   const c=document.querySelector('#saint-of-the-day');const cb=c.getBoundingClientRect();
   for(const e of c.querySelectorAll('*')){
    const b=e.getBoundingClientRect();
    if(b.width&&getComputedStyle(e).position!=='absolute'&&(b.right>cb.right+1||b.left<cb.left-1))out.push(e.tagName+'.'+e.className);
   }
   return out;
  });
  expect(bad).toEqual([]);
  const results=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa','best-practice']).exclude('iframe[src*="youtube"]').analyze();
  expect(results.violations.map(v=>({id:v.id,nodes:v.nodes.map(n=>n.target)}))).toEqual([]);
 });
}
