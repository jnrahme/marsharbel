import assert from 'node:assert/strict';
import {chromium} from 'playwright';
const base=process.env.BASE_URL||'http://127.0.0.1:4173';
const browser=await chromium.launch();
try {
  for (const width of [390,768,1440]) {
    const page=await browser.newPage({viewport:{width,height:920},reducedMotion:'reduce'});
    await page.goto(base+'/');
    const section=page.locator('#latest-news.home-news');
    assert.equal(await section.count(),1);
    assert.equal(await page.locator('.home-cinematic-hero .home-news, .home-cinematic-hero [class*="news"]').count(),0,'news must not sit inside the hero');
    const order=await page.evaluate(()=>{const h=document.querySelector('.home-cinematic-hero').getBoundingClientRect(),n=document.querySelector('#latest-news').getBoundingClientRect();return n.top>=h.bottom-1;});
    assert.equal(order,true,'news section sits below the hero');
    assert.equal(await page.locator('#latest-news .home-news-lead').count(),1);
    const rows=await page.locator('#latest-news .home-news-row').count();
    assert.ok(rows>=3,'at least three headline rows');
    const lead=await page.locator('.home-news-lead .home-news-photo img').boundingBox();
    assert.ok(lead.width >= (width<=820?300:500));
    assert.ok(lead.height >= 180);
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),true);
    const links=page.locator('#latest-news .home-news-lead, #latest-news .home-news-row');
    for(const item of await links.all()){
      const href=await item.getAttribute('href');
      assert.ok(href && new URL(href,base).pathname.length > 1);
      assert.ok(await item.locator('img').getAttribute('alt'));
      assert.ok((await item.locator('.home-news-title').innerText()).trim().length>0);
      const box=await item.boundingBox();
      const imgBox=await item.locator('img').boundingBox();
      assert.ok(box.height>=imgBox.height,'whole item is the link, photo inside it');
    }
    assert.ok(await page.locator('#latest-news .home-news-all').getAttribute('href'));
    await page.close();
    console.log(`News section layout passed at ${width}px`);
  }
} finally {await browser.close();}
