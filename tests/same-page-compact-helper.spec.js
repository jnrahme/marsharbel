const {test,expect}=require('@playwright/test');
for(const width of [390,1440])for(const route of ['/','/story','/history','/travel'])test(`${route} at ${width} preserves compact header with discoverable pending translation note`,async({page})=>{
 await page.route(url=>!['127.0.0.1','localhost'].includes(new URL(url).hostname),r=>r.abort());
 await page.setViewportSize({width,height:844});await page.goto(route,{waitUntil:'domcontentloaded'});await page.waitForFunction(()=>window.SC_LANGUAGE_SWITCH);
 const height=()=>page.locator('header.topbar').evaluate(el=>el.getBoundingClientRect().height);
 const before=await height();console.log(route,'compact header height',before);if(width===390)expect(before).toBeLessThanOrEqual(105);
 await expect(page.locator('#sc-language-select')).toHaveAttribute('aria-describedby','sc-language-helper');
 await expect(page.locator('#sc-language-helper')).toHaveText('Some translations are not available for this page.');
 await expect(page.locator('.sc-language-feedback')).not.toHaveClass(/is-open/);
 await page.locator('#sc-language-select').focus();await expect(page.locator('.sc-language-feedback')).toHaveClass(/is-open/);
 expect(await height()).toBe(before);
 const box=await page.locator('.sc-language-feedback').boundingBox();expect(box.width).toBeGreaterThan(100);expect(box.x).toBeGreaterThanOrEqual(0);expect(box.x+box.width).toBeLessThanOrEqual(width);
 await page.keyboard.press('Tab');await expect(page.locator('.sc-language-feedback')).not.toHaveClass(/is-open/);
 expect(await height()).toBe(before);
});
