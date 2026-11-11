"""Capture NEW pairing candidates; never approves review or rewrites an existing record."""
import hashlib
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from i18n.reviewed_rosary_books import LOCALES, SLUGS, SCOPE
from i18n.reviewed_history import digest

path = ROOT / 'locales/rosary-books-pairing.json'
if path.exists():
    raise SystemExit('Refusing to overwrite existing pairing evidence')
import subprocess
record = {'version': 1, 'gateStatus': 'pending-live-click', 'activationStatus': 'pending-authorization',
          'sourceRevision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
          'review': {'scope': SCOPE, 'nativeReviewStatus': 'not-certified', 'editorialReviewStatus': 'not-certified',
                     'technicalReviewStatus': 'pending-live-click', 'reviewer': '', 'evidenceRef': ''}, 'books': {}}
for slug in SLUGS:
    variants = {}
    for code in LOCALES:
        file = ROOT / (('' if code == 'en' else code + '/') + slug + '.html')
        variants[code] = {'bodySha256': digest(file.read_text()),
            'catalogSha256': hashlib.sha256((ROOT / f'locales/{code}/{slug}-master-copy.json').read_bytes()).hexdigest()}
    artifacts = [f'content/books/{slug}/{c}.json' for c in LOCALES] + [f'content/books/{slug}/book.json', f'{slug}-story-i18n-data.js']
    record['books'][slug] = {'variants': variants, 'artifacts': {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in artifacts}}
path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
print('Wrote pending pairing candidate; no review approval invented')
