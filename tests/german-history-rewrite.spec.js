const{test,expect}=require('@playwright/test');
for(const width of[390,1440])test(`complete German history rewrite at ${width}`,async({page,baseURL},info)=>{
 await page.setViewportSize({width,height:900});await page.route('**/*',r=>new URL(r.request().url()).origin===new URL(baseURL).origin?r.continue():r.abort());await page.goto('/de/biografie',{waitUntil:'domcontentloaded'});await page.emulateMedia({reducedMotion:'reduce'});
 await expect(page.locator('main > section')).toHaveCount(17);await expect(page.locator('main img')).toHaveCount(5);await expect(page.locator('h1')).toHaveText('Das Leben des heiligen Charbel Makhlouf');
 expect((await page.locator('main').innerText()).split(/\s+/).length).toBeGreaterThan(3000);
 for(const anchor of await page.locator('main a[href^="#"]').all()){const href=await anchor.getAttribute('href');await expect(page.locator(href)).toHaveCount(1);await anchor.click();await expect(page.locator(href)).toBeInViewport();}
 for(const img of await page.locator('main img').all()){await img.scrollIntoViewIfNeeded();await expect.poll(()=>img.evaluate(e=>e.complete&&e.naturalWidth>0)).toBe(true);expect(await img.getAttribute('alt')).not.toMatch(/Old black|Snow-covered|The front|A carved/);}
 const text=await page.locator('main').innerText();for(const fragment of ['nach der englischen Fassung des MARI','unsere Übersetzung aus dem Französischen','in deutscher Wiedergabe des zitierten Fragments','engelhaft und nicht menschlich','Berichte unterscheiden sich'])expect(text).toContain(fragment);
 for(const table of await page.locator('main table').all()){await table.scrollIntoViewIfNeeded();expect(await table.evaluate(e=>e.getBoundingClientRect().right<=innerWidth)).toBe(true);await page.screenshot({path:info.outputPath('table-'+await table.count()+'-'+await table.locator('tr').count()+'.png')});}
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
});
