// marsharbel content API: read-only JSON, zero dependencies, data from files that reload on change.
import { createServer } from 'node:http';
import { readFileSync, statSync, writeFileSync, renameSync, existsSync, readdirSync } from 'node:fs';
import { createHash, timingSafeEqual } from 'node:crypto';
import { join } from 'node:path';

const LOCALES = ['en', 'ar', 'de', 'es', 'fr', 'hi', 'it', 'pl', 'pt', 'ru', 'th'];
const ORIGINS = new Set(['https://marsharbel.com', 'https://www.marsharbel.com']);
const WEEKDAYS = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'];
const DATE_RE = /^(\d{4})-(\d{2})-(\d{2})$/;
// Strict calendar check shared by every ?date= parameter: Date.parse rolls an impossible
// date like 2026-02-31 over to March, so format-plus-parse alone accepts fabricated dates.
export function isValidDate(date) {
  const m = DATE_RE.exec(date);
  if (!m) return false;
  const y = +m[1], mo = +m[2], d = +m[3];
  if (mo < 1 || mo > 12 || d < 1 || d > 31) return false;
  const dt = new Date(0);
  dt.setUTCFullYear(y, mo - 1, d);
  return dt.getUTCFullYear() === y && dt.getUTCMonth() === mo - 1 && dt.getUTCDate() === d;
}

