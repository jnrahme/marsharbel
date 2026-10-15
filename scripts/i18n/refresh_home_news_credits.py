"""Bind the home news photo-credits block (source + license links outside the card anchors) into the locale mirrors."""
import argparse, hashlib, json, sys
from pathlib import Path
from bs4 import BeautifulSoup, NavigableString
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from i18n.refresh_film_home_bindings import selector

REMOVED = []
KEYS = {
    'heading': 'home.latest-news.sources-and-photo-credits',
    'photo': 'home.latest-news.photo',
    'via': 'home.latest-news.via-wikimedia-commons',
    'derivative': 'home.latest-news.the-webp-derivative-is-shared-under-the-same-license',
}
EN = {
    'heading': 'Sources and photo credits',
    'photo': 'Photo:',
    'via': 'via Wikimedia Commons',
    'derivative': 'The WebP derivative is shared under the same license.',
}
TRANSLATIONS = {
'ar': {'heading': 'المصادر وحقوق الصور', 'photo': 'الصورة:', 'via': 'عبر ويكيميديا كومنز', 'derivative': 'النسخة المشتقة بصيغة WebP تُشارك تحت الرخصة نفسها.'},
'fr': {'heading': 'Sources et crédits photo', 'photo': 'Photo :', 'via': 'via Wikimedia Commons', 'derivative': "L'œuvre dérivée WebP est partagée sous la même licence."},
'es': {'heading': 'Fuentes y créditos de las fotos', 'photo': 'Foto:', 'via': 'via Wikimedia Commons', 'derivative': 'La obra derivada WebP se comparte bajo la misma licencia.'},
'pt': {'heading': 'Fontes e créditos das fotos', 'photo': 'Foto:', 'via': 'via Wikimedia Commons', 'derivative': 'A obra derivada WebP é partilhada sob a mesma licença.'},
'it': {'heading': 'Fonti e crediti fotografici', 'photo': 'Foto:', 'via': 'via Wikimedia Commons', 'derivative': "L'opera derivata WebP è condivisa con la stessa licenza."},
'de': {'heading': 'Quellen und Bildnachweis', 'photo': 'Foto:', 'via': 'via Wikimedia Commons', 'derivative': 'Das WebP-Derivat wird unter derselben Lizenz geteilt.'},
'pl': {'heading': 'Źródła i autorzy zdjęć', 'photo': 'Zdjęcie:', 'via': 'via Wikimedia Commons', 'derivative': 'Utwór zależny WebP jest udostępniany na tej samej licencji.'},
'ru': {'heading': 'Источники и авторы фотографий', 'photo': 'Фото:', 'via': 'через Викисклад', 'derivative': 'Производная работа WebP распространяется под той же лицензией.'},
'hi': {'heading': 'स्रोत और फ़ोटो श्रेय', 'photo': 'फ़ोटो:', 'via': 'विकिमीडिया कॉमन्स के माध्यम से', 'derivative': 'WebP व्युत्पन्न कृति उसी लाइसेंस के तहत साझा की गई है।'},
'th': {'heading': 'แหล่งที่มาและเครดิตภาพ', 'photo': 'ภาพ:', 'via': 'ผ่านวิกิมีเดียคอมมอนส์', 'derivative': 'ผลงานดัดแปลง WebP เผยแพร่ภายใต้สัญญาอนุญาตเดียวกัน'},
}

