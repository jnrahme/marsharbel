const assert=require('assert');const api=require('../../same-page-resolver.js');
const hash='a'.repeat(64);const page={sourcePath:'travel.html',sourceSha256:hash,sourceRevision:'b'.repeat(40)};
const v={status:'verified',path:'/de/travel',contentSha256:hash,sourceSha256:hash,proof:{type:'reviewed-travel-release',reviewedContentSha256:hash,nativeReviewStatus:'pending-post-release',nativeFollowUp:'review-record',contentReviewMode:'model-only',editorialReview:'content-review',renderedReview:'pixels',keyedTextComplete:true,mediaParity:true,linkParity:true,schemaParity:true,anchorParity:true,interactionParity:true}};
assert(api.verified(page,v));
for(const key of ['reviewedContentSha256','nativeReviewStatus','nativeFollowUp','contentReviewMode','editorialReview','renderedReview','keyedTextComplete','mediaParity','linkParity','schemaParity','anchorParity','interactionParity']){let bad=JSON.parse(JSON.stringify(v));delete bad.proof[key];assert(!api.verified(page,bad),key);}
assert(!api.verified({...page,sourcePath:'rosary.html'},v),'unrelated source');
assert(!api.verified(page,{...v,path:'/de/rosary'}),'unrelated destination');
assert(!api.verified(page,{...v,sourceSha256:'c'.repeat(64)}),'stale master');
assert(!api.verified(page,{...v,contentSha256:'c'.repeat(64)}),'stale content');
assert(!api.verified(page,{...v,path:'/xx/travel'}),'unregistered locale');
assert(!api.verified(page,{...v,path:'/de/bekaa-kafra'}),'wrong family');
console.log('Travel release proof: positive + 16 refusal controls PASS');
