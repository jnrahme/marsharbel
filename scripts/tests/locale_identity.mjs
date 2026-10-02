import assert from 'node:assert/strict';
import {chromium} from 'playwright';
import {spawn} from 'node:child_process';
const server=spawn('node',['scripts/dev-server.mjs','--port=4214']);
const browser=await chromium.launch();
try {
 await new Promise(r=>setTimeout(r,700));
 for(const width of [390,1440]) {
  const context=await browser.newContext({viewport:{width,height:850}});
  await context.addInitScript(()=>{window.__MARSHARBEL_QA__={kind:'monitoring',runner:'i18n-foundation'};});
  await context.route(/googletagmanager|google-analytics|analytics\.google/,r=>r.abort());
  const page=await context.newPage();
  await page.goto('http://127.0.0.1:4214/en/prayers');
  assert.equal(await page.locator('#sc-language-select').count(),1);
  await page.selectOption('#sc-language-select','de');
  await page.waitForURL('**/de/gebete');
  assert.equal(await page.locator('html').getAttribute('lang'),'de');
  await page.selectOption('#sc-language-select','it');
  await page.waitForURL('**/it/preghiere');
  assert.equal(await page.locator('html').getAttribute('lang'),'it');
  await page.selectOption('#sc-language-select','en');
  await page.waitForURL('**/en/prayers');
  assert.equal(await page.locator('html').getAttribute('lang'),'en');
  // Synthetic future publication: no live zh-Hans registration in this patch.
  const routes={homes:{en:'/', 'zh-Hans':'/zh-Hans/'}, topics:{'/en/prayers':{en:'/en/prayers','zh-Hans':'/zh-Hans/prayers'}},aliases:{en:'en','zh-cn':'zh-Hans','zh-hans':'zh-Hans'}};
  await context.route('**/locale-routes.js',r=>r.fulfill({contentType:'application/javascript',body:'window.SC_LOCALE_ROUTES='+JSON.stringify(routes)}));
  await context.route('**/zh-Hans/prayers',r=>r.fulfill({contentType:'text/html',body:'<html lang="zh-Hans"><head></head><body><h1>祈祷</h1></body></html>'}));
  await page.goto('http://127.0.0.1:4214/en/prayers?lang=en');
  assert.equal(await page.locator('#sc-language-select option[value="zh-Hans"]').count(),1);
  assert.equal(await page.locator('#sc-language-select option[value="zh-cn"]').count(),0);
  await page.selectOption('#sc-language-select','zh-Hans');
  await page.waitForURL('**/zh-Hans/prayers');
  await page.evaluate(()=>localStorage.setItem('sc_lang_pref','zh-cn'));
  await page.goto('http://127.0.0.1:4214/en/prayers');
  await page.waitForURL('**/zh-Hans/prayers');
  await page.goto('http://127.0.0.1:4214/en/prayers?lang=ZH-CN');
  await page.waitForURL('**/zh-Hans/prayers');
  await context.close();
 }
 console.log('390/1440: en/de/it selector round-trip; canonical zh-Hans option, old zh-cn preference and mixed-case query alias routing passed.');
} finally {await browser.close();server.kill();}
