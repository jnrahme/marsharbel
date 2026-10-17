"""Batch 1 Tier 2: finish Order-owned photo swaps on mirrored families.

Same provenance as tier 1: owner-reported reuse permission (saintcharbel.com,
Monastery of Saint Maron - Annaya); attribution terms not independently
documented; prior credits removed because the previously credited images are
no longer used. Guarded, idempotent. Runs AFTER build-pages.mjs regenerates
the edited src masters. Executor: python3 scripts/i18n/refresh_annaya_batch1_tier2.py [--check]
"""
import argparse, hashlib, json, re, sys
from pathlib import Path
from bs4 import BeautifulSoup, NavigableString

ROOT = Path(__file__).resolve().parents[2]

def slug(text, n=60):
    s = re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')
    return s[:n].strip('-') or 'text'

CREDIT_MARKERS = [' Photograph:', ' Photo:', ' تصوير', ' Foto:', ' Fotografía', ' Fotografia',
                  ' Фото', ' фото', ' फोटो', ' 照片', ' ภาพ', ' Zdjęcie', ' Fotoğraf']

AERIAL_TR = {
 'ar': 'دير مار مارون في عنّايا من الجو، مع الكنيسة وسفح الجبل',
 'fr': "Le monastère Saint-Maron à Annaya vu du ciel, avec l'église et le flanc de la montagne",
 'es': 'El monasterio de San Marón en Annaya desde el aire, con la iglesia y la ladera',
 'pt': 'O Mosteiro de São Maron em Annaya visto do ar, com a igreja e a encosta',
 'it': "Il monastero di San Marone ad Annaya visto dall'alto, con la chiesa e il fianco della montagna",
 'de': 'Das Kloster St. Maron in Annaya aus der Luft, mit der Kirche und dem Berghang',
 'pl': 'Klasztor św. Marona w Annaji z lotu ptaka, z kościołem i zboczem góry',
 'ru': 'Монастырь святого Марона в Аннайе с высоты птичьего полета: церковь и горный склон',
 'zh-Hans': '从空中俯瞰安纳亚的圣马龙修道院，教堂与山坡相映',
}

NIGHT_ALT = 'The monastery of Saint Maron at Annaya at night, the church and monastic buildings lit above the valley'
NIGHT_TR = {
 'ar': 'دير مار مارون في عنّايا ليلاً، الكنيسة والمباني الرهبانية مضاءة فوق الوادي',
 'fr': "Le monastère Saint-Maron d'Annaya la nuit, l'église et les bâtiments monastiques éclairés au-dessus de la vallée",
 'es': 'El monasterio de San Marón en Annaya de noche, la iglesia y los edificios monásticos iluminados sobre el valle',
 'pt': 'O Mosteiro de São Marom em Annaya à noite, a igreja e os edifícios monásticos iluminados sobre o vale',
 'it': "Il monastero di San Marone ad Annaya di notte, la chiesa e gli edifici monastici illuminati sopra la valle",
 'de': 'Das Kloster St. Maron in Annaya bei Nacht, die Kirche und die Klostergebäude erleuchtet über dem Tal',
 'pl': 'Klasztor św. Marona w Annaji nocą, kościół i zabudowania klasztorne oświetlone nad doliną',
 'ru': 'Монастырь святого Марона в Аннайе ночью: церковь и монастырские здания освещены над долиной',
 'hi': 'रात में अन्नाया का सेंट मैरन मठ, घाटी के ऊपर चर्च और मठ की इमारतें जगमगाई हुई',
 'th': 'อารามนักบุญมาโรนในอันนายาตอนกลางคืน โบสถ์และอาคารอารามสว่างไสวเหนือหุบเขา',
}

