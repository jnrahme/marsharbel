#!/usr/bin/env node
// Story pages from the canonical tree: content/books/<slug>/page.json + templates/books/story-page.html
//   node scripts/books/pages.mjs extract   tolerant parse of existing src/pages/<slug>.html into page.json (one-time migration)
//   node scripts/books/pages.mjs build     write src/pages/<slug>.html from page.json
//   node scripts/books/pages.mjs --check   fail if a generated page differs from its source file
// Optional sections (summary, family reading, about, FAQ, related, production note, film, learn cards,
// true dates, research basis) are omitted when their field is null. pageCount and the film transcript
// are derived from content/books/<slug>/en.json so the static text can never drift from the book data.
import fs from 'node:fs';
import path from 'node:path';

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '../..');
const R = (...p) => path.join(ROOT, ...p);
const mode = process.argv[2] || '--check';
const TEMPLATE = fs.readFileSync(R('templates/books/story-page.html'), 'utf8');
const SITE = 'https://marsharbel.com';
const q = s => '"' + s.replace(/(?<!\\)"/g, '\\"') + '"'; // partial args are inserted verbatim (build-pages does no unescaping); inner quotes must stay backslash-escaped
const faqArgs = pairs => pairs.flatMap(p => [q(p.q), q(p.ldA ?? p.a)]).join(' ');
const faqCard = pairs => pairs.map(p => `<h3>${p.q}</h3><p>${p.a}</p>`).join('');
const relList = rel => rel.map(r => `<li><a href="${r.href}">${r.label}</a></li>`).join('');
const esc = s => s.replace(/&/g, '&amp;').replace(/"/g, '&quot;');
const DEFAULT_NOTE = 'AI-generated read-aloud narration. Illustrations are original composite scenes, not historical footage.';

const bookPages = slug => { try { return JSON.parse(fs.readFileSync(R('content/books', slug, 'en.json'), 'utf8')).pages; } catch { return null; } };

const learnHtml = l => `<section class="section reveal">
<h2>${l.heading}</h2>
<div class="grid-2">
${l.cards.map(c => `<article class="card story"><h3>${c.title}</h3><p>${c.textHtml}</p></article>`).join('\n')}
</div>
</section>`;
const datesHtml = d => `<section class="section reveal">
<h2>${d.heading}</h2>
<article class="card story">
<ul>
${d.items.map(i => `<li>${i}</li>`).join('\n')}
</ul>${d.noteHtml ? `
<p style="margin-top:0.8rem; opacity:0.88;">${d.noteHtml}</p>` : ''}
</article>
</section>`;
const researchHtml = r => `<section class="section reveal">
<h2>${r.heading}</h2>
<article class="card story">
<ul>
${r.items.map(i => `<li>${i}</li>`).join('\n')}
</ul>${r.tailHtml ? `
<p>${r.tailHtml}</p>` : ''}
</article>
</section>`;

// Film section + transcript. The transcript is generated from the book's en.json (title, body,
// prayer, heart per page) so it always matches the storybook text; only the chrome is configured.
function filmHtml(film, slug) {
  const pages = bookPages(slug) || [];
  const tr = pages.map((p, i) => `<h3>Page ${i + 1}: ${esc(p.title)}</h3>
<p>${esc(p.body)}</p>${p.prayer ? `
<p>${esc(p.prayer)}</p>` : ''}${p.heart ? `
<p>${esc(p.heart)}</p>` : ''}`).join('\n');
  const t = film.transcript;
  const trSection = t ? `
<section class="section" id="${t.sectionId}">
<h2>${t.heading}</h2>
<p class="section-sub">${t.subHtml}</p>
<details class="card story">
<summary>${t.summary}</summary>
${tr}
</details>
</section>` : '';
  return `<section class="section reveal" id="storybook-film" aria-label="Storybook film">
<h2 class="section-title">${film.heading}</h2>
<p class="section-sub">${film.subHtml}</p>
<div class="film-frame" style="position:relative;">
<video id="${film.videoId}" controls playsinline preload="none" poster="${film.poster}" style="width:100%; border-radius:14px; border:1px solid rgba(211,178,110,.28); background:#000;">
<source src="${film.src}" type="video/mp4" />
Your browser does not support video playback.
</video>
<span class="film-ai-badge" aria-label="AI-animated disclosure" style="position:absolute; top:10px; left:10px; padding:3px 10px; border-radius:999px; font-size:0.72rem; letter-spacing:0.04em; background:rgba(20,16,10,.72); color:#e9d9ae; border:1px solid rgba(211,178,110,.45); pointer-events:none;">${film.badgeLabel}</span>
</div>
<p class="story-production-note" style="margin-top:0.9rem;">${film.noteHtml}</p>
</section>${trSection}`;
}

function derive(f) {
  const url = `${SITE}/${f.slug}`;
  const hasFaq = f.faq && f.faq.length;
  const pages = bookPages(f.slug);
  return {
    url, storyIdAttr: f.storyId ? ` data-story="${f.storyId}"` : '', storybookIdAttr: f.storybookAnchor ? ' id="storybook"' : '',
    title: f.seoTitle, desc: f.seoDescription, descLd: f.descLd ?? f.seoDescription,
    ogImage: f.ogImage ?? `${SITE}/${f.firstImage}`, firstImage: './' + f.firstImage, firstScene: f.firstScene,
    ages: `${f.ageMin}-${f.ageMax}`, ageMin: String(f.ageMin), ageMax: String(f.ageMax), h1: f.h1, crumb: f.breadcrumbLabel ?? f.h1, intro: f.intro, short: f.shortAnswer,
    ogLocale: f.ogLocales === 'all' ? '  {{> head-og-locales}}' : (f.ogLocales || []).map((l, i) => i === 0 ? `<meta property="og:locale" content="${l}" />` : `<meta property="og:locale:alternate" content="${l}" />`).join('\n'),
    pageCount: String(pages ? pages.length : f.pageCount), disclosureAttr: f.specificDisclosure ? ' data-story-specific-disclosure=""' : '', footerFragment: f.footerFragment || 'footer-credit-b',
    summary: f.summaryHtml ?? '', family: f.familyReadingHtml ?? '', about: f.aboutHtml ?? '', faqArgs: hasFaq ? faqArgs(f.faq) : '',
    faqCard: hasFaq ? faqCard(f.faq) : '', related: f.related ? relList(f.related) : '', footer: f.footerCredit, dataFile: f.dataFile ?? '',
    fontPreloads: f.fontPreloadsFragment ? '  {{> head-font-preloads}}' : `<link as="font" crossorigin="" href="./media/fonts/cormorant-garamond-latin-v1.woff2" rel="preload" type="font/woff2"/>
<link as="font" crossorigin="" href="./media/fonts/manrope-latin-v1.woff2" rel="preload" type="font/woff2"/>`,
    productionNote: f.productionNote === null ? '' : (f.productionNote ?? DEFAULT_NOTE),
    videoLd: f.film?.videoLd ? [f.film.videoLd.name, f.film.videoLd.description, f.film.videoLd.thumbnail, f.film.videoLd.contentUrl, f.film.videoLd.uploadDate, f.film.videoLd.duration, f.film.videoLd.inLanguage].map(q).join(' ') : '',
    film: f.film ? filmHtml(f.film, f.slug) : '',
    learn: f.learn ? learnHtml(f.learn) : '', dates: f.dates ? datesHtml(f.dates) : '', research: f.research ? researchHtml(f.research) : '',
    bioHeading: f.saintBio?.heading ?? '', bioFacts: f.saintBio?.facts ?? '', bioBody: f.saintBio?.body ?? '', bioTail: f.saintBio?.tail ?? ''
  };
}
const BOOL = ['defer', 'disabled', 'hidden', 'crossorigin', 'data-story-specific-disclosure'];
function render(f) {
  const d = derive(f);
  const on = { ogLocale: !!(f.ogLocales && f.ogLocales.length), preLine: !!f.reflectionPreLine, summary: f.summaryHtml != null, family: f.familyReadingHtml != null, dataFile: !!f.dataFile, saintBio: !!f.saintBio, faq: !!(f.faq && f.faq.length), faqSection: !!(f.faq && f.faq.length), related: !!f.related, about: f.aboutHtml != null, productionNote: f.productionNote !== null, videoLd: !!f.film?.videoLd, film: !!f.film, learn: !!f.learn, dates: !!f.dates, research: !!f.research };
  let t = TEMPLATE.replace(/<!--opt:(\w+)-->([\s\S]*?)<!--\/opt:\1-->/g, (_, k, body) => on[k] ? body : '');
  t = t.replace(/@@(\w+)@@/g, (_, k) => { if (!(k in d)) throw new Error('template slot ' + k); return d[k]; });
  for (const a of f.bareAttrs || []) t = t.split(` ${a}=""`).join(` ${a}`); // legacy pages write boolean attributes bare
  return t;
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
  const lv = (/\{\{> ld-video ([^}]*)\}\}/.exec(c) || [])[1];
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
  // production note: the page-level note carries no inline style; the film section's note does
  const notes = [...c.matchAll(/<p class="story-production-note"( style="[^"]*")?[^>]*>(.*?)<\/p>/g)].filter(m => !m[1]).map(m => m[2]);
  // bespoke sections
  const learnM = /<h2>(What Young Hearts Can Learn)<\/h2><div class="grid-2">(.*?)<\/div><\/section>/.exec(c);
  const datesM = /<h2>(True Dates in the Story)<\/h2><article class="card story"><ul>(.*?)<\/ul>(?:<p style="margin-top:0\.8rem; opacity:0\.88;">(.*?)<\/p>)?<\/article><\/section>/.exec(c);
  const researchM = /<h2>(Research Basis)<\/h2><article class="card story"><ul>(.*?)<\/ul>(?:<p>(.*?)<\/p>)?<\/article><\/section>/.exec(c);
  const filmM = /<section class="section reveal" id="storybook-film" aria-label="Storybook film"><h2 class="section-title">(.*?)<\/h2><p class="section-sub">(.*?)<\/p><div class="film-frame" style="position:relative;"><video id="([^"]+)" controls playsinline preload="none" poster="([^"]+)"[^>]*><source src="([^"]+)" type="video\/mp4" \/>.*?<span class="film-ai-badge"[^>]*>(.*?)<\/span><\/div><p class="story-production-note" style="margin-top:0\.9rem;">(.*?)<\/p><\/section>/.exec(c);
  const trM = /<section class="section" id="([\w-]+)"><h2>(.*?)<\/h2><p class="section-sub">(.*?)<\/p><details class="card story"><summary>(.*?)<\/summary>/.exec(c);
  const out = {
    slug: url.slice(SITE.length + 1), storyId: sec(/<body class="is-story-page" data-story="([^"]+)"/) ?? null, seoTitle: get(/<title>(.*?)<\/title>/, 'title')[1],
    seoDescription: get(/<meta name="description" content="([^"]*)"/, 'description')[1], firstImage: scene[2].replace(/^\.\//, ''), firstScene: scene[1],
    ageMin: +ages[1], ageMax: +ages[2], h1: hero[1], intro: hero[2], shortAnswer: hero[3],
    summaryHtml: sec(/<h2>Story Summary<\/h2><div class="card story">(.*?)<\/div><\/section>/),
    familyReadingHtml: sec(/<h2[^>]*>Read the Bible and pray together<\/h2><div class="card story">(.*?)<\/div><\/section>/),
    aboutHtml: sec(/<h2>About this story<\/h2><(?:article|div) class="card story">(.*?)<\/(?:article|div)><\/section>/),
    faq, related: rel == null ? null : [...rel.matchAll(/<li><a href="([^"]+)">(.*?)<\/a><\/li>/g)].map(m => ({ href: m[1], label: m[2] })),
    ...(notes.length ? (notes[0] !== DEFAULT_NOTE ? { productionNote: notes[0] } : {}) : { productionNote: null }),
    ...(/\{\{> head-font-preloads\}\}/.test(c) ? { fontPreloadsFragment: true } : {}),
    ...((b => b.length ? { bareAttrs: b } : {})(BOOL.filter(a => new RegExp(`\\s${a}(?=[\\s>/])`).test(c)))),
    ...(bio ? { saintBio: { heading: bio[1], facts: bio[2], body: bio[3], tail: bio[4] } } : {}),
    footerFragment: footer[1], footerCredit: footer[2],
    ...(/\{\{> head-og-locales\}\}/.test(c) ? { ogLocales: 'all' } : og.length ? { ogLocales: og } : {}), ...(/<style>#story-body\.is-reflection \{ white-space: pre-line; \}<\/style>/.test(c) ? { reflectionPreLine: true } : {}),
    ...(/data-story-specific-disclosure/.test(c) ? { specificDisclosure: true } : {}),
    ...(/<section[^>]*class="storybook reveal"[^>]*id="storybook"|id="storybook"[^>]*class="storybook reveal"/.test(c) || /<section class="storybook reveal" id="storybook"/.test(c) ? { storybookAnchor: true } : {}),
    ...(learnM ? { learn: { heading: learnM[1], cards: [...learnM[2].matchAll(/<article class="card story"><h3>(.*?)<\/h3><p>(.*?)<\/p><\/article>/g)].map(m => ({ title: m[1], textHtml: m[2] })) } } : {}),
    ...(datesM ? { dates: { heading: datesM[1], items: [...datesM[2].matchAll(/<li>(.*?)<\/li>/g)].map(m => m[1]), ...(datesM[3] ? { noteHtml: datesM[3] } : {}) } } : {}),
    ...(researchM ? { research: { heading: researchM[1], items: [...researchM[2].matchAll(/<li>(.*?)<\/li>/g)].map(m => m[1]), ...(researchM[3] ? { tailHtml: researchM[3] } : {}) } } : {}),
    ...(filmM ? { film: { ...(lv ? { videoLd: (([n, d, th, cu, ud, dur, lang]) => ({ name: n, description: d, thumbnail: th, contentUrl: cu, uploadDate: ud, duration: dur, inLanguage: lang }))(tokens(lv)) } : {}), heading: filmM[1], subHtml: filmM[2], videoId: filmM[3], poster: filmM[4], src: filmM[5], badgeLabel: filmM[6], noteHtml: filmM[7], ...(trM ? { transcript: { sectionId: trM[1], heading: trM[2], subHtml: trM[3], summary: trM[4] } } : {}) } } : {}),
    dataFile: (/<script defer(?:="")? src="([\w-]+-data\.js)"/.exec(c) || [])[1] ?? null
  };
  if (hs[4] !== `${SITE}/${out.firstImage}`) out.ogImage = hs[4];
  if (lw[5] !== out.seoDescription) out.descLd = lw[5];
  if (lw[9] !== out.h1) out.breadcrumbLabel = lw[9];
  return out;
}

const books = fs.readdirSync(R('content/books')).filter(d => fs.existsSync(R('content/books', d, 'book.json'))).sort();
const srcFile = s => R('src/pages', s + '.html');
let bad = 0;
if (mode === 'extract') {
  for (const slug of books) {
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
