/* Clock-controlled New York availability without changing the browser clock. */
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const source=fs.readFileSync('saint-of-day.js','utf8');
for(const [iso,expected] of [
 ['2026-10-13T23:59:59-04:00',true],
 ['2026-10-14T00:00:00-04:00',false],
 ['2026-10-14T23:59:59-04:00',false],
 ['2026-10-15T00:00:00-04:00',true]]){
 let now=iso,events={},tick;
 const card={hidden:true,getAttribute:()=> '2026-10-14'};
 vm.runInNewContext(source,{Intl,Date:class extends Date{constructor(){super(now)}},document:{getElementById:()=>card,addEventListener:(k,f)=>events[k]=f},setInterval:(f,ms)=>{assert.equal(ms,60000);tick=f}});
 assert.equal(card.hidden,expected,iso);
 now='2026-10-15T00:00:00-04:00';tick();assert.equal(card.hidden,true);
 now='2026-10-14T12:00:00-04:00';events.visibilitychange();assert.equal(card.hidden,false);
}
console.log('PASS: prior/current/expired NY dates, midnight boundary, timer and visibility refresh');
