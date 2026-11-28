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
# scrum 2026-10-15 pilgrimage ruling applies to this photo too: the shipped
# charbel-tomb-pilgrims.webp is an empty candlelit tomb chapel (no people), so
# the intentional alt is the candlelit wording; the earlier pilgrims alt
# described people absent from the frame.
MIRACLES_ALT_DE = 'Die kerzenbeleuchtete Grabkapelle des heiligen Charbel in Annaya.'
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

TOMB_CHAPEL_ALT = ('The candlelit tomb chapel of Saint Charbel in the monastery '
                   'church at Annaya')
TOMB_CHAPEL_ALT_TR = {
    'ar': 'مصلّى ضريح القديس شربل المضاء بالشموع في كنيسة الدير في عنّايا',
    'de': 'Die kerzenbeleuchtete Grabkapelle des heiligen Charbel in der Klosterkirche von Annaya',
    'es': 'La capilla del sepulcro de San Charbel a la luz de las velas en la iglesia del monasterio de Annaya',
    'fr': "La chapelle du tombeau de saint Charbel éclairée de cierges dans l'église du monastère d'Annaya",
    'it': 'La cappella della tomba di San Charbel illuminata a lume di candela nella chiesa del monastero ad Annaya',
    'pl': 'Oświetlona świecami kaplica grobu św. Charbela w kościele klasztornym w Annaji',
    'pt': 'A capela do túmulo de São Charbel à luz de velas na igreja do mosteiro em Annaya',
    'ru': 'Освещённая свечами часовня гроба святого Шарбеля в монастырской церкви в Аннайе',
    'zh-Hans': '安纳亚修道院教堂内烛光映照的圣夏贝尔墓祷堂',
}

# keyed contracts whose rendered masters changed only in og:image/JSON-LD URLs
KEYED_JOBS = [
    # scrum 2026-10-15: alt described people; the photo is an empty candlelit chapel
    dict(family='pilgrimage-master',
         locales=['ar', 'de', 'es', 'fr', 'it', 'pl', 'pt', 'ru', 'zh-Hans'],
         ops=[dict(op='rekey-alt',
                   old='pilgrimage.accessibility.pilgrims-at-the-tomb-of-saint-charbel-in-the-monastery-churc',
                   prefix='pilgrimage.accessibility.',
                   en=TOMB_CHAPEL_ALT, tr=TOMB_CHAPEL_ALT_TR)]),
    # scrum 2026-10-15: alt claimed the modern church interior is where Saint
    # Charbel prayed for forty-seven years - unproven exact-building claim
    dict(family='prayer-library-master',
         locales=['ar'],
         ops=[dict(op='rekey-alt',
                   old='prayer-library.main-img-alt-inside-the-monastery-church-at-annaya-where-saint-charbel-pr',
                   prefix='prayer-library.main-img-alt-',
                   en='Inside the monastery church at Annaya',
                   tr={'ar': 'داخل كنيسة الدير في عنّايا'})]),
]

SHA_JOBS = [
    dict(family='pilgrimage-master', locales=[], ops=[]),
    dict(family='all-saints-and-all-souls-master', locales=[], ops=[]),
]


def validate_applied(job, catalog, new_sources):
    """Narrow --check validation of an already-applied catalog.

    Positive controls: every job.new_text source is bound exactly once to its
    expected translation; changed attribute/top-alt values equal their
    expected values. Negative controls: no slot carries a source the master
    no longer has, no untranslated passthrough, retired image attribute keys
    are gone.
    """
    problems = []
    slots = catalog['slots']
    for source, expected in job['new_text'].items():
        matches = [s for s in slots.values() if s['source'] == source]
        if len(matches) != 1:
            problems.append(f"new_text source bound {len(matches)}x (want exactly 1): {source[:60]}")
        elif matches[0]['text'] != expected:
            problems.append(f"new_text translation mismatch for: {source[:60]}")
        elif job['lang'] != 'en' and matches[0]['text'] == source:
            problems.append(f"untranslated passthrough for: {source[:60]}")
    for s in slots.values():
        if s['source'] not in new_sources:
            problems.append(f"slot source absent from master: {s['source'][:60]}")
    attrs = catalog.get('attributes', {})
    if job['old_img']:
        old_keys = [k for k in attrs if job['old_img'] in k]
        new_keys = [k for k in attrs if job['new_img'] in k]
        if old_keys:
            problems.append(f"retired image attribute key still present: {old_keys[0]}")
        if not new_keys:
            problems.append(f"replacement image attribute key missing ({job['new_img']})")
        elif job['new_alt'] is not None:
            for key in new_keys:
                if attrs[key].get('alt') != job['new_alt']:
                    problems.append(f"replacement attribute alt mismatch on {key}")
    for sel, alt in job['alt_sets'].items():
        if attrs.get(sel, {}).get('alt') != alt:
            problems.append(f"alt_sets expected value mismatch on {sel}")
    if job['top_alt'] is not None and catalog.get('alt') != job['top_alt']:
        problems.append("top-level alt does not equal expected value")
    return problems


def refresh_exact(job, check=False):
    cat_p = ROOT / f"locales/{job['lang']}/{job['name']}-exact.json"
    catalog = json.loads(cat_p.read_text())
    from i18n.keyed_master import strip_static_fallback
    master_bytes = strip_static_fallback((ROOT / job.get('master', catalog['master'])).read_bytes())
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
        problems = [] if stale else validate_applied(job, catalog, new_sources)
        ok = not stale and not problems
        status = 'OK' if ok else ('NOT APPLIED' if stale else 'INVALID')
        print(f"{job['lang']}/{job['name']}-exact: {status}")
        for problem in problems:
            print(f"  - {problem}")
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
    for job in KEYED_JOBS:
        ok = apply_family(job, check=args.check) and ok
    for job in SHA_JOBS:
        ok = apply_family(job, check=args.check) and ok
    sys.exit(0 if ok else 1)
