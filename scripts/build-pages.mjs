// Composes src/pages/**/*.html + partials/fragments/*.html into the served HTML
// files. Output is committed (Hostinger serves the repo as-is), so the build is
// deterministic and `--check` fails if any served page drifts from its source.
// Include syntax: {{> name}} anywhere; {{> name "a" "b"}} fills {{1}} {{2}} (alias {{text}} = {{1}}) verbatim, no unescaping; {{> primary-nav}} is computed per page (active state, link prefix); indentation of the marker is
// prefixes the first line only; fragments are verbatim blocks.
import { readFile, writeFile, readdir, mkdir } from 'node:fs/promises';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { renderWebPage, renderWebPageArticle, renderWebPageAudience, renderFaq } from './lib/jsonld.mjs';
import { renderPrimaryNav } from './lib/primary-nav.mjs';
import { renderVideoFallback } from './lib/video-fallback.mjs';
const videoCopy = JSON.parse(await readFile('locales/en/video-playback.json', 'utf8'));
const check = process.argv.includes('--check');
const selected = process.argv.find(arg => arg.startsWith('--pages='))?.slice(8).split(',');
const SRC = 'src/pages', FRAG = 'partials/fragments';
const navTemplate = (await readFile('partials/primary-navigation.html', 'utf8')).trim();
const frags = {};
for (const f of await readdir(FRAG)) if (f.endsWith('.html')) frags[f.slice(0, -5)] = (await readFile(path.join(FRAG, f), 'utf8')).replace(/\n$/, '');
const rosaryVideos = JSON.parse(await readFile('locales/rosary-videos.json', 'utf8'));
const travelEquivalence = JSON.parse(await readFile('locales/travel-equivalence.json', 'utf8'));
// Travel-pinned masters are byte-locked by reviewed twin evidence; ratio
// classes reach them only through the twin re-pin tooling, so the classifier
// leaves them untouched here.
const travelPinnedMasters = new Set(Object.values(travelEquivalence.groups || travelEquivalence).map(g => g && g.variants && g.variants.en && g.variants.en.file).filter(Boolean));

// Daily-rosary YouTube place: data-driven via locales/rosary-videos.json; each
// published day drops in by editing the JSON (no markup edits). Empty state is
// the channel card; videos render newest-first as lazy youtube-nocookie embeds.
const esc = s => String(s).replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;');
const rosaryVideoCards = rosaryVideos.videos.length
  ? '<div class="grid-2">' + rosaryVideos.videos.slice().reverse().map(v =>
      '<article class="card update"><div class="video-wrap"><iframe src="https://www.youtube-nocookie.com/embed/' + esc(v.videoId) + '" title="' + esc(v.title) + '" loading="lazy" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe></div>'
      + '<p>' + esc(v.title) + ' (' + esc(v.date) + '). <a href="https://www.youtube.com/watch?v=' + esc(v.videoId) + '" target="_blank" rel="noopener">Watch on YouTube</a>.</p></article>').join('') + '</div>'
  : '<div class="grid-2"><article class="card update"><p>A guided video for each day\'s mysteries lands here as the series publishes - one video per day, ready to pray along with.</p><p class="cta-row"><a class="btn subtle" href="' + esc(rosaryVideos.channelUrl) + '" target="_blank" rel="noopener">Open the marsharbel YouTube channel</a></p></article></div>';
frags['rosary-videos'] = '<section class="section" id="pray-along"><h2>Pray along: the daily rosary on YouTube</h2><p class="section-sub">A guided video for each day\'s mysteries, published day by day. Embeds use youtube-nocookie.com - no YouTube cookies are set unless you press play.</p>' + rosaryVideoCards + '</section>';

