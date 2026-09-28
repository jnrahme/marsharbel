import assert from 'node:assert/strict';
import {chromium} from 'playwright';
const base=process.env.BASE_URL || 'http://127.0.0.1:4173';
const languages=['ar','fr','es','pt','it','de','pl'];
const slugs=['lanciano','bolsena-orvieto','siena','santarem','sokolka'];
const browser=await chromium.launch();
try {
 for (const width of [390,1440]) {
  const page=await browser.newPage({viewport:{width,height:850}});
  for (const lang of languages) {
   const url=`${base}/${lang}/miracles/eucharistic/`;
   const response=await page.goto(url);
   assert.equal(response.status(),200,`${lang} hub`);
   assert.equal(await page.locator('html').getAttribute('lang'),lang);
   assert.equal(await page.locator('html').getAttribute('dir'),lang==='ar'?'rtl':'ltr');
   assert.equal(await page.locator('h1').count(),1);
   assert.equal(await page.locator('.euch-card').count(),5);
   assert.equal(await page.locator('.euch-card img').count(),5);
   assert.equal(await page.locator('link[hreflang]').count(),9);
   assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true,`${lang} hub overflows at ${width}`);
   await page.locator('[data-filter="Portugal"]').click();
   assert.equal(await page.locator('.euch-card:visible').count(),1,`${lang} Portugal filter`);
   assert.match(await page.locator('.euch-card:visible').innerText(),/Santarém|سانتاريم/);
   await page.locator('[data-filter="all"]').click();
   assert.equal(await page.locator('.euch-card:visible').count(),5);
   for (const slug of slugs) {
    const item=await page.goto(url+slug);
    assert.equal(item.status(),200,`${lang}/${slug}`);
    assert.equal(await page.locator('h1').count(),1);
    assert.equal(await page.locator('.euch-chapter').count(),3);
    assert.equal(await page.locator('.euch-feature-photo img').evaluate(img=>img.naturalWidth>0),true,`${lang}/${slug} image`);
    assert.equal(await page.locator('.euch-feature-photo figcaption a').count(),2,`${lang}/${slug} credits`);
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true,`${lang}/${slug} overflows at ${width}`);
    assert.equal(await page.locator('link[hreflang]').count(),9);
   }
  }
  await page.close();
 }
 console.log('Eucharistic locale mirrors: 42 routes, filters, images, source links and 390/1440 viewport checks passed.');
} finally {await browser.close()}
