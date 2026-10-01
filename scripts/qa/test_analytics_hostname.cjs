// Execute every checked-in GA snippet in a VM: non-production hosts do nothing.
const {execFileSync}=require('node:child_process');
const fs=require('node:fs');
const vm=require('node:vm');
const assert=require('node:assert/strict');
const files=execFileSync('git',['ls-files'],{encoding:'utf8'}).trim().split('\n').filter(p=>p.endsWith('.html'));
let checked=0;
for(const file of files){
  const html=fs.readFileSync(file,'utf8');
  assert(!/<script[^>]+src=["']https:\/\/www\.googletagmanager\.com\/gtag\//.test(html),`${file}: ungated loader`);
  const snippets=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).filter(s=>s.includes('G-CJX1M0VFKP'));
  for(const snippet of snippets){checked++;for(const host of ['marsharbel.com','www.marsharbel.com','localhost','127.0.0.1','pr-410--marsharbel-preview.netlify.app','marsharbel-preview.surge.sh','evil.marsharbel.com','marsharbel.com.evil.test','']){
    const loaded=[];const window={};
    vm.runInNewContext(snippet,{window,location:{hostname:host},document:{createElement:()=>({}),head:{appendChild:t=>loaded.push(t)}}});
    const production=['marsharbel.com','www.marsharbel.com'].includes(host);
    assert.equal(loaded.length,production?1:0,`${file}: ${host} loader`);
    assert.equal(window.dataLayer?.length||0,production?2:0,`${file}: ${host} events`);
    if(production)assert.equal(loaded[0].src,'https://www.googletagmanager.com/gtag/js?id=G-CJX1M0VFKP');
  }}
}
assert(checked>200);console.log(`PASS: ${checked} page snippets x 9 hosts; only the two exact production hosts load/fire GA.`);
