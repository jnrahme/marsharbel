"""Rebind the October 15 cinema-dates-differ update (VOX October 21 sessions vs Cinemacity
October 22 opening): news rows + opening credit line (VOX link added) on news.html, and the
home film card dek + rollout value on index.html. Same-node updates keep their key names;
the VOX anchor is a different outlet, so its key is renamed; the credit-line layout change
adds bindings for the new Cinemacity anchor and separator. Executor only:
python3 scripts/i18n/refresh_cinema_home_news.py [--check]
"""
import argparse, hashlib, json, sys
from pathlib import Path
from bs4 import BeautifulSoup
ROOT = Path(__file__).resolve().parents[2]

TITLE_KEY = 'news.latest-news.mar-charbel-listed-for-october-22-opening-in-beirut'
ROWSUM_KEY = 'news.latest-news.cinemacity-beirut-souks-lists-october-22-as-the-opening-date'
PREMROW_KEY = 'news.latest-news.the-nmpro-and-mtv-feature-premiered-october-9-at-beirut-medi'
OLD_CINEMA_KEY = 'news.latest-news.cinemacity-beirut-opening-date-and-current-session-status'
VOX_KEY = 'news.latest-news.vox-city-centre-beirut-listed-october-21-sessions'
NEWCINEMA_KEY = 'news.latest-news.cinemacity-beirut-october-22-opening-listing-no-sessions'
LEB24_KEY = 'news.latest-news.lebanon24-october-5-report-arabic'
LEADMETA_KEY = 'news.saint-charbel-in-the-new.premiered-october-9-lebanese-cinema-release-planned-from-oct'
LEADDEK_KEY = 'news.charbel-premieres-in-bei.the-new-feature-film-premiered-october-9-in-beirut-the-leban'
LI7 = '#main-content > section:nth-of-type(3) > div:nth-of-type(1) > details:nth-of-type(1) > ul:nth-of-type(1) > li:nth-of-type(7)'

EN = {
    TITLE_KEY: 'Mar Charbel Cinema Dates Differ: VOX Lists October 21, Cinemacity October 22',
    ROWSUM_KEY: 'Cinema listings checked October 15: VOX City Centre Beirut lists October 21 sessions (Standard 7:00 and 7:30pm, GOLD 7:30pm; Arabic audio with English subtitles); Cinemacity Beirut lists an October 22 opening with no sessions yet. A listed session is a cinema listing, not a seat guarantee - check your cinema.',
    PREMROW_KEY: 'The NMPRO and MTV feature premiered October 9 at Beirut Media Zone; Lebanese cinema dates differ - VOX lists October 21 sessions, Cinemacity lists October 22. International release and streaming remain unconfirmed.',
    VOX_KEY: 'VOX City Centre Beirut: listed October 21 sessions',
    NEWCINEMA_KEY: 'Cinemacity Beirut: October 22 opening listing, no sessions scheduled',
    LEADMETA_KEY: 'Premiered October 9 · Cinema dates differ: VOX October 21, Cinemacity October 22 · 4 sources',
    LEADDEK_KEY: 'The new feature film premiered October 9 in Beirut. Cinema dates differ: VOX lists October 21 sessions, Cinemacity lists an October 22 opening with no sessions yet; international release and streaming remain unconfirmed.',
}
AR = {
    TITLE_KEY: 'مواعيد سينما مار شربل تختلف: فوكس يسرد 21 تشرين الأول وسينما سيتي 22 تشرين الأول',
    ROWSUM_KEY: 'تمت مراجعة لوائح السينما في 15 تشرين الأول: فوكس سيتي سنتر بيروت يسرد عروض 21 تشرين الأول (ستاندرد 7:00 و7:30 مساءً، وغولد 7:30 مساءً؛ بالصوت العربي مع ترجمة إنكليزية)؛ وسينما سيتي بيروت يسرد افتتاحًا في 22 تشرين الأول من دون عروض بعد. العرض المُدرج إدراج سينما وليس ضمانًا لمقعد - راجعوا سينماكم.',
    PREMROW_KEY: 'عُرض فيلم NMPRO وMTV لأول مرة في 9 تشرين الأول في Beirut Media Zone؛ وتختلف مواعيد السينما اللبنانية - فوكس يسرد عروض 21 تشرين الأول وسينما سيتي يسرد 22 تشرين الأول. ويبقى العرض الدولي والبث غير مؤكدين.',
    VOX_KEY: 'فوكس سيتي سنتر بيروت: عروض مسردة في 21 تشرين الأول',
    NEWCINEMA_KEY: 'سينما سيتي بيروت: إدراج افتتاح في 22 تشرين الأول من دون عروض مسجلة',
    LEADMETA_KEY: 'العرض الأول في 9 تشرين الأول · مواعيد السينما تختلف: فوكس 21 تشرين الأول، سينما سيتي 22 تشرين الأول · 4 مصادر',
    LEADDEK_KEY: 'عُرض الفيلم الروائي الجديد لأول مرة في 9 تشرين الأول في بيروت. تختلف مواعيد السينما: فوكس يسرد عروض 21 تشرين الأول وسينما سيتي يسرد افتتاحًا في 22 تشرين الأول من دون عروض بعد؛ ويبقى العرض الدولي والبث غير مؤكدين.',
}
REBIND = (TITLE_KEY, ROWSUM_KEY, PREMROW_KEY, LEADMETA_KEY, LEADDEK_KEY)

