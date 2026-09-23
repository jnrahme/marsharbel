import { readFile, writeFile, readdir } from 'node:fs/promises';
import path from 'node:path';
const check = process.argv.includes('--check');
const template = (await readFile('partials/primary-navigation.html', 'utf8')).trim();
const pages = [...(await readdir('.')).filter(p => p.endsWith('.html')), ...(await readdir('mysteries')).filter(p => p.endsWith('.html')).map(p => `mysteries/${p}`)];
// These are intentionally minimal translated landing pages with language navigation.
const languageLandings = new Set(['ar.html', 'fr.html']);
const aliases = { 'submit-testimony.html':'testimonies.html', 'testimony-review.html':'testimonies.html', 'account.html':'testimonies.html', 'voice-lab.html':'voice-testimony.html', 'shop-mockup.html':'souvenirs.html' };
let count = 0; const stale = [];
for (const file of pages) {
  const source = await readFile(file, 'utf8');
  if (languageLandings.has(file) || !/<header\b/.test(source)) continue;
  const navPattern = /<nav\b[^>]*class=["']links["'][^>]*>[\s\S]*?<\/nav>/;
  if (!navPattern.test(source)) throw new Error(`Missing primary navigation in ${file}`);
  const prefix = file.includes('/') ? '../' : './';
  const current = file.startsWith('mysteries/') ? 'rosary-visual-guide.html' : (aliases[file] || file);
  let nav = template.replaceAll('href="./', `href="${prefix}`);
  nav = nav.replace(/<a([^>]*?)href="([^"]+)"([^>]*)>/g, (tag, before, href, after) => {
    if (path.posix.basename(href) !== current) return tag;
    const isParent = before.includes('nav-parent');
    // A group parent and its matching child may both be highlighted, but only
    // an exact destination receives aria-current="page".
    const active = before.includes('class="') ? before.replace('class="', 'class="active ') : `${before}class="active" `;
    const exact = path.posix.basename(href) === path.posix.basename(file);
    return `<a${active}href="${href}"${after}${exact && !isParent ? ' aria-current="page"' : ''}>`;
  });
  nav = nav.replace(/<div class="nav-group">([\s\S]*?)<\/div><\/div>/g, (group, contents) => contents.includes('class="active"') ? group.replace('class="nav-parent"', 'class="active nav-parent"') : group);
  let updated = source.replace(navPattern, nav);
  const script = `<script src="${prefix}nav.js?v=20260922-1" defer></script>`;
  if (!/<script[^>]+src=["'][^"']*nav\.js/.test(updated)) updated = updated.replace('</body>', `  ${script}\n</body>`);
  if (updated !== source) { stale.push(file); if (!check) await writeFile(file, updated); }
  count++;
}
console.log(`${count} pages checked against shared primary navigation; ${stale.length} ${check ? 'out of sync' : 'updated'}.`);
if (stale.length) console.log(stale.join('\n'));
if (check && stale.length) process.exitCode = 1;
