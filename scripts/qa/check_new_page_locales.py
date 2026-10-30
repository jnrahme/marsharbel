#!/usr/bin/env python3
"""PR-diff gate: new public EN pages require complete keyed locale catalogs.

Existing publication is not grandfathered into translation approval. This check
checks key coverage, not translation quality or permission to publish a twin.
"""
from collections import Counter
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from bs4 import BeautifulSoup, Comment, NavigableString, Doctype, Declaration

ROOT = Path(__file__).resolve().parents[2]
REQUIRED = {'ar', 'fr', 'es', 'pt', 'it', 'de', 'pl'}


def public_page(path):
    return path.endswith('.html') and path.split('/')[0] not in {
        'src', 'templates', 'partials', 'tests', 'scripts', 'docs', '.github',
        'node_modules', 'output', 'tmp', 'test-results', 'playwright-report'}


def required_locales(base_registry):
    # Newly landing language expansions activate the requirement on later PRs.
    return REQUIRED | ({'hi', 'th', 'zh-Hans'} & set(base_registry.get('locales', {})))


def film_shell_coverage(root,page,family,contract,soup,uncovered):
    """Exact film-only alignment of separate catalog ownership models."""
    if page!='charbel-film-premiere.html' or family!='film-premiere-master':return False
    sys.path.insert(0,str(root/'scripts'))
    from i18n.film_master_family import registered
    if not registered(root):return False
    shell=json.loads((root/'locales/en/film-premiere-shell-copy.json').read_text())
    if set(shell)!={page}:raise ValueError('film new-page shell catalog scope mismatch')
    nav=json.loads((root/'locales/en/nav-legacy-copy.json').read_text())['values'][page]
    if any(type(v) is not int or v<1 for v in [*shell[page].values(),*nav.values()]):raise ValueError('film new-page catalog counts must be positive integers')
    caption=[b for b in contract['bindings'] if b['key']=='premiere.videoCaption']
    expected={('text','article#charbel-premiere-release-2026-10 p:nth-of-type(5)',0),('attribute','article#charbel-premiere-release-2026-10 .film-news-video iframe','title')}
    actual={(b['kind'],b['selector'],b.get('nodeIndex') if b['kind']=='text' else b.get('attribute')) for b in caption}
    if len(caption)!=2 or actual!=expected or len({b['source'] for b in caption})!=1:raise ValueError('film new-page exact caption pair required')
    value=caption[0]['source']
    for b in caption:
        nodes=soup.select(b['selector'])
        if len(nodes)!=1:raise ValueError('film new-page caption node ambiguous')
        actual_value=str(nodes[0].contents[b['nodeIndex']]).strip() if b['kind']=='text' else nodes[0].get(b['attribute'])
        if actual_value!=value:raise ValueError('film new-page caption value drift')
    counts=Counter(shell[page])
    if counts[value]!=1:raise ValueError('film new-page caption mapping must be exactly one occurrence')
    counts.subtract({value:1});counts+=Counter(nav)
    if '<nav class="links"' in (root/page).read_text():
        counts.update({json.loads((root/'locales/en/travel.json').read_text())['hubLabel']:1})
    if Counter(uncovered)!=counts:raise ValueError('film new-page exact uncovered/catalog counter mismatch')
    return True


def check_page(root, page, registry, required):
    errors = []
    families = [(name, cfg) for name, cfg in registry.get('pageMirrors', {}).items()
                if cfg.get('master') == page]
    if len(families) != 1:
        return [f'{page}: register exactly one keyed pageMirrors family with master={page}']
    family, cfg = families[0]
    try:
        contract = json.loads((root / f'locales/en/{family}-bindings.json').read_text())
        english = json.loads((root / f'locales/en/{family}-copy.json').read_text())
        if contract['master'] != page:
            raise ValueError('bindings master must be the newly added served page, not unrelated text')
        master = root / contract['master']
        if master.is_absolute() and not master.resolve().is_relative_to(root.resolve()):
            raise ValueError('master outside checkout')
        soup = BeautifulSoup(master.read_text(), 'html.parser')
        bindings = contract['bindings']
        if not english or set(english) != {b['key'] for b in bindings}:
            raise ValueError('English catalog keys must match nonempty full binding set')
        covered = set()
        for binding in bindings:
            nodes = soup.select(binding['selector'])
            if len(nodes) != 1:
                raise ValueError('ambiguous binding: '+binding['key'])
            node = nodes[0]
            if binding['kind'] == 'text':
                covered.add(('text', id(node.contents[binding['nodeIndex']])))
            else:
                covered.add(('attr', id(node), binding['attribute']))
        uncovered=Counter()
        coverage_start=len(errors)
        # Prevent satisfying page coverage with selector/header labels alone.
        for node in soup.descendants:
            if isinstance(node, NavigableString) and not isinstance(node, (Comment, Doctype, Declaration)):
                if node.parent.name in ('script', 'style') or not str(node).strip():
                    continue
                if ('text', id(node)) not in covered:
                    uncovered[' '.join(str(node).split())]+=1
                    errors.append(f'{page}: unkeyed master text: {str(node).strip()[:70]}')
            if getattr(node, 'attrs', None):
                attrs = ['alt', 'title', 'aria-label', 'placeholder']
                if node.name == 'meta' and (node.get('name') == 'description' or
                        node.get('property') in ('og:title','og:description','twitter:title','twitter:description')):
                    attrs.append('content')
                for attr in attrs:
                    if node.get(attr) and ('attr', id(node), attr) not in covered:
                        uncovered[node[attr]]+=1
                        errors.append(f'{page}: unkeyed {attr} attribute')
        if film_shell_coverage(root,page,family,contract,soup,uncovered):
            del errors[coverage_start:]
        # Reuse production validation for SHA pin, source bindings, placeholders,
        # exact key parity, unsafe/empty values and real keyed application.
        sys.path.insert(0, str(root / 'scripts'))
        from i18n.keyed_master import apply_keyed_master
        apply_keyed_master(root, family, 'en')
        for code in sorted(required):
            try:
                apply_keyed_master(root, family, code)
            except (ValueError, KeyError, IndexError, OSError) as exc:
                errors.append(f'{page}: {code}: {exc}')
    except (ValueError, KeyError, IndexError, OSError) as exc:
        errors.append(f'{page}: {exc}')
    return errors


