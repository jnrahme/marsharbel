#!/usr/bin/env node
// Reference sync client for the books content API (what an iOS/Android app does, in Node 18+).
//   node docs/examples/books-sync.mjs [apiOrigin] [cacheDir] [locale]
// Polls manifest.json, downloads only books whose sha256 changed, then downloads their
// media (images, audio) whose sha256 changed. Everything is verified against the hashes.
import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';

const origin = (process.argv[2] || 'https://marsharbel.com').replace(/\/$/, '');
const cache = process.argv[3] || './books-cache';
const locale = process.argv[4] || 'en';
const sha = b => crypto.createHash('sha256').update(b).digest('hex');
const get = async url => { const r = await fetch(url); if (!r.ok) throw new Error(`${r.status} ${url}`); return Buffer.from(await r.arrayBuffer()); };
const have = async f => fs.readFile(f).catch(() => null);

const manifest = JSON.parse((await get(`${origin}/api/v1/manifest.json`)).toString());
const mediaBase = (process.env.MEDIA_BASE_OVERRIDE || manifest.media.base).replace(/\/$/, "") + "/";
const mode = tier => (manifest.media.access[tier] || {}).mode;
const stats = { books: 0, booksSkipped: 0, media: 0, mediaSkipped: 0 };

for (const b of manifest.books) {
  const f = b.files[locale];
  if (!f) continue;                                   // locale not published for this book
  if (b.access !== 'public' && mode(b.access) !== 'direct') { continue; } // subscriber tier: needs a resolver, skipped here
  const local = path.join(cache, 'api', b.slug, `${locale}.json`);
  let bookBuf = await have(local);
  if (bookBuf && sha(bookBuf) === f.sha256) stats.booksSkipped++;
  else {
    bookBuf = await get(origin + f.path);
    if (sha(bookBuf) !== f.sha256) throw new Error(`hash mismatch ${f.path}`);
    await fs.mkdir(path.dirname(local), { recursive: true }); await fs.writeFile(local, bookBuf); stats.books++;
  }
  const book = JSON.parse(bookBuf.toString());
  for (const a of Object.values(book.assets)) {
    if (a.access !== 'public' && mode(a.access) !== 'direct') continue;
    const dest = path.join(cache, 'media', a.path);
    const cur = await have(dest);
    if (cur && sha(cur) === a.sha256) { stats.mediaSkipped++; continue; }
    const buf = await get(mediaBase + a.path);        // URL = media.base + asset.path, never stored in the data
    if (sha(buf) !== a.sha256) throw new Error(`hash mismatch ${a.path}`);
    await fs.mkdir(path.dirname(dest), { recursive: true }); await fs.writeFile(dest, buf); stats.media++;
  }
}
await fs.writeFile(path.join(cache, 'contentVersion.txt'), manifest.contentVersion);
console.log(`contentVersion ${manifest.contentVersion}`, stats);
