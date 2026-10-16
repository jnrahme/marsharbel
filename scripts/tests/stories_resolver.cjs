const assert = require('node:assert/strict');
const fs = require('node:fs');
const api = require('../../same-page-resolver.js');
const record = JSON.parse(fs.readFileSync('locales/stories-equivalence.json', 'utf8'));
const codes = Object.keys(record.variants);
const page = {sourcePath:'stories.html', sourceRevision:record.sourceRevision, sourceSha256:record.variants.en.bodySha256, anchorIDs:{'shelf-lebanon':{}}, variants:{}};
for (const code of codes) {
  const v = record.variants[code];
  page.anchorIDs['shelf-lebanon'][code] = 'shelf-lebanon';
  page.variants[code] = {path:v.path, aliases:[], status:'verified', contentSha256:v.bodySha256, sourceSha256:page.sourceSha256, proof:{type:'scoped-stories-variant', state:'isolated-review-pass', nativeReviewStatus:'not-certified', reviewedContentSha256:v.bodySha256, masterSha256:record.masterSha256, evidenceSha256:record.verdictSha256}};
}
const manifest = {version:1, languages:codes, pages:{stories:page}};
for (const from of codes) for (const to of codes) {
  const result = api.resolve(manifest,'https://marsharbel.com'+page.variants[from].path+'?test=1#shelf-lebanon',to,from);
  assert.equal(result.available,true,from+' -> '+to);
  assert.equal(result.href,'https://marsharbel.com'+page.variants[to].path+'?test=1#shelf-lebanon');
}
const mutators = [
 p=>p.variants.ar.status='pending',
 p=>p.variants.ar.proof.state='pending',
 p=>p.variants.ar.proof.nativeReviewStatus='certified',
 p=>p.variants.ar.proof.evidenceSha256='f'.repeat(64),
 p=>p.variants.ar.proof.masterSha256='f'.repeat(64),
 p=>p.variants.ar.proof.reviewedContentSha256='f'.repeat(64),
 p=>p.variants.ar.sourceSha256='f'.repeat(64),
 p=>p.variants.ar.contentSha256='invalid',
 p=>p.variants.ar.aliases=['/unreviewed'],
 p=>p.variants.fr.path='/fr/other',
 p=>delete p.variants.fr,
 p=>p.variants.extra=structuredClone(p.variants.ar),
 p=>p.sourcePath='history.html',
 p=>p.sourceRevision='invalid'
];
for (const mutate of mutators) {
 const m=structuredClone(manifest); mutate(m.pages.stories);
 assert.equal(api.resolve(m,'https://marsharbel.com/stories','ar','en').available,false,mutate.toString());
}
assert.equal(api.resolve(manifest,'https://marsharbel.com/stories#unmapped','ar','en').available,false);
console.log('Stories resolver:144 exact-route/query/anchor journeys +15 refusal controls PASS; no native certification asserted');
