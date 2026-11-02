"""Rebind the Mar Charbel cinema row after the October 22 in-place update (VOX Cinemas Lebanon
lists the film as Now Showing). Same-node text updates keep their keys; the row chip and date get
the existing Update key and a new October 22 date key; the VOX and Cinemacity credit anchors keep
their keys with new text. Executor only; run after build-pages and build_news_desk:
python3 scripts/i18n/refresh_movie_now_showing_oct22.py [--check]
"""
import argparse, hashlib, json
from pathlib import Path
from bs4 import BeautifulSoup
ROOT = Path(__file__).resolve().parents[2]
ROW = '#mar-charbel-october-opening-2026-10 > '
TITLE_KEY = 'news.latest-news.mar-charbel-listed-for-october-22-opening-in-beirut'
ROWSUM_KEY = 'news.latest-news.cinemacity-beirut-souks-lists-october-22-as-the-opening-date'
VOX_KEY = 'news.latest-news.vox-city-centre-beirut-listed-october-21-sessions'
CINE_KEY = 'news.latest-news.cinemacity-beirut-october-22-opening-listing-no-sessions'
OLD_CHIP, CHIP = 'news.latest-news.announcement', 'news.latest-news.update'
OLD_DATE, DATE = 'news.latest-news.october-5-2026', 'news.latest-news.october-22-2026'
EN = {
    TITLE_KEY: 'Mar Charbel Now Showing at VOX Cinemas Lebanon',
    ROWSUM_KEY: 'VOX Cinemas Lebanon lists Mar Charbel as Now Showing, with an October 21 release date and showtimes at City Centre Beirut on October 22 (Arabic audio with English subtitles). Cinemacity Beirut lists the film for October 22. A listing is not a seat guarantee or an attendance report - check your cinema.',
    VOX_KEY: 'VOX Cinemas Lebanon: Now Showing, release date October 21 (checked October 22)',
    CINE_KEY: 'Cinemacity Beirut: October 22 film listing',
    CHIP: 'Update',
    DATE: 'October 22, 2026',
}
AR = {
    TITLE_KEY: 'فيلم مار شربل يُعرض الآن في سينمات فوكس لبنان',
    ROWSUM_KEY: 'تدرج سينمات فوكس لبنان فيلم مار شربل بوصفه «يُعرض الآن»، مع تاريخ إصدار 21 تشرين الأول وعروض في سيتي سنتر بيروت يوم 22 تشرين الأول (بالعربية مع ترجمة إنكليزية). وتدرج سينما سيتي بيروت الفيلم بتاريخ 22 تشرين الأول. الإدراج ليس ضمانًا للمقعد ولا تقريرًا عن الحضور - تحقق من سينماك.',
    VOX_KEY: 'سينمات فوكس لبنان: يُعرض الآن، تاريخ الإصدار 21 تشرين الأول (تمت المراجعة في 22 تشرين الأول)',
    CINE_KEY: 'سينما سيتي بيروت: إدراج الفيلم في 22 تشرين الأول',
    CHIP: 'تحديث',
    DATE: '22 تشرين الأول 2026',
}

def value_of(n, b):
    if b['kind'] == 'attribute':
        return n.get(b['attribute'])
    return ' '.join(str(n.contents[b['nodeIndex']]).split())

def outputs(root=ROOT):
    contract = json.loads((root / 'locales/en/news-master-bindings.json').read_text())
    raw = (root / 'news.html').read_bytes()
    soup = BeautifulSoup(raw, 'html.parser')
    seen, bindings = set(), []
    for old in contract['bindings']:
        k, new = old['key'], dict(old)
        if old['selector'].startswith(ROW) and k in (OLD_CHIP, CHIP):
            new['key'] = CHIP
        elif old['selector'].startswith(ROW) and k in (OLD_DATE, DATE):
            new['key'] = DATE
        elif k not in (TITLE_KEY, ROWSUM_KEY, VOX_KEY, CINE_KEY):
            bindings.append(new); continue
        elif k in (VOX_KEY, CINE_KEY) and ' > li:nth-of-type(' not in old['selector']:
            bindings.append(new); continue
        new['source'] = EN[new['key']]
        nodes = soup.select(old['selector'])
        if len(nodes) != 1 or value_of(nodes[0], new) != new['source']:
            raise ValueError('Rebind mismatch - run build-pages and build_news_desk first: ' + k)
        bindings.append(new); seen.add(new['key'])
    if seen != set(EN):
        raise ValueError('Expected bindings not found: ' + str(set(EN) - seen))
    copy = json.loads((root / 'locales/en/news-master-copy.json').read_text())
    local = json.loads((root / 'locales/ar/news-master-copy.json').read_text())
    for key in EN:
        copy[key] = EN[key]; local[key] = AR[key]
    if not any(b['key'] == OLD_DATE for b in bindings):
        copy.pop(OLD_DATE, None); local.pop(OLD_DATE, None)
    if set(local) != set(copy):
        raise ValueError('Arabic news keys differ from English')
    contract.update(bindings=bindings, messages=copy, masterSha256=hashlib.sha256(raw).hexdigest())
    return {root / 'locales/en/news-master-copy.json': copy,
            root / 'locales/ar/news-master-copy.json': local,
            root / 'locales/en/news-master-bindings.json': contract}

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--check', action='store_true')
    a = p.parse_args()
    for path, data in outputs().items():
        text = json.dumps(data, ensure_ascii=False, indent=2) + '\n'
        if a.check:
            if path.read_text() != text:
                raise SystemExit('Movie now-showing bindings stale: ' + str(path))
        else:
            path.write_text(text)
    print('Movie now-showing bindings checked' if a.check else 'Movie now-showing bindings refreshed')
