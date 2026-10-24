#!/usr/bin/env node
// Books content API generator: content/ (canonical) -> api/v1/ (static, versioned JSON).
//   node scripts/books/build-api.mjs            write api/v1
//   node scripts/books/build-api.mjs --check    fail if api/v1 is stale or content is invalid
// Output is deterministic (no timestamps) so --check can diff byte for byte.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '../..');
const R = (...p) => path.join(ROOT, ...p);
const CHECK = process.argv.includes('--check');
const API = 'api/v1';
const MEDIA_BASE = 'https://marsharbel.com/';
const TIERS = ['public', 'subscriber'];
const jread = f => JSON.parse(fs.readFileSync(R(f), 'utf8'));
const sha = b => crypto.createHash('sha256').update(b).digest('hex');
const errors = [];
const err = m => errors.push(m);

const out = new Map(); // relative path -> string
const emit = (rel, obj) => out.set(`${API}/${rel}`, JSON.stringify(obj, null, 1) + '\n');

const shelvesSrc = jread('content/shelves.json');
const slugs = fs.readdirSync(R('content/books')).filter(d => fs.existsSync(R('content/books', d, 'book.json'))).sort();
const books = slugs.map(s => ({ dir: s, ...jread(`content/books/${s}/book.json`) })).sort((a, b) => a.order - b.order);
const uiLocales = fs.existsSync(R('content/ui')) ? fs.readdirSync(R('content/ui')).filter(f => f.endsWith('.json')).map(f => f.slice(0, -5)).sort() : [];

const seenIds = new Set();
const uniq = (id, what) => { if (seenIds.has(id)) err(`duplicate id ${id} (${what})`); seenIds.add(id); };
const tier = (v, where) => { if (!TIERS.includes(v)) err(`${where}: access must be one of ${TIERS.join('|')}, got ${v}`); };
const allLocales = new Set(['en']);
const manifestBooks = [];
const summaries = {};

