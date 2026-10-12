// AR-2 twin pairing: every one of the 10 hand-authored Arabic twins must be
// offered by the same-page switcher from its English page (and back), with
// honest not-certified proof scoped to exactly the pinned routes.
// Mutation proof: delete one 'ar2-...-equivalence' entry (or move a variant to
// an unlisted route) and this step goes red.
const assert=require('node:assert/strict');const fs=require('fs');const path=require('path');
const root=path.resolve(__dirname,'../..');
const {resolve,verified}=require('../../same-page-resolver.js');
const manifestFile=process.argv[2]||path.join(root,'same-page-manifest.js');
const text=fs.readFileSync(manifestFile,'utf8');
assert.ok(text.startsWith('window.SC_SAME_PAGE_MANIFEST = '),'manifest serialization');
const manifest=JSON.parse(text.slice('window.SC_SAME_PAGE_MANIFEST = '.length).trim().replace(/;$/,''));
const TWINS=[['gallery','/gallery','/ar/gallery'],['saints','/saints','/ar/saints'],
 ['prayer-library','/prayer-library','/ar/prayer-library'],['encyclopedia','/saint-charbel-encyclopedia','/ar/encyclopedia'],
 ['news','/news','/ar/news'],['videos','/videos','/ar/videos'],['testimonies','/testimonies','/ar/testimonies'],
 ['voice-testimony','/voice-testimony','/ar/voice-testimony'],
 ['home','/','/ar/'],['feast-day','/saint-charbel-feast-day','/ar/feast-day'],
 ['litany','/litany-of-saint-charbel','/ar/litany-of-saint-charbel'],['chaplet','/saint-charbel-chaplet','/ar/saint-charbel-chaplet'],
 ['eucharistic-hub','/miracles/eucharistic/','/ar/miracles/eucharistic/'],
 ...['amsterdam','bolsena-orvieto','faverney','ivorra','lanciano','legnica','ludbreg','santarem','siena','sokolka'].map(n=>['eucharistic-'+n,'/miracles/eucharistic/'+n,'/ar/miracles/eucharistic/'+n])];
// Scrum ruling 2026-10-12: exactly these 8. /feedback and /submit-testimony are noindex,
// the control build skips noindex pages, so they can never render the switcher and must
// stay unpaired until the noindex coverage decision (todo-01M4R14M4SBH49AFECW3MEW5H9).
const NOINDEX_UNPAIRED=['feedback','submit-testimony'];
let n=0;function test(name,f){f();n++;console.log('PASS',name)}
test('all 23 AR-2 pairs present with exact pinned routes',()=>{
 for(const [slug,en,ar] of TWINS){
  const page=manifest.pages['ar2-'+slug+'-equivalence'];
  assert.ok(page,'missing pair '+slug);
  assert.equal(page.variants.en.path,en,slug+' en path');
  assert.equal(page.variants.ar.path,ar,slug+' ar path');
  assert.equal(Object.keys(page.variants).length,2,slug+' en+ar only');
 }});
test('every variant passes the resolver gate with honest not-certified proof',()=>{
 for(const [slug] of TWINS){
  const page=manifest.pages['ar2-'+slug+'-equivalence'];
  for(const code of ['en','ar']){
   const v=page.variants[code];
   assert.equal(v.proof.type,'scoped-ar2-variant',slug+' '+code+' type');
   assert.equal(v.proof.nativeReviewStatus,'not-certified',slug+' '+code+' honesty');
   assert.equal(v.status,'verified',slug+' '+code+' status');
   assert.equal(verified(page,v),true,slug+' '+code+' verified()');
  }}});
test('English page offers the Arabic twin and click-through resolves',()=>{
 for(const [slug,en,ar] of TWINS){
  const r=resolve(manifest,'https://marsharbel.com'+en,'ar','en');
  assert.equal(r.available,true,slug+' ar offered');
  // Home resolves through the published-home route (still lands on the verified /ar/ twin).
  assert.equal(r.reason,slug==='home'?'published-home':'verified-twin',slug);
  assert.equal(r.href,'https://marsharbel.com'+ar,slug+' resolves to twin');
 }});
