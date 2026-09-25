export class IntakeError extends Error {
  constructor(public status: number, message: string) { super(message); }
}
export async function readJsonLimited(request: Request, limit = 30000): Promise<Record<string, unknown>> {
  if (!request.headers.get('content-type')?.toLowerCase().startsWith('application/json')) throw new IntakeError(415, 'Send JSON only.');
  const reader = request.body?.getReader();
  if (!reader) throw new IntakeError(400, 'Missing submission.');
  const chunks: Uint8Array[] = []; let size = 0;
  try {
    while (true) {
      const { done, value } = await reader.read(); if (done) break;
      size += value.byteLength;
      if (size > limit) { await reader.cancel(); throw new IntakeError(413, 'Submission is too large.'); }
      chunks.push(value);
    }
  } finally { reader.releaseLock(); }
  const data = new Uint8Array(size); let offset = 0;
  for (const chunk of chunks) { data.set(chunk, offset); offset += chunk.length; }
  try {
    const value = JSON.parse(new TextDecoder('utf-8', { fatal: true }).decode(data));
    if (!value || typeof value !== 'object' || Array.isArray(value)) throw new Error();
    return value;
  } catch { throw new IntakeError(400, 'Invalid submission.'); }
}
export function youtubeIdFromUrl(value: string): string | null {
  if (value.length > 500) return null;
  let url: URL;
  try { url = new URL(value.trim()); } catch { return null; }
  if (url.protocol !== 'https:' || url.username || url.password || url.port || url.hash) return null;
  const host = url.hostname.toLowerCase();
  const parts = url.pathname.split('/').filter(Boolean);
  if (parts.some(part => part === '.' || part === '..')) return null;
  let id: string | null = null;
  if (host === 'youtu.be' && parts.length === 1) id = parts[0];
  else if (['youtube.com','www.youtube.com','m.youtube.com','youtube-nocookie.com','www.youtube-nocookie.com'].includes(host)) {
    if (url.pathname === '/watch') id = url.searchParams.get('v');
    else if (parts.length === 2 && ['shorts','live','embed'].includes(parts[0])) id = parts[1];
  }
  return /^[A-Za-z0-9_-]{11}$/.test(id || '') ? id : null;
}
export function validateSubmission(body: Record<string, unknown>) {
  const field = (name: string, min: number, max: number) => {
    const value = typeof body[name] === 'string' ? (body[name] as string).trim() : '';
    if (value.length < min || value.length > max || /[\u0000-\u0008\u000b\u000c\u000e-\u001f]/.test(value)) throw new IntakeError(400, `Check ${name.replaceAll('_', ' ')}.`);
    return value;
  };
  if (body.website) throw new IntakeError(400, 'Submission blocked.');
  if (body.age_attested !== true || body.consent_publish !== true || body.ai_consent !== true) throw new IntakeError(400, 'Confirm age, publication consent, and screening consent.');
  const language = field('language', 2, 2);
  if (!['en', 'ar', 'fr'].includes(language)) throw new IntakeError(400, 'Choose a supported language.');
  const event_date = field('event_date', 0, 10);
  if (event_date && (!/^\d{4}-\d{2}-\d{2}$/.test(event_date) || Number.isNaN(Date.parse(event_date)) || new Date(event_date).toISOString().slice(0, 10) !== event_date || event_date > new Date().toISOString().slice(0, 10))) throw new IntakeError(400, 'Choose a valid past event date.');
  const youtube_url = field('youtube_url', 0, 500);
  const youtube_video_id = youtube_url ? youtubeIdFromUrl(youtube_url) : null;
  if (youtube_url && !youtube_video_id) throw new IntakeError(400, 'Enter a valid YouTube video link.');
  return { youtube_video_id, display_name: field('display_name', 2, 80), story: field('story', 60, 7000), language, country: field('country', 0, 100), event_date, age_attested: true, consent_publish: true, ai_consent: true };
}
export function redactForScreening(story: string) {
  return story.replace(/[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/gi, '[email removed]')
    .replace(/https?:\/\/\S+/gi, '[link removed]')
    .replace(/(?:\+?\d[\d ().-]{7,}\d)/g, '[number removed]');
}
export const reviewSchema = {
  type: 'object', additionalProperties: false,
  properties: {
    summary: { type: 'string' },
    recommendation: { type: 'string', enum: ['review', 'clarify', 'reject'] },
    flags: { type: 'array', items: { type: 'string', enum: ['spam', 'abuse', 'personal_information', 'solicitation', 'inconsistency', 'instructions_to_reviewer'] } },
    questions: { type: 'array', items: { type: 'string' } }
  }, required: ['summary', 'recommendation', 'flags', 'questions']
};
export function validateReview(value: unknown) {
  if (!value || typeof value !== 'object') throw new Error('Invalid review');
  const v = value as Record<string, unknown>;
  if (Object.keys(v).some(k => !reviewSchema.required.includes(k)) || typeof v.summary !== 'string' || v.summary.length > 1500 || !['review','clarify','reject'].includes(String(v.recommendation)) || !Array.isArray(v.flags) || v.flags.length > 6 || !v.flags.every(x => reviewSchema.properties.flags.items.enum.includes(x)) || !Array.isArray(v.questions) || v.questions.length > 5 || !v.questions.every(x => typeof x === 'string' && x.length <= 500)) throw new Error('Invalid review');
  return v;
}
