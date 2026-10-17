const assert=require('node:assert/strict');const {resolve,locate}=require('../../same-page-resolver.js');
const hash='a'.repeat(64),revision='b'.repeat(40);
function variant(path){return{path,status:'verified',contentSha256:hash,sourceSha256:hash,proof:{keyedTextComplete:true,mediaParity:true,linkParity:true,schemaParity:true,anchorParity:true,interactionParity:true,editorialReview:'editorial-test-proof',nativeSampleReview:'native-test-proof',renderedReview:'render-test-proof'}}}
const manifest={version:1,languages:['en','ar','fr','es','pt','it','de','pl'],aliases:{en:'en',ar:'ar'},pages:{history:{sourceSha256:hash,sourceRevision:revision,variants:{en:variant('/history'),ar:variant('/ar/full-history')},anchorIDs:{timeline:{en:'timeline',ar:'chronologie'}}},guide:{sourceSha256:hash,sourceRevision:revision,variants:{en:variant('/en/biography'),ar:variant('/ar/biography')},anchorIDs:{}}}};
let n=0;function test(name,f){f();n++;console.log('PASS',name)}
test('same page, preserve query and mapped fragment',()=>{let r=resolve(manifest,'https://marsharbel.com/history?campaign=a#timeline','ar','en');assert.equal(r.href,'https://marsharbel.com/ar/full-history?campaign=a#chronologie')});
test('aliases and reverse English choice, preference irrelevant',()=>assert.equal(resolve(manifest,'https://marsharbel.com/ar/full-history.html?lang=fr#chronologie','en','ar').href,'https://marsharbel.com/history#timeline'));
test('separate guide stays separate guide',()=>assert.equal(resolve(manifest,'https://marsharbel.com/ar/biography','en','ar').href,'https://marsharbel.com/en/biography'));
test('missing third locale preserves exact URL and actual language',()=>{let u='https://marsharbel.com/ar/full-history?a=b#chronologie';let r=resolve(manifest,u,'fr','ar');assert.equal(r.href,u);assert.equal(r.contentLanguage,'ar');assert.equal(r.available,false)});
test('unknown fragment blocks safely',()=>assert.equal(resolve(manifest,'https://marsharbel.com/history#not-reviewed','ar','en').available,false));
test('unknown path stays put',()=>assert.equal(resolve(manifest,'https://marsharbel.com/not-reviewed?x=1#z','ar','en').href,'https://marsharbel.com/not-reviewed?x=1#z'));
test('same-language leaves query/hash untouched',()=>assert.equal(resolve(manifest,'https://marsharbel.com/history?x=1#z','en','en').href,'https://marsharbel.com/history?x=1#z'));
test('all missing review and parity properties fail closed',()=>{let v=manifest.pages.history.variants.ar;for(const key of Object.keys(v.proof)){let value=v.proof[key];delete v.proof[key];assert.equal(resolve(manifest,'https://marsharbel.com/history','ar','en').available,false);v.proof[key]=value}});
test('stale source hash blocks',()=>{let v=manifest.pages.history.variants.ar;v.sourceSha256='c'.repeat(64);assert.equal(resolve(manifest,'https://marsharbel.com/history','ar','en').available,false);v.sourceSha256=hash});
test('pending twin blocks',()=>{let v=manifest.pages.history.variants.ar;v.status='pending';assert.equal(resolve(manifest,'https://marsharbel.com/history','ar','en').available,false);v.status='verified'});
test('every offered code unavailable except actual source and reviewed Arabic',()=>{const fs=require('fs');const langs=JSON.parse(fs.readFileSync('scripts/tests/fixtures/legacy-language-options.json','utf8'));for(const lang of langs){const r=resolve(manifest,'https://marsharbel.com/history',lang.code,'en');assert.equal(r.available,['en','ar'].includes(lang.code))}assert.equal(langs.length,106)});
test('ambiguous identity throws not silent first match',()=>{manifest.pages.duplicate={variants:{fr:variant('/history')}};assert.throws(()=>locate(manifest,'/history'),/ambiguous-page-identity/);delete manifest.pages.duplicate});
console.log(n,'resolver cases passed; review IDs here are test fixtures only');
manifest.englishSources={'/ar/full-history':'/history'};
manifest.pages.history.variants.ar.status='pending';
let sourceEscape=resolve(manifest,'https://marsharbel.com/ar/full-history?lang=ar&campaign=test#unknown','en','ar');
assert.equal(sourceEscape.available,true);assert.equal(sourceEscape.reason,'english-source');assert.equal(sourceEscape.href,'https://marsharbel.com/history?campaign=test');
assert.equal(resolve(manifest,'https://marsharbel.com/ar/full-history','fr','ar').available,false);
console.log('English source is always offered even when current translation is pending; non-English gate unchanged PASS');
manifest.publishedHomes={en:'/',ar:'/ar/',fr:'/fr/'};
assert.equal(resolve(manifest,'https://marsharbel.com/ar/?lang=ar','fr','ar').href,'https://marsharbel.com/fr/');
assert.equal(resolve(manifest,'https://marsharbel.com/ar/full-history','fr','ar').available,false);
console.log('All published home routes switch, article review gate stays unchanged PASS');

// The English source escape preserves only reviewed, explicitly mapped fragments.
manifest.pages.history.variants.ar.status='verified';
assert.equal(resolve(manifest,'https://marsharbel.com/ar/full-history?lang=ar&campaign=test#chronologie','en','ar').href,'https://marsharbel.com/history?campaign=test#timeline');
assert.equal(resolve(manifest,'https://marsharbel.com/ar/full-history#not-reviewed','en','ar').href,'https://marsharbel.com/history');
assert.equal(resolve(manifest,'https://marsharbel.com/ar/full-history#%E0%A4%A','en','ar').href,'https://marsharbel.com/history');
manifest.pages.history.variants.en.status='pending';
assert.equal(resolve(manifest,'https://marsharbel.com/ar/full-history#chronologie','en','ar').href,'https://marsharbel.com/history');
manifest.pages.history.variants.en.status='verified';
manifest.pages.history.variants.ar.status='pending';
assert.equal(resolve(manifest,'https://marsharbel.com/ar/full-history#chronologie','en','ar').href,'https://marsharbel.com/history');
manifest.pages.history.variants.ar.status='verified';
console.log('English escape reviewed anchors preserved; unknown/malformed/pending fragments cleared PASS');
