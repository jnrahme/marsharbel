import test from 'node:test';
import assert from 'node:assert/strict';
import { cpSync, mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { createApp } from './server.mjs';

const root = join(import.meta.dirname, '..', '..');
const dir = mkdtempSync(join(tmpdir(), 'capi-'));
cpSync(join(root, 'content/news'), join(dir, 'news'), { recursive: true });
cpSync(join(root, 'content/rosary'), join(dir, 'rosary'), { recursive: true });
cpSync(join(root, 'locales/saint-of-day.json'), join(dir, 'saint-of-day.json'));
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
