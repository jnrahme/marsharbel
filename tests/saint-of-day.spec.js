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
  if(active){await expect(card).toBeVisible();await expect(card.locator('.home-saint-pair > a')).toHaveCount(2);await expect(card.locator('time')).toHaveText(label(active));}
  const results=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa','best-practice']).exclude('iframe[src*="youtube"]').analyze();
  expect(results.violations.map(v=>({id:v.id,nodes:v.nodes.map(n=>n.target)}))).toEqual([]);
 });
}
test('saint no-JS remains absent',async({browser},info)=>{
 test.skip(info.project.name!=='laptop');
 const context=await browser.newContext({javaScriptEnabled:false});const page=await context.newPage();
 await page.goto('/');await expect(page.locator('#saint-of-the-day')).toHaveCount(0);await context.close();
});
