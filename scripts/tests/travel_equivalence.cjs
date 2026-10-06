const fs=require('fs'),assert=require('assert'),api=require('../../same-page-resolver.js');
const manifest=JSON.parse(fs.readFileSync('same-page-manifest.js','utf8').replace(/^window.SC_SAME_PAGE_MANIFEST = /,'').trim().replace(/;$/,''));
let cases=0;
for(const [id,group]of Object.entries(manifest.pages).filter(([id])=>['annaya-master-equivalence','twenty-second-master-equivalence','pilgrimage-master-equivalence'].includes(id))){
 for(const [lang,v]of Object.entries(group.variants))for(const [target,t]of Object.entries(group.variants)){
  const r=api.resolve(manifest,'https://marsharbel.com'+v.path+'?utm_source=x',target,lang);assert(r.available,id+lang+target);assert.equal(new URL(r.href).pathname,t.path);cases++;
 }
 const bad=structuredClone(manifest);bad.pages[id].variants.fr.proof.renderedReview='';assert(!api.resolve(bad,'https://marsharbel.com'+group.variants.ar.path,'fr','ar').available);
 assert(!api.resolve(manifest,'https://marsharbel.com'+group.variants.ar.path+'#missing-anchor','fr','ar').available);
}
assert.equal(cases,243);assert(!api.resolve(manifest,'https://marsharbel.com/saint-charbel-prayers','fr','en').available);
console.log('243 travel route pairs, missing-review/anchor refusal and unrelated pending prayers PASS');
