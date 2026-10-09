const assert = require('node:assert/strict');
const api = require('../../same-page-resolver.js');
const variant = {path:'/ru/travel',aliases:[],status:'verified',contentSha256:'b'.repeat(64),sourceSha256:'a'.repeat(64),proof:{type:'scoped-travel-variant',state:'approved',nativeReviewStatus:'not-certified',scope:'RU exact artifact',evidenceRef:'actual-review',candidateFileSha256:'c'.repeat(64),reviewedContentSha256:'b'.repeat(64)}};
function manifest(v=variant) {return {version:1,languages:['en','de','ru','hi'],pages:{travel:{sourcePath:'travel.html',sourceRevision:'d'.repeat(40),sourceSha256:'a'.repeat(64),variants:{en:{...structuredClone(variant),path:'/travel'},ru:v},anchorIDs:{}}}};}
function available(m) {return api.resolve(m,'https://marsharbel.com/travel','ru','en').available;}
assert.equal(available(manifest()),true);
for (const [field,value] of [['state','pending'],['nativeReviewStatus','approved'],['evidenceRef',''],['reviewedContentSha256','e'.repeat(64)]]) {
 const v=structuredClone(variant);v.proof[field]=value;assert.equal(available(manifest(v)),false,field);
}
for(const mutate of [m=>m.pages.travel.variants.ru.path='/ru/other',m=>m.pages.travel.sourcePath='other.html',m=>m.pages.travel.variants.ru.aliases=['/alias'],m=>m.pages.travel.sourceRevision='bad']) {const m=manifest();mutate(m);assert.equal(available(m),false);}
console.log('scoped resolver: positive + 8 refusals PASS');
