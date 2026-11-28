import { createClient } from 'https://esm.sh/@supabase/supabase-js@2.57.4';
import { sendEmail } from '../_shared/email-adapter.ts';

// Staleness alerter for the email workers. Ops-only payload (worker name, timestamps) - no PII.
// Fail-closed: an unreadable heartbeat table is itself an alert condition.
const THRESHOLDS: Record<string, number> = {
  'prayer-request': 2 * 60 * 60 * 1000, // expected hourly
  'daily-prayer': 25 * 60 * 60 * 1000 // expected daily
};

function json(status: number, body: unknown): Response {
  return new Response(JSON.stringify(body), { status, headers: { 'content-type': 'application/json', 'cache-control': 'no-store' } });
}

async function alert(db: ReturnType<typeof createClient>, subject: string, lines: string[]): Promise<void> {
  const to = Deno.env.get('WORKER_ALERT_EMAIL') || '47sz72@mail.instinct.com';
  const text = lines.join('\n');
  const html = `<pre style="font:14px/1.5 monospace">${lines.map(l => l.replace(/&/g, '&amp;').replace(/</g, '&lt;')).join('<br>')}</pre>`;
  const result = await sendEmail({ to, subject: `[marsharbel-alert] ${subject}`, html, text });
  if (!result.ok) console.error('alert delivery failed', result.error || '');
}

Deno.serve(async request => {
  if (request.method !== 'POST') return json(405, { error: 'method_not_allowed' });
  const cronSecret = Deno.env.get('WORKER_ALERT_CRON_SECRET');
  const provided = request.headers.get('authorization') || '';
  if (!cronSecret || provided !== `Bearer ${cronSecret}`) return json(401, { error: 'unauthorized' });
  const supabaseUrl = Deno.env.get('SUPABASE_URL'); const serviceKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY');
  if (!supabaseUrl || !serviceKey) return json(503, { error: 'not_configured' });
  const db = createClient(supabaseUrl, serviceKey, { auth: { persistSession: false } });
  const now = Date.now();
  const stale: string[] = [];
  try {
    const { data, error } = await db.from('email_worker_heartbeat').select('worker,last_run_at');
    if (error) throw error;
    const seen = new Map((data || []).map((r: { worker: string; last_run_at: string }) => [r.worker, r.last_run_at]));
    for (const [worker, threshold] of Object.entries(THRESHOLDS)) {
      const last = seen.get(worker);
      const age = last ? now - Date.parse(last) : Infinity;
      if (age > threshold) stale.push(`${worker}: ${last ? `last run ${last} (${Math.round(age / 60000)} min ago)` : 'no heartbeat recorded'} exceeds ${Math.round(threshold / 60000)} min`);
    }
  } catch (error) {
    await alert(db, 'heartbeat check failed', [
      'The staleness alerter could not read email_worker_heartbeat.',
      `detail: ${String(error).slice(0, 200)}`,
      'Fail-closed: treat workers as unmonitored until this resolves.'
    ]);
    return json(200, { alerted: 'read_failure' });
  }
  if (stale.length > 0) {
    await alert(db, `worker heartbeat stale: ${stale.length}`, ['Stale email worker heartbeat(s):', ...stale, `checked at ${new Date(now).toISOString()}`]);
    return json(200, { alerted: stale.length });
  }
  return json(200, { ok: true });
});
