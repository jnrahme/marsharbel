"""Rebind the home trail-row photo copy to the LLEW Annaya derivative; preserve every other home source."""
import argparse, hashlib, json, sys
from pathlib import Path
from bs4 import BeautifulSoup
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from i18n.refresh_film_home_bindings import selector

REMOVED = ['home.accessibility.pilgrims-on-the-saint-charbel-trail-photo-courtesy-of', 'home.latest-news.photo-courtesy-of-father-michael-sliney-lc']
KEYS = {'alt': 'home.accessibility.pilgrims-at-the-entrance-of-the-monastery-of-saint-charbel', 'credit': 'home.latest-news.context-photo-the-monastery-of-saint-charbel-in-annaya'}
EN = {'alt': 'Pilgrims at the entrance of the monastery of Saint Charbel in Annaya, Lebanon', 'credit': 'Context photo: the monastery of Saint Charbel in Annaya, not the trail itself. Photo: LLEW, Wikimedia Commons, CC BY-SA 4.0; cropped and converted to WebP.'}
TRANSLATIONS = {
'ar': {'alt': 'حجاج عند مدخل دير مار شربل في عنّايا، لبنان', 'credit': 'صورة سياقية: دير مار شربل في عنّايا، وليست صورة الدرب نفسه. الصورة: LLEW، ويكيميديا كومنز، CC BY-SA 4.0؛ اقتُصّت وحُوّلت إلى WebP.'},
'fr': {'alt': "Pèlerins à l'entrée du monastère de saint Charbel à Annaya, au Liban", 'credit': "Photo d'illustration : le monastère de saint Charbel à Annaya, et non le chemin lui-même. Photo : LLEW, Wikimedia Commons, CC BY-SA 4.0 ; recadrée et convertie en WebP."},
'es': {'alt': 'Peregrinos a la entrada del monasterio de San Charbel en Annaya, Líbano', 'credit': 'Foto de contexto: el monasterio de San Charbel en Annaya, no el sendero en sí. Foto: LLEW, Wikimedia Commons, CC BY-SA 4.0; recortada y convertida a WebP.'},
'pt': {'alt': 'Peregrinos à entrada do mosteiro de São Charbel em Annaya, Líbano', 'credit': 'Foto de contexto: o mosteiro de São Charbel em Annaya, não a trilha em si. Foto: LLEW, Wikimedia Commons, CC BY-SA 4.0; recortada e convertida para WebP.'},
'it': {'alt': "Pellegrini all'ingresso del monastero di San Charbel ad Annaya, Libano", 'credit': 'Foto di contesto: il monastero di San Charbel ad Annaya, non il sentiero stesso. Foto: LLEW, Wikimedia Commons, CC BY-SA 4.0; ritagliata e convertita in WebP.'},
'de': {'alt': 'Pilger am Eingang des Klosters des Heiligen Charbel in Annaya, Libanon', 'credit': 'Kontextfoto: das Kloster des Heiligen Charbel in Annaya, nicht der Weg selbst. Foto: LLEW, Wikimedia Commons, CC BY-SA 4.0; zugeschnitten und in WebP umgewandelt.'},
'pl': {'alt': 'Pielgrzymi przy wejściu do klasztoru św. Charbela w Annaji, Liban', 'credit': 'Zdjęcie poglądowe: klasztor św. Charbela w Annaji, a nie sam szlak. Zdjęcie: LLEW, Wikimedia Commons, CC BY-SA 4.0; przycięte i przekonwertowane do WebP.'},
'ru': {'alt': 'Паломники у входа в монастырь святого Шарбеля в Аннайе, Ливан', 'credit': 'Иллюстративное фото: монастырь святого Шарбеля в Аннайе, а не сама тропа. Фото: LLEW, Викисклад, CC BY-SA 4.0; обрезано и конвертировано в WebP.'},
'hi': {'alt': 'लेबनान के अन्नाया में संत शरबेल के मठ के प्रवेश द्वार पर तीर्थयात्री', 'credit': 'संदर्भ चित्र: अन्नाया में संत शरबेल का मठ, स्वयं पथ नहीं। फ़ोटो: LLEW, विकिमीडिया कॉमन्स, CC BY-SA 4.0; काटकर WebP में बदला गया।'},
'th': {'alt': 'ผู้แสวงบุญที่ทางเข้าอารามนักบุญชาร์เบลในอันนายา ประเทศเลบานอน', 'credit': 'ภาพประกอบบริบท: อารามนักบุญชาร์เบลในอันนายา ไม่ใช่ตัวเส้นทางเอง ภาพ: LLEW, วิกิมีเดียคอมมอนส์, CC BY-SA 4.0; ครอบตัดและแปลงเป็น WebP'},
}

def outputs(root=ROOT):
    contract = json.loads((root / 'locales/en/home-bindings.json').read_text())
    raw = (root / 'index.html').read_bytes()
    soup = BeautifulSoup(raw, 'html.parser')
    removed = set(REMOVED)
    new_keys = set(KEYS.values())
    bindings = []
    for old in contract['bindings']:
        if (old['key'] in removed or old['key'] in new_keys) and not old['selector'].startswith('#latest-news > details'):
            continue
        nodes = soup.select(old['selector'])
        if len(nodes) != 1:
            raise ValueError('Old binding ambiguous ' + old['key'])
        n = nodes[0]
        value = n.get(old['attribute']) if old['kind'] == 'attribute' else ' '.join(str(n.contents[old['nodeIndex']]).split())
        if value != old['source']:
            raise ValueError('Unrelated home source changed ' + old['key'])
        bindings.append(dict(old))
    copy = json.loads((root / 'locales/en/home-copy.json').read_text())
    for k in removed:
        copy.pop(k, None)
    rows = soup.select('a.home-news-row[href="./saint-charbel-trail"]')
    if len(rows) != 1:
        raise ValueError('Home trail row missing')
    row = rows[0]
    img = row.select_one('img')
    if img is None or img.get('alt') != EN['alt']:
        raise ValueError('Trail row image alt mismatch - run build_news_desk first')
    new_pair = [{'key': KEYS['alt'], 'selector': selector(img), 'source': EN['alt'], 'kind': 'attribute', 'attribute': 'alt'}]
    credit = row.select_one('.home-news-credit')
    if credit is None or credit.get_text(strip=True) != EN['credit']:
        raise ValueError('Trail row credit mismatch - run build_news_desk first')
    new_pair.append({'key': KEYS['credit'], 'selector': selector(credit), 'source': EN['credit'], 'kind': 'text', 'nodeIndex': 0})
    anchor = next((i for i, b in enumerate(bindings) if b['key'] == 'home.latest-news.an-american-priest-walks-the-st-charbel-trail'), None)
    if anchor is None:
        raise ValueError('Trail row title binding missing')
    bindings[anchor + 1:anchor + 1] = new_pair
    for slot, key in KEYS.items():
        copy[key] = EN[slot]
    result = {root / 'locales/en/home-copy.json': copy}
    for lang in json.loads((root / 'locales/registry.json').read_text())['homepageMirrors']['renderLocales']:
        local = json.loads((root / f'locales/{lang}/home-copy.json').read_text())
        for k in removed:
            if k in local:
                del local[k]
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
                raise SystemExit('Trail home photo bindings stale')
        else:
            path.write_text(text)
    print('Trail home photo bindings checked' if a.check else 'Trail home photo bindings refreshed')
