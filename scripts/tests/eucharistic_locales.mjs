import assert from 'node:assert/strict';
import {chromium} from 'playwright';
const base=process.env.BASE_URL || 'http://127.0.0.1:4173';
import {readFileSync} from 'node:fs';
const registry=JSON.parse(readFileSync(new URL('../../locales/registry.json',import.meta.url),'utf8'));
const languages=registry.publicationSets.eucharistic.filter(code=>code!==registry.defaultLocale);
const slugs=['lanciano','bolsena-orvieto','siena','santarem','sokolka','legnica','ludbreg','amsterdam','ivorra','faverney'];
const browser=await chromium.launch();
try {
 for (const width of (process.env.QA_WIDTH ? [Number(process.env.QA_WIDTH)] : [390,1440])) {
  const context=await browser.newContext({viewport:{width,height:850},serviceWorkers:'block'});
  await context.addInitScript(()=>{window.__MARSHARBEL_QA__={kind:'monitoring',runner:'i18n-eucharistic-qa'};});
  await context.route('**/*',r=>new URL(r.request().url()).origin===new URL(base).origin?r.continue():r.abort());
  let page=await context.newPage();
  for (const lang of languages) {
   const url=`${base}/${lang}/miracles/eucharistic/`;
   await page.close(); page=await context.newPage();
   const response=await page.goto(url);
   assert.equal(response.status(),200,`${lang} hub`);
   assert.equal(await page.locator('html').getAttribute('lang'),lang);
   assert.equal(await page.locator('html').getAttribute('dir'),lang==='ar'?'rtl':'ltr');
   assert.equal(await page.locator('h1').count(),1);
   assert.equal(await page.locator('.euch-card').count(),10);
   assert.equal(await page.locator('.euch-card img').count(),10);
   assert.equal(await page.locator('link[hreflang]').count(),languages.length+2);
   assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true,`${lang} hub overflows at ${width}`);
   await page.locator('[data-filter="Portugal"]').click();
   assert.equal(await page.locator('.euch-card:visible').count(),1,`${lang} Portugal filter`);
   assert.match(await page.locator('.euch-card:visible').innerText(),/Santarém|سانتاريم/);
   await page.locator('[data-filter="all"]').click();
   assert.equal(await page.locator('.euch-card:visible').count(),10);
   for (const slug of slugs) {
    await page.close(); page=await context.newPage();
    const item=await page.goto(url+slug);
    assert.equal(item.status(),200,`${lang}/${slug}`);
    assert.equal(await page.locator('h1').count(),1);
    assert.equal(await page.locator('.euch-chapter').count(),3);
    await page.locator('.euch-feature-photo img').evaluate(i=>i.decode());
    assert.equal(await page.locator('.euch-feature-photo img').evaluate(img=>img.naturalWidth>0),true,`${lang}/${slug} image`);
    assert.equal(await page.locator('.euch-feature-photo figcaption a').count(),2,`${lang}/${slug} credits`);
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true,`${lang}/${slug} overflows at ${width}`);
    assert.equal(await page.locator('link[hreflang]').count(),languages.length+2);
   }
  }
  await context.close();
 }
 console.log(`Eucharistic locale mirrors: ${languages.length*11} published routes, filters, images, sources; widths ${process.env.QA_WIDTH || '390/1440'} passed.`);
} finally {await browser.close()}