export function createApp({ dataDir, adminToken = '', now = () => new Date() }) {
  const cache = new Map();
  const load = rel => {
    const p = join(dataDir, rel);
    if (!existsSync(p)) return null;
    const m = statSync(p).mtimeMs;
    const hit = cache.get(p);
    if (hit && hit.m === m) return hit.v;
    const v = JSON.parse(readFileSync(p, 'utf8'));
    cache.set(p, { m, v });
    return v;
  };
  const locale = q => (LOCALES.includes(q) ? q : 'en');
  const today = tz => new Intl.DateTimeFormat('en-CA', { timeZone: tz, year: 'numeric', month: '2-digit', day: '2-digit' }).format(now());

  function news(url) {
    const loc = locale(url.searchParams.get('locale'));
    const limit = Math.min(Math.max(parseInt(url.searchParams.get('limit') || '20', 10) || 20, 1), 50);
    const data = load(`news/${loc}.json`) || load('news/en.json');
    if (!data) return [503, { error: 'news_unavailable' }];
    return [200, { schema: 1, locale: data.locale, fallback: data.locale !== loc, heading: data.heading, allLabel: data.allLabel, items: data.items.slice(0, limit) }];
  }

  function newsItem(id, url) {
    const loc = locale(url.searchParams.get('locale'));
    const data = load(`news/${loc}.json`) || load('news/en.json');
    const item = data && data.items.find(i => i.id === id);
    return item ? [200, { schema: 1, locale: data.locale, fallback: data.locale !== loc, item }] : [404, { error: 'not_found' }];
  }

  function saintToday(url) {
    const loc = locale(url.searchParams.get('locale'));
    const date = url.searchParams.get('date') || today(load('rosary/daily.json')?.timezone || 'America/New_York');
    if (!isValidDate(date)) return [400, { error: 'bad_date' }];
    const saint = (load('saint-of-day.json')?.entries || {})[date];
    return saint ? [200, { schema: 1, date, locale: loc, saint }] : [404, { error: 'no_entry_for_date' }];
  }

  function rosary(url) {
    const loc = locale(url.searchParams.get('locale'));
    const cfg = load('rosary/daily.json');
    if (!cfg) return [503, { error: 'rosary_unavailable' }];
    const date = url.searchParams.get('date') || today(cfg.timezone);
    if (!isValidDate(date)) return [400, { error: 'bad_date' }];
    const weekday = WEEKDAYS[new Date(`${date}T12:00:00Z`).getUTCDay()];
    const set = cfg.weekdaySets[weekday];
    const saint = (load('saint-of-day.json')?.entries || {})[date] || null;
    const episodes = (cfg.episodes || []).filter(e => e.date === date);
    const ep = episodes.find(e => e.locale === loc) || null;
    return [200, { schema: 1, date, weekday, locale: loc, mysterySet: set, mysteryPage: cfg.setPages[set], saintOfDay: saint, episode: ep, episodeFallbackLocales: ep ? [] : episodes.map(e => e.locale) }];
  }

  function publishNews(body) {
    // Replace one locale's news file atomically. Shape-checked; items must keep real hrefs and image paths.
    const d = JSON.parse(body);
    if (!LOCALES.includes(d.locale) || d.schema !== 1 || !Array.isArray(d.items) || d.items.length < 1 || d.items.length > 50) throw new Error('invalid_shape');
    for (const i of d.items) {
      if (!i.id || !i.title || !/^\/[^/]/.test(i.href) || (i.image && !/^\/media\//.test(i.image.src || ''))) throw new Error('invalid_item');
    }
    const p = join(dataDir, `news/${d.locale}.json`);
    writeFileSync(`${p}.tmp`, JSON.stringify(d, null, 2) + '\n');
    renameSync(`${p}.tmp`, p);
    return d.locale;
  }

  const ok = (a, b) => { const x = Buffer.from(a), y = Buffer.from(b); return x.length === y.length && timingSafeEqual(x, y); };

  async function handler(req, res) {
    const origin = req.headers.origin;
    const headers = { 'Content-Type': 'application/json; charset=utf-8', 'X-Content-Type-Options': 'nosniff', Vary: 'Origin' };
    if (origin && ORIGINS.has(origin)) { headers['Access-Control-Allow-Origin'] = origin; headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'; }
    const send = (status, obj, extra = {}) => {
      const body = JSON.stringify(obj);
      const h = { ...headers, ...extra };
      if (status === 200 && req.method === 'GET') {
        h.ETag = `"${createHash('sha1').update(body).digest('hex').slice(0, 16)}"`;
        // An explicit Cache-Control from the route (health: no-store) wins over this default.
        h['Cache-Control'] = h['Cache-Control'] || 'public, max-age=60, stale-while-revalidate=300';
        if (req.headers['if-none-match'] === h.ETag) { res.writeHead(304, h); return res.end(); }
      }
      res.writeHead(status, h); res.end(req.method === 'HEAD' ? undefined : body);
    };
    const url = new URL(req.url, 'http://x');
    if (req.method === 'OPTIONS') { res.writeHead(204, headers); return res.end(); }
    if (req.method === 'PUT' && url.pathname === '/api/v1/admin/news') {
      const auth = (req.headers.authorization || '').replace(/^Bearer /, '');
      if (!adminToken || !ok(auth, adminToken)) return send(401, { error: 'unauthorized' });
      let raw = ''; for await (const c of req) { raw += c; if (raw.length > 200000) return send(413, { error: 'too_large' }); }
      try { return send(200, { published: publishNews(raw) }); } catch (e) { return send(422, { error: e.message }); }
    }
    if (req.method !== 'GET' && req.method !== 'HEAD') return send(405, { error: 'method_not_allowed' });
    try {
      const nm = url.pathname.match(/^\/api\/v1\/news\/([a-z0-9-]{1,120})$/);
      if (nm) return send(...newsItem(nm[1], url));
      switch (url.pathname) {
        case '/api/v1/health': return send(200, { ok: true, news: LOCALES.filter(l => existsSync(join(dataDir, `news/${l}.json`))).length, time: now().toISOString() }, { 'Cache-Control': 'no-store' });
        case '/api/v1/manifest.json': return send(200, { schema: 1, endpoints: ['/api/v1/news?locale=&limit=', '/api/v1/news/{id}?locale=', '/api/v1/rosary/today?locale=&date=', '/api/v1/saints/today?locale=&date='], locales: LOCALES });
        case '/api/v1/news': return send(...news(url));
        case '/api/v1/rosary/today': case '/api/v1/rosary/daily': return send(...rosary(url));
        case '/api/v1/saints/today': return send(...saintToday(url));
        case '/api/v1/prayers': case '/api/v1/search': return send(501, { error: 'not_implemented', phase: 4 });
        default: return send(404, { error: 'not_found' });
      }
    } catch (e) { return send(500, { error: 'internal' }); }
  }
  return { handler, server: () => createServer(handler) };
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const app = createApp({ dataDir: process.env.DATA_DIR || './data', adminToken: process.env.ADMIN_TOKEN || (process.env.ADMIN_TOKEN_FILE && existsSync(process.env.ADMIN_TOKEN_FILE) ? readFileSync(process.env.ADMIN_TOKEN_FILE, 'utf8').trim() : '') });
  app.server().listen(+(process.env.PORT || 8787), process.env.HOST || '127.0.0.1');
}
