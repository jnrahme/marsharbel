#!/usr/bin/env python3
"""Render the daily news blocks from keyed English copy; --check fails on drift."""
import argparse
import html
import json
from pathlib import Path
import re
ROOT = Path(__file__).resolve().parents[1]

SLOT_ANCHORS = {
    'premiere': 'href="./charbel-film-premiere"',
    'popeGemelli': 'href="./news#pope-leo-assisi-cancel-2026-10-23"',
    'popeRosary': 'href="./news#massabki-centenary-aqoura-2026-10-25"',
    'emmitsburg': 'href="./news#emmitsburg-shrine-anniversary-2026-09"',
    'borik': 'href="./news#doctor-borik-interview-2026-09"',
    'trail': 'href="./saint-charbel-trail"',
}
REQUIRED_LICENSE_FIELDS = ('author', 'spdx', 'permittedUse', 'adaptations')
EXPECTED_SCHEMA_VERSION = 1
LICENSE_STATUSES = ('licensed', 'pd-assumed-territory-uncertain', 'courtesy-permission-record-gap')


def load_image_records(root, template_text):
    """Fail-closed image-record contract: every home news image renders from a
    dated, credited record with explicit rights status; a story-ID change
    without a matching record change fails the build. Only slots with status
    'licensed' claim verified licences; other statuses carry explicit reasons
    and are not implied to be cleared."""
    import datetime
    records = json.loads((root / 'locales/en/news-image-records.json').read_text())
    if records.get('schemaVersion') != EXPECTED_SCHEMA_VERSION:
        raise ValueError(f'image records: schemaVersion must be {EXPECTED_SCHEMA_VERSION}')
    slots = records['slots']
    if set(slots) != set(SLOT_ANCHORS):
        raise ValueError(
            f'image records: slot set must be exactly {sorted(SLOT_ANCHORS)}, '
            f'got {sorted(slots)}')
    for slot, anchor in SLOT_ANCHORS.items():
        rec = slots[slot]
        story = anchor.split('#')[-1].rstrip('"').split('/')[-1].rstrip('"')
        if rec.get('storyId') != story:
            raise ValueError(
                f'image records: slot {slot} story drift - template anchor is '
                f'{story!r} but record says {rec.get("storyId")!r}; update the '
                f'record or add an explicit revalidation note')
        if not isinstance(rec.get('subject'), str) or not rec['subject'].strip():
            raise ValueError(f'image records: slot {slot} subject required')
        if type(rec.get('contextNotEvent')) is not bool:
            raise ValueError(f'image records: slot {slot} contextNotEvent must be a boolean')
        rev = rec.get('revalidation', {})
        if not rev.get('note'):
            raise ValueError(f'image records: slot {slot} missing revalidation note')
        try:
            datetime.date.fromisoformat(str(rev.get('checkedAt', '')))
        except ValueError:
            raise ValueError(f'image records: slot {slot} revalidation.checkedAt must be an ISO date')
        lic = rec['license']
        status = lic.get('status')
        if status not in LICENSE_STATUSES:
            raise ValueError(f'image records: slot {slot} license.status must be one of {LICENSE_STATUSES}')
        if status == 'licensed':
            for url_field in ('licenseUrl', 'sourceUrl'):
                if not str(lic.get(url_field, '')).startswith('https://'):
                    raise ValueError(f'image records: licensed slot {slot} requires evidence URL license.{url_field}')
        elif not str(lic.get('reason', '')).strip():
            raise ValueError(f'image records: unlicensed slot {slot} requires an explicit license.reason')
        img = rec['image']
        src = img['src']
        if not re.fullmatch(r'\./media/[A-Za-z0-9._/-]+', src):
            raise ValueError(f'image records: slot {slot} src has invalid characters: {src!r}')
        media_root = (root / 'media').resolve()
        asset = (root / src).resolve()
        if media_root not in asset.parents:
            raise ValueError(f'image records: slot {slot} src escapes media/: {src!r}')
        if not asset.is_file():
            raise ValueError(f'image records: slot {slot} asset missing: {src}')
        for dim in ('width', 'height'):
            v = img[dim]
            if type(v) is not int or v <= 0:
                raise ValueError(f'image records: slot {slot} {dim} must be a positive integer')
        for field in REQUIRED_LICENSE_FIELDS:
            if not rec['license'].get(field):
                raise ValueError(f'image records: slot {slot} license.{field} required')
        if anchor not in template_text:
            raise ValueError(f'image records: template lost the {slot} anchor {anchor}')
    return {f'img.{slot}.src': rec['image']['src'] for slot, rec in slots.items()} | \
           {f'img.{slot}.width': str(rec['image']['width']) for slot, rec in slots.items()} | \
           {f'img.{slot}.height': str(rec['image']['height']) for slot, rec in slots.items()}


def outputs(root=ROOT):
    copy = json.loads((root / 'locales/en/news-desk.json').read_text())
    result = {}
    for file, template, marker in [('news.html', 'cards.html', 'news-desk'), ('index.html', 'home.html', 'news-home')]:
        text = (root / file).read_text()
        content = (root / 'templates/news-desk' / template).read_text()
        values = load_image_records(root, content) if marker == 'news-home' else {}

        def repl(m, values=values):
            key = m[1]
            if key in values:
                return html.escape(values[key], quote=True)
            return html.escape(copy[key], quote=True)

        content = re.sub(r'\$\{([^}]+)\}', repl, content)
        pattern = rf'(<!-- i18n-{marker}:start -->).*?(<!-- i18n-{marker}:end -->)'
        text, n = re.subn(pattern, lambda m: m[1] + '\n' + content + '\n' + m[2], text, flags=re.S)
        if n != 1:
            raise ValueError(f'{file}: expected exactly one {marker} block')
        text = re.sub(r'(<!-- news-copy:([^:]+):start -->).*?(<!-- news-copy:\2:end -->)',
                      lambda m: m[1] + html.escape(copy[m[2]], quote=True) + m[3], text, flags=re.S)
        result[root / file] = text
    return result

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--check', action='store_true')
    args = p.parse_args()
    for path, content in outputs().items():
        if args.check:
            if path.read_text() != content:
                raise SystemExit(f'News desk output stale: {path.name}')
        else:
            path.write_text(content)
    print('News desk catalog output checked.' if args.check else 'News desk catalog output built.')

if __name__ == '__main__':
    main()
