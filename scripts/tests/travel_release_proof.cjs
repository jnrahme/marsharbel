const assert=require('assert');const api=require('../../same-page-resolver.js');
const hash='a'.repeat(64);const page={sourcePath:'travel.html',sourceSha256:hash,sourceRevision:'b'.repeat(40)};
const v={status:'verified',aliases:[],path:'/de/travel',contentSha256:hash,sourceSha256:hash,proof:{type:'reviewed-travel-release',reviewedContentSha256:hash,nativeReviewStatus:'pending-post-release',nativeFollowUp:'review-record',contentReviewMode:'model-only',editorialReview:'content-review',renderedReview:'pixels',keyedTextComplete:true,mediaParity:true,linkParity:true,schemaParity:true,anchorParity:true,interactionParity:true}};
assert(api.verified(page,v));
for(const key of ['reviewedContentSha256','nativeReviewStatus','nativeFollowUp','contentReviewMode','editorialReview','renderedReview','keyedTextComplete','mediaParity','linkParity','schemaParity','anchorParity','interactionParity']){let bad=JSON.parse(JSON.stringify(v));delete bad.proof[key];assert(!api.verified(page,bad),key);}
assert(!api.verified({...page,sourcePath:'rosary.html'},v),'unrelated source');
assert(!api.verified(page,{...v,path:'/de/rosary'}),'unrelated destination');
assert(!api.verified(page,{...v,sourceSha256:'c'.repeat(64)}),'stale master');
assert(!api.verified(page,{...v,contentSha256:'c'.repeat(64)}),'stale content');
assert(!api.verified(page,{...v,path:'/xx/travel'}),'unregistered locale');
assert(!api.verified(page,{...v,path:'/de/bekaa-kafra'}),'wrong family');
console.log('Travel release proof: positive + 18 refusal controls PASS');

function manifest(target) {return {version:1,languages:['en','de','fr','zh-Hans'],pages:{travel:{...page,variants:{en:{...v,path:'/travel'},de:v,...target}}}};}
assert(api.resolve(manifest({}), 'https://marsharbel.com/travel','de','en').available);
assert(!api.resolve(manifest({fr:v}), 'https://marsharbel.com/travel','fr','en').available,'French key on DE path');
assert(!api.locate(manifest({de:{...v,aliases:['/fr/unrelated']}}),'/fr/unrelated'),'unreviewed alias');
let malformed=manifest({});delete malformed.pages.travel.sourcePath;
assert(!api.resolve(malformed,'https://marsharbel.com/travel','de','en').available,'missing source safe refusal');
assert(!api.verified({},v),'missing source verification safe refusal');
console.log('Resolve-level locale binding, aliases and malformed-source controls PASS');

for (const [sourcePath,path] of [['visit-annaya.html','/de/visit-annaya'],['saint-charbel-pilgrimage.html','/de/saint-charbel-pilgrimage'],['saint-charbel-pilgrimage.html','/zh-Hans/saint-charbel-pilgrimage']]) {
 assert(!api.verified({...page,sourcePath},{...v,path}),'unregistered generic alias '+path);
}
assert(!api.resolve(manifest({de:{...v,aliases:['/fr/unrelated']}}),'https://marsharbel.com/travel','de','en').available,'target alias proof refused');
assert(!api.resolve(manifest({de:{...v,aliases:['/fr/unrelated']}}),'https://marsharbel.com/fr/unrelated','en','fr').available,'alias cannot locate family');
console.log('Established-route-only and resolve alias refusal controls PASS');
