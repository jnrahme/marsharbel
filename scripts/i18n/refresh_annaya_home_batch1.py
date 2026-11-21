"""Rebind the home-page Annaya photo copy swapped to owner-granted monastery photos
(Batch 1, 2026-10-15): the trail-row photo (LLEW derivative replaced by the monastery's
dusk church-entrance photo), the home-travel card (Paul Saad winter panorama replaced by
the monastery's snow church photo) and the footer credit span. The travel-credit
paragraph and the footer span are gone from the page, so their keys are pruned from every
locale copy; the trail and travel alt keys keep their names, only their sources change.
Every '#latest-news > details' binding is carried verbatim for refresh_home_news_credits.
Rights basis: owner-reported reuse permission; attribution terms not independently
documented; prior credits removed because the previously credited images are no longer used.
Executor only: python3 scripts/i18n/refresh_annaya_home_batch1.py [--check]
"""
import argparse, hashlib, json, sys
from pathlib import Path
from bs4 import BeautifulSoup
ROOT = Path(__file__).resolve().parents[2]

REBIND = {
    'home.accessibility.pilgrims-at-the-entrance-of-the-monastery-of-saint-charbel': {
        'en': 'The church entrance of the monastery of Saint Maron at Annaya at dusk',
        'ar': 'مدخل كنيسة دير مار مارون في عنّايا عند الغسق',
        'fr': "L'entrée de l'église du monastère Saint-Maron à Annaya au crépuscule",
        'es': 'La entrada de la iglesia del monasterio de San Marón en Annaya al anochecer',
        'pt': 'A entrada da igreja do mosteiro de São Maron em Annaya ao entardecer',
        'it': "L'ingresso della chiesa del monastero di San Marone ad Annaya al crepuscolo",
        'de': 'Der Kircheneingang des Klosters St. Maron in Annaya in der Abenddämmerung',
        'pl': 'Wejście do kościoła klasztoru św. Marona w Annaji o zmierzchu',
        'ru': 'Вход в церковь монастыря святого Марона в Аннайе в сумерках',
        'hi': 'गोधूलि में अन्नाया के संत मारुन मठ के गिरजाघर का प्रवेश द्वार',
        'th': 'ทางเข้าโบสถ์ของอารามนักบุญมารอนในอันนายายามพลบค่ำ'},
    'home.latest-news.context-photo-the-monastery-of-saint-charbel-in-annaya': {
        'en': 'Context photo: the monastery church entrance in Annaya at dusk, not the trail itself.',
        'ar': 'صورة سياقية: مدخل كنيسة الدير في عنّايا عند الغسق، وليست صورة الدرب نفسه.',
        'fr': "Photo d'illustration : l'entrée de l'église du monastère à Annaya au crépuscule, et non le chemin lui-même.",
        'es': 'Foto de contexto: la entrada de la iglesia del monasterio en Annaya al anochecer, no el sendero en sí.',
        'pt': 'Foto de contexto: a entrada da igreja do mosteiro em Annaya ao entardecer, não a trilha em si.',
        'it': "Foto di contesto: l'ingresso della chiesa del monastero ad Annaya al crepuscolo, non il sentiero stesso.",
        'de': 'Kontextfoto: der Kircheneingang des Klosters in Annaya in der Abenddämmerung, nicht der Weg selbst.',
        'pl': 'Zdjęcie poglądowe: wejście do kościoła klasztornego w Annaji o zmierzchu, a nie sam szlak.',
        'ru': 'Иллюстративное фото: вход в церковь монастыря в Аннайе в сумерках, а не сама тропа.',
        'hi': 'संदर्भ चित्र: गोधूलि में अन्नाया के मठ के गिरजाघर का प्रवेश द्वार, स्वयं पथ नहीं।',
        'th': 'ภาพประกอบบริบท: ทางเข้าโบสถ์ของอารามในอันนายายามพลบค่ำ ไม่ใช่ตัวเส้นทางเอง'},
    'home.accessibility.the-church-and-monastery-of-saint-maron-at-annaya': {
        'en': 'The church of the monastery of Saint Maron at Annaya in the snow',
        'ar': 'كنيسة دير مار مارون في عنّايا تحت الثلج',
        'fr': "L'église du monastère Saint-Maron à Annaya sous la neige",
        'es': 'La iglesia del monasterio de San Marón en Annaya bajo la nieve',
        'pt': 'A igreja do mosteiro de São Maron em Annaya na neve',
        'it': 'La chiesa del monastero di San Marone ad Annaya nella neve',
        'de': 'Die Kirche des Klosters St. Maron in Annaya im Schnee',
        'pl': 'Kościół klasztoru św. Marona w Annaji w śniegu',
        'ru': 'Церковь монастыря святого Марона в Аннайе в снегу',
        'hi': 'बर्फ़ में अन्नाया के संत मारुन मठ का गिरजाघर',
        'th': 'โบสถ์ของอารามนักบุญมารอนในอันนายาท่ามกลางหิมะ'},
}
PRUNE = {
    'home.home-travel.photo-paul-saad',
    'home.home-travel.wikimedia-commons',
    'home.home-travel.cc-by-sa-4-0-cropped-and-resized',
    'home.footer.annaya-photo-llew-cc-by-sa-4-0',
}

