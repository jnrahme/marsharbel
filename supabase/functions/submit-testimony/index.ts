import { createClient } from 'https://esm.sh/@supabase/supabase-js@2.57.4';
import { IntakeError, readJsonLimited, validateSubmission } from '../_shared/validation.ts';

Deno.serve(async request => {
  const origins = (Deno.env.get('TESTIMONY_ALLOWED_ORIGINS') || '').split(',').map(s => s.trim()).filter(Boolean);
  const origin = request.headers.get('origin') || '';
  const allowed = origins.includes(origin);
  const headers: Record<string, string> = { 'content-type': 'application/json', 'cache-control': 'no-store', 'x-content-type-options': 'nosniff', 'vary': 'Origin' };
  if (allowed) Object.assign(headers, { 'access-control-allow-origin': origin, 'access-control-allow-headers': 'authorization, apikey, content-type, x-client-info', 'access-control-allow-methods': 'POST, OPTIONS' });
  const reply = (status: number, body: unknown) => new Response(JSON.stringify(body), { status, headers });
  if (!allowed) return reply(403, { message: 'Origin not allowed.' });
  if (request.method === 'OPTIONS') return new Response(null, { status: 204, headers });
  if (request.method !== 'POST') return reply(405, { message: 'Method not allowed.' });
  try {
    const url = Deno.env.get('SUPABASE_URL'); const key = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY'); const provider = Deno.env.get('TESTIMONY_CAPTCHA_PROVIDER') || 'turnstile';
    const captchaSecret = Deno.env.get(provider === 'hcaptcha' ? 'HCAPTCHA_SECRET_KEY' : 'TURNSTILE_SECRET_KEY');
    const hcaptchaSitekey = Deno.env.get('HCAPTCHA_SITE_KEY');
    if (!url || !key || !captchaSecret || !['turnstile', 'hcaptcha'].includes(provider) || (provider === 'hcaptcha' && !hcaptchaSitekey)) return reply(503, { message: 'Submissions are temporarily paused.' });
    const db = createClient(url, key, { auth: { persistSession: false } });
    const body = await readJsonLimited(request); const payload = validateSubmission(body);
    const token = typeof body.turnstile_token === 'string' ? body.turnstile_token : '';
    if (!token || token.length > 8192) return reply(400, { message: 'Complete the human verification.' });
    const response = await fetch(provider === 'hcaptcha' ? 'https://api.hcaptcha.com/siteverify' : 'https://challenges.cloudflare.com/turnstile/v0/siteverify', {
      method: 'POST', body: new URLSearchParams({ secret: captchaSecret, response: token, ...(provider === 'hcaptcha' ? { sitekey: hcaptchaSitekey! } : {}) }), signal: AbortSignal.timeout(8000)
    });
    if (!response.ok) throw new Error('verification unavailable');
    const verdict = await response.json();
    if (!verdict.success || (provider === 'turnstile' && verdict.action !== 'submit_testimony') || verdict.hostname !== new URL(origin).hostname) return reply(403, { message: 'Human verification expired or failed. Please try again.' });
    const { data, error } = await db.rpc('testimony_submit_guest', { p_payload: payload });
    if (error) throw error;
    if (data?.error) {
      const messages: Record<string,string> = { rate_limited: 'Submission limit reached. Please try another day.', pending_limit: 'You already have three stories awaiting review.', duplicate: 'This story has already been submitted.', intake_paused: 'Submissions are temporarily paused.', verified_account_required: 'Verify your email before submitting.' };
      return reply(data.error === 'intake_paused' ? 503 : 429, { message: messages[data.error] || 'Submission unavailable.' });
    }
    return reply(202, { accepted: true, reference: data.id });
  } catch (error) {
    return reply(error instanceof IntakeError ? error.status : 503, { message: error instanceof IntakeError ? error.message : 'Submission service is unavailable. Your story has not been confirmed; check your account before retrying.' });
  }
});