ALLOWLIST = 'locales/private-preview-pages.json'


def load_private_previews(root):
    """Explicit private-preview allowlist. Each entry: page, owner, reason, handoff."""
    path = root / ALLOWLIST
    if not path.exists():
        return {}
    data = json.loads(path.read_text())
    entries = data['pages'] if isinstance(data, dict) else data
    out = {}
    for entry in entries:
        page = entry.get('page', '')
        if not public_page(page):
            raise ValueError('private preview entry is not a served page path: ' + page)
        if page in out:
            raise ValueError('duplicate private preview entry: ' + page)
        for field in ('owner', 'reason', 'handoff'):
            if not str(entry.get(field, '')).strip():
                raise ValueError('private preview entry missing ' + field + ': ' + page)
        if not (root / page).is_file():
            raise ValueError('private preview entry names a missing page: ' + page)
        out[page] = entry
    return out


def private_preview_errors(root, page):
    """Isolation contract for an allowlisted private preview page."""
    errors = []
    soup = BeautifulSoup((root / page).read_text(), 'html.parser')
    robots = soup.find('meta', attrs={'name': 'robots'})
    if not robots or 'noindex' not in robots.get('content', '').lower():
        errors.append(page + ': private preview requires meta robots noindex')
    stem = page[:-len('.html')] if page.endswith('.html') else page
    sitemap = (root / 'sitemap.xml')
    if sitemap.exists():
        for loc in re.findall(r'<loc>([^<]+)</loc>', sitemap.read_text()):
            u = loc.split('marsharbel.com/', 1)[-1].rstrip('/')
            if u in {stem, page}:
                errors.append(page + ': private preview must stay out of sitemap.xml')
    href_pat = re.compile(r'href=["\'](?:https://marsharbel\.com)?/?\.?/?'
                          + re.escape(stem) + r'(?:\.html)?/?["\'#?]')
    sources = [p for p in root.glob('*.html')]
    sources += [p for p in (root / 'partials').glob('**/*.html')] if (root / 'partials').is_dir() else []
    sources += [p for p in (root / 'src/pages').glob('*.html')] if (root / 'src/pages').is_dir() else []
    for other in sources:
        rel = other.relative_to(root).as_posix()
        if rel == page:
            continue
        if href_pat.search(other.read_text()):
            errors.append(page + ': inbound link from ' + rel)
    feed = root / 'feed.xml'
    if feed.exists() and href_pat.search(feed.read_text()):
        errors.append(page + ': referenced in feed.xml')
    return errors


def check(root, added, base_registry):
    registry = json.loads((root / 'locales/registry.json').read_text())
    errors = []
    checked = []
    previews = load_private_previews(root)
    # Isolation is asserted for every allowlisted page on every run, so a later
    # unrelated PR cannot quietly link or index a preview.
    for preview_page in previews:
        errors.extend(private_preview_errors(root, preview_page))
    for page in added:
        if not public_page(page):
            continue
        soup = BeautifulSoup((root/page).read_text(), 'html.parser')
        first = page.split('/')[0]
        known = set(base_registry.get('locales', {})) | REQUIRED | {'hi','th','zh-Hans'}
        if first in known - {'en'} and soup.html and soup.html.get('lang', '').lower() == first.lower():
            continue
        # Public utility/error pages are also pages. No implicit exemptions.
        checked.append(page)
        if page in previews:
            # Explicitly allowlisted private preview: exempt from the keyed-mirror
            # requirement only while the full isolation contract holds.
            errors.extend(private_preview_errors(root, page))
            continue
        errors.extend(check_page(root, page, registry, required_locales(base_registry)))
    return checked, errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', required=True, help='trusted PR base commit SHA')
    args = parser.parse_args()
    if not re.fullmatch(r'[a-f0-9]{40}', args.base):
        parser.error('--base must be a full commit SHA')
    try:
        base_registry = json.loads(subprocess.check_output(
            ['git', 'show', args.base+':locales/registry.json'], cwd=ROOT, text=True))
        # No rename detection: a renamed public URL is a newly added page too.
        added = subprocess.check_output(['git', 'diff', '--no-renames', '--diff-filter=A',
            '--name-only', args.base, 'HEAD'], cwd=ROOT, text=True).splitlines()
        checked, errors = check(ROOT, added, base_registry)
    except (subprocess.CalledProcessError, ValueError, OSError) as exc:
        print('New-page locale gate could not verify base: '+str(exc), file=sys.stderr)
        return 1
    for error in errors:
        print(error, file=sys.stderr)
    print('Note: Russian is first-slice scoped and is not required for new pages.')
    if errors:
        return 1
    print(f'New-page locale gate passed: {len(checked)} new EN pages; required '+
          ','.join(sorted(required_locales(base_registry))))
    return 0


if __name__ == '__main__':
    sys.exit(main())
