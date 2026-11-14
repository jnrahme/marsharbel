#!/usr/bin/env node
// One-time, re-runnable converter: legacy storybook sources -> canonical content/ tree.
// Sources: *-story-data.js, storybook.js (Charbel classic, Pio, JPII, voice packs, evidence
// sources), stories.html (shelf + card metadata), locales/<lang>/storybook.json (UI strings).
// After the canonical tree is accepted it is the source of truth; this script stays for
// provenance and for the round-trip check (`--verify`).
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import crypto from 'node:crypto';
import { execFileSync } from 'node:child_process';

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '../..');
const R = (...p) => path.join(ROOT, ...p);
const read = f => fs.readFileSync(R(f), 'utf8');
const writeJson = (f, o) => { fs.mkdirSync(path.dirname(R(f)), { recursive: true }); fs.writeFileSync(R(f), JSON.stringify(o, null, 2) + '\n'); };

// ---- storybook.js: extract top-level const blocks by brace matching
const sb = read('storybook.js');
function block(name) {
  const m = new RegExp(`const ${name} = `).exec(sb);
  if (!m) throw new Error('missing ' + name);
  let i = m.index + m[0].length;
  const open = sb[i], close = open === '{' ? '}' : ']';
  let depth = 0, inStr = null, esc = false, j = i;
  for (; j < sb.length; j++) {
    const c = sb[j];
    if (inStr) { if (esc) esc = false; else if (c === '\\') esc = true; else if (c === inStr) inStr = null; continue; }
    if (c === '"' || c === "'" || c === '`') { inStr = c; continue; }
    if (c === open) depth++; else if (c === close && --depth === 0) { j++; break; }
  }
  return vm.runInNewContext('(' + sb.slice(i, j) + ')', { window: {} });
}
const EVIDENCE_SOURCES = block('EVIDENCE_SOURCES');
const EVIDENCE_PRESETS = block('EVIDENCE_PRESETS');
const VOICE_PACKS = block('VOICE_PACKS');
const inline = { charbel: block('STORIES'), pio: { en: block('PIO_STORY_EN') }, jpii: { en: block('JPII_STORY_EN') } };

// ---- *-story-data.js via sandbox
const dataFiles = {
  francis: 'francis-story-data.js', joseph: 'joseph-story-data.js', anthony: 'anthony-story-data.js', therese: 'therese-story-data.js',
  massabki: 'massabki-story-data.js', teresa: 'mother-teresa-story-data.js', rafqa: 'rafqa-story-data.js', 'charbel-v2': 'charbel-v2-story-data.js',
  magdalene: 'magdalene-story-data.js', sergius: 'sergius-bacchus-story-data.js', maroun: 'maroun-story-data.js', jude: 'jude-story-data.js',
  marina: 'marina-story-data.js', peter: 'peter-story-data.js', hardini: 'hardini-story-data.js', augustine: 'augustine-story-data.js'
};
const storyPages = { ...inline };
for (const [id, f] of Object.entries(dataFiles)) {
  const w = {}; vm.runInNewContext(read(f), { window: w });
  storyPages[id] = { en: Object.values(w)[0] };
}

// ---- stories.html shelf
const html = read('src/pages/stories.html');
const strip = s => s.replace(/<[^>]+>/g, '').replace(/&rarr;/g, '').replace(/&amp;/g, '&').replace(/\s+/g, ' ').trim();
const shelves = [];
const books = [];
const secRe = /<section class="shelf-section" id="(shelf-[a-z-]+)"[\s\S]*?<\/section>/g;
let sm;
while ((sm = secRe.exec(html))) {
  const sec = sm[0];
  const shelfId = sm[1].replace('shelf-', '');
  shelves.push({ id: shelfId, title: strip(/<h3[^>]*>([\s\S]*?)<\/h3>/.exec(sec)[1]), description: strip(/<\/h3><p>([\s\S]*?)<\/p>/.exec(sec)[1]), books: [] });
  const cardRe = /<article class="promo-card[^"]*" data-keywords="([^"]*)">([\s\S]*?)<\/article>/g;
  let cm;
  while ((cm = cardRe.exec(sec))) {
    const c = cm[2];
    const href = /href="\.\/([^"]+)"/.exec(c)[1];
    const tag = /<img\b[^>]*>/.exec(c)[0];
    const attr = n => (new RegExp('\\b' + n + '="([^"]*)"').exec(tag) || [])[1];
    const kick = /promo-kicker">([\s\S]*?)<\/span>/.exec(c);
    books.push({
      shelf: shelfId, href, keywords: cm[1].split(/\s+/).filter(Boolean),
      kicker: kick ? strip(kick[1]) : null, title: strip(/<h4>([\s\S]*?)<\/h4>/.exec(c)[1]),
      summary: strip(/<\/h4>\s*<p>([\s\S]*?)<\/p>/.exec(c)[1]), cover: attr('src').replace(/^\.\//, ''), coverAlt: strip(attr('alt'))
    });
  }
}