SHRINE_ALT = 'The tomb of Saint Charbel in the monastery church at Annaya, his portrait above the shrine'
SHRINE_TR = {
 'ar': 'ضريح مار شربل في كنيسة الدير في عنّايا، وصورته فوق الضريح',
 'fr': "Le tombeau de saint Charbel dans l'église du monastère d'Annaya, son portrait au-dessus du tombeau",
 'es': 'La tumba de San Charbel en la iglesia del monasterio de Annaya, con su retrato sobre el sepulcro',
 'pt': 'O túmulo de São Charbel na igreja do mosteiro de Annaya, com o seu retrato sobre o túmulo',
 'it': 'La tomba di San Charbel nella chiesa del monastero di Annaya, con il suo ritratto sopra il sepolcro',
 'de': 'Das Grab des heiligen Charbel in der Klosterkirche von Annaya, sein Porträt über dem Schrein',
 'pl': 'Grób św. Charbela w kościele klasztornym w Annaji, jego portret nad grobem',
 'ru': 'Гробница святого Шарбеля в монастырской церкви в Аннайе, его портрет над ракой',
 'hi': 'अन्नाया के मठ के चर्च में सेंट शारबेल की कब्र, समाधि के ऊपर उनका चित्र',
 'th': 'หลุมฝังศพนักบุญชาร์เบลในโบสถ์ของอารามที่อันนายา มีภาพเหมือนของท่านอยู่เหนือแท่น',
}

INTERIOR_ALT = 'Inside the monastery church at Annaya, where Saint Charbel prayed as a monk for forty-seven years'
INTERIOR_TR = {'ar': 'داخل كنيسة الدير في عنّايا، حيث صلى مار شربل راهباً سبعاً وأربعين سنة'}

NOV_CAP = 'The monastery of Saint Maron in Annaya, whose monks published the traditional novena prayers this page follows.'
NOV_CAP_TR = {
 'ar': 'دير مار مارون في عنّايا، الذي نشر رهبانه صلوات التساعية التقليدية التي تتبعها هذه الصفحة.',
 'de': 'Das Kloster St. Maron in Annaya, dessen Mönche die traditionellen Novenengebete veröffentlichten, denen diese Seite folgt.',
 'fr': "Le monastère Saint-Maron d'Annaya, dont les moines ont publié les prières traditionnelles de la neuvaine que suit cette page.",
 'es': 'El monasterio de San Marón en Annaya, cuyos monjes publicaron las oraciones tradicionales de la novena que sigue esta página.',
 'pt': 'O Mosteiro de São Marom em Annaya, cujos monges publicaram as orações tradicionais da novena que esta página segue.',
 'it': 'Il monastero di San Marone ad Annaya, i cui monaci hanno pubblicato le preghiere tradizionali della novena che questa pagina segue.',
 'pl': 'Klasztor św. Marona w Annaji, którego mnisi opublikowali tradycyjne modlitwy nowenny, za którymi podąża ta strona.',
 'ru': 'Монастырь святого Марона в Аннайе, монахи которого опубликовали традиционные молитвы новенны, которым следует эта страница.',
}

COURT_ALT = 'The monastery courtyard at Annaya at dusk, the lit arcades pilgrims cross on their way to the tomb'
COURT_ALT_TR = {
 'ar': 'ساحة الدير في عنّايا عند الغسق، الأروقة المضاءة التي يعبرها الحجاج في طريقهم إلى الضريح',
 'fr': "La cour du monastère d'Annaya au crépuscule, les arcades éclairées que les pèlerins traversent en allant vers le tombeau",
 'es': 'El patio del monasterio de Annaya al anochecer, las arcadas iluminadas que los peregrinos cruzan camino a la tumba',
 'pt': 'O pátio do mosteiro de Annaya ao entardecer, as arcadas iluminadas que os peregrinos atravessam a caminho do túmulo',
 'it': 'Il cortile del monastero di Annaya al tramonto, i portici illuminati che i pellegrini attraversano verso la tomba',
 'de': 'Der Klosterhof von Annaya in der Dämmerung, die erleuchteten Arkaden, die die Pilger auf dem Weg zum Grab durchqueren',
 'pl': 'Dziedziniec klasztoru w Annaji o zmierzchu, oświetlone arkady, które pielgrzymi przechodzą w drodze do grobu',
 'ru': 'Двор монастыря в Аннайе в сумерках: освещенные аркады, через которые паломники идут к гробнице',
}
COURT_CAP = 'The monastery courtyard at Annaya at dusk - the courtyard pilgrims cross on their way to the tomb.'
COURT_CAP_TR = {
 'ar': 'ساحة الدير في عنّايا عند الغسق - الساحة التي يعبرها الحجاج في طريقهم إلى الضريح.',
 'fr': "La cour du monastère d'Annaya au crépuscule - la cour que les pèlerins traversent en allant vers le tombeau.",
 'es': 'El patio del monasterio de Annaya al anochecer - el patio que los peregrinos cruzan camino a la tumba.',
 'pt': 'O pátio do mosteiro de Annaya ao entardecer - o pátio que os peregrinos atravessam a caminho do túmulo.',
 'it': 'Il cortile del monastero di Annaya al tramonto - il cortile che i pellegrini attraversano verso la tomba.',
 'de': 'Der Klosterhof von Annaya in der Dämmerung - der Hof, den die Pilger auf dem Weg zum Grab durchqueren.',
 'pl': 'Dziedziniec klasztoru w Annaji o zmierzchu - dziedziniec, przez który pielgrzymi przechodzą w drodze do grobu.',
 'ru': 'Двор монастыря в Аннайе в сумерках - двор, через который паломники идут к гробнице.',
}