for (const b of books) {
  for (const k of ['id', 'slug', 'access', 'shelf', 'order', 'cover', 'pages', 'locales', 'assets']) if (b[k] == null) err(`${b.slug}: missing ${k}`);
  uniq(b.id, 'book'); tier(b.access, b.slug);
  const assets = Object.fromEntries(b.assets.map(a => [a.id, a]));
  for (const a of b.assets) {
    uniq(a.id, 'asset'); tier(a.access, a.id);
    const f = R(a.path);
    if (!fs.existsSync(f)) { err(`${a.id}: file missing ${a.path}`); continue; }
    const buf = fs.readFileSync(f);
    if (buf.length !== a.bytes || sha(buf) !== a.sha256) err(`${a.id}: bytes/sha256 differ from ${a.path} (re-run extract or update content)`);
  }
  const needAsset = (id, where) => { if (!assets[id]) err(`${where}: unknown asset ${id}`); };
  needAsset(b.cover, b.slug + ' cover');
  const files = {};
  for (const loc of b.locales) {
    allLocales.add(loc);
    const t = jread(`content/books/${b.dir}/${loc}.json`);
    if (t.bookId !== b.id || t.locale !== loc) err(`${b.slug}/${loc}: bookId/locale mismatch`);
    if (t.pages.length !== b.pages.length) err(`${b.slug}/${loc}: ${t.pages.length} pages vs ${b.pages.length}`);
    if (loc === 'en' && !(t.title && t.summary)) err(`${b.slug}/en: title and summary required`);
    const tp = Object.fromEntries(t.pages.map(p => [p.id, p]));
    const used = new Set([b.cover]);
    const pages = b.pages.map(p => {
      uniq(p.id + ':' + loc, 'page-locale'); tier(p.access, p.id);
      const x = tp[p.id];
      if (!x) { err(`${b.slug}/${loc}: missing text for ${p.id}`); return null; }
      if (!x.body.trim()) err(`${p.id}/${loc}: empty body`);
      for (const f of ['title', 'body', 'prayer', 'heart']) if (/https?:\/\//.test(x[f] || '')) err(`${p.id}/${loc}: URL baked into ${f}`);
      needAsset(p.image, p.id);
      used.add(p.image);
      const aud = p.audio[loc] || null; if (aud) { needAsset(aud, p.id); used.add(aud); }
      return {
        id: p.id, index: p.index, kind: p.kind, scene: p.scene, access: p.access,
        title: x.title, body: x.body, prayer: x.prayer || null, heart: x.heart || null,
        image: p.image, imageAlt: x.alt || null, audio: aud,
        evidence: (p.evidence || []).map(e => ({ type: e.type, claim: e.claim, sources: e.sources || [] }))
      };
    });
    const srcIds = new Set(pages.flatMap(p => p ? p.evidence.flatMap(e => e.sources) : []));
    const sources = {};
    for (const s of [...srcIds].sort()) if (b.sources[s]) sources[s] = b.sources[s];
    const doc = {
      schema: 1, id: b.id, slug: b.slug, locale: loc, access: b.access, status: b.status, shelf: b.shelf, ageRange: b.ageRange,
      webUrl: b.pageUrl, title: t.title, summary: t.summary, kicker: t.kicker, keywords: t.keywords, review: t.review,
      cover: b.cover, coverAlt: t.coverAlt || null,
      voices: b.voices[loc] || [], pages, sources,
      assets: Object.fromEntries([...used].sort().map(id => [id, (({ id, kind, path, mime, bytes, sha256, access, width, height, durationMs }) => ({ id, kind, path, mime, bytes, sha256, access, ...(width ? { width, height } : {}), ...(durationMs != null ? { durationMs } : {}) }))(assets[id])]))
    };
    const rel = `books/${b.slug}/${loc}.json`;
    const text = JSON.stringify(doc, null, 1) + '\n';
    out.set(`${API}/${rel}`, text);
    files[loc] = { path: `${API}/${rel}`.replace(/^/, '/'), sha256: sha(text), bytes: Buffer.byteLength(text) };
    (summaries[loc] ||= []).push({ id: b.id, slug: b.slug, access: b.access, shelf: b.shelf, order: b.order, title: t.title, summary: t.summary, kicker: t.kicker, cover: doc.assets[b.cover], coverAlt: t.coverAlt || null, pageCount: pages.length, hasAudio: pages.some(p => p && p.audio) });
  }
  manifestBooks.push({ id: b.id, slug: b.slug, access: b.access, status: b.status, order: b.order, shelf: b.shelf, locales: b.locales, files });
}
for (const s of shelvesSrc.shelves) for (const id of s.books) if (!books.find(b => b.id === id)) err(`shelf ${s.id}: unknown book ${id}`);
for (const b of books) if (!shelvesSrc.shelves.some(s => s.books.includes(b.id))) err(`${b.slug}: not on any shelf`);

// Gate: the /stories shelf and the feed must list exactly the same books.
{
  const shelfHtml = fs.readFileSync(R('src/pages/stories.html'), 'utf8');
  const onShelf = [...shelfHtml.matchAll(/<article class="promo-card[^"]*"[^>]*>[\s\S]*?<\/article>/g)]
    .map(m => (/href="\.\/([^"]+)"/.exec(m[0]) || [])[1]).filter(Boolean);
  const inFeed = books.map(b => b.slug);
  for (const s of onShelf) if (!inFeed.includes(s)) err(`stories.html lists "${s}" but it is not in content/ (add it to the converter list, run extract-legacy.mjs, then books:api)`);
  for (const s of inFeed) if (!onShelf.includes(s)) err(`content/ has "${s}" but stories.html does not list it`);
  if (new Set(onShelf).size !== onShelf.length) err('stories.html lists a book twice');
}

for (const loc of Object.keys(summaries)) emit(`books.${loc}.json`, { schema: 1, locale: loc, books: summaries[loc] });
emit('shelves.json', { schema: 1, shelves: shelvesSrc.shelves.map(s => ({ id: s.id, access: s.access, title: { en: s.title }, description: { en: s.description }, books: s.books })) });
for (const loc of uiLocales) { const u = jread(`content/ui/${loc}.json`); emit(`ui/${loc}.json`, u); }

const hashAll = sha([...out.entries()].sort(([a], [b]) => a < b ? -1 : 1).map(([k, v]) => k + sha(v)).join('\n'));
emit('manifest.json', {
  schema: 1, contentVersion: hashAll.slice(0, 16), apiBase: '/api/v1',
  // Media access is configuration. Today every asset is public and fetched directly from
  // mediaBase + asset.path. A subscriber tier switches `subscriber.mode` to "signed-url" (or
  // an authenticated path) and points `resolver` at it: asset ids, paths and tiers do not change.
  media: { base: MEDIA_BASE, access: { public: { mode: 'direct' }, subscriber: { mode: 'unconfigured', resolver: null } } },
  tiers: TIERS, locales: [...allLocales].sort(), uiLocales,
  indexes: { books: Object.fromEntries(Object.keys(summaries).map(l => [l, `/${API}/books.${l}.json`])), shelves: `/${API}/shelves.json` },
  books: manifestBooks
});

out.set(`${API}/.htaccess`, fs.readFileSync(R('scripts/books/api.htaccess'), 'utf8'));

if (errors.length) { console.error('Books API validation failed:\n- ' + errors.slice(0, 50).join('\n- ') + (errors.length > 50 ? `\n(+${errors.length - 50} more)` : '')); process.exit(1); }

if (CHECK) {
  let stale = 0;
  for (const [rel, text] of out) { const f = R(rel); if (!fs.existsSync(f) || fs.readFileSync(f, 'utf8') !== text) { console.error('stale: ' + rel); stale++; } }
  const have = fs.existsSync(R(API)) ? walk(R(API)) : [];
  for (const f of have) { const rel = path.relative(ROOT, f); if (!out.has(rel)) { console.error('orphan: ' + rel); stale++; } }
  if (stale) process.exit(1);
  console.log(`books api: ${out.size} files up to date (contentVersion ${hashAll.slice(0, 16)})`);
} else {
  fs.rmSync(R(API), { recursive: true, force: true });
  for (const [rel, text] of out) { fs.mkdirSync(path.dirname(R(rel)), { recursive: true }); fs.writeFileSync(R(rel), text); }
  console.log(`books api: wrote ${out.size} files (contentVersion ${hashAll.slice(0, 16)})`);
}
function walk(d) { return fs.readdirSync(d, { withFileTypes: true }).flatMap(e => e.isDirectory() ? walk(path.join(d, e.name)) : [path.join(d, e.name)]); }
