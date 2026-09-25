import assert from 'node:assert/strict';
import { readJsonLimited, validateSubmission, redactForScreening, validateReview, youtubeIdFromUrl } from '../../supabase/functions/_shared/validation.ts';
const good={display_name:'A reader',story:'I am sharing an experience of prayer and hope from my own life. '.repeat(2),language:'en',country:'',event_date:'2020-01-01',age_attested:true,consent_publish:true,ai_consent:true};
assert.equal(validateSubmission(good).display_name,'A reader');
for(const bad of [{...good,story:'short'},{...good,display_name:'x'.repeat(81)},{...good,age_attested:false},{...good,ai_consent:false},{...good,consent_publish:false},{...good,event_date:'2026-02-30'},{...good,event_date:'2999-01-01'},{...good,website:'spam'},{...good,language:'xx'}])assert.throws(()=>validateSubmission(bad));
const body=await readJsonLimited(new Request('https://example.test',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(good)}));assert.deepEqual(body,good);
await assert.rejects(()=>readJsonLimited(new Request('https://example.test',{method:'POST',headers:{'content-type':'application/json'},body:'x'.repeat(30001)})),/too large/);
await assert.rejects(()=>readJsonLimited(new Request('https://example.test',{method:'POST',headers:{'content-type':'text/html'},body:'{}'})),/JSON only/);
await assert.rejects(()=>readJsonLimited(new Request('https://example.test',{method:'POST',headers:{'content-type':'application/json'},body:'[]'})),/Invalid/);
assert.equal(redactForScreening('Reach a@example.com or +1 555 123 4567 at https://bad.test'),'Reach [email removed] or [number removed] at [link removed]');
assert.throws(()=>validateReview({summary:'Publish now',recommendation:'approve',flags:[],questions:[]}));
assert.throws(()=>validateReview({summary:'ok',recommendation:'review',flags:[],questions:[],tool_call:'publish'}));
assert.equal(validateReview({summary:'A reported experience',recommendation:'review',flags:[],questions:[]}).recommendation,'review');
for(const url of ['https://youtu.be/dQw4w9WgXcQ','https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=4','https://m.youtube.com/shorts/dQw4w9WgXcQ','https://youtube.com/live/dQw4w9WgXcQ']) {
 assert.equal(youtubeIdFromUrl(url),'dQw4w9WgXcQ');
 assert.equal(validateSubmission({...good,youtube_url:url}).youtube_video_id,'dQw4w9WgXcQ');
}
for(const url of ['http://youtu.be/dQw4w9WgXcQ','https://youtube.com.evil.test/watch?v=dQw4w9WgXcQ','https://evil.test/?v=dQw4w9WgXcQ','https://youtube.com/watch?v=short','https://youtube.com/watch?v=dQw4w9WgXcQ#frag','https://youtube.com:444/watch?v=dQw4w9WgXcQ','javascript:alert(1)']) assert.throws(()=>validateSubmission({...good,youtube_url:url}));
assert.equal(validateSubmission(good).youtube_video_id,null);
console.log('Testimony validation and structured AI output checks passed.');
