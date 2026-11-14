"""Scoped control regeneration through the shared generator; no content/pin changes."""
import argparse
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from i18n.reviewed_rosary_books import rosary_books_manifest, SLUGS, LOCALES
from i18n.same_page_injection import inject_control, with_english_sources
parser = argparse.ArgumentParser()
parser.add_argument('--check', action='store_true')
args = parser.parse_args()
manifest_path = ROOT / 'same-page-manifest.js'
manifest = json.loads(manifest_path.read_text().split(' = ', 1)[1].rstrip(';\n'))
# Replace only this producer's own namespaced families. Other reviewed families
# and singleton collisions remain subject to the producer's overwrite guard.
for slug in SLUGS:
    key = slug + '-master-equivalence'
    old = manifest['pages'].get(key)
    if old:
        if old.get('sourcePath') != slug + '.html' or any(v.get('proof', {}).get('type') != 'scoped-rosary-books-variant' for v in old['variants'].values()):
            raise ValueError('Cannot replace foreign family: ' + key)
        del manifest['pages'][key]
manifest = rosary_books_manifest(ROOT, {}, manifest)
copy = json.loads((ROOT / 'locales/same-page-copy.json').read_text())
outputs = {}
for slug in SLUGS:
    for code in LOCALES:
        path = ROOT / (('' if code == 'en' else code + '/') + slug + '.html')
        outputs[path] = inject_control(path.read_text(), ROOT, manifest, copy)
outputs[manifest_path] = 'window.SC_SAME_PAGE_MANIFEST = ' + json.dumps(with_english_sources(ROOT, manifest), ensure_ascii=False, separators=(',', ':')) + ';\n'
stale = [str(path.relative_to(ROOT)) for path, text in outputs.items() if path.read_text() != text]
if args.check and stale:
    raise SystemExit('Stale rosary control outputs: ' + ', '.join(stale))
if not args.check:
    for path, text in outputs.items():
        path.write_text(text)
print('Rosary controls: 160 HTML + manifest;', len(stale), 'stale' if args.check else 'written')
