const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const source=fs.readFileSync('saint-of-day.js','utf8');
function world(dates){
 // Build one fake DOM holding a template per date; importNode maps content->card.
 const state={mounted:null,clones:0,removed:[],events:{},tick:null};
 const templates=dates.map(d=>{
  const card={getAttribute:()=>d,remove:()=>{state.removed.push(d);if(state.mounted&&state.mounted.getAttribute()===d)state.mounted=null}};
  const content={card};
  return {content,getAttribute:k=>k==='data-saint-date'?d:'main > .home-news'};
 });
 const document={
  querySelector:()=>({after:f=>{state.mounted=f.querySelector('#saint-of-the-day')}}),
  querySelectorAll:s=>s==='template[data-saint-date]'?templates:[],
  addEventListener:(k,f)=>state.events[k]=f,
  importNode:content=>{state.clones++;return {querySelector:()=>content.card}},
 };
 function run(iso){
  vm.runInNewContext(source,{Intl,Date:class extends Date{constructor(){super(iso)}},document,setInterval:(f,ms)=>{assert.equal(ms,60000);state.tick=f}});
 }
 return {state,run};
}
// Four clocks over a two-unit window: before, date A, date B, after.
for(const [iso,expected] of [['2026-10-13T23:59:59-04:00',null],['2026-10-14T00:00:00-04:00','2026-10-14'],['2026-10-15T12:00:00-04:00','2026-10-15'],['2026-10-16T00:00:00-04:00',null]]){
 const w=world(['2026-10-14','2026-10-15']);
 w.run(iso);
 assert.equal(w.state.mounted?w.state.mounted.getAttribute():null,expected,iso+' mounts '+(expected||'nothing'));
 w.state.tick();
 assert.equal(w.state.clones,expected?1:0,iso+' no duplicate clone');
}
// Midnight rollover: the expired unit is removed and the new one mounts in the same refresh.
{
 const w=world(['2026-10-14','2026-10-15']);
 // Re-run with a mutable clock by driving tick through a date sequence in one context.
 let now='2026-10-14T12:00:00-04:00';
 const dates=['2026-10-14','2026-10-15'];
 const templates=dates.map(d=>{
  const card={getAttribute:()=>d,remove:()=>{w.state.removed.push(d);if(w.state.mounted===card)w.state.mounted=null}};
  return {content:{card},getAttribute:k=>k==='data-saint-date'?d:'main > .home-news'};
 });
 const document={querySelector:()=>({after:f=>{w.state.mounted=f.querySelector('#saint-of-the-day')}}),querySelectorAll:()=>templates,addEventListener:(k,f)=>w.state.events[k]=f,importNode:c=>({querySelector:()=>c.card})};
 let tick;
 vm.runInNewContext(source,{Intl,Date:class extends Date{constructor(){super(now)}},document,setInterval:f=>{tick=f}});
 assert.equal(w.state.mounted.getAttribute(),'2026-10-14','unit A mounted on its date');
 now='2026-10-15T00:00:00-04:00';tick();
 assert.deepEqual(w.state.removed,['2026-10-14'],'expired unit removed');
 assert.equal(w.state.mounted.getAttribute(),'2026-10-15','unit B mounted after rollover');
 now='2026-10-14T12:00:00-04:00';w.state.events.visibilitychange();
 assert.equal(w.state.mounted.getAttribute(),'2026-10-14','back-date remounts the matching unit');
}
// Fail closed: matching template but missing anchor mounts nothing.
{
 let clones=0;
 vm.runInNewContext(source,{Intl,Date:class extends Date{constructor(){super('2026-10-14T12:00:00-04:00')}},document:{querySelectorAll:()=>[{content:{},getAttribute:k=>k==='data-saint-date'?'2026-10-14':'missing'}],querySelector:()=>null,importNode:()=>{clones++},addEventListener:()=>{}},setInterval:()=>{}});
 assert.equal(clones,0,'missing anchor fails closed');
}
// Fail closed: no template at all.
{
 let clones=0;
 vm.runInNewContext(source,{Intl,Date:class extends Date{constructor(){super('2026-10-14T12:00:00-04:00')}},document:{querySelectorAll:()=>[],querySelector:()=>null,importNode:()=>{clones++},addEventListener:()=>{}},setInterval:()=>{}});
 assert.equal(clones,0,'no template fails closed');
}
console.log('PASS four NY clocks over two window units, midnight swap, minute/visibility refresh, no duplicate clone, fail-closed');
