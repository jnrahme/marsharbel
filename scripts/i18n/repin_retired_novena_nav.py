"""Bounded retired-novena nav-only digest repair; independent runner required."""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]
MASTER = 'templates/masters/saint-charbel-novena.html'
CATALOG = re.compile(r'locales/[a-z]+(?:-[A-Za-z]+)?/novena-exact\.json\Z')
DIGEST = re.compile(r'("masterSha256"\s*:\s*")([0-9a-f]{64})(")')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def blob(root, ref, path):
    return subprocess.check_output(['git', 'show', f'{ref}:{path}'], cwd=root)


def retired(registry, code):
    exact = registry.get('exactMirrors', {}).get('novena', {})
    keyed = registry.get('pageMirrors', {}).get('saint-charbel-novena-master', {})
    return (exact.get('renderLocales') == []
            and code in exact.get('routes', {})
            and code in keyed.get('renderLocales', [])
            and keyed.get('routes', {}).get(code) == exact['routes'][code])


def nav_mask(raw):
    # Raw-byte equality outside the one header nav catches comments, attributes,
    # scripts, metadata and non-nav header nodes, not merely parsed text.
    text = raw.decode('utf-8')
    soup = BeautifulSoup(text, 'html.parser')
    if len(soup.select('header')) != 1 or len(soup.select('header nav')) != 1:
        raise ValueError('Expected one header and one header nav')
    headers = list(re.finditer(r'<header\b[^>]*>[\s\S]*?</header\s*>', text, re.I))
    if len(headers) != 1:
        raise ValueError('Ambiguous raw header')
    h = headers[0]
    navs = list(re.finditer(r'<nav\b[^>]*>[\s\S]*?</nav\s*>', h.group(), re.I))
    if len(navs) != 1:
        raise ValueError('Ambiguous raw header nav')
    n = navs[0]
    start, end = h.start() + n.start(), h.start() + n.end()
    return (text[:start] + '<NAV/>' + text[end:]).encode()


def validate(path, old_catalog, current_catalog, before, after, base_registry, registry):
    if not CATALOG.fullmatch(path):
        raise ValueError('Out-of-scope catalog')
    code = path.split('/')[1]
    if not retired(base_registry, code) or not retired(registry, code):
        raise ValueError('Non-retired catalog')
    old, current = json.loads(old_catalog), json.loads(current_catalog)
    if old.get('master') != 'saint-charbel-novena.html' or current.get('master') != old['master']:
        raise ValueError('Unexpected catalog master')
    old_sha, new_sha = sha(before), sha(after)
    if old.get('masterSha256') != old_sha:
        raise ValueError('Base catalog does not pin base frozen master')
    if current.get('masterSha256') not in (old_sha, new_sha):
        raise ValueError('Old digest matches neither base nor target')
    old_fields, current_fields = dict(old), dict(current)
    old_fields.pop('masterSha256'); current_fields.pop('masterSha256')
    if old_fields != current_fields:
        raise ValueError('Review or other catalog fields changed')
    soups = [BeautifulSoup(raw, 'html.parser') for raw in (before, after)]
    if any(len(s.select('main')) != 1 for s in soups):
        raise ValueError('Expected one main')
    body_hashes = [sha(str(s.main).encode()) for s in soups]
    if body_hashes[0] != body_hashes[1]:
        raise ValueError('Body diff')
    if nav_mask(before) != nav_mask(after):
        raise ValueError('Non-nav node change')
    nav = soups[1].header.nav
    media = [a for a in nav.select('a.nav-parent') if a.get_text(' ', strip=True) == 'Media']
    if len(media) != 1:
        raise ValueError('Missing unique Media nav group')
    group = media[0].find_parent(class_='nav-group')
    links = group.select('.nav-sub a') if group else []
    if [(a.get_text(strip=True), a.get('href')) for a in links] != [
            ('Music', './music'), ('Video', './videos'), ('Gallery', './gallery')]:
        raise ValueError('Unexpected Media nav links')
    if len(DIGEST.findall(current_catalog)) != 1:
        raise ValueError('Ambiguous digest field')
    updated = DIGEST.sub(lambda m: m[1] + new_sha + m[3], current_catalog)
    return updated, dict(file=path, old=current['masterSha256'], new=new_sha,
                         body_before=body_hashes[0], body_after=body_hashes[1],
                         reason='header-only, Media nav parity')


def prepare(root, base):
    # All catalogs validate before any write. Only the frozen master is used,
    # never the actively generated served novena master.
    before = blob(root, base, MASTER)
    after = (root / MASTER).read_bytes()
    if after != blob(root, 'HEAD', MASTER):
        raise ValueError('Uncommitted target master')
    base_registry = json.loads(blob(root, base, 'locales/registry.json'))
    registry = json.loads((root / 'locales/registry.json').read_text())
    updates, rows = {}, []
    for p in sorted((root / 'locales').glob('*/novena-exact.json')):
        path = p.relative_to(root).as_posix()
        updated, row = validate(path, blob(root, base, path).decode(), p.read_text(),
                                before, after, base_registry, registry)
        updates[p] = updated
        rows.append(row)
    if not rows:
        raise ValueError('No retired novena catalogs found')
    return updates, rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', required=True)
    parser.add_argument('--write', action='store_true', help='Independent runner only; default is check')
    args = parser.parse_args()
    updates, rows = prepare(ROOT, args.base)
    print(json.dumps({'mode': 'write' if args.write else 'check', 'digests': rows}, indent=2))
    if args.write:
        for path, text in updates.items():
            if path.read_text() != text:
                path.write_text(text)


if __name__ == '__main__':
    main()
