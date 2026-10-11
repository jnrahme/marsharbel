// Delivery-adapter seam: the subscription system owns content, list and logging;
// the provider only delivers. Swap providers with EMAIL_PROVIDER without touching callers.
export interface OutboundEmail {
  to: string;
  subject: string;
  html: string;
  text: string;
  headers?: Record<string, string>;
  replyTo?: string;
}

export interface SendResult {
  ok: boolean;
  providerMessageId?: string;
  error?: string;
}

export async function sendEmail(message: OutboundEmail): Promise<SendResult> {
  const provider = (Deno.env.get('EMAIL_PROVIDER') || 'resend').toLowerCase();
  if (provider !== 'resend') return { ok: false, error: `unsupported_provider:${provider}` };
  const apiKey = Deno.env.get('RESEND_API_KEY');
  const from = Deno.env.get('DAILY_PRAYER_FROM_EMAIL');
  const fromName = Deno.env.get('DAILY_PRAYER_FROM_NAME') || 'Mar Charbel Daily Prayer';
  if (!apiKey || !from) return { ok: false, error: 'provider_not_configured' };
  try {
    const response = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: { authorization: `Bearer ${apiKey}`, 'content-type': 'application/json' },
      body: JSON.stringify({
        from: `${fromName} <${from}>`,
        to: [message.to],
        subject: message.subject,
        html: message.html,
        text: message.text,
        ...(message.replyTo ? { reply_to: message.replyTo } : {}),
        ...(message.headers ? { headers: message.headers } : {})
      }),
      signal: AbortSignal.timeout(10000)
    });
    const body = await response.json().catch(() => ({}));
    if (!response.ok) return { ok: false, error: `resend_${response.status}:${(body?.message || 'send_failed').slice(0, 200)}` };
    return { ok: true, providerMessageId: typeof body?.id === 'string' ? body.id : '' };
  } catch (error) {
    return { ok: false, error: `provider_unreachable:${String(error).slice(0, 120)}` };
  }
}