async function walk(dir) {
  const out = [];
  for (const e of await readdir(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name);
    if (e.isDirectory()) out.push(...await walk(p)); else if (e.name.endsWith('.html')) out.push(p);
  }
  return out;
}
const escapeText = value => String(value).replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;');
const catalogs = new Map();
async function catalog(name) {
  if (!catalogs.has(name)) catalogs.set(name, JSON.parse(await readFile(`locales/en/${name}-copy.json`, 'utf8')).copy);
  return catalogs.get(name);
}
const used = new Set(); let stale = [], n = 0;
for (const file of await walk(SRC).catch(() => [])) {
  const rel = path.relative(SRC, file);
  if (selected && !selected.includes(rel)) continue;
  const source = await readFile(file, 'utf8');
  const copyPattern = /\{\{copy ([a-z0-9-]+) ([a-zA-Z0-9.-]+)\}\}/g;
  for (const match of source.matchAll(copyPattern)) await catalog(match[1]);
  const catalogued = source.replace(copyPattern, (_, name, key) => {
    const copy = catalogs.get(name);
    if (!copy || !(key in copy)) throw new Error(`${rel}: missing ${name} copy key: ${key}`);
    return escapeText(copy[key]);
  });
  let built = catalogued.replace(/([ \t]*)\{\{> ([a-z0-9-]+)((?: "(?:[^"\\]|\\.)*")*)\}\}/g, (_, indent, name, rawArgs) => {
    if (name === 'video-fallback') return indent + renderVideoFallback(videoCopy, ...[...rawArgs.matchAll(/ "((?:[^"\\]|\\.)*)"/g)].map(m => m[1]));
    if (name === 'primary-nav') return indent + renderPrimaryNav(navTemplate, rel);
    if (name === 'ld-faq') return indent + renderFaq([...rawArgs.matchAll(/ "((?:[^"\\]|\\.)*)"/g)].map(m => m[1]));
    if (name === 'ld-webpage-audience') return indent + renderWebPageAudience([...rawArgs.matchAll(/ "((?:[^"\\]|\\.)*)"/g)].map(m => m[1]));
    if (name === 'ld-webpage-article-modified') {
      const [dateModified, ...args] = [...rawArgs.matchAll(/ "((?:[^"\\]|\\.)*)"/g)].map(m => m[1]);
      return indent + renderWebPageArticle(args, dateModified);
    }
    if (name === 'ld-webpage-article') return indent + renderWebPageArticle([...rawArgs.matchAll(/ "((?:[^"\\]|\\.)*)"/g)].map(m => m[1]));
    if (name === 'ld-webpage') return indent + renderWebPage([...rawArgs.matchAll(/ "((?:[^"\\]|\\.)*)"/g)].map(m => m[1]));
    if (!(name in frags)) throw new Error(`${rel}: unknown fragment ${name}`);
    used.add(name);
    const args = [...rawArgs.matchAll(/ "((?:[^"\\]|\\.)*)"/g)].map(m => m[1]);
    const slots = new Set([...frags[name].matchAll(/\{\{(\d+|text)\}\}/g)].map(m => (m[1] === 'text' ? 1 : Number(m[1]))));
    if (slots.size !== args.length || [...slots].some(k => k > args.length)) throw new Error(`${rel}: fragment ${name} takes ${slots.size} argument(s), got ${args.length}`);
    // Arguments are inserted verbatim (no unescaping) so JSON/HTML escapes survive byte for byte.
    return indent + frags[name].replace(/\{\{(\d+|text)\}\}/g, (_m, k) => args[(k === 'text' ? 1 : Number(k)) - 1]);
  });
  // Hero-figure ratio classes (design-director face-crop spec): fixed-box
  // layouts key off the image's own ratio, read from the width/height attrs.
  // Portrait art gets is-portrait, near-square gets is-square-ish; landscape
  // stays unclassed and keeps the contextual default frame.
  if (!travelPinnedMasters.has(rel)) built = built.replace(/(<figure class="hero-figure[^"]*"[^>]*>\s*<img\b)([^>]*?)(\/?)>/g, (m, open, attrs, close) => {
    const w = /width="(\d+)"/.exec(attrs), h = /height="(\d+)"/.exec(attrs);
    if (!w || !h) return m;
    const ratio = Number(w[1]) / Number(h[1]);
    const cls = ratio < 0.9 ? 'is-portrait' : (ratio <= 1.3 ? 'is-square-ish' : null);
    if (!cls) return m;
    const existing = /class="([^"]*)"/.exec(attrs);
    const clean = attrs.replace(/\s+$/, '');
    const next = existing ? clean.replace(existing[0], `class="${existing[1]} ${cls}"`) : clean + ` class="${cls}"`;
    return open + next + close + '>';
  });
  if (built.includes('rel="canonical"') && (rel === 'saint-charbel-prayers.html' || !/name=["']robots["'][^>]*content=["'][^"']*noindex/.test(built))) {
    const composed = spawnSync('python3', ['scripts/inject-same-page-stdin.py'], {input: built, encoding:'utf8',maxBuffer:20*1024*1024});
    if(composed.status!==0)throw new Error(`${rel}: language-control composition failed: ${composed.stderr}`);
    built=composed.stdout;
  }
  let current = null; try { current = await readFile(rel, 'utf8'); } catch {}
  n++;
  if (current !== built) { stale.push(rel); if (!check) { await mkdir(path.dirname(rel) || '.', { recursive: true }); await writeFile(rel, built); } }
}
const unused = Object.keys(frags).filter(k => !used.has(k));
if (!selected && unused.length) { console.error(`Unused fragments: ${unused.join(', ')}`); process.exitCode = 1; }
console.log(`${n} pages built from src/pages; ${stale.length} ${check ? 'out of date' : 'written'}.`);
if (stale.length) console.log(stale.join('\n'));
if (check && stale.length) process.exitCode = 1;
