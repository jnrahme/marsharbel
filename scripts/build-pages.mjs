// Composes src/pages/**/*.html + partials/fragments/*.html into the served HTML
// files. Output is committed (Hostinger serves the repo as-is), so the build is
// deterministic and `--check` fails if any served page drifts from its source.
// Include syntax: {{> name}} anywhere; {{> name "text"}} fills {{text}} in the fragment (\\" escapes a quote); {{> primary-nav}} is computed per page (active state, link prefix); indentation of the marker is
// prefixes the first line only; fragments are verbatim blocks.
import { readFile, writeFile, readdir, mkdir } from 'node:fs/promises';
import path from 'node:path';
import { renderPrimaryNav } from './lib/primary-nav.mjs';
const check = process.argv.includes('--check');
const SRC = 'src/pages', FRAG = 'partials/fragments';
const navTemplate = (await readFile('partials/primary-navigation.html', 'utf8')).trim();
const frags = {};
for (const f of await readdir(FRAG)) if (f.endsWith('.html')) frags[f.slice(0, -5)] = (await readFile(path.join(FRAG, f), 'utf8')).replace(/\n$/, '');
async function walk(dir) {
  const out = [];
  for (const e of await readdir(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name);
    if (e.isDirectory()) out.push(...await walk(p)); else if (e.name.endsWith('.html')) out.push(p);
  }
  return out;
}
const used = new Set(); let stale = [], n = 0;
for (const file of await walk(SRC).catch(() => [])) {
  const rel = path.relative(SRC, file);
  const source = await readFile(file, 'utf8');
  const built = source.replace(/([ \t]*)\{\{> ([a-z0-9-]+)(?: "((?:[^"\\]|\\.)*)")?\}\}/g, (_, indent, name, arg) => {
    if (name === 'primary-nav') return indent + renderPrimaryNav(navTemplate, rel);
    if (!(name in frags)) throw new Error(`${rel}: unknown fragment ${name}`);
    used.add(name);
    if (arg !== undefined) { if (!frags[name].includes('{{text}}')) throw new Error(`${rel}: fragment ${name} takes no argument`); return indent + frags[name].replace('{{text}}', () => arg.replace(/\\(.)/g, '$1')); }
    if (frags[name].includes('{{text}}')) throw new Error(`${rel}: fragment ${name} needs an argument`);
    return indent + frags[name];
  });
  let current = null; try { current = await readFile(rel, 'utf8'); } catch {}
  n++;
  if (current !== built) { stale.push(rel); if (!check) { await mkdir(path.dirname(rel) || '.', { recursive: true }); await writeFile(rel, built); } }
}
const unused = Object.keys(frags).filter(k => !used.has(k));
if (unused.length) { console.error(`Unused fragments: ${unused.join(', ')}`); process.exitCode = 1; }
console.log(`${n} pages built from src/pages; ${stale.length} ${check ? 'out of date' : 'written'}.`);
if (stale.length) console.log(stale.join('\n'));
if (check && stale.length) process.exitCode = 1;