def value_of(n, old):
    if old['kind'] == 'attribute':
        return n.get(old['attribute'])
    return ' '.join(str(n.contents[old['nodeIndex']]).split())

def outputs(root=ROOT):
    contract = json.loads((root / 'locales/en/home-bindings.json').read_text())
    raw = (root / 'index.html').read_bytes()
    soup = BeautifulSoup(raw, 'html.parser')
    rebind_keys = set(REBIND)
    pruned, rebound = [], []
    bindings = []
    for old in contract['bindings']:
        if old['selector'].startswith('#latest-news > details'):
            bindings.append(dict(old))  # rebuilt by refresh_home_news_credits right after
            continue
        if old['key'] in PRUNE:
            nodes = soup.select(old['selector'])
            if nodes:
                try:
                    if value_of(nodes[0], old) == old['source']:
                        raise ValueError('Removed element still present ' + old['key'])
                except IndexError:
                    pass
            pruned.append(old['key'])
            continue
        nodes = soup.select(old['selector'])
        if len(nodes) != 1:
            raise ValueError('Old binding ambiguous ' + old['key'])
        n = nodes[0]
        value = value_of(n, old)
        if old['key'] in rebind_keys:
            if value != REBIND[old['key']]['en']:
                raise ValueError('Rebound home copy mismatch - run build-pages and build_news_desk first: ' + old['key'])
            new = dict(old)
            new['source'] = value
            bindings.append(new)
            rebound.append(old['key'])
            continue
        if value != old['source']:
            raise ValueError('Unrelated home source changed ' + old['key'])
        bindings.append(dict(old))
    missing = PRUNE - set(pruned)
    copy_keys = set(json.loads((root / 'locales/en/home-copy.json').read_text()))
    for key in missing:
        if any(b['key'] == key for b in contract['bindings']) or key in copy_keys:
            raise ValueError('Pruned key still partially present ' + key)
    if sorted(rebound) != sorted(rebind_keys):
        raise ValueError('Expected the three rebound keys, got ' + str(rebound))
    remaining = {b['key'] for b in bindings}
    for key in PRUNE:
        if key in remaining:
            raise ValueError('Pruned key still bound elsewhere ' + key)
    copy = json.loads((root / 'locales/en/home-copy.json').read_text())
    for key in PRUNE:
        copy.pop(key, None)
    for key, texts in REBIND.items():
        copy[key] = texts['en']
    result = {root / 'locales/en/home-copy.json': copy}
    for lang in json.loads((root / 'locales/registry.json').read_text())['homepageMirrors']['renderLocales']:
        local = json.loads((root / f'locales/{lang}/home-copy.json').read_text())
        for key in PRUNE:
            local.pop(key, None)
        for key, texts in REBIND.items():
            local[key] = texts[lang]
        if set(local) != set(copy):
            raise ValueError('Locale home keys differ ' + lang)
        result[root / f'locales/{lang}/home-copy.json'] = local
    contract.update(bindings=bindings, messages=copy, masterSha256=hashlib.sha256(raw).hexdigest())
    result[root / 'locales/en/home-bindings.json'] = contract
    return {p: json.dumps(j, ensure_ascii=False, indent=2) + '\n' for p, j in result.items()}

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--check', action='store_true')
    a = p.parse_args()
    for path, text in outputs().items():
        if a.check:
            if path.read_text() != text:
                raise SystemExit('Annaya batch-1 home bindings stale: ' + str(path))
        else:
            path.write_text(text)
    print('Annaya batch-1 home bindings checked' if a.check else 'Annaya batch-1 home bindings refreshed')