# ops: rekey-alt (new slug key), fixed-alt (keep key), strip-cap (credit tail off, key kept),
# rekey-cap (new slug key, old dropped), drop-binding (key+selector fragment).
JOBS = [
 dict(family='history-master', locales=list(NIGHT_TR), ops=[
   dict(op='rekey-alt', old='history.accessibility.the-church-and-monastery-of-saint-maron-at-annaya',
        prefix='history.accessibility.', en=NIGHT_ALT, tr=NIGHT_TR),
   dict(op='rekey-alt', old='history.accessibility.a-carved-wooden-tomb-chest-inside-a-stone-vaulted',
        prefix='history.accessibility.', en=SHRINE_ALT, tr=SHRINE_TR),
   dict(op='drop-binding', key='history.section.photo-paul-saad', frag='section:nth-of-type(5)'),
   dict(op='drop-binding', key='history.section.wikimedia-commons', frag='section:nth-of-type(5)', keep_key=True),
   dict(op='drop-binding', key='history.section.cc-by-sa-4-0', frag='section:nth-of-type(5)'),
   dict(op='drop-binding', key='history.section.resized', frag='section:nth-of-type(5)'),
   dict(op='drop-binding', key='history.tomb.photo-llew', frag='#tomb'),
   dict(op='drop-binding', key='history.tomb.wikimedia-commons', frag='#tomb'),
   dict(op='drop-binding', key='history.tomb.cc-by-sa-4-0', frag='#tomb'),
   dict(op='drop-binding', key='history.tomb.resized', frag='#tomb'),
 ]),
 dict(family='prayer-library-master', locales=['ar'], ops=[
   dict(op='rekey-alt', old='prayer-library.main-img-alt-the-monastery-of-saint-maron-in-2',
        prefix='prayer-library.main-img-alt-', en=INTERIOR_ALT, tr=INTERIOR_TR),
   dict(op='strip-cap', key='prayer-library.main-main-content-the-monastery-of-saint-maron-in',
        en='The Monastery of Saint Maron in Annaya - where Saint Charbel prayed as a monk for forty-seven years, and where pilgrims still come to pray.'),
   dict(op='drop-binding', key='prayer-library.main-main-content-via-wikimedia-commons', frag=''),
   dict(op='drop-binding', key='prayer-library.main-main-content-cc-by-sa-4-0', frag=''),
 ]),
 dict(family='saint-charbel-novena-master', locales=['ar','de','fr','ru','pt','it','pl','es'], ops=[
   dict(op='rekey-alt', old='saint-charbel-novena.accessibility.the-village-of-annaya-on-its-hill-above-the-sea',
        prefix='saint-charbel-novena.accessibility.', en='The Monastery of Saint Maron in Annaya from the air, with the church and the mountainside', tr=AERIAL_TR),
   dict(op='rekey-cap', old='saint-charbel-novena.saint-charbel-novena.annaya-the-mountain-village-whose-monastery-published-the-tr',
        prefix='saint-charbel-novena.saint-charbel-novena.', en=NOV_CAP, tr=NOV_CAP_TR),
   dict(op='drop-binding', key='saint-charbel-novena.saint-charbel-novena.via-wikimedia-commons', frag=''),
   dict(op='drop-binding', key='saint-charbel-novena.saint-charbel-novena.cc-by-sa-4-0', frag=''),
 ]),
 dict(family='annaya-master', locales=['ar','fr','es','pt','it','de','pl','ru'], ops=[
   dict(op='rekey-alt', old='annaya.accessibility.the-statue-of-saint-charbel-in-the-monastery-courtyard-at-an',
        prefix='annaya.accessibility.', en=COURT_ALT, tr=COURT_ALT_TR),
   dict(op='rekey-cap', old='annaya.body.the-statue-of-saint-charbel-in-the-monastery-courtyard-at-an',
        prefix='annaya.body.', en=COURT_CAP, tr=COURT_CAP_TR),
   dict(op='drop-binding', key='annaya.body.via-wikimedia-commons', frag=''),
   dict(op='drop-binding', key='annaya.body.cc-by-sa-4-0', frag=''),
 ]),
 dict(family='visit-annaya-zh-travel-master', locales=['zh-Hans'], ops=[
   dict(op='rekey-alt', old='visit-annaya.accessibility.the-statue-of-saint-charbel-in-the-monastery-courtyard-at-an',
        prefix='visit-annaya.accessibility.', en=COURT_ALT, tr={'zh-Hans': '黄昏时分安纳亚修道院的庭院，朝圣者穿过灯火通明的拱廊前往圣墓'}),
   dict(op='rekey-cap', old='visit-annaya.body.the-statue-of-saint-charbel-in-the-monastery-courtyard-at-an',
        prefix='visit-annaya.body.', en=COURT_CAP, tr={'zh-Hans': '黄昏时分的安纳亚修道院庭院 - 朝圣者前往圣墓途中穿过的庭院。'}),
   dict(op='drop-binding', key='visit-annaya.body.via-wikimedia-commons', frag=''),
   dict(op='drop-binding', key='visit-annaya.body.cc-by-sa-4-0', frag=''),
 ]),
 dict(family='saint-charbel-hermitage-travel-master', locales=['de','ru'], ops=[
   dict(op='fixed-alt', key='travel.images.alt1',
        en='The Monastery of Saint Maron in Annaya from the air, with the church and the mountainside', tr=AERIAL_TR),
   dict(op='strip-cap', key='travel.hero.caption1',
        en='The Monastery of Saint Maron in Annaya, the monastery below the hermitage where Saint Charbel lived from 1875.'),
   dict(op='drop-binding', key='travel.hero.captionLink1', frag=''),
   dict(op='drop-binding', key='travel.hero.captionLink2', frag=''),
 ]),
 dict(family='saint-charbel-hermitage-zh-travel-master', locales=['zh-Hans'], ops=[
   dict(op='rekey-alt', old='saint-charbel-hermitage.accessibility.the-monastery-of-saint-maron-in-annaya-seen-across-the-valle',
        prefix='saint-charbel-hermitage.accessibility.', en='The Monastery of Saint Maron in Annaya from the air, with the church and the mountainside', tr=AERIAL_TR),
   dict(op='strip-cap', key='saint-charbel-hermitage.body.the-monastery-of-saint-maron-in-annaya-th',
        en='The Monastery of Saint Maron in Annaya, the monastery below the hermitage where Saint Charbel lived from 1875.'),
   dict(op='drop-binding', key='saint-charbel-hermitage.body.via-wikimedia-commons', frag=''),
   dict(op='drop-binding', key='saint-charbel-hermitage.body.cc-by-sa-4-0', frag=''),
 ]),
]

