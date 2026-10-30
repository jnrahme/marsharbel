const {test,expect}=require('@playwright/test');
test('Arabic miracles keeps pending locales honest and English source clickable',async({page,baseURL},info)=>{
 await page.route('**/*',r=>new URL(r.request().url()).origin===new URL(baseURL).origin?r.continue():r.fulfill({status:204,body:''}));
 await page.goto('/ar/miracles/');
 await expect(page.locator('#sc-language-select')).toHaveCount(1);
 await expect(page.locator('#sc-language-select')).toHaveValue('ar');
 await expect(page.locator('#sc-language-select option[value=en]')).toBeEnabled();
 for(const code of ['fr','es','pt','it','de','pl','ru'])await expect(page.locator(`#sc-language-select option[value=${code}]`)).toBeDisabled();
 const before=page.url();expect(await page.evaluate(()=>SC_LANGUAGE_SWITCH.request('fr'))).toBe(false);expect(page.url()).toBe(before);
 await page.screenshot({path:info.outputPath('miracles-english-enabled.png')});
 await page.selectOption('#sc-language-select','en');
 await expect(page).toHaveURL(baseURL+'/miracles/');
 await expect(page.locator('html')).toHaveAttribute('lang','en');
 await expect(page.locator('#sc-language-select option[value=en]')).toBeEnabled();
});
