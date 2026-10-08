import { createClient } from 'https://esm.sh/@supabase/supabase-js@2.57.4';
import { sendEmail } from '../_shared/email-adapter.ts';
import { issueEmail, IssueContent } from '../_shared/prayer-email-templates.ts';
import { mintSubscriberToken } from '../_shared/subscriber-token.ts';

// Rosary mystery rotation by weekday (standard): the names only, meditated with the site's rosary pages.
const MYSTERIES: Record<number, { set: string; items: string[] }> = {
  0: { set: 'Glorious', items: ['The Resurrection', 'The Ascension', 'The Descent of the Holy Spirit', 'The Assumption of Mary', 'The Coronation of Mary'] },
  1: { set: 'Joyful', items: ['The Annunciation', 'The Visitation', 'The Nativity', 'The Presentation in the Temple', 'The Finding of the Child Jesus in the Temple'] },
  2: { set: 'Sorrowful', items: ['The Agony in the Garden', 'The Scourging at the Pillar', 'The Crowning with Thorns', 'The Carrying of the Cross', 'The Crucifixion'] },
  3: { set: 'Glorious', items: ['The Resurrection', 'The Ascension', 'The Descent of the Holy Spirit', 'The Assumption of Mary', 'The Coronation of Mary'] },
  4: { set: 'Luminous', items: ['The Baptism of the Lord', 'The Wedding at Cana', 'The Proclamation of the Kingdom', 'The Transfiguration', 'The Institution of the Eucharist'] },
  5: { set: 'Sorrowful', items: ['The Agony in the Garden', 'The Scourging at the Pillar', 'The Crowning with Thorns', 'The Carrying of the Cross', 'The Crucifixion'] },
  6: { set: 'Joyful', items: ['The Annunciation', 'The Visitation', 'The Nativity', 'The Presentation in the Temple', 'The Finding of the Child Jesus in the Temple'] }
};

// Daily Saint Charbel prayer: verbatim from the published saint-charbel-prayers page (never reworded).
const CHARBEL_PRAYER = 'O God, infinitely holy and glorified in Your saints, You inspired Saint Charbel to live and die in perfect union with Christ. Through his intercession, grant me the grace I seek in faith and trust: [name your intention]. Help me to walk in conversion, humility, and perseverance, and to surrender completely to Your will. Through Christ our Lord. Amen.';
const PRAYER_PAGES = [
  'saint-charbel-prayer-for-healing', 'saint-charbel-prayer-for-anxiety', 'saint-charbel-prayer-for-family',
  'saint-charbel-prayer-for-the-sick', 'saint-charbel-prayer-for-a-miracle', 'saint-charbel-prayer-for-students',
  'saint-charbel-prayers'
];

function json(status: number, body: unknown): Response {
  return new Response(JSON.stringify(body), { status, headers: { 'content-type': 'application/json', 'cache-control': 'no-store' } });
}

Deno.serve(async request => {
  if (request.method !== 'POST') return json(405, { error: 'method_not_allowed' });
  const cronSecret = Deno.env.get('DAILY_PRAYER_CRON_SECRET');
  const provided = request.headers.get('authorization') || '';
  if (!cronSecret || provided !== `Bearer ${cronSecret}`) return json(401, { error: 'unauthorized' });
  try {
    const supabaseUrl = Deno.env.get('SUPABASE_URL'); const serviceKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY');
    if (!supabaseUrl || !serviceKey) return json(503, { error: 'not_configured' });
    const db = createClient(supabaseUrl, serviceKey, { auth: { persistSession: false } });

    // Issue date anchors to the site owner's calendar (America/New_York).
    const nowEt = new Date(new Date().toLocaleString('en-US', { timeZone: 'America/New_York' }));
    const issueDate = `${nowEt.getFullYear()}-${String(nowEt.getMonth() + 1).padStart(2, '0')}-${String(nowEt.getDate()).padStart(2, '0')}`;
    const weekday = nowEt.getDay();
    const mystery = MYSTERIES[weekday];
    const prayerPage = PRAYER_PAGES[weekday];
    const issueDateLabel = nowEt.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' });

    const { data: claim, error: claimError } = await db.rpc('prayer_issue_claim', {
      p_issue_date: issueDate, p_mystery: mystery.set, p_prayer_key: prayerPage
    });
    if (claimError) throw claimError;
    if (claim?.error === 'send_disabled') return json(200, { skipped: 'send_disabled' });
    if (claim?.error === 'already_sent') return json(200, { skipped: 'already_sent', issue: claim.id });
    if (claim?.error || !claim?.id) return json(503, { error: 'claim_failed' });

    const issueId = claim.id as string;
    const cap = Math.max(1, Number(claim.cap) || 90);
    let attempted = Number(claim.attempted) || 0;
    let sent = Number(claim.sent) || 0;
    let failed = Number(claim.failed) || 0;
    let afterId: string | null = null;
    let deferred = 0;

    while (attempted < cap) {
      const { data: batch, error: batchError } = await db.rpc('prayer_confirmed_batch', { p_after_id: afterId, p_limit: 100 });
      if (batchError) throw batchError;
      if (!batch || batch.length === 0) break;
      for (const subscriber of batch) {
        if (attempted >= cap) { deferred++; continue; }
        afterId = subscriber.id;
        const unsubscribeUrl = `${supabaseUrl}/functions/v1/unsubscribe-prayer?token=${await mintSubscriberToken(subscriber.id)}`;
        const content: IssueContent = {
          issueDateLabel,
          mysterySet: mystery.set,
          mysteries: mystery.items,
          prayerTitle: 'Prayer to Saint Charbel',
          prayerText: CHARBEL_PRAYER,
          prayerPageUrl: `https://marsharbel.com/${prayerPage}`,
          prayersOfDayUrl: 'https://marsharbel.com/prayer-library',
          unsubscribeUrl
        };
        const email = issueEmail(content);
        const result = await sendEmail({
          to: subscriber.email,
          subject: email.subject,
          html: email.html,
          text: email.text,
          headers: { 'List-Unsubscribe': `<${unsubscribeUrl}>`, 'List-Unsubscribe-Post': 'List-Unsubscribe=One-Click' }
        });
        attempted++;
        if (result.ok) sent++; else failed++;
        await db.rpc('prayer_record_send', {
          p_issue_id: issueId, p_subscriber_id: subscriber.id,
          p_status: result.ok ? 'sent' : 'failed',
          p_provider_id: result.providerMessageId || '', p_error: result.error || ''
        });
        await new Promise(resolve => setTimeout(resolve, 120));
      }
      if (batch.length < 100) break;
    }
    if (deferred === 0) await db.rpc('prayer_issue_complete', { p_issue_id: issueId });
    return json(200, { issue: issueId, attempted, sent, failed, deferred, completed: deferred === 0 });
  } catch (error) {
    return json(503, { error: 'send_unavailable', detail: String(error).slice(0, 200) });
  }
});
