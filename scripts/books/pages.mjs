#!/usr/bin/env node
// Story pages from the canonical tree: content/books/<slug>/page.json + templates/books/story-page.html
//   node scripts/books/pages.mjs extract   tolerant parse of existing src/pages/<slug>.html into page.json (one-time migration)
//   node scripts/books/pages.mjs build     write src/pages/<slug>.html from page.json
//   node scripts/books/pages.mjs --check   fail if a generated page differs from its source file
// Optional sections (summary, family reading, FAQ, related) are omitted when their field is null.
import fs from 'node:fs';
import path from 'node:path';

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '../..');
const R = (...p) => path.join(ROOT, ...p);
const mode = process.argv[2] || '--check';
const TEMPLATE = fs.readFileSync(R('templates/books/story-page.html'), 'utf8');
const SITE = 'https://marsharbel.com';
const q = s => '"' + s + '"'; // partial args are inserted verbatim (build-pages does no unescaping)
const faqArgs = pairs => pairs.flatMap(p => [q(p.q), q(p.ldA ?? p.a)]).join(' ');
const faqCard = pairs => pairs.map(p => `<h3>${p.q}</h3><p>${p.a}</p>`).join('');
const relList = rel => rel.map(r => `<li><a href="${r.href}">${r.label}</a></li>`).join('');

function derive(f) {
  const url = `${SITE}/${f.slug}`;
  const hasFaq = f.faq && f.faq.length;
  return {
    url, storyId: f.storyId, title: f.seoTitle, desc: f.seoDescription, descLd: f.descLd ?? f.seoDescription,
    ogImage: f.ogImage ?? `${SITE}/${f.firstImage}`, firstImage: './' + f.firstImage, firstScene: f.firstScene,
    ages: `${f.ageMin}-${f.ageMax}`, ageMin: String(f.ageMin), ageMax: String(f.ageMax), h1: f.h1, intro: f.intro, short: f.shortAnswer,
    ogLocale: f.ogLocales === 'all' ? '{{> head-og-locales}}' : (f.ogLocales || []).map((l, i) => i === 0 ? `<meta property="og:locale" content="${l}" />` : `<meta property="og:locale:alternate" content="${l}" />`).join('\n'),
    pageCount: String(f.pageCount), disclosureAttr: f.specificDisclosure ? ' data-story-specific-disclosure=""' : '', footerFragment: f.footerFragment || 'footer-credit-b',
    summary: f.summaryHtml ?? '', family: f.familyReadingHtml ?? '', about: f.aboutHtml, faqArgs: hasFaq ? faqArgs(f.faq) : '',
    faqCard: hasFaq ? faqCard(f.faq) : '', related: f.related ? relList(f.related) : '', footer: f.footerCredit, dataFile: f.dataFile ?? '',
    productionNote: f.productionNote ?? 'AI-generated read-aloud narration. Illustrations are original composite scenes, not historical footage.',
    bioHeading: f.saintBio?.heading ?? '', bioFacts: f.saintBio?.facts ?? '', bioBody: f.saintBio?.body ?? '', bioTail: f.saintBio?.tail ?? ''
  };
}
function render(f) {
  const d = derive(f);
  const on = { ogLocale: !!(f.ogLocales && f.ogLocales.length), preLine: !!f.reflectionPreLine, summary: f.summaryHtml != null, family: f.familyReadingHtml != null, dataFile: !!f.dataFile, saintBio: !!f.saintBio, faq: !!(f.faq && f.faq.length), faqSection: !!(f.faq && f.faq.length), related: !!f.related };
  let t = TEMPLATE.replace(/<!--opt:(\w+)-->([\s\S]*?)<!--\/opt:\1-->/g, (_, k, body) => on[k] ? body : '');
  return t.replace(/@@(\w+)@@/g, (_, k) => { if (!(k in d)) throw new Error('template slot ' + k); return d[k]; });
}