HOME_KEYS = ('home.latest-news.premiere.homeDek', 'home.latest-news.premiere.openingValue')
HOME_EN = {
    'home.latest-news.premiere.homeDek': 'The NMPRO and MTV feature has premiered at Beirut Media Zone. Cinema dates differ: VOX lists October 21 sessions, Cinemacity lists October 22; check individual cinemas for sessions.',
    'home.latest-news.premiere.openingValue': 'Planned from October 21-22, 2026',
}
HOME_TR = {
 'ar': ('أُقيم العرض الأول لفيلم NMPRO وMTV في Beirut Media Zone. تختلف مواعيد السينما: فوكس يسرد عروض 21 تشرين الأول وسينما سيتي يسرد 22 تشرين الأول؛ راجعوا كل سينما لمعرفة مواعيد الجلسات.', 'مقرر ابتداءً من 21-22 تشرين الأول 2026'),
 'fr': ('Le long métrage de NMPRO et MTV a été présenté en première au Beirut Media Zone. Les dates de cinéma diffèrent : VOX annonce des séances le 21 octobre, Cinemacity le 22 octobre ; consultez chaque cinéma pour les séances.', 'Prévue à partir des 21-22 octobre 2026'),
 'es': ('El largometraje de NMPRO y MTV se ha presentado en Beirut Media Zone. Las fechas de cine difieren: VOX anuncia sesiones el 21 de octubre y Cinemacity el 22 de octubre; consulte cada cine para ver las sesiones.', 'Previsto a partir del 21-22 de octubre de 2026'),
 'pt': ('O longa-metragem da NMPRO e da MTV estreou no Beirut Media Zone. As datas de cinema diferem: a VOX lista sessões a 21 de outubro e a Cinemacity a 22 de outubro; consulte cada cinema para as sessões.', 'Previsto a partir de 21-22 de outubro de 2026'),
 'it': ('Il lungometraggio di NMPRO e MTV è stato presentato in anteprima al Beirut Media Zone. Le date al cinema differiscono: VOX elenca proiezioni il 21 ottobre, Cinemacity il 22 ottobre; controllate i singoli cinema per le proiezioni.', 'Prevista dal 21-22 ottobre 2026'),
 'de': ('Der Spielfilm von NMPRO und MTV wurde in der Beirut Media Zone erstmals gezeigt. Die Kinotermine weichen voneinander ab: VOX listet Vorstellungen am 21. Oktober, Cinemacity am 22. Oktober; erkundigen Sie sich beim jeweiligen Kino nach Vorstellungen.', 'Geplant ab 21.-22. Oktober 2026'),
 'pl': ('Film fabularny NMPRO i MTV miał premierę w Beirut Media Zone. Daty kinowe różnią się: VOX podaje seanse 21 października, a Cinemacity 22 października; sprawdź seanse w poszczególnych kinach.', 'Planowane od 21-22 października 2026'),
 'ru': ('Премьера полнометражного фильма NMPRO и MTV состоялась в Beirut Media Zone. Даты показов различаются: VOX указывает сеансы 21 октября, Cinemacity — 22 октября; расписание сеансов уточняйте в каждом кинотеатре.', 'Запланировано с 21-22 октября 2026 года'),
 'hi': ('NMPRO और MTV की फ़ीचर फ़िल्म का प्रीमियर Beirut Media Zone में हो चुका है। सिनेमा की तारीख़ें अलग-अलग हैं: VOX 21 अक्टूबर के शो सूचीबद्ध करता है, Cinemacity 22 अक्टूबर; शो के लिए संबंधित सिनेमाघर से जाँच करें।', '21-22 अक्टूबर 2026 से शुरू करने की योजना'),
 'th': ('ภาพยนตร์ขนาดยาวของ NMPRO และ MTV เปิดตัวแล้วที่ Beirut Media Zone วันฉายในโรงภาพยนตร์แตกต่างกัน: VOX ระบุรอบฉาย 21 ตุลาคม Cinemacity ระบุ 22 ตุลาคม โปรดตรวจสอบรอบฉายกับโรงภาพยนตร์แต่ละแห่ง', 'กำหนดเริ่มตั้งแต่ 21-22 ตุลาคม 2026'),
}

