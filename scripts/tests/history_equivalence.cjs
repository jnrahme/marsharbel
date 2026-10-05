const fs=require('fs'),assert=require('assert'),api=require('../../same-page-resolver.js');
const manifest=JSON.parse(fs.readFileSync('same-page-manifest.js','utf8').replace(/^window.SC_SAME_PAGE_MANIFEST = /,'').trim().replace(/;$/,''));
const group=manifest.pages['history-master-equivalence'];
for(const [lang,v]of Object.entries(group.variants))for(const [target,t]of Object.entries(group.variants)){
 const r=api.resolve(manifest,'https://marsharbel.com'+v.path+'?utm_source=x#visit',target,lang);assert(r.available);if(lang!==target){assert.equal(new URL(r.href).pathname,t.path);assert.equal(new URL(r.href).search,'?utm_source=x');assert.equal(new URL(r.href).hash,'#visit');}}
const copy=structuredClone(manifest);copy.pages['history-master-equivalence'].variants.fr.proof.renderedReviewStatus='pending';assert(!api.resolve(copy,'https://marsharbel.com/ar/biography','fr','ar').available);
console.log('81 history route pairs, anchors/query preservation and missing-review refusal PASS');
