"""Finite post-generation MB16 citation-owner deltas, same immutable C2 pins.

This is reconstruction only. citation prove retains raw HEAD == disk W0.
"""
import json
import re
from pathlib import Path
import subprocess
from i18n import mb16_home_continuation as home

MODULE = 'scripts/i18n/mb16_citation_home.py'
RECORD = 'locales/mb16-citation-home.json'
LABELS = {
    'ar/biography.html': 'اللغات', 'ar/prayers.html': 'اللغات',
    'de/biografie.html': 'Sprachen', 'de/gebete.html': 'Sprachen',
    'en/prayers.html': 'Languages',
    'es/biografia.html': 'Idiomas', 'es/oraciones.html': 'Idiomas',
    'fr/biographie.html': 'Langues', 'fr/prieres.html': 'Langues',
    'hi/history.html': 'भाषाएँ',
    'it/biografia.html': 'Lingue', 'it/preghiere.html': 'Lingue',
    'pl/biografia.html': 'Języki', 'pl/modlitwy.html': 'Języki',
    'pt/biografia.html': 'Idiomas', 'pt/oracoes.html': 'Idiomas',
    'ru/biography.html': 'Языки', 'ru/molitvy.html': 'Языки',
    'th/history.html': 'ภาษา',
}
TRAVEL = 'zh-Hans/saint-charbel-places-lebanon.html'
PATHS = frozenset(LABELS) | {TRAVEL}
# Four literal replacement occurrences in one finite travel file: one brand,
# two identical visible home anchors (header + breadcrumb), one JSON breadcrumb.
TRAVEL_EDITS = (
    ('<a aria-label="✦ 圣夏尔贝勒 （英语）" class="brand" href="/" hreflang="en"><span class="brand-mark">✦</span><span>圣夏尔贝勒</span><span class="partial-home-language"> （英语）</span></a>',
     '<a class="brand" href="/zh-Hans/"><span class="brand-mark">✦</span><span>圣夏尔贝勒</span></a>', 1),
    ('<a aria-label="首页 （英语）" href="/" hreflang="en">首页<span class="partial-home-language"> （英语）</span></a>',
     '<a href="/zh-Hans/">首页</a>', 2),
    ('"position": 1, "name": "首页", "item": "https://marsharbel.com/"',
     '"position": 1, "name": "首页", "item": "https://marsharbel.com/zh-Hans/"', 1),
)

def footer_span(path, raw):
    if path != 'en/prayers.html':
        return home.span(raw, b'i18n-navigation', b'footer')
    # This historical guide has an EMPTY marked block in main and one actual
    # unmarked footer nav. Preserve the empty block exactly, never relocate it.
    empty=b'<!-- i18n-navigation:start -->\n\n<!-- i18n-navigation:end -->'
    if raw.count(empty)!=1 or raw.count(b'<!-- i18n-navigation:start -->')!=1 or raw.count(b'<!-- i18n-navigation:end -->')!=1:
        raise ValueError('MB16 citation: English guide empty markers drift')
    matches=list(re.finditer(rb'<nav aria-label="Languages" class="footer-locales">[\s\S]*?</nav>',raw))
    if len(matches)!=1:raise ValueError('MB16 citation: English guide footer nav count')
    a,z=matches[0].span()
    if raw.rfind(b'<footer',0,a)<0 or raw.find(b'</footer>',a)<z:
        raise ValueError('MB16 citation: English guide footer nav moved')
    return a,z

def footer_block(path, homes):
    value=home.footer(homes).replace(b'aria-label="Languages"', ('aria-label="'+LABELS[path]+'"').encode())
    return value.split(b'\n')[1] if path=='en/prayers.html' else value

def derive(path, original):
    if path not in PATHS:
        raise ValueError('MB16 citation: path outside finite inventory')
    if path == TRAVEL:
        for before, after, count in TRAVEL_EDITS:
            if original.count(before.encode()) != count:
                raise ValueError('MB16 citation: travel occurrence drift')
            original = original.replace(before.encode(), after.encode())
        return original
    a, z = footer_span(path, original)
    old = footer_block(path, home.HOMES)
    new = footer_block(path, home.HOMES+(home.CHINESE,))
    if original[a:z] != old:
        raise ValueError('MB16 citation: old locale footer differs from explicit serializer')
    return original[:a]+new+original[z:]

def verify_delta(path, original, candidate):
    if candidate != original and candidate != derive(path, original):
        raise ValueError('MB16 citation: bytes outside fixed home delta')
    return original

def has_old_home(path, raw):
    if path == TRAVEL:
        return all(raw.count(before.encode()) == count for before, _, count in TRAVEL_EDITS)
    a, z = footer_span(path, raw)
    old = footer_block(path, home.HOMES)
    return raw[a:z] == old

def preimage(root, path, current):
    if path not in PATHS:
        return current
    root = Path(root)
    record = root / RECORD
    if not record.exists() and not record.is_symlink():
        return current
    from i18n.seo_continuations import require_regular_inputs
    inputs = [MODULE, RECORD, home.MODULE, home.RECORD, 'locales/registry.json',
              'scripts/build-international.py', 'scripts/i18n/same_page_injection.py', path]
    require_regular_inputs(root, inputs)
    data = json.loads(record.read_bytes())
    if set(data) != {'base', 'paths'} or data['base'] != home.BASE or set(data['paths']) != PATHS:
        raise ValueError('MB16 citation: record scope drift')
    try:
        head = home.git(root, 'rev-parse', 'HEAD').decode().strip()
        subprocess.run(['git', '-C', str(root), 'merge-base', '--is-ancestor', home.BASE, head],
                       check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        for rel in inputs[:-1]:
            if (root/rel).read_bytes() != home.git(root, 'show', head+':'+rel):
                raise ValueError('MB16 citation: proof input differs from native HEAD '+rel)
        # Reuse the independently bound registry/generator/home identity checks.
        home.preimage(root, 'index.html', (root/'index.html').read_bytes())
        original = home.git(root, 'show', home.BASE+':'+path)
        if home.sha(original) != data['paths'][path]:
            raise ValueError('MB16 citation: original fixed-base pin differs')
        from i18n import citation_history
        if original != home.git(root, 'show', citation_history.REVIEWED_C+':'+path):
            raise ValueError('MB16 citation: original is not SAME immutable C2')
        committed = home.git(root, 'show', head+':'+path)
        disk = (root/path).read_bytes()
        # No MB16 delta supplies no proof: other owners receive original bytes.
        if all(has_old_home(path, raw) for raw in (committed, disk, current)):
            return current
        verify_delta(path, original, committed)
        verify_delta(path, original, (root/path).read_bytes())
        return verify_delta(path, original, current)
    except (OSError, subprocess.CalledProcessError) as error:
        raise ValueError('MB16 citation: native proof unavailable, export rejected') from error
