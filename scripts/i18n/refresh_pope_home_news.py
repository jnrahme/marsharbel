"""Rebind the October 13 pope home-news rows; preserve every other home source."""
import argparse, hashlib, json, sys
from pathlib import Path
from bs4 import BeautifulSoup, NavigableString
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from i18n.refresh_film_home_bindings import selector

REMOVED = ['home.accessibility.pope-leo-xiv-praying-at-the-tomb-of-saint-charbel-in-annaya', 'home.latest-news.september-26-2026', 'home.latest-news.prayer-walk-to-annaya-brings-prayers-for-south-lebanon', 'home.latest-news.annaya-monastery-entrance-photo-llew-cc-by-sa-4', 'home.latest-news.october-2-2026', 'home.latest-news.kfifan-receives-relics-of-its-patron-saints-from-rome', 'home.latest-news.kfifan-monastery-2012-venue-context-not-the-relic-reception', 'home.accessibility.a-pilgrim-touching-the-statue-of-saint-charbel-at', 'home.accessibility.the-stone-kfifan-monastery-buildings-and-courtyard-in-lebanon', 'home.latest-news.pope-leo-xiv-s-lung-surgery-completed-successfully', 'home.latest-news.the-holy-see-says-the-operation-was-successful-with-no-compl', 'home.latest-news.pope-leo-has-a-calm-first-night-after-lung-surgery', 'home.latest-news.the-holy-see-says-pope-leo-had-a-calm-first-night-after-surg']
KEYS = {'date1': 'home.latest-news.october-14-2026', 'date2': 'home.latest-news.october-13-2026', 'title1': 'home.latest-news.pope-leo-s-recovery-is-progressing-normally', 'credit1': 'home.latest-news.the-holy-see-says-postoperative-tests-are-within-the-expecte', 'title2': 'home.latest-news.catholics-pray-for-pope-leo-at-gemelli', 'credit2': 'home.latest-news.cardinal-baldassarre-reina-led-the-evening-rosary-in-the-hos', 'alt1': 'home.accessibility.gemelli-hospital-in-rome-seen-from-its-forecourt', 'alt2': 'home.accessibility.interior-of-the-sacro-cuore-church-at-gemelli-hospital'}
EN = {'date1': 'October 14, 2026', 'date2': 'October 13, 2026', 'title1': "Pope Leo's recovery is progressing normally", 'credit1': 'The Holy See says postoperative tests are within the expected range. Pope Leo has begun walking in his room and has resumed eating normally. Context photo: Gemelli Hospital, Rome. Photo: Blackcat, Wikimedia Commons, CC BY-SA 3.0; resized to WebP.', 'title2': 'Catholics pray for Pope Leo at Gemelli', 'credit2': 'Cardinal Baldassarre Reina led the evening Rosary in the hospital chapel as Catholics prayed for the Pope. Context photo: the Sacro Cuore church at Gemelli, not the Rosary itself. Photo: Pufui PcPifpef, Wikimedia Commons, CC BY-SA 4.0; resized to WebP.', 'alt1': 'Gemelli Hospital in Rome seen from its forecourt', 'alt2': 'Interior of the Sacro Cuore church at Gemelli Hospital in Rome, looking toward the altar'}
TRANSLATIONS = {'ar': {'date1': '14 تشرين الأول 2026', 'date2': '13 تشرين الأول 2026', 'title1': 'تعافي البابا لاوُن يسير بشكل طبيعي', 'credit1': 'الكرسي الرسولي: الفحوصات اللاحقة للعملية ضمن النطاق المتوقع. البابا لاوُن بدأ المشي في غرفته واستأنف تناول الطعام بشكل طبيعي. صورة سياقية: مستشفى جيميلي، روما. الصورة: Blackcat، ويكيميديا كومنز، CC BY-SA 3.0؛ تغيير الحجم وتحويل إلى WebP.', 'title2': 'الكاثوليك يصلّون من أجل البابا لاوُن في جيميلي', 'credit2': 'الكاردينال بالداسارّي رينا ترأس صلاة المسبحة المسائية في كنيسة المستشفى الصغيرة بينما صلّى الكاثوليك من أجل البابا. صورة سياقية: كنيسة القلب الأقدس في جيميلي، وليست صورة المسبحة نفسها. الصورة: Pufui PcPifpef، ويكيميديا كومنز، CC BY-SA 4.0؛ تغيير الحجم وتحويل إلى WebP.', 'alt1': 'مستشفى جيميلي في روما من ساحته الأمامية', 'alt2': 'داخل كنيسة القلب الأقدس في مستشفى جيميلي في روما، بالنظر نحو المذبح'}, 'fr': {'date1': '14 octobre 2026', 'date2': '13 octobre 2026', 'title1': 'Le rétablissement du pape Léon progresse normalement', 'credit1': "Le Saint-Siège indique que les examens postopératoires sont dans la fourchette attendue. Le pape Léon a commencé à marcher dans sa chambre et s'est remis à s'alimenter normalement. Photo d'illustration : hôpital Gemelli, Rome. Photo : Blackcat, Wikimedia Commons, CC BY-SA 3.0 ; redimensionnée en WebP.", 'title2': 'Les catholiques prient pour le pape Léon à Gemelli', 'credit2': "Le cardinal Baldassarre Reina a présidé le chapelet du soir dans la chapelle de l'hôpital tandis que les catholiques priaient pour le pape. Photo d'illustration : l'église du Sacré-Cœur à Gemelli, et non le chapelet lui-même. Photo : Pufui PcPifpef, Wikimedia Commons, CC BY-SA 4.0 ; redimensionnée en WebP.", 'alt1': "L'hôpital Gemelli à Rome, vu depuis son parvis", 'alt2': "Intérieur de l'église du Sacré-Cœur de l'hôpital Gemelli à Rome, vue vers l'autel"}, 'es': {'date1': '14 de octubre de 2026', 'date2': '13 de octubre de 2026', 'title1': 'La recuperación del papa León avanza con normalidad', 'credit1': 'La Santa Sede informa de que las pruebas postoperatorias están dentro del rango esperado. El papa León ha comenzado a caminar en su habitación y ha retomado la alimentación normal. Foto de contexto: Hospital Gemelli, Roma. Foto: Blackcat, Wikimedia Commons, CC BY-SA 3.0; redimensionada a WebP.', 'title2': 'Los católicos rezan por el papa León en Gemelli', 'credit2': 'El cardenal Baldassarre Reina presidió el rosario de la tarde en la capilla del hospital mientras los católicos rezaban por el papa. Foto de contexto: la iglesia del Sagrado Corazón en el Gemelli, no el rosario en sí. Foto: Pufui PcPifpef, Wikimedia Commons, CC BY-SA 4.0; redimensionada a WebP.', 'alt1': 'El Hospital Gemelli de Roma visto desde su explanada', 'alt2': 'Interior de la iglesia del Sagrado Corazón del Hospital Gemelli de Roma, mirando hacia el altar'}, 'pt': {'date1': '14 de outubro de 2026', 'date2': '13 de outubro de 2026', 'title1': 'A recuperação do papa Leão está a progredir normalmente', 'credit1': 'A Santa Sé informa que os exames pós-operatórios estão dentro do intervalo esperado. O papa Leão começou a caminhar no seu quarto e retomou a alimentação normal. Foto de contexto: Hospital Gemelli, Roma. Foto: Blackcat, Wikimedia Commons, CC BY-SA 3.0; redimensionada para WebP.', 'title2': 'Católicos rezam pelo papa Leão no Gemelli', 'credit2': 'O cardeal Baldassarre Reina presidiu o terço da noite na capela do hospital enquanto os católicos rezavam pelo Papa. Foto de contexto: a igreja do Sagrado Coração no Gemelli, não o próprio terço. Foto: Pufui PcPifpef, Wikimedia Commons, CC BY-SA 4.0; redimensionada para WebP.', 'alt1': 'O Hospital Gemelli, em Roma, visto do seu largo', 'alt2': 'Interior da igreja do Sagrado Coração no Hospital Gemelli, em Roma, olhando para o altar'}, 'it': {'date1': '14 ottobre 2026', 'date2': '13 ottobre 2026', 'title1': 'Il recupero di papa Leone procede normalmente', 'credit1': 'La Santa Sede riferisce che gli esami postoperatori sono nella fascia prevista. Papa Leone ha iniziato a camminare nella sua stanza e ha ripreso ad alimentarsi normalmente. Foto di contesto: Policlinico Gemelli, Roma. Foto: Blackcat, Wikimedia Commons, CC BY-SA 3.0; ridimensionata in WebP.', 'title2': 'I cattolici pregano per papa Leone al Gemelli', 'credit2': "Il cardinale Baldassarre Reina ha guidato il Rosario serale nella cappella dell'ospedale mentre i cattolici pregavano per il Papa. Foto di contesto: la chiesa del Sacro Cuore al Gemelli, non il Rosario stesso. Foto: Pufui PcPifpef, Wikimedia Commons, CC BY-SA 4.0; ridimensionata in WebP.", 'alt1': 'Il Policlinico Gemelli di Roma visto dal piazzale', 'alt2': "Interno della chiesa del Sacro Cuore al Policlinico Gemelli di Roma, verso l'altare"}, 'de': {'date1': '14. Oktober 2026', 'date2': '13. Oktober 2026', 'title1': 'Die Genesung von Papst Leo macht normale Fortschritte', 'credit1': 'Der Heilige Stuhl teilt mit, die postoperativen Untersuchungen lägen im erwarteten Bereich. Papst Leo hat begonnen, in seinem Zimmer zu gehen, und nimmt wieder normal Nahrung zu sich. Kontextfoto: Gemelli-Krankenhaus, Rom. Foto: Blackcat, Wikimedia Commons, CC BY-SA 3.0; in WebP verkleinert.', 'title2': 'Katholiken beten für Papst Leo in Gemelli', 'credit2': 'Kardinal Baldassarre Reina leitete den abendlichen Rosenkranz in der Krankenhauskapelle, während Katholiken für den Papst beteten. Kontextfoto: die Herz-Jesu-Kirche am Gemelli, nicht der Rosenkranz selbst. Foto: Pufui PcPifpef, Wikimedia Commons, CC BY-SA 4.0; in WebP verkleinert.', 'alt1': 'Das Gemelli-Krankenhaus in Rom, vom Vorplatz aus gesehen', 'alt2': 'Innenraum der Herz-Jesu-Kirche am Gemelli-Krankenhaus in Rom mit Blick zum Altar'}, 'pl': {'date1': '14 października 2026', 'date2': '13 października 2026', 'title1': 'Rekonwalescencja papieża Leona przebiega prawidłowo', 'credit1': 'Stolica Apostolska informuje, że badania pooperacyjne mieszczą się w oczekiwanym zakresie. Papież Leon zaczął chodzić po swoim pokoju i wrócił do normalnego odżywiania. Zdjęcie poglądowe: szpital Gemelli, Rzym. Zdjęcie: Blackcat, Wikimedia Commons, CC BY-SA 3.0; zmniejszone do WebP.', 'title2': 'Katolicy modlą się za papieża Leona w Gemelli', 'credit2': 'Kardynał Baldassarre Reina przewodniczył wieczornemu różańcowi w kaplicy szpitala, gdy katolicy modlili się za papieża. Zdjęcie poglądowe: kościół Najświętszego Serca w Gemelli, nie sam różaniec. Zdjęcie: Pufui PcPifpef, Wikimedia Commons, CC BY-SA 4.0; zmniejszone do WebP.', 'alt1': 'Szpital Gemelli w Rzymie widziany z dziedzińca', 'alt2': 'Wnętrze kościoła Najświętszego Serca w szpitalu Gemelli w Rzymie, widok w stronę ołtarza'}, 'ru': {'date1': '14 октября 2026 г.', 'date2': '13 октября 2026 г.', 'title1': 'Восстановление папы Льва проходит нормально', 'credit1': 'Святой Престол сообщает, что послеоперационные обследования находятся в ожидаемых пределах. Папа Лев начал ходить по своей палате и вернулся к обычному питанию. Иллюстративное фото: больница Джемелли, Рим. Фото: Blackcat, Wikimedia Commons, CC BY-SA 3.0; уменьшено до WebP.', 'title2': 'Католики молятся за Папу Льва в Джемелли', 'credit2': 'Кардинал Бальдассарре Рейна возглавил вечерний розарий в больничной часовне, пока католики молились за папу. Иллюстративное фото: церковь Святейшего Сердца в Джемелли, а не сам розарий. Фото: Pufui PcPifpef, Wikimedia Commons, CC BY-SA 4.0; уменьшено до WebP.', 'alt1': 'Больница Джемелли в Риме, вид с площади', 'alt2': 'Интерьер церкви Святейшего Сердца в больнице Джемелли в Риме, вид на алтарь'}, 'hi': {'date1': '14 अक्टूबर 2026', 'date2': '13 अक्टूबर 2026', 'title1': 'पोप लियो की रिकवरी सामान्य रूप से आगे बढ़ रही है', 'credit1': 'होली सी का कहना है कि ऑपरेशन के बाद के परीक्षण अपेक्षित सीमा के भीतर हैं। पोप लियो ने अपने कमरे में चलना शुरू कर दिया है और सामान्य रूप से भोजन लेने लगे हैं। संदर्भ चित्र: जेमेली अस्पताल, रोम। फ़ोटो: Blackcat, विकिमीडिया कॉमन्स, CC BY-SA 3.0; WebP में आकार बदला गया।', 'title2': 'कैथोलिक जेमेली में पोप लियो के लिए प्रार्थना कर रहे हैं', 'credit2': 'कार्डिनल बाल्डास्सारे रेइना ने अस्पताल के प्रार्थनालय में संध्या रोज़री की अगुवाई की, जबकि कैथोलिक पोप के लिए प्रार्थना कर रहे थे। संदर्भ चित्र: जेमेली का पवित्र हृदय गिरजाघर, रोज़री का दृश्य नहीं। फ़ोटो: Pufui PcPifpef, विकिमीडिया कॉमन्स, CC BY-SA 4.0; WebP में आकार बदला गया।', 'alt1': 'रोम का जेमेली अस्पताल, अपने अग्रांगण से देखा गया', 'alt2': 'रोम के जेमेली अस्पताल में पवित्र हृदय गिरजाघर का अंदरूनी भाग, वेदी की ओर दृश्य'}, 'th': {'date1': '14 ตุลาคม ค.ศ. 2026', 'date2': '13 ตุลาคม ค.ศ. 2026', 'title1': 'การฟื้นตัวของสมเด็จพระสันตะปาปาลีโอเป็นไปตามปกติ', 'credit1': 'สันตะสำนักแจ้งว่าผลตรวจหลังการผ่าตัดอยู่ในช่วงที่คาดไว้ สมเด็จพระสันตะปาปาลีโอทรงเริ่มเดินในห้องพักและทรงรับประทานอาหารตามปกติแล้ว ภาพประกอบบริบท: โรงพยาบาลเจเมลลี กรุงโรม ภาพ: Blackcat, วิกิมีเดียคอมมอนส์, CC BY-SA 3.0; ปรับขนาดเป็น WebP', 'title2': 'ชาวคาทอลิกอธิษฐานเพื่อสมเด็จพระสันตะปาปาลีโอที่เจเมลลี', 'credit2': 'พระคาร์ดินัลบัลดาสซาร์เร เรอีนา เป็นประธานสวดสายประคำภาคค่ำในโบสถ์น้อยของโรงพยาบาล ขณะที่ชาวคาทอลิกอธิษฐานเพื่อสมเด็จพระสันตะปาปา ภาพประกอบบริบท: โบสถ์พระหฤทัยที่เจเมลลี ไม่ใช่ภาพการสวดสายประคำ ภาพ: Pufui PcPifpef, วิกิมีเดียคอมมอนส์, CC BY-SA 4.0; ปรับขนาดเป็น WebP', 'alt1': 'โรงพยาบาลเจเมลลีในกรุงโรม มองจากลานด้านหน้า', 'alt2': 'ภายในโบสถ์พระหฤทัยที่โรงพยาบาลเจเมลลีในกรุงโรม มองไปทางพระแท่น'}}
ROWS = [
    ('./news#pope-leo-gemelli-prayer-2026-10-13', 'date1', 'title1', 'credit1', 'alt1'),
    ('./news#pope-leo-rosary-announcement-2026-10-13', 'date2', 'title2', 'credit2', 'alt2'),
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
    for href, date_slot, title_slot, credit_slot, alt_slot in ROWS:
        anchors = soup.select(f'a.home-news-row[href="{href}"]')
        if len(anchors) != 1:
            raise ValueError('Home news row missing ' + href)
        row = anchors[0]
        img = row.select_one('img')
        if img is None or img.get('alt') != EN[alt_slot]:
            raise ValueError('Row image alt mismatch ' + href)
        bindings.append({'key': KEYS[alt_slot], 'selector': selector(img), 'source': EN[alt_slot], 'kind': 'attribute', 'attribute': 'alt'})
        meta = row.select_one('.home-news-meta')
        if meta is None or meta.get_text(strip=True) != EN[date_slot]:
            raise ValueError('Row date mismatch ' + href)
        bindings.append({'key': KEYS[date_slot], 'selector': selector(meta), 'source': EN[date_slot], 'kind': 'text', 'nodeIndex': 0})
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
