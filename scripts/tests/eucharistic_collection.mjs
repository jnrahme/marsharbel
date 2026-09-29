import assert from 'node:assert/strict';
import {chromium} from 'playwright';
const base = process.env.BASE_URL || 'http://127.0.0.1:4173';
const browser = await chromium.launch();
try {
  for (const width of [390, 1440]) {
    const page = await browser.newPage({viewport:{width,height:850}});
    await page.goto(base+'/miracles/eucharistic/');
    assert.equal(await page.locator('.euch-card').count(),6);
    assert.equal(await page.locator('h1').count(),1);
    await page.locator('[data-filter="Portugal"]').click();
    assert.equal(await page.locator('.euch-card:visible').count(),1);
    assert.match(await page.locator('.euch-card:visible').innerText(),/Santarém/);
    await page.locator('[data-filter="all"]').click();
    assert.equal(await page.locator('.euch-card:visible').count(),6);
    for (const slug of ['lanciano','bolsena-orvieto','siena','santarem','sokolka','legnica']) {
      const response=await page.goto(base+'/miracles/eucharistic/'+slug);
      assert.equal(response.status(),200);
      assert.equal(await page.locator('h1').count(),1);
      assert.equal(await page.locator('.euch-chapter').count(),3);
      assert.equal(await page.locator('.euch-feature-photo img').evaluate(i=>i.naturalWidth>0),true);
      assert.equal(await page.locator('.euch-feature-photo figcaption a').count(),2);
      assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
    }
    await page.close();
  }
  console.log('Eucharistic collection: seven routes, six images, country filter, source links, responsive widths passed.');
} finally {await browser.close()}
