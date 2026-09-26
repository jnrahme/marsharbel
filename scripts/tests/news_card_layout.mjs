import assert from 'node:assert/strict';
import {chromium} from 'playwright';
const base=process.env.BASE_URL||'http://127.0.0.1:4173';
const browser=await chromium.launch();
try {
  for (const width of [390,768,1440]) {
    const page=await browser.newPage({viewport:{width,height:920},reducedMotion:'reduce'});
    await page.goto(base+'/');
    const card=page.locator('.news-rotator-card');
    assert.equal(await card.isVisible(),true);
    assert.equal(await page.locator('.news-rotator-card').count(),1);
    assert.equal(await page.locator('.news-rotator-item.is-active').count(),1);
    const image=await card.locator('.news-rotator-item.is-active img').boundingBox();
    const bounds=await card.boundingBox();
    assert.ok(image.width >= (width<=820?88:100));
    assert.ok(bounds.width >= (width<=820?300:410));
    assert.ok(bounds.height >= 215);
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),true);
    const links=await page.locator('.news-rotator-item').count();
    assert.equal(links,5);
    for(const item of await page.locator('.news-rotator-item').all()){
      const href=await item.getAttribute('href');
      assert.ok(href && new URL(href,base).pathname.length > 1);
      assert.ok(await item.locator('img').getAttribute('alt'));
    }
    await page.close();
    console.log(`News card layout passed at ${width}px`);
  }
} finally {await browser.close();}
