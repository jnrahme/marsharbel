const {test,expect}=require('@playwright/test');
for(const width of [390,1440])for(const route of ['/','/story','/history','/travel'])test(`${route} at ${width} keeps compact header without blanket unavailable helper`,async({page})=>{
 await page.route(url=>!['127.0.0.1','localhost'].includes(new URL(url).hostname),r=>r.abort());
 await page.setViewportSize({width,height:844});await page.goto(route,{waitUntil:'domcontentloaded'});await page.waitForFunction(()=>window.SC_LANGUAGE_SWITCH);
 const height=()=>page.locator('header.topbar').evaluate(el=>el.getBoundingClientRect().height);
 const before=await height();if(width===390)expect(before).toBeLessThanOrEqual(105);
 await expect(page.locator('#sc-language-helper')).toHaveCount(0);
 await expect(page.locator('#sc-language-select')).not.toHaveAttribute('aria-describedby','sc-language-helper');
 await page.locator('#sc-language-select').focus();await expect(page.locator('.sc-language-feedback')).not.toHaveClass(/is-open/);
 for(const option of await page.locator('#sc-language-select option:disabled').all())await expect(option).toContainText('not available');
 expect(await height()).toBe(before);await page.keyboard.press('Tab');expect(await height()).toBe(before);
});
