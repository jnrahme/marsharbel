const {test,expect}=require('@playwright/test');
const routes={'/saint-charbel-prayers':'en','/saint-charbel-novena':'en','/ar/prayers':'ar','/ar/novena':'ar','/de/gebete':'de','/de/novene':'de','/fr/prieres':'fr','/fr/neuvaine':'fr','/ru/molitvy':'ru','/ru/novena':'ru'};
for(const [route,lang]of Object.entries(routes))test(`${route} reviewed share labels render and work`,async({page,baseURL},info)=>{
 await page.route('**/*',r=>new URL(r.request().url()).origin===new URL(baseURL).origin?r.continue():r.fulfill({status:204,body:''}));
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto(route);const labels=require(`../locales/${lang}/share.json`);
 await expect(page.locator('#sc-share-labels')).toHaveCount(1);
 const trigger=page.locator('.share-trigger').first();await expect(trigger).toContainText(labels['share.label']);
 await trigger.click();const panel=page.locator('#'+await trigger.getAttribute('aria-controls'));await expect(panel).toBeVisible();
 await expect(panel.locator('.share-copy')).toContainText(labels['share.copy.label']);await expect(panel.locator('.share-email')).toContainText(labels['share.target.email.label']);
 for(const a of await panel.locator('a.share-btn').all())await expect(a).toHaveAttribute('aria-label',/.+/);
 await page.screenshot({path:info.outputPath('share-open.png')});
 await page.keyboard.press('Escape');await expect(panel).toBeHidden();await expect(trigger).toBeFocused();
 await trigger.click();await expect(panel).toBeVisible();expect(errors).toEqual([]);
});
