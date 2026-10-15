"""Batch 1 (A1+A2): swap credited Annaya/tomb photos for Order-owned assets on mirrored pages.

Owner-reported reuse permission (saintcharbel.com, Monastery of Saint Maron - Annaya);
attribution terms not independently documented; prior credits removed because the
previously credited images are no longer used. Guarded, idempotent: --check validates
the target state, default applies it. Executor: python3 scripts/i18n/refresh_annaya_batch1.py [--check]
"""
import argparse, hashlib, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def slug(text, n=60):
    s = re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')
    return s[:n].strip('-') or 'text'

# Each job: one figure swap on one mirrored page family.
JOBS = [
 dict(
  page='all-saints-and-all-souls', family='all-saints-and-all-souls-master',
  img_old='<img alt="The vigil lamp burning at the tomb of Saint Charbel in Annaya" height="468" loading="lazy" src="./media/annaya/charbel-tomb-vigil-lamp.webp" width="589"/>',
  img_new='<img alt="An oil lamp burning in a stone niche at the monastery of Annaya" height="667" loading="lazy" src="./media/annaya/charbel-oil-lamp-hermitage.webp" width="1000"/>',
  cap_old_inner='The vigil lamp at Saint Charbel\'s tomb in Annaya: a small flame kept before a saint, like the candles many families light for their dead in early November. Photograph: LLEW, <a href="https://commons.wikimedia.org/wiki/File:Charbel_Makhlouf_grave.JPG" rel="noopener" target="_blank">via Wikimedia Commons</a>, <a href="https://creativecommons.org/licenses/by-sa/4.0/" rel="noopener" target="_blank">CC BY-SA 4.0</a>.',
  alt_en='An oil lamp burning in a stone niche at the monastery of Annaya',
  alt_old_key='allsaints.accessibility.the-vigil-lamp-burning-at-the-tomb-of-saint-charbel-in-annay',
  cap_en='An oil lamp burning in a stone niche at the monastery of Annaya: a small flame before the hermit saint, like the candles many families light for their dead in early November.',
  cap_old_key='allsaints.all-saints-and-all-souls.the-vigil-lamp-at-saint-charbel-s-tomb-in-annaya-a-small-fla',
  drop_keys=['allsaints.all-saints-and-all-souls.via-wikimedia-commons','allsaints.all-saints-and-all-souls.cc-by-sa-4-0'],
  tr={
   'ar': ('مصباح زيت يشتعل في محراب حجري بدير عنّايا','مصباح زيت يشتعل في محراب حجري بدير عنّايا: شعلة صغيرة أمام القديس الناسك، مثل الشموع التي تضيئها عائلات كثيرة لموتاها في مطلع تشرين الثاني.'),
   'fr': ("Une lampe à huile brûlant dans une niche de pierre du monastère d'Annaya","Une lampe à huile brûlant dans une niche de pierre du monastère d'Annaya : une petite flamme devant le saint ermite, comme les cierges que tant de familles allument pour leurs morts début novembre."),
   'es': ('Una lámpara de aceite ardiendo en un nicho de piedra del monasterio de Annaya','Una lámpara de aceite ardiendo en un nicho de piedra del monasterio de Annaya: una pequeña llama ante el santo ermitaño, como las velas que muchas familias encienden por sus difuntos a principios de noviembre.'),
   'pt': ('Uma lâmpada a óleo acesa num nicho de pedra do mosteiro de Annaya','Uma lâmpada a óleo acesa num nicho de pedra do mosteiro de Annaya: uma pequena chama diante do santo eremita, como as velas que muitas famílias acendem pelos seus falecidos no início de novembro.'),
   'it': ("Una lampada a olio accesa in una nicchia di pietra del monastero di Annaya","Una lampada a olio accesa in una nicchia di pietra del monastero di Annaya: una piccola fiamma davanti al santo eremita, come i ceri che tante famiglie accendono per i loro defunti all'inizio di novembre."),
   'de': ('Eine Öllampe, die in einer Steinnische des Klosters von Annaya brennt','Eine Öllampe, die in einer Steinnische des Klosters von Annaya brennt: eine kleine Flamme vor dem Einsiedlerheiligen, wie die Kerzen, die viele Familien Anfang November für ihre Verstorbenen anzünden.'),
   'pl': ('Lampa oliwna płonąca w kamiennej niszy klasztoru w Annaji','Lampa oliwna płonąca w kamiennej niszy klasztoru w Annaji: mały płomień przed świętym pustelnikiem, jak świece, które wiele rodzin zapala za swoich zmarłych na początku listopada.'),
   'hi': ('अन्नाया के मठ की पत्थर की आला में जलता हुआ तेल का दीपक','अन्नाया के मठ की पत्थर की आला में जलता तेल का दीपक: त्यागी संत के समक्ष एक छोटी सी लौ, ठीक उन मोमबत्तियों जैसी जो कई परिवार नवंबर की शुरुआत में अपने मृतकों के लिए जलाते हैं।'),
   'th': ('ตะเกียงน้ำมันที่ลุกอยู่ในช่องหินของอารามอันนายา','ตะเกียงน้ำมันที่ลุกอยู่ในช่องหินของอารามอันนายา: เปลวไฟเล็กๆ ต่อหน้านักบุญสมถะ เช่นเดียวกับเทียนที่ครอบครัวมากมายจุดให้ผู้ล่วงลับในช่วงต้นเดือนพฤศจิกายน'),
   'zh-Hans': ('在安纳亚修道院的石龛中燃烧的油灯','在安纳亚修道院的石龛中燃烧的油灯：隐修圣人面前的一点小火焰，正如许多家庭在十一月初为逝者点燃的蜡烛。'),
  }),
 dict(
  page='saint-charbel-pilgrimage', family='pilgrimage-master',
  img_old='<img src="./media/annaya/annaya-monastery.webp" alt="The Monastery of Saint Maron in Annaya seen across the valley, with the church and forested mountainside" width="1100" height="618" loading="eager" fetchpriority="high" />',
  img_new='<img src="./media/annaya/annaya-monastery-aerial-day.webp" alt="The Monastery of Saint Maron in Annaya from the air, with the church and the mountainside" width="1080" height="608" loading="eager" fetchpriority="high" />',
  cap_old_inner='The Monastery of Saint Maron in Annaya - the heart of every pilgrimage to Saint Charbel. Photograph: Paul Saad, <a href="https://commons.wikimedia.org/wiki/File:Pan_Annaya_Church_And_Monastry.jpg" target="_blank" rel="noopener">via Wikimedia Commons</a>, <a href="https://creativecommons.org/licenses/by-sa/4.0/" target="_blank" rel="noopener">CC BY-SA 4.0</a>.',
  alt_en='The Monastery of Saint Maron in Annaya from the air, with the church and the mountainside',
  alt_old_key='pilgrimage.accessibility.the-monastery-of-saint-maron-in-annaya-seen-across-the-valle',
  cap_en='The Monastery of Saint Maron in Annaya - the heart of every pilgrimage to Saint Charbel.',
  cap_old_key='pilgrimage.body.the-monastery-of-saint-maron-in-annaya-the-heart-of-every-pi',
  drop_keys=['pilgrimage.body.via-wikimedia-commons','pilgrimage.body.cc-by-sa-4-0'],
  tr={
   'ar': ('دير مار مارون في عنّايا من الجو، مع الكنيسة وسفح الجبل','دير مار مارون في عنّايا - قلب كل حج إلى مار شربل.'),
   'fr': ("Le monastère Saint-Maron à Annaya vu du ciel, avec l'église et le flanc de la montagne","Le monastère Saint-Maron à Annaya - le cœur de tout pèlerinage à saint Charbel."),
   'es': ('El monasterio de San Marón en Annaya desde el aire, con la iglesia y la ladera','El monasterio de San Marón en Annaya - el corazón de toda peregrinación a San Charbel.'),
   'pt': ('O Mosteiro de São Maron em Annaya visto do ar, com a igreja e a encosta','O Mosteiro de São Maron em Annaya - o coração de toda peregrinação a São Charbel.'),
   'it': ("Il monastero di San Marone ad Annaya visto dall'alto, con la chiesa e il fianco della montagna","Il monastero di San Marone ad Annaya - il cuore di ogni pellegrinaggio a San Charbel."),
   'de': ('Das Kloster St. Maron in Annaya aus der Luft, mit der Kirche und dem Berghang','Das Kloster St. Maron in Annaya - das Herz jeder Wallfahrt zum heiligen Charbel.'),
   'pl': ('Klasztor św. Marona w Annaji z lotu ptaka, z kościołem i zboczem góry','Klasztor św. Marona w Annaji - serce każdej pielgrzymki do św. Charbela.'),
   'hi': ('हवाई दृश्य में अन्नाया का संत मैरुन मठ, गिरजाघर और पहाड़ी ढलान सहित','अन्नाया का संत मैरुन मठ - संत शरबेल की हर तीर्थयात्रा का हृदय।'),
   'th': ('อารามนักบุญมารอนในอันนายาจากมุมสูง พร้อมโบสถ์และไหล่เขา','อารามนักบุญมารอนในอันนายา - หัวใจของการแสวงบุญทุกครั้งต่อนักบุญชาร์เบล'),
   'zh-Hans': ('从空中俯瞰安纳亚的圣马龙修道院，教堂与山坡相映','安纳亚的圣马龙修道院 - 每一次朝圣圣夏贝尔之旅的核心。'),
  }),
 dict(
  page='saint-charbel-pilgrimage', family='pilgrimage-master',
  img_old='<img src="./media/annaya/charbel-tomb.webp" alt="The tomb of Saint Charbel in the monastery church at Annaya, with his portrait and a vigil lamp" width="1280" height="720" loading="lazy" />',
  img_new='<img src="./media/annaya/charbel-tomb-pilgrims.webp" alt="Pilgrims at the tomb of Saint Charbel in the monastery church at Annaya" width="1000" height="667" loading="lazy" />',
  cap_old_inner='Saint Charbel\'s tomb in the monastery church at Annaya - pilgrims kneel, rest a hand on the marble, and leave written intentions. Photograph: LLEW, <a href="https://commons.wikimedia.org/wiki/File:Charbel_Makhlouf_grave.JPG" target="_blank" rel="noopener">via Wikimedia Commons</a>, <a href="https://creativecommons.org/licenses/by-sa/4.0/" target="_blank" rel="noopener">CC BY-SA 4.0</a>.',
  alt_en='Pilgrims at the tomb of Saint Charbel in the monastery church at Annaya',
  alt_old_key='pilgrimage.accessibility.the-tomb-of-saint-charbel-in-the-monastery-church-at-annaya',
  cap_en="Saint Charbel's tomb in the monastery church at Annaya - pilgrims kneel, rest a hand on the marble, and leave written intentions.",
  cap_old_key='pilgrimage.the-heart-of-it-annaya.saint-charbel-s-tomb-in-the-monastery-church-at-annaya-pilgr',
  drop_keys=['pilgrimage.the-heart-of-it-annaya.via-wikimedia-commons','pilgrimage.the-heart-of-it-annaya.cc-by-sa-4-0'],
  tr={
   'ar': ('حجاج عند ضريح مار شربل في كنيسة الدير في عنّايا','ضريح مار شربل في كنيسة الدير في عنّايا - يركع الحجاج، ويضعون اليد على الرخام، ويتركون النيات مكتوبة.'),
   'fr': ("Pèlerins au tombeau de saint Charbel dans l'église du monastère à Annaya","Le tombeau de saint Charbel dans l'église du monastère à Annaya - les pèlerins s'agenouillent, posent une main sur le marbre et laissent des intentions écrites."),
   'es': ('Peregrinos ante la tumba de San Charbel en la iglesia del monasterio de Annaya','La tumba de San Charbel en la iglesia del monasterio de Annaya - los peregrinos se arrodillan, apoyan la mano en el mármol y dejan intenciones escritas.'),
   'pt': ('Peregrinos junto ao túmulo de São Charbel na igreja do mosteiro em Annaya','O túmulo de São Charbel na igreja do mosteiro em Annaya - os peregrinos ajoelham-se, pousam a mão no mármore e deixam intenções escritas.'),
   'it': ('Pellegrini alla tomba di San Charbel nella chiesa del monastero ad Annaya','La tomba di San Charbel nella chiesa del monastero ad Annaya - i pellegrini si inginocchiano, posano una mano sul marmo e lasciano intenzioni scritte.'),
   'de': ('Pilger am Grab des heiligen Charbel in der Klosterkirche von Annaya','Das Grab des heiligen Charbel in der Klosterkirche von Annaya - Pilger knien, legen eine Hand auf den Marmor und hinterlassen schriftliche Anliegen.'),
   'pl': ('Pielgrzymi przy grobie św. Charbela w kościele klasztornym w Annaji','Grób św. Charbela w kościele klasztornym w Annaji - pielgrzymi klękają, kładą dłoń na marmurze i zostawiają pisemne intencje.'),
   'hi': ('अन्नाया के मठ के गिरजाघर में संत शरबेल की कब्र पर तीर्थयात्री','अन्नाया के मठ के गिरजाघर में संत शरबेल की कब्र - तीर्थयात्री घुटने टेकते हैं, संगमरमर पर हाथ रखते हैं, और लिखित प्रार्थना-नियत छोड़ जाते हैं।'),
   'th': ('ผู้แสวงบุญที่สุสานนักบุญชาร์เบลในโบสถ์ของอารามที่อันนายา','สุสานนักบุญชาร์เบลในโบสถ์ของอารามที่อันนายา - ผู้แสวงบุญคุกเข่า วางมือบนหินอ่อน และทิ้งคำอธิษฐานที่เขียนไว้'),
   'zh-Hans': ('朝圣者在安纳亚修道院教堂内的圣夏贝尔墓前','安纳亚修道院教堂内的圣夏贝尔墓 - 朝圣者跪下，手抚大理石，留下书写的祈祷意向。'),
  }),
]

