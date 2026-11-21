/* Exact built manifest, not fixture approvals: all 20 x 8 x 8 routes and refusals. */
const assert=require('node:assert/strict');
const fs=require('node:fs');
const {loadBuiltManifest}=require('./same_page_contract.cjs');
const {resolve}=require('../../same-page-resolver.js');
const m=loadBuiltManifest(process.cwd());
const r=JSON.parse(fs.readFileSync('locales/rosary-books-pairing.json'));
const langs=['en','ar','de','es','fr','it','pl','pt'];
let count=0;
for(const slug of Object.keys(r.books)) {
 const page=m.pages[slug+'-master-equivalence'];assert(page,slug+' missing');
 assert.deepEqual(Object.keys(page.variants).sort(),langs.slice().sort());
 for(const from of langs)for(const to of langs){
  const path='/'+(from==='en'?'':from+'/')+slug;
  const target='/'+(to==='en'?'':to+'/')+slug;
  const out=resolve(m,'https://marsharbel.com'+path+'?campaign=pairing',to,from);
  assert.equal(out.available,true,slug+' '+from+'->'+to);assert.equal(new URL(out.href).pathname,target);
  assert.equal(new URL(out.href).search,'?campaign=pairing');count++;
 }
 for(const to of ['ru','hi','th','zh-Hans'])assert.equal(resolve(m,'https://marsharbel.com/'+slug,to,'en').available,false);
 for(const edit of [p=>p.variants.ar.path='/ar/history',p=>p.variants.ar.proof.reviewedContentSha256='0'.repeat(64),p=>p.variants.ar.proof.editorialReview='invented',p=>delete p.variants.pl,p=>p.variants.ar.proof.activationStatus='pending-authorization',p=>p.variants.ar.proof.technicalReviewStatus='approved',p=>p.variants.ar.proof.reviewer='Instinct main (model review)']){
  const bad=structuredClone(m);edit(bad.pages[slug+'-master-equivalence']);
  assert.equal(resolve(bad,'https://marsharbel.com/'+slug,'ar','en').available,false,slug+' mutation must refuse');
 }
}
assert.equal(Object.keys(r.books).length,20);
console.log(count+' exact-built cross-locale routes PASS; excluded locales and route/hash/scope mutations refused');
