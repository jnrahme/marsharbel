import assert from 'node:assert/strict';
import {chromium} from 'playwright';
import {spawn} from 'node:child_process';

// Actual published pages remain separate until full twin reviews are recorded.
// Positive reviewed-twin routing is covered by same_page_enabled_navigation.cjs.
const base='http://127.0.0.1:4314';
const server=spawn('node',['scripts/dev-server.mjs','--port=4314'],{stdio:'ignore'});
const browser=await chromium.launch();
try {
 for(let attempt=0;;attempt++) {
  try {if((await fetch(base+'/en/prayers')).ok)break;} catch {}
  if(attempt===39)throw new Error('Local server did not become ready');
  await new Promise(r=>setTimeout(r,100));
 }
 for(const width of [390,1440]) {
  const context=await browser.newContext({viewport:{width,height:850},serviceWorkers:'block'});
  const machineRequests=[];
  await context.route('**/*',r=>{
   const u=new URL(r.request().url());
   if(/translate\.google|translate\.googleapis/.test(u.hostname))machineRequests.push(u.href);
   return u.origin===base?r.continue():r.abort();
  });
  const page=await context.newPage();
  await page.goto(base+'/en/prayers');
  await page.waitForFunction(()=>window.SC_LANGUAGE_SWITCH);
  assert.equal(await page.locator('#sc-language-select').count(),1);
  assert.equal(await page.locator('#sc-language-select option').count(),8);
  assert.equal(await page.locator('#sc-language-select').inputValue(),'en');
  const snapshot=()=>page.evaluate(()=>({url:location.href,main:document.querySelector('main').innerHTML,lang:document.documentElement.lang,links:[...document.querySelectorAll('main a')].map(a=>a.getAttribute('href'))}));
  await page.evaluate(()=>scrollTo(0,300));
  const before=await snapshot();
  for(const lang of ['de','it','zh-Hans']) {
   if(lang!=='zh-Hans')assert.equal(await page.locator(`#sc-language-select option[value="${lang}"]`).isDisabled(),true);
   assert.equal(await page.evaluate(lang=>SC_LANGUAGE_SWITCH.request(lang),lang),false);
   assert.deepEqual(await snapshot(),before);
  }
  assert.equal(await page.locator('#sc-language-select option[value="zh-Hans"]').count(),0);
  assert.equal(await page.locator('#sc-language-select option[value="zh-cn"]').count(),0);
  await page.evaluate(()=>localStorage.setItem('sc_lang_pref','zh-cn'));
  for(const suffix of ['', '?lang=ZH-CN', '?lang=de']) {
   await page.goto(base+'/en/prayers'+suffix);
   await page.waitForFunction(()=>window.SC_LANGUAGE_SWITCH);
   assert.equal(new URL(page.url()).pathname,'/en/prayers');
   assert.equal(await page.locator('html').getAttribute('lang'),'en');
   assert.equal(await page.locator('#sc-language-select').inputValue(),'en');
  }
  // Direct editorial destinations retain their own actual language.
  for(const [route,lang]of [['/de/gebete','de'],['/it/preghiere','it']]) {
   await page.goto(base+route);
   await page.waitForFunction(()=>window.SC_LANGUAGE_SWITCH);
   assert.equal(new URL(page.url()).pathname,route);
   assert.equal(await page.locator('html').getAttribute('lang'),lang);
   assert.equal(await page.locator('#sc-language-select').inputValue(),lang);
  }
  assert.deepEqual(machineRequests,[]);
  await context.close();
  console.log(width,'honest pending identities, unsupported language refusal, preference/query non-redirect, direct actual languages, no machine requests PASS');
 }
} finally {await browser.close();server.kill();}
