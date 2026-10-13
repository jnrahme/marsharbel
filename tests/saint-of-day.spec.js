const {test,expect}=require('@playwright/test');
const AxeBuilder=require('@axe-core/playwright').default;
for(const path of ['/','/ar/','/hi/','/th/'])for(const [date,active] of [['2026-10-13T23:59:59-04:00',false],['2026-10-14T12:00:00-04:00',true],['2026-10-15T00:00:00-04:00',false]]){
 test(`saint date and axe ${path} ${date}`,async({page},info)=>{
  test.skip(!['phone','laptop'].includes(info.project.name));
  await page.route(url=>!['127.0.0.1','localhost'].includes(new URL(url).hostname),r=>r.abort());
  await page.emulateMedia({reducedMotion:'reduce'});
  await page.clock.setFixedTime(new Date(date));
  await page.goto(path,{waitUntil:'load'});
  const card=page.locator('#saint-of-the-day');
  await expect(card).toHaveCount(active?1:0);
  if(active){await expect(card).toBeVisible();await expect(card.locator('.home-saint-pair > a')).toHaveCount(2);await expect(card.locator('time')).toHaveText('14.10.2026');}
  const results=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa','best-practice']).exclude('iframe[src*="youtube"]').analyze();
  expect(results.violations.map(v=>({id:v.id,nodes:v.nodes.map(n=>n.target)}))).toEqual([]);
 });
}
test('saint no-JS remains absent',async({browser},info)=>{
 test.skip(info.project.name!=='laptop');
 const context=await browser.newContext({javaScriptEnabled:false});const page=await context.newPage();
 await page.goto('/');await expect(page.locator('#saint-of-the-day')).toHaveCount(0);await context.close();
});
