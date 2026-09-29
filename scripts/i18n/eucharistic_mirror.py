GTAG_BLOCK = '''<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-CJX1M0VFKP"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-CJX1M0VFKP');
</script>'''

"""Render complete localized Eucharistic mirrors from the reviewed English pages.

The English catalog owns structure, photo provenance and sources. Each locale catalog
owns only copy. Failure is preferable to a silent English fallback.
"""
from pathlib import Path
import json
import re
from bs4 import BeautifulSoup, NavigableString
from i18n.catalog import ROOT, read_json

SLUGS = ('lanciano', 'bolsena-orvieto', 'siena', 'santarem', 'sokolka', 'legnica', 'ludbreg')
PROVENANCE = ('image', 'credit', 'licenseurl', 'photo', 'source', 'source2')
COUNTRIES = {'lanciano':'Italy', 'bolsena-orvieto':'Italy', 'siena':'Italy', 'santarem':'Portugal', 'sokolka':'Poland', 'legnica':'Poland', 'ludbreg':'Croatia'}
TEXT_ONLY = ('title', 'place', 'era', 'label', 'alt', 'license', 'sourceLabel', 'source2Label', 'lead', 'reflection')
HTML_TAG = re.compile(r'<\s*/?\s*[a-zA-Z!]')


def validate(en, local, lang):
    if set(local) != set(en) or set(local['hub']) != set(en['hub']) or set(local['stories']) != set(en['stories']):
        raise ValueError(f'{lang}: catalog shape differs from English')
    for slug in SLUGS:
        source, translated = en['stories'][slug], local['stories'][slug]
        if set(translated) != set(source) or len(translated['sections']) != len(source['sections']):
            raise ValueError(f'{lang}/{slug}: catalog or section count differs')
        if any(len(pair) != 2 for pair in translated['sections']):
            raise ValueError(f'{lang}/{slug}: section title/body missing')
        for field in PROVENANCE:
            if field not in source: continue
            if translated[field] != source[field]:
                raise ValueError(f'{lang}/{slug}: changed provenance {field}')
    def walk(value):
        if isinstance(value, dict):
            for item in value.values():walk(item)
        elif isinstance(value, list):
            for item in value:walk(item)
        elif not isinstance(value, str) or not value.strip() or HTML_TAG.search(value):
            raise ValueError(f'{lang}: blank or markup in catalog')
    walk(local)


def sole(soup, selector):
    found = soup.select(selector)
    if len(found) != 1: raise ValueError(f'Expected one element: {selector}, found {len(found)}')
    return found[0]


def replace_text(node, source, target):
    matches = [n for n in node.descendants if isinstance(n, NavigableString) and str(n) == source]
    if not matches: raise ValueError(f'Cannot locate English text {source[:60]!r} in {node.name}')
    for match in matches: match.replace_with(target)