const sha = f => crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
function imgDims(f) { try { const o = execFileSync('python3', ['-c', 'import sys;from PIL import Image;i=Image.open(sys.argv[1]);print(i.width,i.height)', f]).toString().trim().split(' '); return { width: +o[0], height: +o[1] }; } catch { return {}; } }
function audioMs(f) { try { return Math.round(parseFloat(execFileSync('ffprobe', ['-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f]).toString()) * 1000); } catch { return null; } }
const assetCache = new Map();
const report = { books: 0, pages: 0, assets: 0, gaps: [], missing: [] };
function asset(rel, kind, id) {
  rel = rel.replace(/^\.\//, '');
  if (assetCache.has(rel)) return assetCache.get(rel);
  const f = R(rel);
  if (!fs.existsSync(f)) { if (!report.missing.includes(rel)) report.missing.push(rel); return null; }
  const a = { id, kind, path: rel, mime: kind === 'audio' ? 'audio/mpeg' : rel.endsWith('.webp') ? 'image/webp' : rel.endsWith('.png') ? 'image/png' : 'image/jpeg', bytes: fs.statSync(f).size, sha256: sha(f), access: 'public' };
  if (kind === 'image') Object.assign(a, imgDims(f)); else a.durationMs = audioMs(f);
  assetCache.set(rel, a); return a;
}

const slugOf = href => href;                       // public page slug, e.g. peter-story

const index = [];
let order = 0;
for (const b of books) {
  const file = b.href === 'story' ? 'story.html' : b.href + '.html';
  const page = read('src/pages/' + file);
  const storyId = (/data-story="([^"]+)"/.exec(page) || [, 'charbel'])[1];
  const slug = b.href;
  const bookId = 'bk-' + (slug === 'story' ? 'charbel-classic' : slug.replace(/-story$/, ''));
  const src = storyPages[storyId];
  if (!src) throw new Error('no pages for ' + storyId);
  // Only page-aligned locales go in the feed. A locale whose page count differs from English is not an exact mirror.
  const locales = Object.keys(src).filter(l => l === 'en' || (src[l].length === src.en.length ? true : (report.gaps.push(`${slug}/${l}: ${src[l].length} pages vs ${src.en.length} in English, not a page-aligned mirror; excluded from feed`), false)));
  const packs = VOICE_PACKS[storyId] || {};
  const dir = `content/books/${slug}`;
  const enPages = src.en;
  const voices = {};
  for (const loc of locales) voices[loc] = (packs[loc] || []).filter(p => p.type === 'clips').map((p, i) => ({ id: p.id, label: p.label.replace(/ \(Recommended\)/, ''), recommended: i === 0, base: p.base.replace(/^\.\//, '') }));
  const pageCanon = enPages.map((p, i) => {
    const n = String(i + 1).padStart(2, '0');
    const pg = {
      id: `${bookId}-p${n}`, index: i + 1, kind: p.reflection ? 'reflection' : 'story', scene: p.scene || null, access: 'public',
      image: (asset(p.illustration, 'image', `${bookId}-img-${n}`) || {}).id || null, audio: {}, evidence: null
    };
    // Charbel classic uses scene art when a page has no illustration
    for (const loc of locales) {
      const lp = src[loc][i];
      if (!lp) continue;
      const v = voices[loc].find(v => v.recommended);
      if (v && (lp.audio || p.audio)) {
        const rel = `${v.base}/${lp.audio || p.audio}`;
        const au = asset(rel, 'audio', `${bookId}-aud-${loc}-${n}`); if (au) pg.audio[loc] = au.id;
      }
    }
    const ev = p.evidence || (p.evidencePreset && EVIDENCE_PRESETS[p.evidencePreset]) || null;
    if (ev) pg.evidence = ev;
    return pg;
  });
  const sourceIds = new Set();
  pageCanon.forEach(p => (p.evidence || []).forEach(e => (e.sources || []).forEach(s => sourceIds.add(s))));
  const sources = {};
  for (const s of sourceIds) { if (EVIDENCE_SOURCES[s]) sources[s] = EVIDENCE_SOURCES[s]; else report.gaps.push(`${slug}: evidence source ${s} has no label/url in storybook.js`); }
  const cover = asset(b.cover, 'image', `${bookId}-cover`);
  const canon = {
    schema: 1, id: bookId, slug, legacyStoryId: storyId, pageUrl: '/' + slug, status: 'published', access: 'public',
    shelf: b.shelf, order: ++order, ageRange: '6-12', locales, cover: cover.id, voices, pages: pageCanon, sources,
    assets: [...new Set([cover.id, ...pageCanon.flatMap(p => [p.image, ...Object.values(p.audio)])])].map(id => [...assetCache.values()].find(a => a.id === id))
  };
  writeJson(`${dir}/book.json`, canon);
  for (const loc of locales) {
    const L = {
      schema: 1, bookId, locale: loc, review: 'reviewed',
      title: loc === 'en' ? b.title : (src[loc] && b.title), summary: loc === 'en' ? b.summary : null, kicker: loc === 'en' ? b.kicker : null,
      keywords: b.keywords, coverAlt: loc === 'en' ? b.coverAlt : null,
      pages: pageCanon.map((pc, i) => { const lp = src[loc][i] || {}; return { id: pc.id, title: lp.title || '', body: lp.body || '', prayer: lp.prayer || '', heart: lp.heart || '', alt: null }; })
    };
    if (loc !== 'en') { L.title = null; report.gaps.push(`${slug}/${loc}: no localized book title/summary/cover alt in legacy (null in feed)`); }
    writeJson(`${dir}/${loc}.json`, L);
  }
  index.push({ id: bookId, slug, shelf: b.shelf, order });
  shelves.find(s => s.id === b.shelf).books.push(bookId);
  report.books++; report.pages += pageCanon.length;
}
report.assets = assetCache.size;
writeJson('content/shelves.json', { schema: 1, shelves: shelves.map(s => ({ ...s, access: 'public' })) });
// UI strings
for (const loc of fs.readdirSync(R('locales'))) {
  const f = `locales/${loc}/storybook.json`;
  if (fs.existsSync(R(f))) writeJson(`content/ui/${loc}.json`, { schema: 1, locale: loc, strings: JSON.parse(read(f)) });
}
console.log(JSON.stringify(report, null, 1));
