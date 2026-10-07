const {test,expect}=require('@playwright/test');
const registry=require('../locales/registry.json');
for(const code of Object.keys(registry.locales))test(`${code} explicit choice persists across reviewed navigation`,async({page})=>{
 await page.goto('/');await page.evaluate(c=>window.SC_LANGUAGE_SWITCH.request(c),code);
 await expect(page).toHaveURL(new RegExp(registry.locales[code].home+'$'));
 await expect(page.locator('#sc-language-select')).toHaveValue(code);
 await expect(page.locator('html')).toHaveAttribute('lang',code);
 expect(await page.evaluate(()=>localStorage.getItem('sc_last_explicit_language'))).toBe(code);
 const link=page.locator('main a[href="/history"], main a[href="./history"], main a[href="'+(registry.pageMirrors['history-master'].routes[code]||'/history')+'"]').first();
 await link.scrollIntoViewIfNeeded();await link.click();
 await expect(page.locator('html')).toHaveAttribute('lang',code);
 expect(await page.evaluate(()=>localStorage.getItem('sc_last_explicit_language'))).toBe(code);
});
for(const code of ['hi','th'].filter(c=>registry.locales[c]))test(`${code} honest English fallback retains choice and later returns to localized history`,async({page})=>{
 await page.goto('/');await page.evaluate(c=>window.SC_LANGUAGE_SWITCH.request(c),code);
 await expect(page).toHaveURL(new RegExp(registry.locales[code].home+'$'));
 await expect(page.locator('#sc-language-select')).toHaveValue(code);
 await page.goto('/news');await expect(page.locator('html')).toHaveAttribute('lang','en');
 expect(await page.evaluate(()=>localStorage.getItem('sc_last_explicit_language'))).toBe(code);
 await page.evaluate(()=>{const a=document.createElement('a');a.href='/history';a.id='persistence-test-history';a.textContent='History';document.querySelector('main').prepend(a);});
 await page.locator('#persistence-test-history').click();await expect(page.locator('html')).toHaveAttribute('lang',code);
});
for(const code of ['ar','de','fr','es','pt','it','pl','ru'])test(`${code} saved explicit choice routes an English internal history link to its reviewed twin`,async({page})=>{
 await page.goto('/');await page.evaluate(c=>window.SC_LANGUAGE_SWITCH.request(c),code);
 await expect(page).toHaveURL(new RegExp(registry.locales[code].home+'$'));
 await page.goto('/news');await expect(page.locator('html')).toHaveAttribute('lang','en');
 await page.evaluate(()=>{const a=document.createElement('a');a.href='/history';a.id='persistent-history-link';a.textContent='History';document.querySelector('main').prepend(a);});
 await page.locator('#persistent-history-link').click();
 await expect(page).toHaveURL(new RegExp(registry.pageMirrors['history-master'].routes[code]+'$'));
 await expect(page.locator('html')).toHaveAttribute('lang',code);
});
test('footer choice persists but explicit English source remains English',async({page})=>{
 await page.goto('/');await page.locator('footer a[hreflang="de"]').click();await expect(page).toHaveURL(/\/de\/$/);
 expect(await page.evaluate(()=>localStorage.getItem('sc_last_explicit_language'))).toBe('de');
 await page.goto('/news');await page.evaluate(()=>{const a=document.createElement('a');a.href='/history';a.hreflang='en';a.id='explicit-english-link';a.textContent='English source';document.querySelector('main').prepend(a);});
 await page.locator('#explicit-english-link').click();await expect(page).toHaveURL(/\/history$/);await expect(page.locator('html')).toHaveAttribute('lang','en');
 expect(await page.evaluate(()=>localStorage.getItem('sc_last_explicit_language'))).toBe('en');
});
