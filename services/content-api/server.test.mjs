import test from 'node:test';
import assert from 'node:assert/strict';
import { cpSync, mkdtempSync, readFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { createApp } from './server.mjs';

const root = join(import.meta.dirname, '..', '..');
const contentDir = join(root, 'content');
// Writable copy of the real deployment data set: everything the tests exercise ships in content/.
const dir = mkdtempSync(join(tmpdir(), 'capi-'));
cpSync(contentDir, dir, { recursive: true });
const app = createApp({ dataDir: dir, adminToken: 'secret', now: () => new Date('2026-10-14T15:00:00Z') });
const srv = app.server();
await new Promise(r => srv.listen(0, '127.0.0.1', r));
const base = `http://127.0.0.1:${srv.address().port}`;
const get = (p, h = {}) => fetch(base + p, { headers: h });
test.after(() => srv.close());

test('news en and ar', async () => {
  const en = await (await get('/api/v1/news?locale=en&limit=3')).json();
  assert.equal(en.items.length, 3); assert.equal(en.fallback, false);
  const ar = await (await get('/api/v1/news?locale=ar')).json();
  assert.equal(ar.locale, 'ar'); assert.match(ar.heading, /[\u0600-\u06FF]/);
  const bad = await (await get('/api/v1/news?locale=zz')).json();
  assert.equal(bad.locale, 'en');
});
test('rosary daily uses weekday set and saint', async () => {
  const r = await (await get('/api/v1/rosary/today?date=2026-10-14')).json();
  assert.equal(r.weekday, 'wednesday'); assert.equal(r.mysterySet, 'glorious'); assert.equal(r.saintOfDay.saint, 'jude');
  assert.equal((await (await get('/api/v1/rosary/today')).json()).date, '2026-10-14');
  assert.equal((await get('/api/v1/rosary/today?date=nope')).status, 400);
  assert.equal((await (await get('/api/v1/rosary/today?date=2026-10-15')).json()).mysterySet, 'luminous');
});
test('cors, etag, methods', async () => {
  const r = await get('/api/v1/news', { Origin: 'https://marsharbel.com' });
  assert.equal(r.headers.get('access-control-allow-origin'), 'https://marsharbel.com');
  assert.equal((await get('/api/v1/news', { 'If-None-Match': r.headers.get('etag') })).status, 304);
  assert.equal((await get('/api/v1/news', { Origin: 'https://evil.example' })).headers.get('access-control-allow-origin'), null);
  assert.equal((await fetch(base + '/api/v1/news', { method: 'DELETE' })).status, 405);
});
test('admin publish needs token and valid shape', async () => {
  const body = JSON.stringify({ schema: 1, locale: 'en', heading: 'Latest news', allLabel: 'x', items: [{ id: 'a', kind: 'row', href: '/news#a', title: 'T', image: { src: '/media/news/a.webp' } }] });
  assert.equal((await fetch(base + '/api/v1/admin/news', { method: 'PUT', body })).status, 401);
  assert.equal((await fetch(base + '/api/v1/admin/news', { method: 'PUT', body, headers: { Authorization: 'Bearer secret' } })).status, 200);
  assert.equal((await (await get('/api/v1/news?locale=en')).json()).items[0].id, 'a');
  const evil = body.replace('/media/news/a.webp', 'https://evil.example/x.png');
  assert.equal((await fetch(base + '/api/v1/admin/news', { method: 'PUT', body: evil, headers: { Authorization: 'Bearer secret' } })).status, 422);
});

test('news by id, saints today, unbuilt endpoints', async () => {
  const list = await (await get('/api/v1/news?locale=ar')).json();
  const one = await (await get('/api/v1/news/' + list.items[1].id + '?locale=ar')).json();
  assert.equal(one.item.id, list.items[1].id);
  assert.equal((await get('/api/v1/news/nope')).status, 404);
  assert.equal((await (await get('/api/v1/saints/today?date=2026-10-14')).json()).saint.saint, 'jude');
  assert.equal((await get('/api/v1/search?q=x')).status, 501);
});

test('shipped content seed serves the saint of the day for today', async () => {
  // The deployment seed itself, read straight from content/ - not an augmented fixture.
  const seed = JSON.parse(readFileSync(join(contentDir, 'saint-of-day.json'), 'utf8'));
  const today = new Intl.DateTimeFormat('en-CA', { timeZone: seed.timezone || 'America/New_York', year: 'numeric', month: '2-digit', day: '2-digit' }).format(new Date());
  const real = createApp({ dataDir: contentDir });
  const rs = real.server();
  await new Promise(r => rs.listen(0, '127.0.0.1', r));
  try {
    const res = await fetch(`http://127.0.0.1:${rs.address().port}/api/v1/saints/today?date=${today}`);
    assert.equal(res.status, 200, `seed must cover ${today}: regenerate content/saint-of-day.json from a fresh locales/saint-of-day.json`);
    assert.equal((await res.json()).saint.saint, seed.entries[today].saint);
  } finally {
    rs.close();
  }
});

test('impossible and malformed dates are rejected with 400', async () => {
  for (const bad of ['2026-02-31', '2026-02-29', '2026-13-01', '2026-00-10', '2026-10-00', '2026-2-3', '2026-10-14x']) {
    assert.equal((await get('/api/v1/rosary/today?date=' + bad)).status, 400, 'rosary ' + bad);
    assert.equal((await get('/api/v1/saints/today?date=' + bad)).status, 400, 'saints ' + bad);
  }
  // Leap day is real in 2024; rosary answers for any valid date, entry or not.
  assert.equal((await get('/api/v1/rosary/today?date=2024-02-29')).status, 200);
  const r = await (await get('/api/v1/rosary/today?date=2024-02-29')).json();
  assert.equal(r.date, '2024-02-29'); assert.equal(r.weekday, 'thursday');
});

test('health keeps its explicit Cache-Control: no-store', async () => {
  const h = await get('/api/v1/health');
  assert.equal(h.status, 200);
  assert.equal(h.headers.get('cache-control'), 'no-store');
  // Ordinary GET responses still get the public default.
  const n = await get('/api/v1/news?locale=en&limit=1');
  assert.match(n.headers.get('cache-control'), /^public, max-age=60/);
});