def strip_credit(value):
    for m in CREDIT_MARKERS:
        i = value.find(m)
        if i > 0:
            return value[:i].rstrip() + ('.' if not value[:i].rstrip().endswith('.') else '')
    return value

def repair_node_index(contract, root_html):
    soup = BeautifulSoup(root_html, 'html.parser')
    fixed = 0
    for b in contract['bindings']:
        if b.get('kind') != 'text':
            continue
        nodes = soup.select(b['selector'])
        if len(nodes) != 1:
            continue
        node = nodes[0]
        def match(t):
            return isinstance(t, NavigableString) and ' '.join(str(t).split()) == b['source']
        if b['nodeIndex'] < len(node.contents) and match(node.contents[b['nodeIndex']]):
            continue
        found = [i for i, ch in enumerate(node.contents) if match(ch)]
        if len(found) == 1:
            b['nodeIndex'] = found[0]; fixed += 1
    return fixed

def apply_family(job, check=False):
    fam = job['family']
    en_copy_p = ROOT / f'locales/en/{fam}-copy.json'
    en_bind_p = ROOT / f'locales/en/{fam}-bindings.json'
    en_copy = json.loads(en_copy_p.read_text())
    contract = json.loads(en_bind_p.read_text())
    root_html = (ROOT / contract['master']).read_text(encoding='utf-8')

    # plan mutations
    drop_keys = set()
    rekeys = {}   # old -> new
    sets_en = {}  # key -> en value
    sets_loc = {} # key -> {loc: value}
    binding_drops = []  # (key, frag)
    for op in job['ops']:
        if op['op'] == 'rekey-alt' or op['op'] == 'rekey-cap':
            new = op['prefix'] + slug(op['en'])
            rekeys[op['old']] = new
            drop_keys.add(op['old'])
            sets_en[new] = op['en']
            sets_loc[new] = op['tr']
        elif op['op'] == 'fixed-alt':
            sets_en[op['key']] = op['en']
            sets_loc[op['key']] = op['tr']
        elif op['op'] == 'strip-cap':
            sets_en[op['key']] = op['en']
        elif op['op'] == 'drop-binding':
            binding_drops.append((op['key'], op['frag']))
            if not op.get('keep_key'):
                drop_keys.add(op['key'])

    master_sha = hashlib.sha256((ROOT / contract['master']).read_bytes()).hexdigest()
    stale = (contract.get('masterSha256') != master_sha
             or any(k in en_copy for k in drop_keys)
             or any(en_copy.get(k) != v for k, v in sets_en.items())
             or any(b['key'] in drop_keys for b in contract['bindings'])
             or any(b['key'] == k and (not frag or frag in b['selector'])
                    for k, frag in binding_drops for b in contract['bindings']))
    if check:
        ok = not stale
        print(f"{fam}: {'OK' if ok else 'NOT APPLIED'}")
        return ok
    if not stale:
        print(f'{fam}: already applied')
        return True

    # bindings: rekey / resourced / dropped
    new_bindings = []
    for b in contract['bindings']:
        drop = any(b['key'] == k and (not frag or frag in b['selector']) for k, frag in binding_drops)
        if drop:
            continue
        if b['key'] in rekeys:
            newk = rekeys[b['key']]
            b = dict(b, key=newk, source=sets_en[newk])
        elif b['key'] in sets_en:
            b = dict(b, source=sets_en[b['key']])
        new_bindings.append(b)
    contract['bindings'] = new_bindings

    # en copy
    for k in drop_keys:
        en_copy.pop(k, None)
    en_copy.update(sets_en)
    # strip-cap locale values handled per locale below

    # locale copies
    writes = {en_copy_p: en_copy}
    for loc in job['locales']:
        p = ROOT / f'locales/{loc}/{fam}-copy.json'
        if not p.exists():
            continue
        local = json.loads(p.read_text())
        for k in drop_keys:
            local.pop(k, None)
        for k, v in sets_en.items():
            if k in sets_loc and loc in sets_loc[k]:
                local[k] = sets_loc[k][loc]
            elif k in local and any(op['op'] == 'strip-cap' and op['key'] == k for op in job['ops']):
                local[k] = strip_credit(local[k])
            else:
                local[k] = v  # fallback: EN string (asserted below only on key sets)
        if set(local) != set(en_copy):
            raise ValueError(f'{loc} {fam}: key set differs after update: {sorted(set(en_copy) ^ set(local))[:4]}')
        writes[p] = local

    # drop keys that lost their last binding (e.g. shared credit keys stay if still bound)
    bound = {b['key'] for b in contract['bindings']}
    for p in list(writes):
        d = writes[p]
        for k in list(d):
            if k in drop_keys and k in bound:
                continue  # safety, should not happen
        writes[p] = d

    fixed = repair_node_index(contract, root_html)
    contract['messages'] = en_copy
    contract['masterSha256'] = master_sha
    writes[en_bind_p] = contract
    for p, obj in writes.items():
        p.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'{fam}: applied (nodeIndex repaired: {fixed})')
    return True

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true')
    ap.add_argument('--only', default='')
    args = ap.parse_args()
    only = {x for x in args.only.split(',') if x}
    ok = True
    for job in JOBS:
        if only and job['family'] not in only:
            continue
        ok = apply_family(job, check=args.check) and ok
    sys.exit(0 if ok else 1)