def apply_job(job, check=False):
    page_path = ROOT / 'src/pages' / f"{job['page']}.html"
    html = page_path.read_text(encoding='utf-8')
    if job['img_new'] in html and job['img_old'] not in html:
        html_done = True
    else:
        html_done = False
        assert job['img_old'] in html, f"{job['page']}: old img tag not found"
        assert job['cap_old_inner'] in html, f"{job['page']}: old figcaption not found"
        if not check:
            html = html.replace(job['img_old'], job['img_new'], 1)
            html = html.replace(job['cap_old_inner'], job['cap_en'], 1)
            page_path.write_text(html, encoding='utf-8')
            html = page_path.read_text(encoding='utf-8')

    alt_key = 'allsaints.accessibility.' + slug(job['alt_en']) if job['family']=='all-saints-and-all-souls' else None
    # generic key derivation from the family prefix and old key prefixes
    fam = job['family']
    alt_prefix = job['alt_old_key'].rsplit('.', 1)[0]
    cap_prefix = job['cap_old_key'].rsplit('.', 1)[0]
    alt_key = alt_prefix + '.' + slug(job['alt_en'])
    cap_key = cap_prefix + '.' + slug(job['cap_en'])

    en_copy_p = ROOT / f'locales/en/{fam}-copy.json'
    en_bind_p = ROOT / f'locales/en/{fam}-bindings.json'
    en_copy = json.loads(en_copy_p.read_text())
    contract = json.loads(en_bind_p.read_text())
    master_rel = contract['master']

    drop = set(job['drop_keys']) | {job['alt_old_key'], job['cap_old_key']}
    writes = {}
    # JSON/sha repair runs whenever keys or the master hash are stale (idempotent).
    root_html_now = (ROOT / master_rel).read_text(encoding='utf-8')
    new_src = re.search(r'src="([^"]+)"', job['img_new']).group(1)
    if not check and new_src not in root_html_now:
        print(f"{job['page']}: src edited; run node scripts/build-pages.mjs, then re-run this script")
        return True
    stale = (job['alt_old_key'] in en_copy or job['cap_old_key'] in en_copy
             or any(b['key'] in set(job['drop_keys']) for b in contract['bindings'])
             or en_copy.get(alt_key) != job['alt_en'] or en_copy.get(cap_key) != job['cap_en']
             or contract.get('masterSha256') != hashlib.sha256((ROOT / master_rel).read_bytes()).hexdigest()
             or contract.get('messages', {}).get(alt_key) != job['alt_en'])
    if stale and not check:
        for k in drop:
            en_copy.pop(k, None)
        en_copy[alt_key] = job['alt_en']
        en_copy[cap_key] = job['cap_en']
        bindings = []
        for b in contract['bindings']:
            if b['key'] in set(job['drop_keys']):
                continue
            if b['key'] == job['alt_old_key']:
                b = dict(b, key=alt_key, source=job['alt_en'])
            elif b['key'] == job['cap_old_key']:
                b = dict(b, key=cap_key, source=job['cap_en'])
            bindings.append(b)
        contract['bindings'] = bindings
        contract['messages'] = en_copy
        contract['masterSha256'] = hashlib.sha256((ROOT / master_rel).read_bytes()).hexdigest()
        writes[en_copy_p] = en_copy
        writes[en_bind_p] = contract
        for loc, (alt_t, cap_t) in job['tr'].items():
            p = ROOT / f'locales/{loc}/{fam}-copy.json'
            if not p.exists():
                continue
            local = json.loads(p.read_text())
            for k in drop:
                local.pop(k, None)
            local[alt_key] = alt_t
            local[cap_key] = cap_t
            if set(local) != set(en_copy):
                raise ValueError(f'{loc} {fam}: key set differs after update')
            writes[p] = local
        for p, obj in writes.items():
            p.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    elif check:
        root_html = (ROOT / master_rel).read_text(encoding='utf-8')
        new_src = re.search(r'src="([^"]+)"', job['img_new']).group(1)
        ok = (new_src in root_html and job['cap_en'] in root_html
              and en_copy.get(alt_key) == job['alt_en'] and en_copy.get(cap_key) == job['cap_en']
              and all(b['key'] not in set(job['drop_keys']) for b in contract['bindings'])
              and not any('Photograph:' in (b.get('source') or '') and b['key'].startswith((alt_key.split('.')[0])) and False for b in contract['bindings']))
        print(f"{job['page']}: {'OK' if ok else 'NOT APPLIED'}")
        return ok
    print(f"{job['page']}: applied")
    return True

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true')
    args = ap.parse_args()
    ok = True
    for job in JOBS:
        ok = apply_job(job, check=args.check) and ok
    sys.exit(0 if ok else 1)