def render_eucharistic(root=ROOT, registry=None):
    registry = registry or read_json(root/'locales/registry.json')
    en = read_json(root/'locales/en/eucharistic-miracles.json')
    domain = registry['site']
    routes = {slug:{lang:f'/{lang}/miracles/eucharistic/{slug}' for lang in registry['locales'] if lang != 'en'} for slug in SLUGS}
    routes['index'] = {lang:f'/{lang}/miracles/eucharistic/' for lang in registry['locales'] if lang != 'en'}
    for slug in routes: routes[slug]['en'] = '/miracles/eucharistic/' + ('' if slug=='index' else slug)
    source = {slug:(root/'miracles/eucharistic'/('index.html' if slug=='index' else slug+'.html')).read_text() for slug in routes}
    result = {}
    english_header = read_json(root/'locales/en/mirrors/prayers.json')
    chrome_lookup = {v:k for k,v in english_header.items() if k.startswith('header.')}
    for lang in registry['locales']:
        if lang == 'en': continue
        local = read_json(root/f'locales/{lang}/eucharistic-miracles.json')
        validate(en, local, lang)
        common = read_json(root/f'locales/{lang}/common.json')
        headers = root/f'locales/{lang}/mirrors/qadisha.json'
        if not headers.exists():headers = root/f'locales/{lang}/mirrors/prayers.json'
        header = read_json(headers)
        for slug, english in source.items():
            soup = BeautifulSoup(english,'html.parser')
            soup.html['lang'] = lang
            soup.html['dir'] = registry['locales'][lang]['direction']
            OG_MAP = {'en':'en_US','ar':'ar_AR','es':'es_ES','fr':'fr_FR','pt':'pt_PT','it':'it_IT','de':'de_DE','pl':'pl_PL'}
            for stale in list(soup.select('meta[property="og:locale"],meta[property="og:locale:alternate"]')):
                stale.extract()
            anchor = soup.find('meta', property='og:url') or soup.find('link', rel='canonical')
            for code in [lang] + [k for k in OG_MAP if k != lang]:
                t = soup.new_tag('meta'); t['property'] = 'og:locale' if code == lang else 'og:locale:alternate'; t['content'] = OG_MAP[code]
                anchor.insert_after(t); anchor = t
            if 'G-CJX1M0VFKP' not in str(soup.head):
                head_tag = soup.find('meta', attrs={'charset': True})
                if head_tag:
                    from bs4 import BeautifulSoup as _BS
                    frag = _BS(GTAG_BLOCK, 'html.parser')
                    for node in list(frag.contents):
                        head_tag.insert_after(node); head_tag = node
            soup.html['data-authored-mirror'] = ''
            catalog = local['hub'] if slug=='index' else local['stories'][slug]
            original = en['hub'] if slug=='index' else en['stories'][slug]
            # Translate all catalog-backed text and metadata, preserving link destinations.
            pairs = [(v,catalog[k]) for k,v in original.items() if k in TEXT_ONLY or slug=='index']
            pairs = [(a,b) for a,b in pairs if isinstance(a,str) and a!=b and not a.startswith('https://')]
            if slug!='index':
                pairs += [(a,b) for pair_en,pair_local in zip(original['sections'],catalog['sections']) for a,b in zip(pair_en,pair_local)]
                pairs += [(v,local['hub'][k]) for k,v in en['hub'].items() if isinstance(v,str) and k in ('back','photo','reflection','sources','updated','note','originalPhoto')]
            # Longest first avoids a shorter title replacing a substring inside a longer label.
            for text in soup.find_all(string=True):
                if text.parent.name == 'script':continue
                translated = str(text)
                for before,after in sorted(pairs,key=lambda pair:len(pair[0]),reverse=True):
                    translated = translated.replace(before,after)
                if translated != str(text):text.replace_with(translated)
            for tag in soup.find_all(True):
                for attribute in ('content','alt','aria-label'):
                    if tag.has_attr(attribute):
                        value = tag[attribute]
                        for before,after in sorted(pairs,key=lambda pair:len(pair[0]),reverse=True):value=value.replace(before,after)
                        tag[attribute]=value
            if slug=='index':
                for country,key in [('Italy','filterItaly'),('Portugal','filterPortugal'),('Poland','filterPoland'),('Croatia','filterCroatia')]:
                    button=sole(soup,f'button[data-filter="{country}"]')
                    button.string=local['hub'][key]
                for story_slug in SLUGS:
                    # Filtering uses invariant data-country codes; all visible labels are translated.
                    row=sole(soup,f'#story-{story_slug}')
                    row['data-country']=COUNTRIES[story_slug]
                    card=sole(row,'.euch-card')
                    card['href']='./'+story_slug
                    translated_story=local['stories'][story_slug]
                    card.select_one('small').string=translated_story['place']+' · '+translated_story['era']
                    card.select_one('strong').string=translated_story['title']
                    card.select_one('.euch-card-copy > span').string=translated_story['lead']
                    card.select_one('em').clear()
                    card.select_one('em').append(local['hub']['browse']+' →')
                    sole(row,'img')['alt']=translated_story['alt']
                    sole(soup,f'.euch-places a[href="#story-{story_slug}"]').string=translated_story['place']
                sole(soup,'.euch-heading .euch-eyebrow').string=f'01 / {len(SLUGS):02d}'
            else:
                for section, pair in zip(soup.select('.euch-chapter'), catalog['sections']):
                    sole(section,'h2').string=pair[0]
                    sole(section,'p:not(.euch-eyebrow)').string=pair[1]
                for back in soup.select('.euch-back'):
                    back['href']='./'
                    back.string='← '+local['hub']['back']
                sole(soup,'.euch-reflection h2').string=local['hub']['reflection']
                sole(soup,'.euch-reflection p').string=catalog['reflection']
                sole(soup,'.euch-sources h2').string=local['hub']['sources']
                sole(soup,'.euch-sources p:first-of-type a').string=catalog['sourceLabel']
                if 'source2' in catalog:
                    links=soup.select('.euch-sources p a')
                    if len(links)!=2: raise ValueError(f'{lang}/{slug}: missing second source')
                    links[1].string=catalog['source2Label']
                # v3 image credits include an English production note not present in the catalog.
                caption=sole(soup,'.euch-feature-photo figcaption')
                replace_text(caption,'; resized to WebP for this site. ', '; '+{
                    'ar':'حُوّلت إلى صيغة WebP لهذا الموقع. ', 'fr':'convertie au format WebP pour ce site. ',
                    'es':'convertida a WebP para este sitio. ', 'pt':'convertida em WebP para este site. ',
                    'it':'convertita in WebP per questo sito. ', 'de':'für diese Website als WebP verkleinert. ',
                    'pl':'przeskalowane do formatu WebP dla tej strony. '}[lang])
                for txt in caption.find_all(string=True):
                    fixed=str(txt).replace(' ; ','; ').replace(' ,',',').replace(' .','.').replace('CC0 1.0 ;','CC0 1.0;')
                    if fixed!=str(txt):txt.replace_with(fixed)
                # Avoid literal punctuation left as separate nodes around links.
                for child in caption.contents:
                    if isinstance(child, str):
                        fixed=str(child).replace(' ; ','; ').replace(' .','.').replace(' ,',',')
                        if fixed!=str(child):child.replace_with(fixed)
            # Site chrome follows the existing reviewed translation dictionary.
            for label in soup.select('.topbar .brand span'):
                if 'brand-mark' not in label.get('class',[]):label.string=header['header.siteBrand']
            for link in soup.select('.topbar .links a'):
                text=link.get_text(strip=True).replace('▾','')
                if text=='Miracles & Reports':
                    link.string=header['header.miraclesAndReports']
                else:
                    key=chrome_lookup.get(text)
                    if key and key in header:
                        # Preserve the chevron child in dropdown parent anchors.
                        child=link.find('span',class_='nav-chev')
                        if child:child.extract()
                        link.clear();link.append(header[key]);
                        if child:link.append(child)
                href=link.get('href','')
                if href.startswith('../../'):
                    target='/'+href[6:]
                    # The collection hub links to its own locale mirror.
                    if target.rstrip('/')=='/miracles/eucharistic':
                        target=f'/{lang}/miracles/eucharistic/'
                        link['href']=target
                        continue
                    # Redirect only published paths; never invent a translated route.
                    for topic, config in registry['topics'].items():
                        english_route=config['relatedEnglish']
                        if target.rstrip('/')==english_route.rstrip('/') and lang in config.get('locales',registry['locales']):
                            target=f'/{lang}/{registry["locales"][lang]["slugs"][topic]}'
                            break
                    for mirror in registry.get('authoredMirrors',{}).values():
                        if target.rstrip('/')==mirror['english'].rstrip('/') and lang in mirror['routes']:
                            target=mirror['routes'][lang];break
                    link['href']=target
            sole(soup,'.topbar .brand')['href']=registry['locales'][lang]['home']
            for tag in soup.select('title'):
                tag.string=tag.get_text().replace('Saint Charbel',common['site.brand'])
            if slug=='index':
                caption=sole(soup,'.euch-hero-caption')
                caption.contents[0].replace_with(local['stories']['lanciano']['alt']+' · ')
                caption.select('a')[1].string=local['stories']['lanciano']['license']
            # Update remaining text attributes and captions after central translations.
            for tag in soup.select('.euch-card img, .euch-feature-photo img'):
                original_slug=slug if slug!='index' else tag.parent.parent.parent.get('id','').replace('story-','')
                if original_slug in local['stories']: tag['alt']=local['stories'][original_slug]['alt']
            sole(soup,'.topbar .links')['aria-label']=header.get('header.primaryLabel',common['navigation.home'])
            if slug=='index':
                sole(soup,'.euch-hero-content .euch-action')['href']='#journey'
            # The page remains the English skeleton, including all images, sections and interactions.
            # Rewrite assets to root paths so the deeper locale prefix cannot affect loading.
            for tag in soup.find_all(['link','script','img']):
                attr='href' if tag.name=='link' else 'src'
                if tag.has_attr(attr) and tag[attr].startswith('../../'):
                    tag[attr]='/'+tag[attr][6:]
            current=domain+routes[slug][lang]
            sole(soup,'link[rel="canonical"]')['href']=current
            for selector in ('meta[property="og:url"]',):sole(soup,selector)['content']=current
            for tag in soup.select('link[rel=alternate]'): tag.decompose()
            for code in reversed((*registry['locales'],'x-default')):
                actual='en' if code=='x-default' else code
                node=soup.new_tag('link',rel='alternate',hreflang=code,href=domain+routes[slug][actual])
                sole(soup,'link[rel="canonical"]').insert_after(node)
            for script in soup.select('script[type="application/ld+json"]'):
                data=json.loads(script.string)
                data['headline']=catalog['title'] if slug!='index' else local['hub']['title']
                data['description']=catalog['lead'] if slug!='index' else local['hub']['intro']
                data['url']=current;data['inLanguage']=lang
                crumbs=data['breadcrumb']['itemListElement']
                crumbs[0]['name']=common['navigation.home'];crumbs[0]['item']=domain+registry['locales'][lang]['home']
                crumbs[1]['name']=header['header.miracles']
                if lang=='ar':crumbs[1]['item']=domain+'/ar/miracles/'
                crumbs[-1]['name']=catalog['title'] if slug!='index' else local['hub']['title']
                crumbs[-1]['item']=current
                if slug!='index':crumbs[-2]['name']=local['hub']['title'];crumbs[-2]['item']=domain+routes['index'][lang]
                script.string=json.dumps(data,ensure_ascii=False).replace('<','\\u003c')
            if slug=='index':path=root/lang/'miracles/eucharistic/index.html'
            else:path=root/lang/'miracles/eucharistic'/f'{slug}.html'
            result[path]='<!doctype html>\n'+str(soup).lstrip().removeprefix('<!DOCTYPE html>\n').lstrip()
    return result
