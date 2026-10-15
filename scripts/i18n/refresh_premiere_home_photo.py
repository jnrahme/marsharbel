"""Rebind the home premiere-card photo copy to the owner-granted Annaya night aerial; preserve every other home source.

Owner directive 2026-10-15 (WhatsApp, verbatim): "i told you you have permission to use any
photos you need and you still kept this one" - the credited Paul Saad / Wikimedia context
photo on the home premiere card is replaced by the monastery's own night aerial
(media/tour/annaya-night-aerial.webp, saintcharbel.com, owner-reported Order permission).
The two premiere photo keys keep their names; only their sources change. The home
"Sources and photo credits" details entry for this item is dropped (no attribution
required), so every '#latest-news > details' binding is left to refresh_home_news_credits.
Executor only: python3 scripts/i18n/refresh_premiere_home_photo.py [--check]
"""
import argparse, hashlib, json, sys
from pathlib import Path
from bs4 import BeautifulSoup
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from i18n.refresh_film_home_bindings import selector

KEYS = {'alt': 'home.latest-news.premiere.photoAlt', 'credit': 'home.latest-news.premiere.photoCaption'}
EN = {
    'alt': "Aerial view of Saint Charbel's church and the monastery of Saint Maron at Annaya, lit up at dusk",
    'credit': "Saint Charbel's church and the monastery of Saint Maron at Annaya, lit up at dusk.",
}
TRANSLATIONS = {
'ar': {'alt': 'منظر جوي لكنيسة مار شربل ودير مار مارون في عنّايا مضاءَين عند الغسق', 'credit': 'كنيسة مار شربل ودير مار مارون في عنّايا مضاءان عند الغسق.'},
'fr': {'alt': "Vue aérienne de l'église Saint-Charbel et du monastère Saint-Maron à Annaya, illuminés au crépuscule", 'credit': "L'église Saint-Charbel et le monastère Saint-Maron à Annaya, illuminés au crépuscule."},
'es': {'alt': 'Vista aérea de la iglesia de San Charbel y el monasterio de San Marón en Annaya, iluminados al anochecer', 'credit': 'La iglesia de San Charbel y el monasterio de San Marón en Annaya, iluminados al anochecer.'},
'pt': {'alt': 'Vista aérea da igreja de São Charbel e do mosteiro de São Maron em Annaya, iluminados ao entardecer', 'credit': 'A igreja de São Charbel e o mosteiro de São Maron em Annaya, iluminados ao entardecer.'},
'it': {'alt': "Vista aerea della chiesa di San Charbel e del monastero di San Marone ad Annaya, illuminati al crepuscolo", 'credit': 'La chiesa di San Charbel e il monastero di San Marone ad Annaya, illuminati al crepuscolo.'},
'de': {'alt': 'Luftaufnahme der St.-Charbel-Kirche und des Klosters St. Maron in Annaya, in der Abenddämmerung beleuchtet', 'credit': 'Die St.-Charbel-Kirche und das Kloster St. Maron in Annaya, in der Abenddämmerung beleuchtet.'},
'pl': {'alt': 'Widok z lotu ptaka na kościół św. Charbela i klasztor św. Marona w Annaji, rozświetlone o zmierzchu', 'credit': 'Kościół św. Charbela i klasztor św. Marona w Annaji, rozświetlone o zmierzchu.'},
'ru': {'alt': 'Вид с воздуха на церковь святого Шарбеля и монастырь святого Марона в Аннайе, освещённые в сумерках', 'credit': 'Церковь святого Шарбеля и монастырь святого Марона в Аннайе, освещённые в сумерках.'},
'hi': {'alt': 'अन्नाया में संत शरबेल के गिरजाघर और संत मारुन के मठ का हवाई दृश्य, गोधूलि में जगमगाए हुए', 'credit': 'अन्नाया में संत शरबेल का गिरजाघर और संत मारुन का मठ, गोधूलि में जगमगाए हुए।'},
'th': {'alt': 'มุมมองทางอากาศของโบสถ์นักบุญชาร์เบลและอารามนักบุญมารอนในอันนายา สว่างไสวยามพลบค่ำ', 'credit': 'โบสถ์นักบุญชาร์เบลและอารามนักบุญมารอนในอันนายา สว่างไสวยามพลบค่ำ'},
}

def outputs(root=ROOT):
    contract = json.loads((root / 'locales/en/home-bindings.json').read_text())
    raw = (root / 'index.html').read_bytes()
    soup = BeautifulSoup(raw, 'html.parser')
    new_keys = set(KEYS.values())
    bindings = []
    rebound = []
    for old in contract['bindings']:
        if old['selector'].startswith('#latest-news > details'):
            # Credits-block bindings are owned by refresh_home_news_credits: carry
            # them verbatim (stale ones are rebuilt by that script right after).
            bindings.append(dict(old))
            continue
        if old['key'] in new_keys:
            rebound.append(old['key'])
            continue  # re-bound fresh below, in place
        nodes = soup.select(old['selector'])
        if len(nodes) != 1:
            raise ValueError('Old binding ambiguous ' + old['key'])
        n = nodes[0]
        value = n.get(old['attribute']) if old['kind'] == 'attribute' else ' '.join(str(n.contents[old['nodeIndex']]).split())
        if value != old['source']:
            raise ValueError('Unrelated home source changed ' + old['key'])
        bindings.append(dict(old))
    if sorted(rebound) != sorted(new_keys):
        raise ValueError('Expected exactly the two card premiere photo bindings outside details, got ' + str(rebound))
    card = soup.select_one('.home-news-lead--film')
    if card is None:
        raise ValueError('Home premiere card missing')
    img = card.select_one('img')
    if img is None or img.get('alt') != EN['alt']:
        raise ValueError('Premiere card image alt mismatch - run build_news_desk first')
    if not img.get('src', '').endswith('media/tour/annaya-night-aerial.webp'):
        raise ValueError('Premiere card image src mismatch - run build_news_desk first')
    credit = card.select_one('.home-news-copy > .home-news-credit')
    if credit is None or credit.get_text(strip=True) != EN['credit']:
        raise ValueError('Premiere card credit mismatch - run build_news_desk first')
    anchor = next((i for i, b in enumerate(bindings) if b['key'] == 'home.latest-news.premiere.read'), None)
    if anchor is None:
        raise ValueError('Premiere read binding anchor missing')
    new_pair = [
        {'key': KEYS['alt'], 'selector': selector(img), 'source': EN['alt'], 'kind': 'attribute', 'attribute': 'alt'},
        {'key': KEYS['credit'], 'selector': selector(credit), 'source': EN['credit'], 'kind': 'text', 'nodeIndex': 0},
    ]
    bindings[anchor + 1:anchor + 1] = new_pair
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
                raise SystemExit('Premiere home photo bindings stale')
        else:
            path.write_text(text)
    print('Premiere home photo bindings checked' if a.check else 'Premiere home photo bindings refreshed')
