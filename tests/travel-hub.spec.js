const {test,expect}=require('@playwright/test');
const {default:AxeBuilder}=require('@axe-core/playwright');
for(const language of ['en','ar','fr','es','pt','it','de','pl']) {
  const route=language==='en'?'/travel':`/${language}/travel`;
  test(`${route} has usable photos, authored copy and one selector`,async({page})=>{
    const errors=[];page.on('pageerror',error=>errors.push(error.message));
    await page.goto(route);
    await page.evaluate(async()=>{for(const image of document.images){image.loading='eager';await image.decode();}});
    await expect(page.locator('html')).toHaveAttribute('lang',language);
    await expect(page.locator('#sc-language-select')).toHaveCount(1);
    await expect(page.locator('.travel-place')).toHaveCount(12);
    expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy();
    expect(errors).toEqual([]);
    const axe=await new AxeBuilder({page}).analyze();
    expect(axe.violations).toEqual([]);
    await page.locator('.travel-hero .btn.primary').click();
    await expect(page).toHaveURL(/\/annaya-tour(?:\?lang=[a-z]+)?$/);
  });
}
test('Travel selector keeps pending translations unavailable instead of switching pages',async({page})=>{
  await page.goto('/travel');
  const select=page.locator('#sc-language-select');
  await expect(select.locator('option[value="ar"]')).toBeDisabled();
  await expect(select).toHaveValue('en');
  await expect(page).toHaveURL(/\/travel$/);
});
test('Photo destination opens the Qadisha guide',async({page})=>{
  await page.goto('/travel');await page.locator('.travel-place[href="/qadisha-valley"]').click();
  await expect(page).toHaveURL(/\/qadisha-valley$/);
  await page.locator('.travel-hero .btn.primary').click();
  await expect(page).toHaveURL(/#visiting$/);
  await expect(page.locator('#visiting')).toBeInViewport();
});

for (const route of ['/qadisha-valley','/ar/qadisha-valley']) {
  test(`${route} has whole-page accessible contrast including footer`, async({page})=>{
    await page.goto(route);
    await page.evaluate(async()=>{for(const image of document.images){image.loading='eager';await image.decode();}});
    const axe=await new AxeBuilder({page}).analyze();
    expect(axe.violations).toEqual([]);
    await expect(page.locator('#sc-language-select')).toHaveCount(1);
  });
}
