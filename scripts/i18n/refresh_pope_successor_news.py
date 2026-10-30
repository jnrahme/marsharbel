"""Rebind the October 15 Pope Leo successor card: 'Pope Leo resumes work as recovery
progresses normally' (afternoon Vatican News bulletin, pope-leo-s-postoperative-recovery-
progressing-normally.html). Same anchor, same date (October 15), same context photo and
rights; Aoun/LBC paragraph and sources kept. News contract EN+AR, home contract EN + 10
locale copies. Executor only: python3 scripts/i18n/refresh_pope_successor_news.py [--check]
"""
import argparse, hashlib, json
from pathlib import Path
from bs4 import BeautifulSoup
ROOT = Path(__file__).resolve().parents[2]

T_KEY = 'news.latest-news.pope-leo-has-a-good-second-night-at-gemelli'
S_KEY = 'news.latest-news.the-holy-see-press-office-says-pope-leo-xiv-had-a-good-secon'
V_KEY = 'news.latest-news.vatican-news-second-night-recovery-update-october-15-2026'
EN = {
    T_KEY: 'Pope Leo resumes work as recovery progresses normally',
    S_KEY: "The Holy See Press Office says Pope Leo XIV resumed his work on October 15 as his postoperative recovery progresses normally. Morning routine checks yielded normal results and the chest X-ray showed good recovery of the lung that underwent surgery; he carried out his daily activities independently, and his physiotherapy included a full range of physical activities. He concelebrated Mass in a room prepared for him on the hospital's 10th floor, and in the afternoon met the Substitute for General Affairs, Archbishop Paolo Rudelli.",
    V_KEY: "Vatican News: Pope Leo's postoperative recovery 'progressing normally' (October 15, 2026)",
}
AR = {
    T_KEY: 'البابا لاوُن يستأنف عمله وتعافيه يتقدم بشكل طبيعي',
    S_KEY: 'قال المكتب الصحفي للكرسي الرسولي إن البابا لاوُن الرابع عشر استأنف عمله في 15 تشرين الأول بينما يتقدم تعافيه بعد الجراحة بشكل طبيعي. وأظهرت الفحوص الروتينية الصباحية نتائج طبيعية، وبيّن تصوير الصدر بالأشعة السينية تعافيًا جيدًا للرئة التي خضعت للجراحة؛ وقام بأنشطته اليومية باستقلالية، وتضمّنت جلسة علاجه الطبيعي مجموعة كاملة من الأنشطة البدنية. وشارك في القداس في غرفة أُعدّت له في الطابق العاشر من المستشفى، والتقى بعد الظهر رئيس الأساقفة باولو روديلي، المعاون للشؤون العامة.',
    V_KEY: 'Vatican News: تعافي البابا لاوُن بعد الجراحة «يتقدم بشكل طبيعي» (15 تشرين الأول 2026)',
}
HT_KEY = 'home.latest-news.pope-leo-has-a-good-second-night-at-gemelli'
HC_KEY = 'home.latest-news.the-holy-see-says-pope-leo-had-a-good-second-hospital-night'
HOME_EN = {
    HT_KEY: EN[T_KEY],
    HC_KEY: 'The Holy See says Pope Leo resumed work on October 15 as his postoperative recovery progresses normally. Context photo: Gemelli Hospital, Rome. Photo: Blackcat, Wikimedia Commons, CC BY-SA 3.0 IT; resized to WebP.',
}
HOME_TR = {
 'ar': ('البابا لاوُن يستأنف عمله وتعافيه يتقدم بشكل طبيعي', 'الكرسي الرسولي: البابا لاوُن استأنف عمله في 15 تشرين الأول بينما يتقدم تعافيه بعد الجراحة بشكل طبيعي. صورة سياقية: مستشفى جيميلي، روما. الصورة: Blackcat، ويكيميديا كومنز، CC BY-SA 3.0 IT؛ تغيير الحجم وتحويل إلى WebP.'),
 'fr': ('Le pape Léon reprend son travail tandis que sa convalescence progresse normalement', "Le Saint-Siège indique que le pape Léon a repris son travail le 15 octobre tandis que sa convalescence postopératoire progresse normalement. Photo d'illustration : hôpital Gemelli, Rome. Photo : Blackcat, Wikimedia Commons, CC BY-SA 3.0 IT ; redimensionnée en WebP."),
 'es': ('El papa León retoma su trabajo mientras su recuperación progresa con normalidad', 'La Santa Sede informa de que el papa León retomó su trabajo el 15 de octubre mientras su recuperación postoperatoria progresa con normalidad. Foto de contexto: Hospital Gemelli, Roma. Foto: Blackcat, Wikimedia Commons, CC BY-SA 3.0 IT; redimensionada a WebP.'),
 'pt': ('O papa Leão retoma o trabalho enquanto a sua recuperação progride normalmente', 'A Santa Sé informa que o papa Leão retomou o trabalho a 15 de outubro, com a sua recuperação pós-operatória a progredir normalmente. Foto de contexto: Hospital Gemelli, Roma. Foto: Blackcat, Wikimedia Commons, CC BY-SA 3.0 IT; redimensionada para WebP.'),
 'it': ('Papa Leone riprende il lavoro mentre la convalescenza procede normalmente', 'La Santa Sede riferisce che papa Leone ha ripreso il lavoro il 15 ottobre, con la convalescenza postoperatoria che procede normalmente. Foto di contesto: Policlinico Gemelli, Roma. Foto: Blackcat, Wikimedia Commons, CC BY-SA 3.0 IT; ridimensionata in WebP.'),
 'de': ('Papst Leo nimmt die Arbeit wieder auf, seine Genesung verläuft weiter normal', 'Der Heilige Stuhl teilt mit, dass Papst Leo am 15. Oktober die Arbeit wieder aufgenommen hat und seine postoperative Genesung normal verläuft. Kontextfoto: Gemelli-Krankenhaus, Rom. Foto: Blackcat, Wikimedia Commons, CC BY-SA 3.0 IT; in WebP verkleinert.'),
 'pl': ('Papież Leon wraca do pracy, a jego rekonwalescencja przebiega prawidłowo', 'Stolica Apostolska informuje, że papież Leon wznowił pracę 15 października, a jego pooperacyjna rekonwalescencja przebiega prawidłowo. Zdjęcie poglądowe: szpital Gemelli, Rzym. Zdjęcie: Blackcat, Wikimedia Commons, CC BY-SA 3.0 IT; zmniejszone do WebP.'),
 'ru': ('Папа Лев возобновил работу, его восстановление проходит нормально', 'Святой Престол сообщает, что Папа Лев возобновил работу 15 октября, его послеоперационное восстановление проходит нормально. Иллюстративное фото: больница Джемелли, Рим. Фото: Blackcat, Wikimedia Commons, CC BY-SA 3.0 IT; уменьшено до WebP.'),
 'hi': ('पोप लियो ने काम फिर से शुरू किया, उनका स्वास्थ्य लाभ सामान्य रूप से बढ़ रहा है', 'होली सी का कहना है कि पोप लियो ने 15 अक्टूबर को काम फिर से शुरू किया और उनकी सर्जरी के बाद की रिकवरी सामान्य रूप से बढ़ रही है। संदर्भ चित्र: जेमेली अस्पताल, रोम। फ़ोटो: Blackcat, विकिमीडिया कॉमन्स, CC BY-SA 3.0 IT; WebP में आकार बदला गया।'),
 'th': ('สมเด็จพระสันตะปาปาลีโอทรงกลับมาทำงาน อาการฟื้นตัวเป็นไปตามปกติ', 'สันตะสำนักแจ้งว่าสมเด็จพระสันตะปาปาลีโอทรงกลับมาทำงานในวันที่ 15 ตุลาคม อาการฟื้นตัวหลังผ่าตัดเป็นไปตามปกติ ภาพประกอบบริบท: โรงพยาบาลเจเมลลี กรุงโรม ภาพ: Blackcat, วิกิมีเดียคอมมอนส์, CC BY-SA 3.0 IT; ปรับขนาดเป็น WebP'),
}

