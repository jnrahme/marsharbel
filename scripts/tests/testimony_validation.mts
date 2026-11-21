import assert from 'node:assert/strict';
import { readJsonLimited, validateSubmission, redactForScreening, validateReview } from '../../supabase/functions/_shared/validation.ts';
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
console.log('Testimony validation and structured AI output checks passed.');
// Form-abuse probes: hostile content is inert data; structural abuse is rejected.
{
  const hostileStory = '<script>alert(1)</script> <img src=x onerror=alert(1)> ' + 'I am sharing a real experience of prayer. '.repeat(3);
  const ok = validateSubmission({ ...good, display_name: '<b>Reader</b>', story: hostileStory });
  assert.equal(ok.story, hostileStory.trim(), 'markup is preserved as inert text, rendered with textContent');
  const attempts: Record<string, unknown>[] = [
    { ...good, website: 'http://spam.test' }, { ...good, language: 'xx' }, { ...good, language: 'en\u0000' },
    { ...good, story: 'x'.repeat(7001) }, { ...good, story: 'a\u0007b'.repeat(30) }, { ...good, display_name: 'a' },
    { ...good, event_date: '2020-13-01' }, { ...good, event_date: '2020-1-1' }, { ...good, age_attested: 'true' },
    { ...good, consent_publish: 1 }, { ...good, ai_consent: undefined }, { ...good, story: { toString: () => good.story } },
    { ...good, country: 'x'.repeat(101) }
  ];
  for (const bad of attempts) assert.throws(() => validateSubmission(bad as Record<string, unknown>), `should reject ${JSON.stringify(bad).slice(0, 60)}`);
  // Unknown/extra keys such as prototype pollution attempts must not reach the payload.
  const polluted = validateSubmission(JSON.parse('{"__proto__":{"admin":true},"constructor":{"x":1},"status":"approved","author_id":"x"}' ) && { ...good, status: 'approved', author_id: 'attacker', __proto__: { admin: true } } as Record<string, unknown>);
  assert.ok(!('status' in polluted) && !('author_id' in polluted) && !('admin' in polluted), 'unexpected keys are dropped');
}
console.log('Testimony form-abuse probes passed.');
