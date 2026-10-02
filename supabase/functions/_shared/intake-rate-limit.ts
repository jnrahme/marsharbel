// Only enable after the named gateway header's overwrite behavior is verified.
// Neither Origin nor arbitrary forwarding headers establish client identity.
export function normalizedGatewayIp(headers: Headers): string | null {
  const raw = headers.get('cf-connecting-ip')?.trim();
  if (!raw || raw.length > 64 || raw.includes(',') || raw.includes('%')) return null;
  if (/^\d{1,3}(\.\d{1,3}){3}$/.test(raw)) {
    const octets = raw.split('.');
    if (octets.some(part => String(Number(part)) !== part || Number(part) > 255)) return null;
    return octets.join('.');
  }
  if (!raw.includes(':') || !/^[0-9a-fA-F:]+$/.test(raw)) return null;
  try { return new URL(`http://[${raw}]/`).hostname.slice(1, -1).toLowerCase(); }
  catch { return null; }
}

export async function intakeRateAllowed(
  headers: Headers,
  config: { enabled: boolean; secret?: string },
  count: (hash: string) => Promise<boolean>
): Promise<boolean> {
  // Fail-open applies only to this supplemental limiter, not CAPTCHA/intake.
  if (!config.enabled || !config.secret || config.secret.length < 32) return true;
  const ip = normalizedGatewayIp(headers);
  if (!ip) return true;
  try {
    const key = await crypto.subtle.importKey('raw', new TextEncoder().encode(config.secret), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']);
    // Domain separation avoids reusing hashes as identifiers elsewhere.
    const digest = await crypto.subtle.sign('HMAC', key, new TextEncoder().encode('testimony-intake-v1:' + ip));
    const hash = [...new Uint8Array(digest)].map(byte => byte.toString(16).padStart(2, '0')).join('');
    return await count(hash);
  } catch { return true; }
}
