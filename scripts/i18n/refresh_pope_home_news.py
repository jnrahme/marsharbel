"""Rebind the October 13 pope home-news rows; preserve every other home source."""
import argparse, hashlib, json, sys
from pathlib import Path
from bs4 import BeautifulSoup, NavigableString
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from i18n.refresh_film_home_bindings import selector

REMOVED = ['home.latest-news.september-26-2026', 'home.latest-news.prayer-walk-to-annaya-brings-prayers-for-south-lebanon', 'home.latest-news.annaya-monastery-entrance-photo-llew-cc-by-sa-4', 'home.latest-news.october-2-2026', 'home.latest-news.kfifan-receives-relics-of-its-patron-saints-from-rome', 'home.latest-news.kfifan-monastery-2012-venue-context-not-the-relic-reception',
 'home.accessibility.a-pilgrim-touching-the-statue-of-saint-charbel-at',
 'home.accessibility.the-stone-kfifan-monastery-buildings-and-courtyard-in-lebanon']
KEYS = {'date': 'home.latest-news.october-13-2026', 'title1': 'home.latest-news.pope-leo-xiv-s-lung-surgery-completed-successfully', 'alt': 'home.accessibility.pope-leo-xiv-praying-at-the-tomb-of-saint-charbel-in-annaya', 'credit1': 'home.latest-news.the-holy-see-says-the-operation-was-successful-with-no-compl', 'title2': 'home.latest-news.catholics-pray-for-pope-leo-at-gemelli', 'credit2': 'home.latest-news.cardinal-baldassarre-reina-led-the-evening-rosary-in-the-hos'}
EN = {'date': 'October 13, 2026', 'title1': "Pope Leo XIV's lung surgery completed successfully", 'alt': 'Pope Leo XIV praying at the tomb of Saint Charbel in Annaya', 'credit1': 'The Holy See says the operation was successful with no complications and Pope Leo has returned to his room. Photo: Vatican Media / Vatican News.', 'title2': 'Catholics pray for Pope Leo at Gemelli', 'credit2': 'Cardinal Baldassarre Reina led the evening Rosary in the hospital chapel as Catholics prayed for the Pope. Photo: Vatican Media / Vatican News.'}
TRANSLATIONS = {'ar': {'date': '13 تشرين الأول 2026', 'title1': 'اكتُملت جراحة رئة البابا لاوُن الرابع عشر بنجاح', 'alt': 'البابا لاوُن الرابع عشر يصلّي عند ضريح القديس شربل في عنايا', 'credit1': 'الكرسي الرسولي: العملية نجحت دون مضاعفات، والبابا لاوُن عاد إلى غرفته. الصورة: فاتيكان ميديا / فاتيكان نيوز.', 'title2': 'الكاثوليك يصلّون من أجل البابا لاوُن في جيميلي', 'credit2': 'الكاردينال بالداسارّي رينا ترأس صلاة المسبحة المسائية في كنيسة المستشفى الصغيرة بينما صلّى الكاثوليك من أجل البابا. الصورة: فاتيكان ميديا / فاتيكان نيوز.'}, 'fr': {'date': '13 octobre 2026', 'title1': "L'opération du poumon du pape Léon XIV s'est déroulée avec succès", 'alt': 'Le pape Léon XIV priant au tombeau de saint Charbel à Annaya', 'credit1': "Le Saint-Siège indique que l'opération s'est déroulée avec succès, sans complications, et que le pape Léon a regagné sa chambre. Photo : Vatican Media / Vatican News.", 'title2': 'Les catholiques prient pour le pape Léon à Gemelli', 'credit2': "Le cardinal Baldassarre Reina a présidé le chapelet du soir dans la chapelle de l'hôpital tandis que les catholiques priaient pour le pape. Photo : Vatican Media / Vatican News."}, 'es': {'date': '13 de octubre de 2026', 'title1': 'La cirugía de pulmón del papa León XIV se completó con éxito', 'alt': 'El papa León XIV ora ante la tumba de san Charbel en Annaya', 'credit1': 'La Santa Sede afirma que la operación fue un éxito, sin complicaciones, y que el papa León ha vuelto a su habitación. Foto: Vatican Media / Vatican News.', 'title2': 'Los católicos rezan por el papa León en Gemelli', 'credit2': 'El cardenal Baldassarre Reina presidió el rosario de la tarde en la capilla del hospital mientras los católicos rezaban por el Papa. Foto: Vatican Media / Vatican News.'}, 'pt': {'date': '13 de outubro de 2026', 'title1': 'Cirurgia no pulmão do papa Leão XIV concluída com sucesso', 'alt': 'O papa Leão XIV rezando junto ao túmulo de São Charbel em Annaya', 'credit1': 'A Santa Sé afirma que a operação foi bem-sucedida, sem complicações, e que o papa Leão voltou ao seu quarto. Foto: Vatican Media / Vatican News.', 'title2': 'Católicos rezam pelo papa Leão no Gemelli', 'credit2': 'O cardeal Baldassarre Reina conduziu o terço da noite na capela do hospital enquanto os católicos rezavam pelo Papa. Foto: Vatican Media / Vatican News.'}, 'it': {'date': '13 ottobre 2026', 'title1': "L'intervento al polmone di papa Leone XIV è riuscito con successo", 'alt': 'Papa Leone XIV in preghiera alla tomba di san Charbel ad Annaya', 'credit1': "La Santa Sede riferisce che l'operazione è riuscita senza complicazioni e che papa Leone è tornato nella sua stanza. Foto: Vatican Media / Vatican News.", 'title2': 'I cattolici pregano per papa Leone al Gemelli', 'credit2': "Il cardinale Baldassarre Reina ha guidato il rosario serale nella cappella dell'ospedale mentre i cattolici pregavano per il Papa. Foto: Vatican Media / Vatican News."}, 'de': {'date': '13. Oktober 2026', 'title1': 'Lungenoperation von Papst Leo XIV. erfolgreich abgeschlossen', 'alt': 'Papst Leo XIV. betet am Grab des heiligen Charbel in Annaya', 'credit1': 'Der Heilige Stuhl erklärt, die Operation sei erfolgreich und ohne Komplikationen verlaufen, und Papst Leo sei in sein Zimmer zurückgekehrt. Foto: Vatican Media / Vatican News.', 'title2': 'Katholiken beten für Papst Leo in Gemelli', 'credit2': 'Kardinal Baldassarre Reina leitete den abendlichen Rosenkranz in der Krankenhauskapelle, während Katholiken für den Papst beteten. Foto: Vatican Media / Vatican News.'}, 'pl': {'date': '13 października 2026', 'title1': 'Operacja płuca papieża Leona XIV zakończona sukcesem', 'alt': 'Papież Leon XIV modlący się przy grobie św. Charbela w Annaya', 'credit1': 'Stolica Apostolska informuje, że operacja zakończyła się sukcesem bez powikłań, a papież Leon wrócił do swojego pokoju. Zdjęcie: Vatican Media / Vatican News.', 'title2': 'Katolicy modlą się za papieża Leona w Gemelli', 'credit2': 'Kardynał Baldassarre Reina przewodniczył wieczornemu różańcowi w kaplicy szpitalnej, gdy katolicy modlili się za papieża. Zdjęcie: Vatican Media / Vatican News.'}, 'ru': {'date': '13 октября 2026 г.', 'title1': 'Операция на лёгком Папы Льва XIV прошла успешно', 'alt': 'Папа Лев XIV молится у гробницы святого Шарбеля в Аннайе', 'credit1': 'Святой Престол сообщает, что операция прошла успешно, без осложнений, и Папа Лев вернулся в свою палату. Фото: Vatican Media / Vatican News.', 'title2': 'Католики молятся за Папу Льва в Джемелли', 'credit2': 'Кардинал Бальдассарре Рейна возглавил вечерний розарий в больничной часовне, пока католики молились за Папу. Фото: Vatican Media / Vatican News.'}, 'hi': {'date': '13 अक्टूबर 2026', 'title1': 'पोप लियो XIV के फेफड़े का ऑपरेशन सफलतापूर्वक पूरा हुआ', 'alt': 'पोप लियो XIV अन्नाया में संत शारबेल की कब्र पर प्रार्थना करते हुए', 'credit1': 'पवित्र सिंहासन के अनुसार ऑपरेशन बिना किसी जटिलता के सफल रहा और पोप लियो अपने कमरे में लौट आए हैं। फोटो: Vatican Media / Vatican News.', 'title2': 'कैथोलिक जेमेली में पोप लियो के लिए प्रार्थना कर रहे हैं', 'credit2': 'कार्डिनल बाल्डासारे रेइना ने अस्पताल की चैपल में सांझ की रोज़री प्रार्थना का नेतृत्व किया, जबकि कैथोलिक पोप के लिए प्रार्थना कर रहे थे। फोटो: Vatican Media / Vatican News.'}, 'th': {'date': '13 ตุลาคม ค.ศ. 2026', 'title1': 'การผ่าตัดปอดของสมเด็จพระสันตะปาปาลีโอที่ 14 สำเร็จลุล่วงด้วยดี', 'alt': 'สมเด็จพระสันตะปาปาลีโอที่ 14 กำลังอธิษฐานที่หลุมศพนักบุญชาร์เบลในอันนายา', 'credit1': 'สำนักวาติกันระบุว่าการผ่าตัดสำเร็จโดยไม่มีภาวะแทรกซ้อน และสมเด็จพระสันตะปาปาลีโอได้กลับถึงห้องพักแล้ว ภาพ: Vatican Media / Vatican News.', 'title2': 'ชาวคาทอลิกอธิษฐานเพื่อสมเด็จพระสันตะปาปาลีโอที่เจเมลลี', 'credit2': 'พระคาร์ดินัลบัลดัสซาร์เร เรอินา เป็นประธานสวดลูกประคำยามเย็นที่โบสถ์น้อยในโรงพยาบาล ขณะที่ชาวคาทอลิกอธิษฐานเพื่อสมเด็จพระสันตะปาปา ภาพ: Vatican Media / Vatican News.'}}
ROWS = [
    ('./news#pope-leo-gemelli-prayer-2026-10-13', 'title1', 'credit1'),
    ('./news#pope-leo-rosary-announcement-2026-10-13', 'title2', 'credit2'),
]

