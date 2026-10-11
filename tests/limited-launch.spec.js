const {test,expect}=require('@playwright/test');
for(const lang of ['hi','th'])for(const surface of ['','history']){
 test(`${lang} ${surface||'home'} launch truth`,async({page},info)=>{
  test.setTimeout(60000);
  await page.goto(`/${lang}/${surface}`);await page.evaluate(()=>document.fonts.ready);
  await expect(page.locator('html')).toHaveAttribute('lang',lang);
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1)).toBeTruthy();
  expect(await page.evaluate(()=>document.fonts.check('16px "'+(document.documentElement.lang==='hi'?'Noto Serif Devanagari':'Noto Serif Thai')+'"'))).toBeTruthy();
  if(!surface){await expect(page.locator('.launch-availability')).toBeVisible();await expect(page.locator(`main a[href="/${lang}/history"]`).first()).toBeVisible();}
  for(const section of await page.locator('main > *').all()){await section.scrollIntoViewIfNeeded();await page.waitForTimeout(80);}
  await page.evaluate(()=>scrollTo(0,0));
  await page.screenshot({path:info.outputPath(`hi-th-${lang}-${surface||'home'}-${info.project.name}.png`),fullPage:true,scale:'css',timeout:20000});
 });
}