def value_of(n, b):
    if b['kind'] == 'attribute':
        return n.get(b['attribute'])
    return ' '.join(str(n.contents[b['nodeIndex']]).split())

def news_outputs(root=ROOT):
    contract = json.loads((root / 'locales/en/news-master-bindings.json').read_text())
    raw = (root / 'news.html').read_bytes()
    soup = BeautifulSoup(raw, 'html.parser')
    bindings, seen = [], set()
    have_newcinema = have_sep7 = False
    for old in contract['bindings']:
        sel = old['selector']
        nodes = soup.select(sel)
        if len(nodes) != 1:
            raise ValueError('Binding selector drift ' + old['key'] + ' ' + sel)
        n = nodes[0]
        if old['key'] in REBIND:
            new = dict(old); new['source'] = EN[old['key']]
            if value_of(n, new) != new['source']:
                raise ValueError('Rebind value mismatch - run build_news_desk first: ' + old['key'])
            bindings.append(new); seen.add(old['key']); continue
        if old['key'] == OLD_CINEMA_KEY or (old['key'] == VOX_KEY and sel.endswith('li:nth-of-type(7) > a:nth-of-type(1)')):
            if not sel.endswith('li:nth-of-type(7) > a:nth-of-type(1)'):
                raise ValueError('Unexpected VOX binding location ' + sel)
            new = dict(old); new['key'] = VOX_KEY; new['source'] = EN[VOX_KEY]
            if value_of(n, new) != new['source']:
                raise ValueError('VOX anchor mismatch - run build_news_desk first')
            bindings.append(new); seen.add('vox'); continue
        if old['key'] == NEWCINEMA_KEY and sel.endswith('li:nth-of-type(7) > a:nth-of-type(2)'):
            if value_of(n, old) != EN[NEWCINEMA_KEY]:
                raise ValueError('New Cinemacity anchor mismatch')
            bindings.append(dict(old)); have_newcinema = True; continue
        if old['key'] == LEB24_KEY and sel.endswith('li:nth-of-type(7) > a:nth-of-type(2)'):
            new = dict(old); new['selector'] = LI7 + ' > a:nth-of-type(3)'
            nodes3 = soup.select(new['selector'])
            if len(nodes3) != 1 or value_of(nodes3[0], new) != new['source']:
                raise ValueError('Lebanon24 anchor did not move to position 3')
            bindings.append(new); seen.add('leb24-move'); continue
        if old['key'] == LEB24_KEY and sel.endswith('li:nth-of-type(7) > a:nth-of-type(3)'):
            if value_of(n, old) != old['source']:
                raise ValueError('Lebanon24 anchor mismatch at position 3')
            bindings.append(dict(old)); seen.add('leb24-move'); continue
        if old['key'] == 'news.latest-news.text' and sel == LI7 and old.get('nodeIndex') == 7:
            new = dict(old); new['nodeIndex'] = 9
            if value_of(n, new) != '.':
                raise ValueError('Trailing period did not move to node 9')
            bindings.append(new); seen.add('period-move'); continue
        if old['key'] == 'news.latest-news.text' and sel == LI7 and old.get('nodeIndex') == 9:
            if value_of(n, old) != '.':
                raise ValueError('Trailing period mismatch at node 9')
            bindings.append(dict(old)); seen.add('period-move'); continue
        if old['key'] == 'news.latest-news.text-2' and sel == LI7 and old.get('nodeIndex') == 7:
            if value_of(n, old) != '·':
                raise ValueError('Separator mismatch at node 7')
            bindings.append(dict(old)); have_sep7 = True; continue
        value = value_of(n, old)
        if value != old['source']:
            raise ValueError('Unrelated news source changed ' + old['key'] + ' ' + sel)
        bindings.append(dict(old))
    for want in set(REBIND) | {'vox', 'leb24-move', 'period-move'}:
        if want not in seen:
            raise ValueError('Expected binding not found: ' + want)
    # new nodes from the credit-line layout change
    if not have_newcinema:
        cin = soup.select(LI7 + ' > a:nth-of-type(2)')
        if len(cin) != 1 or ' '.join(str(cin[0].contents[0]).split()) != EN[NEWCINEMA_KEY]:
            raise ValueError('New Cinemacity anchor missing at position 2')
        bindings.append({'key': NEWCINEMA_KEY, 'selector': LI7 + ' > a:nth-of-type(2)', 'source': EN[NEWCINEMA_KEY], 'kind': 'text', 'nodeIndex': 0})
    li = soup.select(LI7)[0]
    if not have_sep7:
        if ' '.join(str(li.contents[7]).split()) != '·':
            raise ValueError('New separator missing at node 7')
        bindings.append({'key': 'news.latest-news.text-2', 'selector': LI7, 'source': '·', 'kind': 'text', 'nodeIndex': 7})
    copy = json.loads((root / 'locales/en/news-master-copy.json').read_text())
    local = json.loads((root / 'locales/ar/news-master-copy.json').read_text())
    copy.pop(OLD_CINEMA_KEY, None); local.pop(OLD_CINEMA_KEY, None)
    for key in list(REBIND) + [VOX_KEY, NEWCINEMA_KEY]:
        copy[key] = EN[key]; local[key] = AR[key]
    if set(local) != set(copy):
        raise ValueError('Arabic news keys differ from English')
    contract.update(bindings=bindings, messages=copy, masterSha256=hashlib.sha256(raw).hexdigest())
    return {root / 'locales/en/news-master-copy.json': copy,
            root / 'locales/ar/news-master-copy.json': local,
            root / 'locales/en/news-master-bindings.json': contract}

