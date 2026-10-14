#!/usr/bin/env node
// Seeds content/news/<locale>.json from the latest-news block of each generated home page.
// One-time bridge: after cutover the news lane edits content/news/*.json (or publishes to the
// service) and the homes follow. --check fails when a home block no longer matches the seed.
import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..', '..');
const LOCALES = ['en', 'ar', 'de', 'es', 'fr', 'hi', 'it', 'pl', 'pt', 'ru', 'th'];
const ent = s => s.replace(/&amp;/g, '&').replace(/&quot;/g, '"').replace(/&#39;|&apos;/g, "'")
  .replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&middot;/g, '\u00b7').replace(/&rarr;/g, '\u2192');
const text = html => ent(html.replace(/<[^>]+>/g, '').replace(/\s+/g, ' ').trim());
const attr = (tag, name) => { const m = tag.match(new RegExp(`\\s${name}="([^"]*)"`)); return m ? ent(m[1]) : null; };
const span = (html, cls) => { const m = html.match(new RegExp(`<span class="${cls}">([\\s\\S]*?)</span>`)); return m ? text(m[1]) : null; };

export function parseHome(html) {
  const sec = html.match(/<section[^>]*id="latest-news"[^>]*>[\s\S]*?<\/section>/);
  if (!sec) throw new Error('latest-news block not found');
  const items = [];
  const re = /<a ([^>]*class="home-news-(lead|row)[^"]*"[^>]*)>([\s\S]*?)<\/a>/g;
  let m;
  while ((m = re.exec(sec[0]))) {
    const open = `<a ${m[1]}>`; const body = m[3];
    const img = body.match(/<img[^>]*>/);
    const abs = v => (v && v.startsWith('./') ? v.slice(1) : v);
    const href = abs(attr(open, 'href'));
    const titles = [...body.matchAll(/<span class="home-news-title">([\s\S]*?)<\/span>/g)].map(x => text(x[1]));
    items.push({
      id: href.replace(/^\.?\/?/, '').replace(/^[a-z]{2}\//, '').replace(/[#/]/g, '-').replace(/^-+|-+$/g, '') || 'home',
      kind: m[2], href,
      image: img ? { src: abs(attr(img[0], 'src')), alt: attr(img[0], 'alt'), width: +attr(img[0], 'width') || null, height: +attr(img[0], 'height') || null } : null,
      date: span(body, 'home-news-meta'), title: titles[0] || null,
      dek: span(body, 'home-news-dek'), credit: span(body, 'home-news-credit'),
    });
  }
  const h = sec[0].match(/<h2[^>]*>([\s\S]*?)<\/h2>/); const all = sec[0].match(/<a class="home-news-all"[^>]*>([\s\S]*?)<\/a>/);
  return { heading: h ? text(h[1]) : null, allLabel: all ? text(all[1]).replace(/\s*\u2192$/, '') : null, items };
}

export function build() {
  const out = {};
  for (const loc of LOCALES) {
    const file = join(ROOT, loc === 'en' ? 'index.html' : `${loc}/index.html`);
    if (!existsSync(file)) continue;
    const p = parseHome(readFileSync(file, 'utf8'));
    out[loc] = { schema: 1, locale: loc, section: 'home-latest', ...p };
  }
  return out;
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const check = process.argv.includes('--check');
  for (const [loc, data] of Object.entries(build())) {
    const path = join(ROOT, 'content', 'news', `${loc}.json`);
    const body = JSON.stringify(data, null, 2) + '\n';
    if (check) { if (!existsSync(path) || readFileSync(path, 'utf8') !== body) { console.error(`stale: ${path}`); process.exitCode = 1; } }
    else writeFileSync(path, body);
  }
  console.log(check ? 'news seed checked' : 'news seed written');
}