test('Arabic twin offers the English source page back',()=>{
 for(const [slug,en,ar] of TWINS){
  const r=resolve(manifest,'https://marsharbel.com'+ar,'en','ar');
  assert.equal(r.available,true,slug+' en offered');
  assert.equal(r.href,'https://marsharbel.com'+en,slug);
 }});
test('a not-certified twin on an unlisted route is refused',()=>{
 const page=JSON.parse(JSON.stringify(manifest.pages['ar2-gallery-equivalence']));
 page.variants.ar.path='/ar/feast-day';
 assert.equal(verified(page,page.variants.ar),false,'unlisted ar route must fail');
 page.variants.ar.path='/ar/gallery';page.variants.ar.proof.nativeReviewStatus='certified';
 assert.equal(verified(page,page.variants.ar),false,'certified claim must fail');});
test('the two noindex pages stay unpaired (no switcher stack, no pair)',()=>{
 for(const slug of NOINDEX_UNPAIRED){
  assert.ok(!manifest.pages['ar2-'+slug+'-equivalence'],'noindex page must not be paired: '+slug);
 }
 assert.equal(Object.keys(manifest.pages).filter(k=>k.startsWith('ar2-')).length,TWINS.length,'exactly the 23 approved pairs');
});
test('every paired English page actually carries the switcher stack',()=>{
 // A pair for a page without the control stack can never render the switcher:
 // refuse it here so a future noindex pair fails red instead of shipping dead.
 for(const [slug,en] of TWINS){
  const file=en==='/' ? 'index.html' : en.endsWith('/') ? en.slice(1)+'index.html' : en.slice(1)+'.html';
  const html=fs.readFileSync(path.join(root,file),'utf8');
  assert.ok(html.includes('/same-page-switcher.js'),slug+' EN page lacks the switcher stack - do not pair it');
 }});
test('no other manifest family claims the 46 pinned routes',()=>{
 const paths=new Set();for(const [,en,ar] of TWINS){paths.add(en);paths.add(ar)}
 for(const [id,page] of Object.entries(manifest.pages)){
  if(id.startsWith('ar2-'))continue;
  for(const v of Object.values(page.variants))assert.ok(!paths.has(v.path),id+' collides on '+v.path);
 }});
test('sourceRevision is the frozen evidence revision, never the build HEAD',()=>{
 const evidence=JSON.parse(fs.readFileSync(path.join(root,'locales/ar2-pairing-evidence.json'),'utf8'));
 assert.match(evidence.sourceRevision,/^[0-9a-f]{40}$/,'evidence pins a frozen 40-hex sourceRevision');
 for(const [slug] of TWINS){
  assert.equal(manifest.pages['ar2-'+slug+'-equivalence'].sourceRevision,evidence.sourceRevision,slug+' sourceRevision frozen');
 }
 // Static determinism guard: the emitter must not consult git state at build time.
 const emitterSrc=fs.readFileSync(path.join(root,'scripts/i18n/ar2_equivalence.py'),'utf8');
 assert.ok(!emitterSrc.includes('rev-parse') && !emitterSrc.includes('subprocess'),'emitter must not read git HEAD (non-deterministic builds)');
});
test('index-matched pairing: no Arabic page under an English route',()=>{
 const page=JSON.parse(JSON.stringify(manifest.pages['ar2-saints-equivalence']));
 page.variants.ar.path='/gallery'; // ar variant on an EN-pinned path
 assert.equal(verified(page,page.variants.ar),false,'ar variant on EN path must fail');
 const page2=JSON.parse(JSON.stringify(manifest.pages['ar2-saints-equivalence']));
 page2.variants.en.path='/gallery'; // en variant at the WRONG index (saints pair, gallery path)
 assert.equal(verified(page2,page2.variants.en),false,'index-mismatched en path must fail');
});
console.log(n,'AR-2 pairing cases passed on',path.basename(manifestFile));