def home_outputs(root=ROOT):
    contract = json.loads((root / 'locales/en/home-bindings.json').read_text())
    raw = (root / 'index.html').read_bytes()
    soup = BeautifulSoup(raw, 'html.parser')
    seen = set()
    for b in contract['bindings']:
        if b['key'] in HOME_KEYS:
            nodes = soup.select(b['selector'])
            if len(nodes) != 1:
                raise ValueError('Home binding selector drift ' + b['key'])
            b['source'] = HOME_EN[b['key']]
            if value_of(nodes[0], b) != b['source']:
                raise ValueError('Home value mismatch - run build_news_desk first: ' + b['key'])
            seen.add(b['key'])
    if seen != set(HOME_KEYS):
        raise ValueError('Expected both home premiere keys, got ' + str(seen))
    result = {}
    copy = json.loads((root / 'locales/en/home-copy.json').read_text())
    for key in HOME_KEYS:
        copy[key] = HOME_EN[key]
    result[root / 'locales/en/home-copy.json'] = copy
    for code, (dek, value) in HOME_TR.items():
        path = root / f'locales/{code}/home-copy.json'
        catalog = json.loads(path.read_text())
        catalog['home.latest-news.premiere.homeDek'] = dek
        catalog['home.latest-news.premiere.openingValue'] = value
        result[path] = catalog
    pack_path = root / 'locales/film-home-translations.json'
    pack = json.loads(pack_path.read_text())
    if pack['status'] != 'agent-translated-native-not-certified':
        raise ValueError('Unexpected translation pack status')
    keys = list(pack['keys'])
    for code, (dek, value) in HOME_TR.items():
        pack['locales'][code][keys.index('homeDek')] = dek
        pack['locales'][code][keys.index('openingValue')] = value
    result[pack_path] = pack
    contract.update(messages=copy, masterSha256=hashlib.sha256(raw).hexdigest())
    result[root / 'locales/en/home-bindings.json'] = contract
    return result

def pack_text(pack):
    lines = ['{', ' "status": ' + json.dumps(pack['status'], ensure_ascii=False) + ',',
             ' "keys": [' + ', '.join(json.dumps(k) for k in pack['keys']) + '],', ' "locales": {']
    codes = list(pack['locales'])
    for i, code in enumerate(codes):
        arr = ', '.join(json.dumps(v, ensure_ascii=False) for v in pack['locales'][code])
        lines.append(' ' + json.dumps(code) + ': [' + arr + ']' + (',' if i < len(codes) - 1 else ''))
    lines.append(' }')
    lines.append('}')
    return '\n'.join(lines) + '\n'

def outputs(root=ROOT):
    merged = news_outputs(root)
    merged.update(home_outputs(root))
    pack_path = root / 'locales/film-home-translations.json'
    pack = merged.pop(pack_path)
    result = {p: json.dumps(j, ensure_ascii=False, indent=2) + '\n' for p, j in merged.items()}
    result[pack_path] = pack_text(pack)
    return result

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--check', action='store_true')
    a = p.parse_args()
    for path, text in outputs().items():
        if a.check:
            if path.read_text() != text:
                raise SystemExit('Cinema home/news bindings stale: ' + str(path))
        else:
            path.write_text(text)
    print('Cinema home/news bindings checked' if a.check else 'Cinema home/news bindings refreshed')