def value_of(n, b):
    if b['kind'] == 'attribute':
        return n.get(b['attribute'])
    return ' '.join(str(n.contents[b['nodeIndex']]).split())

def news_outputs(root=ROOT):
    contract = json.loads((root / 'locales/en/news-master-bindings.json').read_text())
    raw = (root / 'news.html').read_bytes()
    soup = BeautifulSoup(raw, 'html.parser')
    seen = set()
    for b in contract['bindings']:
        if b['key'] in EN:
            nodes = soup.select(b['selector'])
            if len(nodes) != 1:
                raise ValueError('News binding selector drift ' + b['key'])
            b['source'] = EN[b['key']]
            if value_of(nodes[0], b) != b['source']:
                raise ValueError('News value mismatch - run build_news_desk first: ' + b['key'])
            seen.add(b['key'])
    if seen != set(EN):
        raise ValueError('Expected all three news keys, got ' + str(seen))
    copy = json.loads((root / 'locales/en/news-master-copy.json').read_text())
    local = json.loads((root / 'locales/ar/news-master-copy.json').read_text())
    for key in EN:
        copy[key] = EN[key]; local[key] = AR[key]
    if set(local) != set(copy):
        raise ValueError('Arabic news keys differ from English')
    contract.update(messages=copy, masterSha256=hashlib.sha256(raw).hexdigest())
    return {root / 'locales/en/news-master-copy.json': copy,
            root / 'locales/ar/news-master-copy.json': local,
            root / 'locales/en/news-master-bindings.json': contract}

