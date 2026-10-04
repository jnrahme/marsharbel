#!/usr/bin/env node
// Proves the feed is lossless against the legacy sources (storybook.js + *-story-data.js):
// every page title/body/prayer/heart, illustration path and audio clip path must match.
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '../..');
const read = f => fs.readFileSync(path.join(ROOT, f), 'utf8');
const sb = read('storybook.js');
function block(name) {
  const m = new RegExp(`const ${name} = `).exec(sb); let i = m.index + m[0].length;
  const open = sb[i], close = open === '{' ? '}' : ']'; let d = 0, q = null, e = false, j = i;
  for (; j < sb.length; j++) { const c = sb[j]; if (q) { if (e) e = false; else if (c === '\\') e = true; else if (c === q) q = null; continue; } if ('"\'`'.includes(c)) { q = c; continue; } if (c === open) d++; else if (c === close && --d === 0) { j++; break; } }
  return vm.runInNewContext('(' + sb.slice(i, j) + ')', { window: {} });
}
const VOICE = block('VOICE_PACKS');
const legacy = { charbel: block('STORIES').en, pio: block('PIO_STORY_EN'), jpii: block('JPII_STORY_EN') };
const files = { francis: 'francis-story-data.js', joseph: 'joseph-story-data.js', anthony: 'anthony-story-data.js', therese: 'therese-story-data.js', massabki: 'massabki-story-data.js', teresa: 'mother-teresa-story-data.js', rafqa: 'rafqa-story-data.js', 'charbel-v2': 'charbel-v2-story-data.js', magdalene: 'magdalene-story-data.js', sergius: 'sergius-bacchus-story-data.js', maroun: 'maroun-story-data.js', jude: 'jude-story-data.js', marina: 'marina-story-data.js', peter: 'peter-story-data.js', hardini: 'hardini-story-data.js' };
for (const [id, f] of Object.entries(files)) { const w = {}; vm.runInNewContext(read(f), { window: w }); legacy[id] = Object.values(w)[0]; }
const manifest = JSON.parse(read('api/v1/manifest.json'));
let pages = 0, bad = 0;
for (const mb of manifest.books) {
  const book = JSON.parse(read(`api/v1/books/${mb.slug}/en.json`));
  const sid = JSON.parse(read(`content/books/${mb.slug}/book.json`)).legacyStoryId;
  const src = legacy[sid];
  if (src.length !== book.pages.length) { console.error(`${mb.slug}: page count ${src.length} vs ${book.pages.length}`); bad++; continue; }
  const base = VOICE[sid].en.find(v => v.type === 'clips').base.replace(/^\.\//, '');
  src.forEach((p, i) => {
    const g = book.pages[i]; pages++;
    const chk = (a, b, w) => { if ((a || '') !== (b || '')) { console.error(`${mb.slug} p${i + 1} ${w} differs`); bad++; } };
    chk(p.title, g.title, 'title'); chk(p.body, g.body, 'body'); chk(p.prayer, g.prayer, 'prayer'); chk(p.heart, g.heart, 'heart');
    chk(p.illustration.replace(/^\.\//, ''), book.assets[g.image].path, 'image');
    chk(`${base}/${p.audio}`, g.audio ? book.assets[g.audio].path : '', 'audio');
  });
}
console.log(`roundtrip: ${manifest.books.length} books, ${pages} pages, ${bad} differences`);
process.exit(bad ? 1 : 0);