def outputs(root=ROOT):
    contract = json.loads((root / 'locales/en/home-bindings.json').read_text())
    raw = (root / 'index.html').read_bytes()
    soup = BeautifulSoup(raw, 'html.parser')
    new_keys = set(KEYS.values())
    bindings = []
    by_source = {}
    for old in contract['bindings']:
        if old['key'] in new_keys or old['selector'].startswith('#latest-news > details'):
            continue
        nodes = soup.select(old['selector'])
        if len(nodes) != 1:
            raise ValueError('Old binding ambiguous ' + old['key'])
        n = nodes[0]
        value = n.get(old['attribute']) if old['kind'] == 'attribute' else ' '.join(str(n.contents[old['nodeIndex']]).split())
        if value != old['source']:
            raise ValueError('Unrelated home source changed ' + old['key'])
        bindings.append(dict(old))
        by_source.setdefault(old['source'], old['key'])
    details = soup.select_one('#latest-news details.home-news-credits')
    if details is None:
        raise ValueError('Home news credits block missing - run build_news_desk first')
    new_entries = []
    summ = details.select_one('summary')
    if summ.get_text(strip=True) != EN['heading']:
        raise ValueError('Credits heading mismatch - run build_news_desk first')
    new_entries.append({'key': KEYS['heading'], 'selector': selector(summ), 'source': EN['heading'], 'kind': 'text', 'nodeIndex': 0})
    lis = details.select('li')
    if len(lis) != 4:
        raise ValueError('Credits block should list four photo slots (premiere and trail entries dropped 2026-10-15: previously credited images no longer used)')
    for li in lis:
        title = li.select_one('.news-credit-title')
        title_key = by_source.get(title.get_text(strip=True))
        if title_key is None:
            raise ValueError('Credits row title has no existing binding ' + title.get_text(strip=True)[:40])
        new_entries.append({'key': title_key, 'selector': selector(title), 'source': title.get_text(strip=True), 'kind': 'text', 'nodeIndex': 0})
        label = li.find('span', class_='news-credit-label', string=lambda s: s and s.strip() == EN['photo'])
        if label is None:
            raise ValueError('Credits row photo label missing')
        new_entries.append({'key': KEYS['photo'], 'selector': selector(label), 'source': EN['photo'], 'kind': 'text', 'nodeIndex': 0})
        credit_node = None
        for i, node in enumerate(li.contents):
            if isinstance(node, NavigableString) and ' '.join(str(node).split()) in by_source:
                credit_node = (i, ' '.join(str(node).split()))
                break
        if credit_node is None:
            raise ValueError('Credits row credit text has no existing binding')
        new_entries.append({'key': by_source[credit_node[1]], 'selector': selector(li), 'source': credit_node[1], 'kind': 'text', 'nodeIndex': credit_node[0]})
        via = li.find('a', string=lambda s: s and s.strip() == EN['via'])
        if via is None:
            raise ValueError('Credits row source link missing')
        new_entries.append({'key': KEYS['via'], 'selector': selector(via), 'source': EN['via'], 'kind': 'text', 'nodeIndex': 0})
        deriv = li.find('span', class_='news-credit-derivative', string=lambda s: s and s.strip() == EN['derivative'])
        if deriv is not None:
            new_entries.append({'key': KEYS['derivative'], 'selector': selector(deriv), 'source': EN['derivative'], 'kind': 'text', 'nodeIndex': 0})
    anchor = next((i for i, b in enumerate(bindings) if b['key'] == 'home.latest-news.context-photo-the-monastery-of-saint-charbel-in-annaya'), None)
    if anchor is None:
        raise ValueError('Trail credit binding anchor missing')
    bindings[anchor + 1:anchor + 1] = new_entries
    copy = json.loads((root / 'locales/en/home-copy.json').read_text())
    for slot, key in KEYS.items():
        copy[key] = EN[slot]
    result = {root / 'locales/en/home-copy.json': copy}
    for lang in json.loads((root / 'locales/registry.json').read_text())['homepageMirrors']['renderLocales']:
        local = json.loads((root / f'locales/{lang}/home-copy.json').read_text())
        for slot, key in KEYS.items():
            local[key] = TRANSLATIONS[lang][slot]
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
                raise SystemExit('Home news credits bindings stale')
        else:
            path.write_text(text)
    print('Home news credits bindings checked' if a.check else 'Home news credits bindings refreshed')
