import assert from 'node:assert/strict';
import {chromium} from 'playwright';
import {spawn} from 'node:child_process';
import {createRequire} from 'node:module';

// Actual published pages remain separate until full twin reviews are recorded.
// Positive reviewed-twin routing is covered by same_page_enabled_navigation.cjs.
// Expectations derive from the built same-page-manifest.js + the real resolver
// (intl ruling 2026-10-11): /en/prayers is en-only/pending, so every non-English
// option - Arabic included - must render disabled and refuse navigation.
const require=createRequire(import.meta.url);
const {repoRoot,loadBuiltManifest,loadResolver,optionExpectations}=require('./same_page_contract.cjs');
const root=repoRoot();
const manifest=loadBuiltManifest(root);
const resolver=loadResolver(root);
const expected=optionExpectations(manifest,resolver,'http://127.0.0.1:4314/en/prayers','en');
assert.deepEqual(Object.keys(expected.enabled),['en'],'/en/prayers contract: English only');
assert.equal(expected.disabled.length,manifest.languages.length-1);

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
  assert.equal(await page.locator('#sc-language-select option').count(),expected.count);
  assert.equal(await page.locator('#sc-language-select').inputValue(),'en');
  const snapshot=()=>page.evaluate(()=>({url:location.href,main:document.querySelector('main').innerHTML,lang:document.documentElement.lang,links:[...document.querySelectorAll('main a')].map(a=>a.getAttribute('href'))}));
  await page.evaluate(()=>scrollTo(0,300));
  const before=await snapshot();
  for(const lang of expected.disabled) {
   assert.equal(await page.locator(`#sc-language-select option[value="${lang}"]`).isDisabled(),true,`${lang} option disabled`);
   assert.equal(await page.evaluate(lang=>SC_LANGUAGE_SWITCH.request(lang),lang),false,`${lang} request refused`);
   assert.deepEqual(await snapshot(),before,`${lang} refusal leaves the page untouched`);
  }
  assert.equal(await page.locator('#sc-language-select option[value="zh-Hans"]').count(),1,'zh-Hans is a published-locale option');
  assert.equal(await page.locator('#sc-language-select option[value="zh-cn"]').count(),0);
  await page.evaluate(()=>localStorage.setItem('sc_lang_pref','zh-cn'));
  for(const suffix of ['', '?lang=ZH-CN', '?lang=de', '?lang=ar']) {
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
  console.log(width,'honest pending identities, every unavailable option disabled+refused (Arabic included), unsupported language refusal, preference/query non-redirect, direct actual languages, no machine requests PASS');
 }
} finally {await browser.close();server.kill();}
