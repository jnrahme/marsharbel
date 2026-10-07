import { createClient } from 'https://esm.sh/@supabase/supabase-js@2.57.4';
import { intakeRateAllowed } from '../_shared/intake-rate-limit.ts';
import { IntakeError, readJsonLimited } from '../_shared/validation.ts';

function validateFeedback(body: Record<string, unknown>) {
  const field = (name: string, min: number, max: number) => {
    const value = typeof body[name] === 'string' ? (body[name] as string).trim() : '';
    if (value.length < min || value.length > max || /[\u0000-\u0008\u000b\u000c\u000e-\u001f]/.test(value)) throw new IntakeError(400, `Check ${name.replaceAll('_', ' ')}.`);
    return value;
  };
  if (body.website) throw new IntakeError(400, 'Submission blocked.');
  const category = field('category', 0, 20) || 'suggestion';
  if (!['suggestion', 'bug', 'praise', 'question', 'other'].includes(category)) throw new IntakeError(400, 'Choose a feedback type.');
  const email = field('email', 0, 254);
  if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email)) throw new IntakeError(400, 'Check email.');
  const page_url = field('page_url', 0, 300);
  if (page_url && !/^https:\/\/([a-z0-9-]+\.)?marsharbel\.com(\/|$)/.test(page_url)) throw new IntakeError(400, 'Check page link.');
  return { display_name: field('display_name', 0, 80), email, category, message: field('message', 10, 2000), page_url };
}

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
    if (!url || !key || !captchaSecret || !['turnstile', 'hcaptcha'].includes(provider) || (provider === 'hcaptcha' && !hcaptchaSitekey)) return reply(503, { message: 'Feedback is temporarily paused.' });
    const db = createClient(url, key, { auth: { persistSession: false } });
    const rateAllowed = await intakeRateAllowed(request.headers, {
      enabled: Deno.env.get('TESTIMONY_TRUST_CF_CONNECTING_IP') === 'true',
      secret: Deno.env.get('TESTIMONY_RATE_HMAC_KEY')
    }, async hash => {
      const result = await db.rpc('feedback_check_intake_rate', { p_ip_hash: hash }).abortSignal(AbortSignal.timeout(1500));
      if (result.error || typeof result.data !== 'boolean') throw new Error('Rate counter unavailable');
      return result.data;
    });
    if (!rateAllowed) return new Response(JSON.stringify({ message: 'Too many attempts. Please wait a few minutes and try again.' }), { status: 429, headers: { ...headers, 'retry-after': '300' } });

    const body = await readJsonLimited(request); const payload = validateFeedback(body);
    const token = typeof body.turnstile_token === 'string' ? body.turnstile_token : '';
    if (!token || token.length > 8192) return reply(400, { message: 'Complete the human verification.' });
    const response = await fetch(provider === 'hcaptcha' ? 'https://api.hcaptcha.com/siteverify' : 'https://challenges.cloudflare.com/turnstile/v0/siteverify', {
      method: 'POST', body: new URLSearchParams({ secret: captchaSecret, response: token, ...(provider === 'hcaptcha' ? { sitekey: hcaptchaSitekey! } : {}) }), signal: AbortSignal.timeout(8000)
    });
    if (!response.ok) throw new Error('verification unavailable');
    const verdict = await response.json();
    if (!verdict.success || (provider === 'turnstile' && verdict.action !== 'submit_feedback') || verdict.hostname !== new URL(origin).hostname) return reply(403, { message: 'Human verification expired or failed. Please try again.' });
    const { data, error } = await db.rpc('feedback_submit_guest', { p_payload: payload });
    if (error) throw error;
    if (data?.error) {
      const messages: Record<string,string> = { rate_limited: 'Submission limit reached. Please try another day.', duplicate: 'This feedback has already been sent.', intake_paused: 'Feedback is temporarily paused.' };
      return reply(data.error === 'intake_paused' ? 503 : 429, { message: messages[data.error] || 'Submission unavailable.' });
    }
    return reply(202, { accepted: true, reference: data.id });
  } catch (error) {
    return reply(error instanceof IntakeError ? error.status : 503, { message: error instanceof IntakeError ? error.message : 'Feedback service is unavailable. Your message has not been sent; please try again.' });
  }
});
