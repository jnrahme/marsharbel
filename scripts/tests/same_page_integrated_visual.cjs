const {chromium}=require('playwright');
const fs=require('fs'),os=require('os'),path=require('path'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'../..');
const{loadBuiltManifest,loadResolver,loadCopy,optionExpectations}=require('./same_page_contract.cjs');
// Integrated visual pass on real files with the built manifest + real resolver.
// Per route, refusal uses a language the resolver marks unavailable there; the
// unavailable suffix wording derives from the copy catalog. Screenshots go to
// the OS temp dir so the script is runner-portable.
const manifest=loadBuiltManifest(root);const resolver=loadResolver(root);const copy=loadCopy(root);

(async()=>{const b=await chromium.launch();
try{for(const width of [390,1440])for(const [route,file,lang]of [['/history','history.html','en'],['/ar/biography','ar/biography.html','ar'],['/pl/biografia','pl/biografia.html','pl']]){const c=await b.newContext({viewport:{width,height:900},serviceWorkers:'block'}),p=await c.newPage();
await p.route('**/*',r=>{let u=new URL(r.request().url());
if(u.hostname!=='preview.local')return r.abort();
let f=path.join(root,u.pathname===route?file:u.pathname.slice(1));
if(!fs.existsSync(f)&&fs.existsSync(f+'.html'))f=f+'.html';
if(!fs.existsSync(f)||fs.statSync(f).isDirectory())return r.abort();
return r.fulfill({path:f})});
await p.goto('https://preview.local'+route);
await p.locator('#sc-language-select').waitFor();
const expected=optionExpectations(manifest,resolver,'https://preview.local'+route,lang);
assert.equal(await p.locator('#sc-language-select').inputValue(),lang);
assert.equal(await p.locator('#sc-language-select option').count(),expected.count);
assert.equal(await p.locator('#sc-language-select option:disabled').count(),expected.disabled.length);
assert.equal(await p.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
assert.equal(expected.disabled.length>0,true,route+' has an unavailable language to refuse');
const refused=expected.disabled[0];
const suffix=copy[lang].suffix;
for(const dead of expected.disabled){assert.match(await p.locator(`#sc-language-select option[value="${dead}"]`).textContent(),new RegExp(suffix.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')),route+' '+dead+' suffix')}
await p.screenshot({path:path.join(os.tmpdir(),`same-page-integrated-${lang}-${width}.png`)});
await p.locator('#sc-language-select').focus();
await p.keyboard.press('Tab');
const before=await p.evaluate(()=>({url:location.href,main:document.querySelector('main').innerHTML,lang:document.documentElement.lang}));
await p.evaluate(l=>SC_LANGUAGE_SWITCH.request(l),refused);
assert.deepEqual(await p.evaluate(()=>({url:location.href,main:document.querySelector('main').innerHTML,lang:document.documentElement.lang})),before);
const status=await p.locator('#sc-language-status').boundingBox();
assert(status.width<=1&&status.height<=1,'Live announcement must not create a second visible helper');
await p.screenshot({path:path.join(os.tmpdir(),`same-page-integrated-refusal-${lang}-${width}.png`)});
console.log(width,lang,'integrated source, actual language, published-locale choices, exact suffix, overflow, refusal PASS (refused:',refused+')');
await c.close()}}finally{await b.close()}})().catch(e=>{console.error(e);
process.exit(1)});
