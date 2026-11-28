"""Finite EN/AR/FR Secret Prayers continuation. Predecessor stays immutable."""
import hashlib
import json
import re
from pathlib import Path

RECORD = 'locales/secret-prayers-ar-fr-release.json'
# Filled from the authored record, never from a caller-controlled argument.
RECORD_SHA256 = 'bce1d1050ff22164170ad02f011003fc1b78b46d80be6529ce30076a2874f6bf'
SLUGS = ('powerful-secret-prayers', 'mary-who-goes-ahead-prayer', 'lebanese-mountain-prayers', 'terco-da-batalha')
APPROVED = ('en', 'ar', 'fr')
HELD = ('de', 'es', 'hi', 'it', 'pl', 'pt', 'ru', 'th', 'zh-Hans')


def load(root):
    root = Path(root)
    p = root / RECORD
    if not p.exists():
        return None
    if p.is_symlink() or hashlib.sha256(p.read_bytes()).hexdigest() != RECORD_SHA256:
        raise ValueError('Secret AR/FR continuation record drift')
    d = json.loads(p.read_bytes())
    if (d['releaseLocales'] != list(APPROVED) or d['heldLocales'] != list(HELD)
            or d['pages'] != {s + '.html': s + '-master' for s in SLUGS}):
        raise ValueError('Secret AR/FR continuation scope drift')
    previous = root / 'locales/secret-prayers-en-release.json'
    if previous.is_symlink() or hashlib.sha256(previous.read_bytes()).hexdigest() != d['predecessorSha256']:
        raise ValueError('Secret EN predecessor changed')
    return d


def errors(root):
    root = Path(root)
    d = load(root)
    if d is None:
        return []
    out = []
    registry = json.loads((root / 'locales/registry.json').read_bytes())
    for slug in SLUGS:
        family = slug + '-master'
        expected = {c: '/' + c + '/' + slug for c in APPROVED[1:]}
        cfg = registry.get('pageMirrors', {}).get(family, {})
        if (cfg.get('master') != slug + '.html' or cfg.get('english') != '/' + slug
                or cfg.get('routes') != expected or cfg.get('renderLocales') != list(APPROVED[1:])):
            out.append('Secret AR/FR exact family registration differs: ' + family)
        for code in APPROVED[1:]:
            catalog = root / ('locales/' + code + '/' + family + '-copy.json')
            if not catalog.is_file() or catalog.is_symlink():
                out.append('Secret AR/FR required catalog missing: ' + code + '/' + family)
    for code in HELD:
        for slug in SLUGS:
            if (root / code / (slug + '.html')).exists() or (root / code / slug / 'index.html').exists():
                out.append('Held Secret page present: ' + code + '/' + slug)
    held = re.compile(r'(?:https?://(?:www\.)?marsharbel\.com)?/(?:' + '|'.join(re.escape(c) for c in HELD) + ')/(?:' + '|'.join(SLUGS) + r')(?:["<>/?#\s]|$)')
    ignored={'.git','node_modules','scripts','tests','docs','src','templates','partials','test-results','playwright-report'}
    for p in root.rglob('*'):
        if not p.is_file() or p.suffix.lower() not in {'.html','.xml','.json','.js','.txt','.map'}:
            continue
        parts=p.relative_to(root).parts
        if any(c in ignored for c in parts):
            continue
        # Authored translation catalogs are inputs, not published route artifacts.
        # Generated locale manifest and route artifacts stay in scope.
        if parts[0]=='locales' and p.name not in {'same-page-manifest.json','locale-routes.json'}:
            continue
        text=p.read_text(errors='replace')
        if held.search(text):
            out.append('Held Secret URL in generated artifact ' + str(p.relative_to(root)))
        if p.suffix.lower()=='.html' and p.name in {s+'.html' for s in SLUGS}:
            for tag in re.findall(r'<meta\b[^>]*>',text):
                if 'og:locale:alternate' in tag:
                    value=re.search(r'content=[\"\']([^\"\']+)',tag)
                    if value and value.group(1) not in ('en_US','ar_AR','fr_FR'):
                        out.append('Held Secret Open Graph locale in ' + str(p.relative_to(root)))
    return out
