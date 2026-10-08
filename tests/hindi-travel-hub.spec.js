const {test,expect}=require('@playwright/test');
const {default:AxeBuilder}=require('@axe-core/playwright');
test('Hindi Travel hub is reachable from home nav with working photos and destinations',async({page})=>{
  const errors=[];page.on('pageerror',error=>errors.push(error.message));
  await page.goto('/hi/');
  await expect(page.locator('.home-travel-card')).toHaveAttribute('href','/annaya-tour');
  const travel=page.locator('header a.nav-parent[href="/hi/travel"]');
  await expect(travel).toHaveCount(1);
  if(await page.evaluate(()=>matchMedia('(hover: none)').matches)){
    await travel.click();
    await page.locator('header .nav-sub a[href="/hi/travel"]').click();
  }else await travel.click();
  await expect(page).toHaveURL(/\/hi\/travel$/);
  await expect(page.locator('html')).toHaveAttribute('lang','hi');
  await expect(page.locator('#sc-language-select')).toHaveCount(1);
  await expect(page.locator('.travel-place')).toHaveCount(12);
  await page.evaluate(async()=>{for(const image of document.images){image.loading='eager';await image.decode();}});
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy();
  expect(errors).toEqual([]);
  const axe=await new AxeBuilder({page}).analyze();
  expect(axe.violations).toEqual([]);
  await page.locator('.travel-place[href="/qadisha-valley"]').click();
  await expect(page).toHaveURL(/\/qadisha-valley$/);
});
