#!/usr/bin/env python3
"""Batch 1 tier 3: Annaya photo swap on the German exact masters + keyed sha refreshes.

miracles-exact.html (de /de/miracles/) and history-exact.html (de biography)
drop the retired externally credited hero/figure images for Order-owned
replacements. Exact catalogs are positional and fail closed, so slots are
realigned against the new masters and the image alt attributes re-pointed.

pilgrimage-master and all-saints-and-all-souls-master keyed contracts only
need a masterSha256 refresh: the og:image/JSON-LD URLs moved to the
replacement assets, which carries no translatable text.
"""
import argparse
import difflib
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bs4 import BeautifulSoup
from i18n.catalog import ROOT
from i18n.guarded_dom import translatable_nodes
from i18n.refresh_annaya_batch1_tier2 import apply_family

MIRACLES_CAP_EN = ('At the tomb of Saint Charbel in Annaya, where pilgrims bring their '
                   'prayers and the monastery gathers the recorded miracles.')
MIRACLES_CAP_DE = ('Am Grab des heiligen Charbel in Annaya, wo Pilger ihre Gebete und '
                   'Anliegen vorbringen und das Kloster die verzeichneten Wunder sammelt.')
MIRACLES_ALT_DE = 'Pilger am Grab des heiligen Charbel in Annaya.'
AERIAL_ALT_DE = 'Das Kloster St. Maron in Annaya aus der Luft, mit der Kirche und dem Berghang'

NOV_CAP = ('The monastery of Saint Maron in Annaya, whose monks published the '
         'traditional novena prayers this page follows.')
NOV_CAP_DE = ('Das Kloster St. Maron in Annaya, dessen Mönche die traditionellen '
              'Novenengebete veröffentlichten, denen diese Seite folgt.')

EXACT_JOBS = [
    dict(name='miracles', lang='de',
         old_img='annaya-entrance-pilgrims.webp', new_img='charbel-tomb-pilgrims.webp',
         new_alt=MIRACLES_ALT_DE, new_text={MIRACLES_CAP_EN: MIRACLES_CAP_DE},
         top_alt=MIRACLES_ALT_DE, alt_sets={}),
    dict(name='biography', lang='de',
         old_img='annaya-monastery.webp', new_img='annaya-monastery-aerial-day.webp',
         new_alt=AERIAL_ALT_DE, new_text={}, top_alt=None, alt_sets={}),
    # tier-2 leftover: the retired novena exact renderer is characterized against
    # templates/masters/saint-charbel-novena.html; realign after its hero swap.
    dict(name='novena', lang='de', master='templates/masters/saint-charbel-novena.html',
         old_img=None, new_img=None, new_alt=None,
         new_text={NOV_CAP: NOV_CAP_DE}, top_alt=None,
         alt_sets={'main figure.hero-figure img': AERIAL_ALT_DE}),
]

# keyed contracts whose rendered masters changed only in og:image/JSON-LD URLs
SHA_JOBS = [
    dict(family='pilgrimage-master', locales=[], ops=[]),
    dict(family='all-saints-and-all-souls-master', locales=[], ops=[]),
]


def refresh_exact(job, check=False):
    cat_p = ROOT / f"locales/{job['lang']}/{job['name']}-exact.json"
    catalog = json.loads(cat_p.read_text())
    master_bytes = (ROOT / job.get('master', catalog['master'])).read_bytes()
    new_sha = hashlib.sha256(master_bytes).hexdigest()
    soup = BeautifulSoup(master_bytes, 'html.parser')
    nodes = translatable_nodes(soup.main)
    new_sources = [' '.join(str(n).split()) for n in nodes]
    old_slots = [catalog['slots'][str(i)] for i in range(len(catalog['slots']))]
    old_sources = [s['source'] for s in old_slots]
    sm = difflib.SequenceMatcher(a=old_sources, b=new_sources, autojunk=False)
    plan = []
    dropped = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'equal':
            for k in range(i2 - i1):
                plan.append(('carry', old_slots[i1 + k]))
        else:
            dropped.extend(s['source'] for s in old_slots[i1:i2])
            plan.extend(('new', src) for src in new_sources[j1:j2])

    attrs = catalog.get('attributes', {})
    old_attr_keys = [k for k in attrs if job['old_img'] and job['old_img'] in k]
    stale = (catalog['masterSha256'] != new_sha
             or len(catalog['slots']) != len(nodes)
             or bool(old_attr_keys)
             or any(attrs.get(sel, {}).get('alt') != alt for sel, alt in job['alt_sets'].items())
             or any(kind == 'new' for kind, _ in plan))
    if check:
        ok = not stale
        print(f"{job['lang']}/{job['name']}-exact: {'OK' if ok else 'NOT APPLIED'}")
        return ok
    if not stale:
        print(f"{job['lang']}/{job['name']}-exact: already applied")
        return True

    new_slots = {}
    for idx, (kind, payload) in enumerate(plan):
        if kind == 'carry':
            new_slots[str(idx)] = payload
        else:
            if payload not in job['new_text']:
                raise ValueError(f"{job['name']}: no translation for new node: {payload[:70]}")
            new_slots[str(idx)] = {'source': payload, 'text': job['new_text'][payload]}
    for key in old_attr_keys:
        new_key = key.replace(job['old_img'], job['new_img'])
        attrs[new_key] = dict(attrs.pop(key), alt=job['new_alt'])
    for sel, alt in job['alt_sets'].items():
        if sel in attrs:
            attrs[sel] = dict(attrs[sel], alt=alt)
    if job['top_alt'] and 'alt' in catalog:
        catalog['alt'] = job['top_alt']
    catalog['slots'] = new_slots
    catalog['masterSha256'] = new_sha
    cat_p.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f"{job['lang']}/{job['name']}-exact: applied "
          f"(dropped {len(dropped)} credit slots, carried {sum(1 for k, _ in plan if k == 'carry')})")
    return True


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true')
    args = ap.parse_args()
    ok = True
    for job in EXACT_JOBS:
        ok = refresh_exact(job, check=args.check) and ok
    for job in SHA_JOBS:
        ok = apply_family(job, check=args.check) and ok
    sys.exit(0 if ok else 1)