def outputs(root=ROOT):
    contract = json.loads((root / 'locales/en/home-bindings.json').read_text())
    raw = (root / 'index.html').read_bytes()
    soup = BeautifulSoup(raw, 'html.parser')
    if soup.select_one('#latest-news') is None:
        raise ValueError('latest-news section absent')
    removed = set(REMOVED)
    new_keys = set(KEYS.values())
    bindings = []
    for old in contract['bindings']:
        if old['key'] in removed or old['key'] in new_keys:
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
    for href, title_slot, credit_slot in ROWS:
        anchors = soup.select(f'a.home-news-row[href="{href}"]')
        if len(anchors) != 1:
            raise ValueError('Home news row missing ' + href)
        row = anchors[0]
        img = row.select_one('img')
        if img is None or img.get('alt') != EN['alt']:
            raise ValueError('Row image alt mismatch ' + href)
        bindings.append({'key': KEYS['alt'], 'selector': selector(img), 'source': EN['alt'], 'kind': 'attribute', 'attribute': 'alt'})
        meta = row.select_one('.home-news-meta')
        if meta is None or meta.get_text(strip=True) != EN['date']:
            raise ValueError('Row date mismatch ' + href)
        bindings.append({'key': KEYS['date'], 'selector': selector(meta), 'source': EN['date'], 'kind': 'text', 'nodeIndex': 0})
        title = row.select_one('.home-news-title')
        if title is None or title.get_text(strip=True) != EN[title_slot]:
            raise ValueError('Row title mismatch ' + href)
        bindings.append({'key': KEYS[title_slot], 'selector': selector(title), 'source': EN[title_slot], 'kind': 'text', 'nodeIndex': 0})
        credit = row.select_one('.home-news-credit')
        if credit is None or credit.get_text(strip=True) != EN[credit_slot]:
            raise ValueError('Row credit mismatch ' + href)
        bindings.append({'key': KEYS[credit_slot], 'selector': selector(credit), 'source': EN[credit_slot], 'kind': 'text', 'nodeIndex': 0})
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
                raise SystemExit('Pope home news bindings stale')
        else:
            path.write_text(text)
    print('Pope home news bindings checked' if a.check else 'Pope home news bindings refreshed')
