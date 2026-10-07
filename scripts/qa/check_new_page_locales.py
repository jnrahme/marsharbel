#!/usr/bin/env python3
"""PR-diff gate: new public EN pages require complete keyed locale catalogs.

Existing publication is not grandfathered into translation approval. This check
checks key coverage, not translation quality or permission to publish a twin.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from bs4 import BeautifulSoup, Comment, NavigableString

ROOT = Path(__file__).resolve().parents[2]
REQUIRED = {'ar', 'fr', 'es', 'pt', 'it', 'de', 'pl'}


def public_page(path):
    return path.endswith('.html') and path.split('/')[0] not in {
        'src', 'templates', 'partials', 'tests', 'scripts', 'docs', '.github',
        'node_modules', 'output', 'tmp', 'test-results', 'playwright-report'}


def required_locales(base_registry):
    # Newly landing language expansions activate the requirement on later PRs.
    return REQUIRED | ({'hi', 'th', 'zh-Hans'} & set(base_registry.get('locales', {})))


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
        # Prevent satisfying page coverage with selector/header labels alone.
        for node in soup.descendants:
            if isinstance(node, NavigableString) and not isinstance(node, Comment):
                if node.parent.name in ('script', 'style') or not str(node).strip():
                    continue
                if ('text', id(node)) not in covered:
                    errors.append(f'{page}: unkeyed master text: {str(node).strip()[:70]}')
            if getattr(node, 'attrs', None):
                attrs = ['alt', 'title', 'aria-label', 'placeholder']
                if node.name == 'meta' and (node.get('name') == 'description' or
                        node.get('property') in ('og:title','og:description','twitter:title','twitter:description')):
                    attrs.append('content')
                for attr in attrs:
                    if node.get(attr) and ('attr', id(node), attr) not in covered:
                        errors.append(f'{page}: unkeyed {attr} attribute')
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


def check(root, added, base_registry):
    registry = json.loads((root / 'locales/registry.json').read_text())
    errors = []
    checked = []
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
