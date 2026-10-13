const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const source=fs.readFileSync('saint-of-day.js','utf8');
for(const [iso,expected] of [['2026-10-13T23:59:59-04:00',false],['2026-10-14T00:00:00-04:00',true],['2026-10-15T00:00:00-04:00',false]]){
 let now=iso,events={},tick,mounted=null,clones=0;
 const template={content:{},getAttribute:k=> k==='data-saint-date'?'2026-10-14':'main > .home-news'};
 const document={querySelector:()=>({after:f=>{mounted=f.card}}),getElementById:()=>template,addEventListener:(k,f)=>events[k]=f,importNode:()=>{clones++;const card={remove:()=>{mounted=null}};return {card,querySelector:()=>card}}};
 vm.runInNewContext(source,{Intl,Date:class extends Date{constructor(){super(now)}},document,setInterval:(f,ms)=>{assert.equal(ms,60000);tick=f}});
 assert.equal(!!mounted,expected,iso);tick();assert.equal(clones,expected?1:0,'no duplicate clone');
 now='2026-10-14T23:59:59-04:00';events.visibilitychange();assert.ok(mounted);
 now='2026-10-15T00:00:00-04:00';tick();assert.equal(mounted,null,'expired card removed');
 now='2026-10-14T12:00:00-04:00';events.visibilitychange();assert.ok(mounted,'resume mounts');
}
console.log('PASS three NY clocks, minute/visibility refresh, expiration and no duplicate clone');

let clones=0;vm.runInNewContext(source,{Intl,Date:class extends Date{constructor(){super('2026-10-14T12:00:00-04:00')}},document:{getElementById:()=>({content:{},getAttribute:k=>k==='data-saint-date'?'2026-10-14':'missing'}),querySelector:()=>null,importNode:()=>{clones++},addEventListener:()=>{}},setInterval:()=>{}});assert.equal(clones,0,'missing anchor fails closed');