// ---- tolerant extraction (whitespace-insensitive) -------------------------------------------
const collapse = h => h.replace(/\s+/g, ' ').replace(/> </g, '><').trim();
const tokens = s => [...s.matchAll(/"((?:[^"\\]|\\.)*)"/g)].map(m => m[1]);
function extract(html) {
  const c = collapse(html);
  const get = (re, what) => { const m = re.exec(c); if (!m) throw new Error('no ' + what); return m; };
  const hs = tokens(get(/\{\{> head-social ([^}]*)\}\}/, 'head-social')[1]);
  const lw = tokens(get(/\{\{> ld-webpage-audience ([^}]*)\}\}/, 'ld-webpage-audience')[1]);
  const lf = (/\{\{> ld-faq ([^}]*)\}\}/.exec(c) || [])[1];
  const url = hs[3];
  const hero = get(/<section class="story-hero reveal"><span class="kicker">[^<]*<\/span><h1>(.*?)<\/h1><p>(.*?)<\/p><p class="short-answer"><strong>Short answer:<\/strong> (.*?)<\/p><\/section>/, 'hero');
  const scene = get(/<div class="scene-art scene-(\w+)"><img[^>]*?src="([^"]+)"/, 'first scene');
  const sec = (re) => { const m = re.exec(c); return m ? m[1] : null; };
  const faqHtml = sec(/<h2>Frequently Asked Questions<\/h2><div class="card story">(.*?)<\/div><\/section>/);
  let faq = null;
  if (faqHtml != null) {
    faq = [...faqHtml.matchAll(/<h3>(.*?)<\/h3><p>(.*?)<\/p>/g)].map(m => ({ q: m[1], a: m[2] }));
    const ld = lf ? tokens(lf) : [];
    faq.forEach((p, i) => { if (ld[2 * i + 1] !== undefined && ld[2 * i + 1] !== p.a) p.ldA = ld[2 * i + 1]; });
  }
  const rel = sec(/<h2>More Saint Storybooks for Children<\/h2><div class="card story"><ul>(.*?)<\/ul><\/div>/);
  const ages = get(/<span class="kicker">A Book for Ages (\d+)-(\d+)<\/span>/, 'ages');
  const footer = get(/\{\{> (footer-credit-[ab]) "([^"]*)"/, 'footer');
  const og = [...c.matchAll(/<meta property="og:locale(?::alternate)?" content="([^"]+)" ?\/?>/g)].map(m => m[1]);
  const bio = /\{\{> saint-bio "([^"]*)" "([^"]*)" "([^"]*)" "([^"]*)"\}\}/.exec(c);
  const out = {
    slug: url.slice(SITE.length + 1), storyId: get(/data-story="([^"]+)"/, 'data-story')[1], seoTitle: get(/<title>(.*?)<\/title>/, 'title')[1],
    seoDescription: get(/<meta name="description" content="([^"]*)"/, 'description')[1], firstImage: scene[2].replace(/^\.\//, ''), firstScene: scene[1],
    ageMin: +ages[1], ageMax: +ages[2], h1: hero[1], intro: hero[2], shortAnswer: hero[3],
    summaryHtml: sec(/<h2>Story Summary<\/h2><div class="card story">(.*?)<\/div><\/section>/),
    familyReadingHtml: sec(/<h2[^>]*>Read the Bible and pray together<\/h2><div class="card story">(.*?)<\/div><\/section>/),
    aboutHtml: sec(/<h2>About this story<\/h2><(?:article|div) class="card story">(.*?)<\/(?:article|div)><\/section>/),
    faq, related: rel == null ? null : [...rel.matchAll(/<li><a href="([^"]+)">(.*?)<\/a><\/li>/g)].map(m => ({ href: m[1], label: m[2] })),
    ...((pn => pn && pn !== 'AI-generated read-aloud narration. Illustrations are original composite scenes, not historical footage.' ? { productionNote: pn } : {})((/<p class="story-production-note"[^>]*>(.*?)<\/p>/.exec(c) || [])[1])),
    ...(bio ? { saintBio: { heading: bio[1], facts: bio[2], body: bio[3], tail: bio[4] } } : {}),
    footerFragment: footer[1], footerCredit: footer[2],
    ...(/\{\{> head-og-locales\}\}/.test(c) ? { ogLocales: 'all' } : og.length ? { ogLocales: og } : {}), ...(/<style>#story-body\.is-reflection \{ white-space: pre-line; \}<\/style>/.test(c) ? { reflectionPreLine: true } : {}),
    ...(/data-story-specific-disclosure/.test(c) ? { specificDisclosure: true } : {}), pageCount: +get(/<p[^>]*id="story-step"[^>]*>Page 1 of (\d+)</, 'page count')[1], dataFile: (/<script defer(?:="")? src="([\w-]+-data\.js)"/.exec(c) || [])[1] ?? null
  };
  if (hs[4] !== `${SITE}/${out.firstImage}`) out.ogImage = hs[4];
  if (lw[5] !== out.seoDescription) out.descLd = lw[5];
  return out;
}

// Pages whose body is not the standard story template (own film section, raw JSON-LD, 16 pages...). They stay hand-authored.
const BESPOKE = new Set(['pio-story', 'jpii-story', 'story']);
const books = fs.readdirSync(R('content/books')).filter(d => fs.existsSync(R('content/books', d, 'book.json'))).sort();
const srcFile = s => R('src/pages', s + '.html');
let bad = 0;
if (mode === 'extract') {
  for (const slug of books) {
    if (BESPOKE.has(slug)) { console.log('hand-authored (bespoke layout, no page.json):', slug); continue; }
    try {
      const f = extract(fs.readFileSync(srcFile(slug), 'utf8'));
      fs.writeFileSync(R('content/books', slug, 'page.json'), JSON.stringify({ schema: 1, template: 'story-page', ...f }, null, 2) + '\n');
      console.log('extracted', slug);
    } catch (e) { console.log('NOT EXTRACTED', slug, '-', e.message); }
  }
} else {
  for (const slug of books) {
    const pf = R('content/books', slug, 'page.json');
    if (!fs.existsSync(pf)) continue;
    const { schema, template, ...f } = JSON.parse(fs.readFileSync(pf, 'utf8'));
    const out = render(f);
    if (mode === 'build') fs.writeFileSync(srcFile(slug), out);
    else if (fs.readFileSync(srcFile(slug), 'utf8') !== out) { console.error('differs: ' + slug); bad++; }
  }
  if (!bad) console.log(`story pages: ${mode === 'build' ? 'written' : 'up to date'}`);
}
process.exit(bad ? 1 : 0);
