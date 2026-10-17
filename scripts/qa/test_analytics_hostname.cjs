// Execute the shared GA init file in a VM (non-production hosts do nothing) and verify every page loads it
// instead of carrying an inline snippet (inline script is blocked once CSP script-src is enforced).
const {execFileSync}=require('node:child_process');
const fs=require('node:fs');
const vm=require('node:vm');
const assert=require('node:assert/strict');
const files=execFileSync('git',['ls-files'],{encoding:'utf8'}).trim().split('\n').filter(p=>p.endsWith('.html'));
let checked=0;
for(const file of files){
  const html=fs.readFileSync(file,'utf8');
  assert(!/<script[^>]+src=["']https:\/\/www\.googletagmanager\.com\/gtag\//.test(html),`${file}: ungated loader`);
  assert(!/<script>[^<]*G-CJX1M0VFKP/.test(html),`${file}: inline GA snippet`);
  const refs=(html.match(/<script defer(?:="")? src="\/analytics-init\.js"><\/script>/g)||[]).length;
  assert(refs<=1,`${file}: duplicate analytics-init reference`);
  const snippets=refs?[fs.readFileSync('analytics-init.js','utf8')]:[];
  for(const snippet of snippets){checked++;for(const host of ['marsharbel.com','www.marsharbel.com','localhost','127.0.0.1','pr-410--marsharbel-preview.netlify.app','marsharbel-preview.surge.sh','evil.marsharbel.com','marsharbel.com.evil.test','']){
    const loaded=[];const window={};
    vm.runInNewContext(snippet,{window,location:{hostname:host},document:{createElement:()=>({}),head:{appendChild:t=>loaded.push(t)}}});
    const production=['marsharbel.com','www.marsharbel.com'].includes(host);
    assert.equal(loaded.length,production?1:0,`${file}: ${host} loader`);
    assert.equal(window.dataLayer?.length||0,production?2:0,`${file}: ${host} events`);
    if(production)assert.equal(loaded[0].src,'https://www.googletagmanager.com/gtag/js?id=G-CJX1M0VFKP');
    // Production reader pageviews must never carry traffic_type; only a QA marker sets it.
    assert(![...(window.dataLayer||[])].some(a=>JSON.stringify([...a]).includes('traffic_type')),`${file}: ${host} reader leaks traffic_type`);
    for(const marker of [{kind:'monitoring',runner:'seo-technical-monitoring'},true]){
      const qaLoaded=[];const qaWindow={__MARSHARBEL_QA__:marker};
      vm.runInNewContext(snippet,{window:qaWindow,location:{hostname:host},document:{createElement:()=>({}),head:{appendChild:t=>qaLoaded.push(t)}}});
      const events=[...(qaWindow.dataLayer||[])].map(a=>[...a]);
      if(production){
        assert.equal(events.length,3,`${file}: ${host} QA events`);
        assert.equal(JSON.stringify(events.find(e=>e[0]==='set')),JSON.stringify(['set',{traffic_type:'internal'}]),`${file}: ${host} QA traffic_type`);
        assert.equal(events.findIndex(e=>e[0]==='set')<events.findIndex(e=>e[0]==='config'),true,`${file}: set must precede config`);
      }else assert.equal(events.length,0,`${file}: ${host} QA must not fire off production`);
    }
  }}
}
assert(checked>200);console.log(`PASS: ${checked} page snippets x 9 hosts; only the two exact production hosts load/fire GA; readers never set traffic_type, QA marker runs always do.`);
