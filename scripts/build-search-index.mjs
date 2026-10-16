#!/usr/bin/env node
// Builds search-index/<locale>.json from the pages listed in sitemap.xml (the indexable canonical set).
// --check verifies coverage (every sitemap URL has a row), not byte equality of excerpts.
// Row shape: [url, title, description, headings, body, priority]. Run: npm run build:search-index (--check in CI).
import { readFile, writeFile, mkdir, readdir } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import path from 'node:path';

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const check = process.argv.includes('--check');
const BODY_MAX = 1600;
const LOCALES = ['ar', 'de', 'es', 'fr', 'hi', 'it', 'pl', 'pt', 'ru', 'th', 'zh-Hans'];

const ENT = { amp: '&', lt: '<', gt: '>', quot: '"', apos: "'", nbsp: ' ', rsquo: '’', lsquo: '‘', ldquo: '“', rdquo: '”', ndash: '–', mdash: '—', hellip: '…', laquo: '«', raquo: '»' };
const decode = s => s.replace(/&(#x[0-9a-f]+|#\d+|[a-z]+);/gi, (m, e) => {
  if (e[0] === '#') { const n = e[1].toLowerCase() === 'x' ? parseInt(e.slice(2), 16) : parseInt(e.slice(1), 10); try { return String.fromCodePoint(n); } catch { return ' '; } }
  return ENT[e.toLowerCase()] ?? m;
});
const squash = s => decode(s).replace(/\s+/g, ' ').trim();
const strip = html => squash(html.replace(/<[^>]*>/g, ' '));

function pageFile(url) {
  let p = decodeURIComponent(new URL(url).pathname);
  const cands = p.endsWith('/') ? [path.join(p, 'index.html')] : [p + '.html', path.join(p, 'index.html'), p];
  for (const c of cands) { const f = path.join(ROOT, c); if (existsSync(f) && f.endsWith('.html')) return f; }
  return null;
}

function localeOf(url) {
  const seg = new URL(url).pathname.split('/')[1] || '';
  return LOCALES.includes(seg) ? seg : 'en';
}

function extract(html) {
  if (/<meta[^>]+name=["']robots["'][^>]+content=["'][^"']*noindex/i.test(html)) return null;
  const title = squash((html.match(/<title[^>]*>([\s\S]*?)<\/title>/i) || [])[1] || '').replace(/\s*[|\u2013\u2014-]\s*(Saint Charbel|marsharbel\.com)\s*$/i, '');
  const desc = squash(((html.match(/<meta[^>]+name=["']description["'][^>]*>/i) || [''])[0].match(/content=["']([^"']*)["']/i) || [])[1] || '');
  let main = (html.match(/<main\b[^>]*>([\s\S]*?)<\/main>/i) || [])[1];
  if (!main) main = (html.match(/<body\b[^>]*>([\s\S]*)<\/body>/i) || [])[1] || '';
  main = main
    .replace(/<(script|style|noscript|svg|template|nav|header|footer|form|select|button)\b[\s\S]*?<\/\1>/gi, ' ')
    .replace(/<!--[\s\S]*?-->/g, ' ')
    .replace(/<[^>]+\bhidden\b[^>]*>[\s\S]*?(?=<)/gi, m => m); // hidden attr kept; text cheap
  const heads = [];
  main.replace(/<h([1-3])\b[^>]*>([\s\S]*?)<\/h\1>/gi, (_, __, inner) => { const t = strip(inner); if (t && !heads.includes(t)) heads.push(t); return ''; });
  let body = strip(main.replace(/<h[1-6]\b[\s\S]*?<\/h[1-6]>/gi, ' '));
  if (body.length > BODY_MAX) body = body.slice(0, BODY_MAX).replace(/\s+\S*$/, '');
  return { title, desc, heads: heads.join(' · ').slice(0, 600), body };
}

const sitemap = await readFile(path.join(ROOT, 'sitemap.xml'), 'utf8');
const entries = [...sitemap.matchAll(/<url>([\s\S]*?)<\/url>/g)].map(m => ({
  loc: (m[1].match(/<loc>([^<]+)<\/loc>/) || [])[1],
  pri: parseFloat((m[1].match(/<priority>([^<]+)<\/priority>/) || [])[1] || '0.5')
})).filter(e => e.loc);

const byLocale = {};
const skipped = [];
for (const e of entries) {
  const file = pageFile(e.loc);
  if (!file) { skipped.push(e.loc); continue; }
  const x = extract(await readFile(file, 'utf8'));
  if (!x || !x.title) { skipped.push(e.loc); continue; }
  const u = new URL(e.loc).pathname;
  (byLocale[localeOf(e.loc)] ||= []).push([u, x.title, x.desc, x.heads, x.body, e.pri]);
}

const outDir = path.join(ROOT, 'search-index');
await mkdir(outDir, { recursive: true });
const stale = [];
const expected = new Set();
for (const [loc, rows] of Object.entries(byLocale)) {
  rows.sort((a, b) => b[5] - a[5] || a[0].localeCompare(b[0]));
  const out = JSON.stringify(rows);
  const file = path.join(outDir, `${loc}.json`);
  expected.add(`${loc}.json`);
  const cur = existsSync(file) ? await readFile(file, 'utf8') : '';
  if (check) {
    // Coverage check only: page text drifts with every edit and news cycle, so CI
    // requires that each sitemap URL is present, not that excerpts are byte-identical.
    let have = [];
    try { have = JSON.parse(cur).map(r => r[0]); } catch { /* missing or corrupt */ }
    const want = rows.map(r => r[0]);
    if (want.length !== have.length || want.some(u => !have.includes(u))) stale.push(`search-index/${loc}.json`);
  } else if (cur !== out) { stale.push(`search-index/${loc}.json`); await writeFile(file, out); }
}
for (const f of await readdir(outDir)) if (!expected.has(f)) stale.push(`search-index/${f} (unexpected)`);
const total = Object.values(byLocale).reduce((n, r) => n + r.length, 0);
console.log(`search index: ${total} pages, ${Object.keys(byLocale).length} locales, ${skipped.length} sitemap URLs skipped${skipped.length ? ' (' + skipped.slice(0, 5).join(', ') + ')' : ''}; ${stale.length} ${check ? 'missing pages or out of coverage' : 'written'}.`);
if (stale.length) console.log(stale.join('\n'));
if (check && stale.length) process.exitCode = 1;
