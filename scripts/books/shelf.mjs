#!/usr/bin/env node
// /stories shelf from the canonical tree: counts, jump nav, shelf sections and every book card.
//   node scripts/books/shelf.mjs build | --check
// Template: templates/books/shelf-page.html (static copy and head stay hand-written there).
import fs from 'node:fs';
import path from 'node:path';
const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '../..');
const R = (...p) => path.join(ROOT, ...p);
const mode = process.argv[2] || '--check';
const jread = f => JSON.parse(fs.readFileSync(R(f), 'utf8'));
const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
const WORDS = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen', 'seventeen', 'eighteen', 'nineteen', 'twenty', 'twenty-one', 'twenty-two', 'twenty-three', 'twenty-four', 'twenty-five', 'twenty-six', 'twenty-seven', 'twenty-eight', 'twenty-nine', 'thirty', 'thirty-one', 'thirty-two', 'thirty-three', 'thirty-four', 'thirty-five', 'thirty-six', 'thirty-seven', 'thirty-eight', 'thirty-nine', 'forty'];

const dirs = fs.readdirSync(R('content/books')).filter(d => fs.existsSync(R('content/books', d, 'book.json')));
const byId = {};
for (const d of dirs) { const b = jread(`content/books/${d}/book.json`); byId[b.id] = { b, t: jread(`content/books/${d}/en.json`) }; }
const shelves = jread('content/shelves.json').shelves;
const total = shelves.reduce((n, s) => n + s.books.length, 0);
if (total >= WORDS.length) throw new Error('extend WORDS');

function card(id) {
  const { b, t } = byId[id];
  const cover = b.assets.find(a => a.id === b.cover);
  if (!t.linkLabel) throw new Error(`${b.slug}: en.json needs linkLabel`);
  return `<article class="promo-card reveal" data-keywords="${esc(t.keywords.join(' '))}">
          <picture><img src="./${cover.path}" width="${cover.width}" height="${cover.height}" alt="${esc(t.coverAlt)}" loading="lazy" decoding="async" /></picture>
          <div class="promo-body">${t.kicker ? `<span class="promo-kicker">${esc(t.kicker)}</span>` : ''}<h4>${esc(t.title)}</h4>
            <p>${esc(t.summary)}</p>
            <a class="promo-link" href="./${b.slug}">${esc(t.linkLabel)} <span aria-hidden="true">&rarr;</span></a>
          </div>
        </article>`;
}
const jump = `      <nav class="shelf-jump" aria-label="Storybook sections">\n${shelves.map(s => `        <a href="#shelf-${s.id}">${esc(s.title)} <span class="shelf-n">${s.books.length}</span></a>`).join('\n')}\n      </nav>`;
const sections = shelves.map(s => `      <section class="shelf-section" id="shelf-${s.id}" aria-labelledby="shelf-${s.id}-h">
        <div class="shelf-head"><h3 id="shelf-${s.id}-h">${esc(s.title)}</h3><p>${esc(s.description)}</p></div>
        <div class="grid-2 promo-grid">
${s.books.map(card).join('\n')}
        </div>
      </section>`).join('\n');
const out = fs.readFileSync(R('templates/books/shelf-page.html'), 'utf8')
  .replace(/@@count@@/g, String(total)).replace('@@countWord@@', WORDS[total]).replace('@@jump@@', () => jump).replace('@@sections@@', () => sections);
const file = R('src/pages/stories.html');
if (mode === 'build') { fs.writeFileSync(file, out); console.log('stories shelf: written'); }
else if (fs.readFileSync(file, 'utf8') !== out) { console.error('differs: src/pages/stories.html (run npm run books:pages)'); process.exit(1); }
else console.log('stories shelf: up to date');