def home_outputs(root=ROOT):
    contract = json.loads((root / 'locales/en/home-bindings.json').read_text())
    raw = (root / 'index.html').read_bytes()
    soup = BeautifulSoup(raw, 'html.parser')
    seen = set()
    for b in contract['bindings']:
        if b['key'] in HOME_EN:
            nodes = soup.select(b['selector'])
            if len(nodes) != 1:
                raise ValueError('Home binding selector drift ' + b['key'])
            b['source'] = HOME_EN[b['key']]
            if value_of(nodes[0], b) != b['source']:
                raise ValueError('Home value mismatch - run build_news_desk first: ' + b['key'])
            seen.add(b['key'])
    if seen != set(HOME_EN):
        raise ValueError('Expected both home keys, got ' + str(seen))
    result = {}
    copy = json.loads((root / 'locales/en/home-copy.json').read_text())
    for key in HOME_EN:
        copy[key] = HOME_EN[key]
    result[root / 'locales/en/home-copy.json'] = copy
    for code, (title, credit) in HOME_TR.items():
        path = root / f'locales/{code}/home-copy.json'
        catalog = json.loads(path.read_text())
        catalog[HT_KEY] = title; catalog[HC_KEY] = credit
        result[path] = catalog
    contract.update(messages=copy, masterSha256=hashlib.sha256(raw).hexdigest())
    result[root / 'locales/en/home-bindings.json'] = contract
    return result

def outputs(root=ROOT):
    merged = news_outputs(root)
    merged.update(home_outputs(root))
    return {p: json.dumps(j, ensure_ascii=False, indent=2) + '\n' for p, j in merged.items()}

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--check', action='store_true')
    a = p.parse_args()
    for path, text in outputs().items():
        if a.check:
            if path.read_text() != text:
                raise SystemExit('Pope successor bindings stale: ' + str(path))
        else:
            path.write_text(text)
    print('Pope successor bindings checked' if a.check else 'Pope successor bindings refreshed')
