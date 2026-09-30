import{chromium}from'playwright';import{installQaMarker}from'../analytics/qa-browser.cjs';import{spawn}from'node:child_process';import assert from'node:assert/strict';import fs from'node:fs';
const server=spawn('node',['scripts/dev-server.mjs','--port=4371'],{stdio:'ignore'});let browser;let proof=[];
try{await new Promise(r=>setTimeout(r,500));browser=await chromium.launch();for(const kind of['normal','monitoring','analytics_debug']){
 const b=await chromium.launch();if(kind!=='normal')installQaMarker(b,`proof.${kind}`,kind);const page=await b.newPage();let requests=[];
 // Offline transport substitute: observes serialized event values, not a claim about Google's receipt.
 await page.route('https://www.googletagmanager.com/gtag/js**',r=>r.fulfill({contentType:'application/javascript',body:`(()=>{let defaults={};function send(a){if(a[0]==='set')Object.assign(defaults,a[1]);if(a[0]==='config'||a[0]==='event'){let e=a[0]==='config'?'page_view':a[1];fetch('/__analytics-proof?'+new URLSearchParams({event:e,...defaults}),{method:'POST'});}}const q=window.dataLayer;for(const a of q)send(a);q.push=function(a){Array.prototype.push.call(q,a);send(a)}})()`}));
 await page.route('**/__analytics-proof?**',r=>{requests.push(Object.fromEntries(new URL(r.request().url()).searchParams));return r.fulfill({status:204})});
 for(const route of['/','/ar/','/massabki-story']){await page.goto(`http://localhost:4371${route}`);await page.waitForTimeout(250);await page.evaluate(()=>gtag('event','qa_custom_probe'));await page.waitForTimeout(100);}
 assert.equal(requests.length,6);for(const event of requests){if(kind==='normal')assert.equal(event.traffic_type,undefined);else{assert.equal(event.traffic_type,'qa_monitoring');assert.equal(event.qa_kind,kind);assert.equal(event.qa_runner,`proof.${kind}`);}}
 proof.push({kind,requests});await b.close();
 }fs.writeFileSync('/tmp/ga-network-offline.json',JSON.stringify(proof,null,2));console.log('QA marker transport proof: normal/monitoring/debug,3 navigations,auto+custom events PASS');
}finally{await browser?.close();server.kill()}
