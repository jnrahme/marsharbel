import path from 'node:path';
// Shared by sync-navigation.mjs and build-pages.mjs: one implementation of the
// primary navigation (prefixing + active-page highlighting).
const aliases = { 'submit-testimony.html':'testimonies.html', 'testimony-review.html':'testimonies.html', 'account.html':'testimonies.html', 'voice-lab.html':'voice-testimony.html', 'shop-mockup.html':'souvenirs.html', 'miracles/index.html':'miracles/index.html', 'miracles/nohad-el-shami.html':'miracles/index.html', 'miracles/dafne-gutierrez.html':'miracles/index.html', 'miracles/canonization.html':'miracles/index.html', 'miracles/raymond-nader.html':'miracles/index.html', 'miracles/latest-register-entries.html':'miracles/index.html' };
// Links are written as clean URLs (./story, ./ for home); compare pages by
// their clean name so highlighting works for both forms.
const cleanName = value => {
  const normalized=value.replace(/\.html$/, '').replace(/\/$/, '');
  if (normalized === 'miracles' || normalized.endsWith('/miracles') || normalized === 'miracles/index') return 'miracles';
  const base=path.posix.basename(normalized);
  return base === '.' || base === '..' || base === '' ? 'index' : base;
};
export function renderPrimaryNav(template, file) {
  const prefix = file.startsWith('miracles/eucharistic/') ? '../../' : file.includes('/') ? '../' : './';
  const current = file.startsWith('mysteries/') ? 'rosary-visual-guide.html' : (aliases[file] || file);
  let nav = template.replaceAll('href="./', `href="${prefix}`);
  if (file === 'miracles/index.html') nav = nav.replaceAll('href="../miracles"', 'href="../miracles/"');
  nav = nav.replace(/<a([^>]*?)href="([^"]+)"([^>]*)>/g, (tag, before, href, after) => {
    if ((href === '../' || href === './' || href === '../../') && file !== 'index.html') return tag;
    if (file.startsWith('miracles/') && cleanName(href) === 'miracles') {
      const active=before.includes('class="') ? before.replace('class="', 'class="active ') : `${before}class="active" `;
      const exact=file === 'miracles/index.html' && !before.includes('nav-parent');
      if (file.startsWith('miracles/eucharistic/') && !before.includes('nav-parent')) return tag;
      return `<a${active}href="${href}"${after}${exact ? ' aria-current="page"' : ''}>`;
    }
    if (cleanName(href) !== cleanName(current)) return tag;
    const isParent = before.includes('nav-parent');
    // A group parent and its matching child may both be highlighted, but only
    // an exact destination receives aria-current="page".
    const active = before.includes('class="') ? before.replace('class="', 'class="active ') : `${before}class="active" `;
    const exact = cleanName(href) === cleanName(file) && !(file.startsWith('miracles/') && file !== 'miracles/index.html');
    return `<a${active}href="${href}"${after}${exact && !isParent ? ' aria-current="page"' : ''}>`;
  });
  nav = nav.replace(/<div class="nav-group">([\s\S]*?)<\/div><\/div>/g, (group, contents) => contents.includes('class="active"') ? group.replace('class="nav-parent"', 'class="active nav-parent"') : group);
  return nav;
}
