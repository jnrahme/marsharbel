// Stateless confirm/unsubscribe links: token = <subscriber uuid>.<hmac-sha256 hex of the uuid>.
// Verification recomputes the MAC; nothing token-like is stored in the database.
const encoder = new TextEncoder();

async function hmacHex(secret: string, value: string): Promise<string> {
  const key = await crypto.subtle.importKey('raw', encoder.encode(secret), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']);
  const signature = await crypto.subtle.sign('HMAC', key, encoder.encode(value));
  return Array.from(new Uint8Array(signature)).map(byte => byte.toString(16).padStart(2, '0')).join('');
}

const UUID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/;

export async function mintSubscriberToken(subscriberId: string): Promise<string> {
  const secret = Deno.env.get('DAILY_PRAYER_TOKEN_SECRET');
  if (!secret) throw new Error('token_secret_missing');
  return `${subscriberId}.${await hmacHex(secret, subscriberId)}`;
}

// Constant-time-ish: compare hex digests of equal length without early exit on position.
export async function verifySubscriberToken(token: string): Promise<string | null> {
  const secret = Deno.env.get('DAILY_PRAYER_TOKEN_SECRET');
  if (!secret) throw new Error('token_secret_missing');
  const dot = token.indexOf('.');
  if (dot <= 0) return null;
  const id = token.slice(0, dot);
  const mac = token.slice(dot + 1);
  if (!UUID_RE.test(id) || !/^[0-9a-f]{64}$/.test(mac)) return null;
  const expected = await hmacHex(secret, id);
  let diff = 0;
  for (let index = 0; index < 64; index++) diff |= expected.charCodeAt(index) ^ mac.charCodeAt(index);
  return diff === 0 ? id : null;
}
