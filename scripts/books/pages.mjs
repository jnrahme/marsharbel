#!/usr/bin/env node
// Story pages from the canonical tree.
//   node scripts/books/pages.mjs extract   parse existing src/pages/<slug>.html into content/books/<slug>/page.json
//                                          when (and only when) the page regenerates byte-identically
//   node scripts/books/pages.mjs build     write src/pages/<slug>.html for every book that has page.json
//   node scripts/books/pages.mjs --check   fail if any generated page differs from its source file
// Books without page.json are "hand-authored": their src/pages file stays the source of truth.
import fs from 'node:fs';
import path from 'node:path';

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '../..');
const R = (...p) => path.join(ROOT, ...p);
const mode = process.argv[2] || '--check';
const TEMPLATES = Object.fromEntries(fs.readdirSync(R('templates/books')).filter(f => f.endsWith('.html')).sort().map(f => [f.slice(0, -5), fs.readFileSync(R('templates/books', f), 'utf8')]));
const SITE = 'https://marsharbel.com';
const esc = s => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

const q = s => '"' + s + '"';  // args are inserted verbatim (build-pages does no unescaping)
const faqArgs = pairs => pairs.flatMap(p => [q(p.q), q(p.ldA ?? p.a)]).join(' ');
const faqCard = pairs => pairs.map(p => `<h3>${p.q}</h3><p>${p.a}</p>`).join('');
const relList = rel => rel.map(r => `<li><a href="${r.href}">${r.label}</a></li>`).join('');

function derive(f) {
  const url = `${SITE}/${f.slug}`;
  const img = `${SITE}/${f.firstImage}`;
  return {
    slug: f.slug, url, storyId: f.storyId, title: f.seoTitle, desc: f.seoDescription, ogImage: f.ogImage ?? img, descLd: f.descLd ?? f.seoDescription, firstImage: './' + f.firstImage,
    firstScene: f.firstScene, ageMin: String(f.ageMin), ageMax: String(f.ageMax), h1: f.h1, intro: f.intro, short: f.shortAnswer, summary: f.summaryHtml,
    family: f.familyReadingHtml, about: f.aboutHtml, faqArgs: faqArgs(f.faq), faqCard: faqCard(f.faq), related: relList(f.related), footer: f.footerCredit, dataFile: f.dataFile
  };
}
function render(f, tpl) { const d = derive(f); return TEMPLATES[tpl].replace(/@@(\w+)@@/g, (_, k) => { if (!(k in d)) throw new Error('template slot ' + k); return d[k]; }); }

// Inverse: build a regex from the template; repeated slots must capture identical text.
function parse(html, tpl) {
  const T = TEMPLATES[tpl];
  const seen = new Set();
  const re = new RegExp('^' + esc(T).replace(/@@(\w+)@@/g, (_, k) => { if (seen.has(k)) return `\\k<${k}>`; seen.add(k); return `(?<${k}>[\\s\\S]*?)`; }) + '$');
  const m = re.exec(html);
  return m ? m.groups : null;
}
function fieldsFrom(g, ageDefault) {
  const unq = s => s;
  const pairs = [...g.faqCard.matchAll(/<h3>([\s\S]*?)<\/h3><p>([\s\S]*?)<\/p>/g)].map(m => ({ q: m[1], a: m[2] }));
  const related = [...g.related.matchAll(/<li><a href="([^"]+)">([\s\S]*?)<\/a><\/li>/g)].map(m => ({ href: m[1], label: m[2] }));
  // ld-faq answers can differ from the card text (e.g. quotes stripped); keep the difference explicit.
  const ld = g.faqArgs.length > 1 ? g.faqArgs.slice(1, -1).split('" "') : [];
  pairs.forEach((p, i) => { if (ld[2 * i + 1] !== undefined && ld[2 * i + 1] !== p.a) p.ldA = ld[2 * i + 1]; });
  return {
    slug: g.url.slice(SITE.length + 1), storyId: g.storyId, seoTitle: g.title, seoDescription: g.desc, firstImage: g.firstImage.replace(/^\.\//, ''), firstScene: g.firstScene,
    ageMin: +g.ageMin, ageMax: +g.ageMax, h1: g.h1, intro: g.intro, shortAnswer: g.short, summaryHtml: g.summary, familyReadingHtml: g.family,
    ...(g.ogImage !== `${SITE}/${g.firstImage.replace(/^\.\//, '')}` ? { ogImage: g.ogImage } : {}), ...(g.descLd !== undefined && g.descLd !== g.desc ? { descLd: g.descLd } : {}),
    aboutHtml: g.about, faq: pairs, related, footerCredit: g.footer, dataFile: g.dataFile
  };
}

const books = fs.readdirSync(R('content/books')).filter(d => fs.existsSync(R('content/books', d, 'book.json'))).sort();
const srcFile = s => R('src/pages', s + '.html');
let bad = 0;
if (mode === 'extract') {
  const generated = [], legacy = [];
  for (const slug of books) {
    const html = fs.readFileSync(srcFile(slug), 'utf8');
    let ok = false;
    for (const tpl of Object.keys(TEMPLATES)) {
      const g = parse(html, tpl); if (!g) continue;
      const f = fieldsFrom(g);
      if (render(f, tpl) === html) { fs.writeFileSync(R('content/books', slug, 'page.json'), JSON.stringify({ schema: 1, template: tpl, ...f }, null, 2) + '\n'); ok = true; break; }
    }
    (ok ? generated : legacy).push(slug);
  }
  console.log('templated:', generated.join(' ') || '-'); console.log('hand-authored (no match):', legacy.join(' ') || '-');
} else {
  for (const slug of books) {
    const pf = R('content/books', slug, 'page.json');
    if (!fs.existsSync(pf)) continue;
    const { schema, template, ...f } = JSON.parse(fs.readFileSync(pf, 'utf8'));
    const out = render(f, template);
    if (mode === 'build') fs.writeFileSync(srcFile(slug), out);
    else if (fs.readFileSync(srcFile(slug), 'utf8') !== out) { console.error('differs: ' + slug); bad++; }
  }
  if (!bad) console.log(`story pages: ${mode === 'build' ? 'written' : 'up to date'}`);
}
process.exit(bad ? 1 : 0);
