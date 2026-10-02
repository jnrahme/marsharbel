"""Locale-agnostic feast mirror: preserve the English DOM and fail on untranslated master edits."""
from i18n.metadata import og_locales
from i18n.catalog import page_url, topic_locales
from i18n.guarded_dom import translate_slots
from bs4 import BeautifulSoup
import json
from i18n.catalog import ROOT, read_json


def render_feast_locale(root=ROOT, lang='ar', registry=None):
    registry=registry or read_json(root/'locales/registry.json')
    config=registry['domMirrors']['feast']
    copy=read_json(root/f'locales/{lang}'/config['catalog'])
    soup=BeautifulSoup((root/(config['english'].lstrip('/')+'.html')).read_text(),'html.parser')
    skip=soup.select_one('.skip-link')
    if skip is not None: skip.string=read_json(root/f'locales/{lang}/common.json')['navigation.skip']
    translate_slots(soup.main, copy['slots'], 'Feast')
    from i18n.encyclopedia_trail import apply_trail
    apply_trail(soup, root, lang, '/history')
    soup.html['lang']=lang;soup.html['dir']=registry['locales'][lang]['direction'];soup.html['data-authored-mirror']='feast'
    title=copy['title'];description=soup.select_one('main .hero > p:not(.enc-trail)').get_text(' ',strip=True);url=registry['site']+config['routes'][lang]
    soup.title.string=title
    for selector,value in [('meta[name=description]',description),('meta[property="og:title"]',title),('meta[property="og:description"]',description),('meta[name="twitter:title"]',title),('meta[name="twitter:description"]',description),('meta[property="og:url"]',url)]:soup.select_one(selector)['content']=value
    soup.select_one('link[rel=canonical]')['href']=url
    for tag in soup.select('meta[property="og:locale:alternate"]'):
        if tag.get('content')==og_locales(registry)[lang]:tag['content']=og_locales(registry)['en']
    og=soup.select_one('meta[property="og:locale"]')
    if og:og['content']=og_locales(registry)[lang]
    soup.select_one('main img')['alt']=copy['alt']
    schemas=soup.select('script[type="application/ld+json"]')
    if len(schemas)!=2:raise ValueError('Feast schema count changed')
    page=json.loads(schemas[0].string)
    page.update(name=title,description=description,url=url,inLanguage=lang)
    if len(copy['breadcrumbs'])+1!=len(page['breadcrumb']['itemListElement']):raise ValueError('Feast breadcrumb count changed')
    for item,name in zip(page['breadcrumb']['itemListElement'],(*copy['breadcrumbs'],copy['slots']['1']['text'])):item['name']=name
    page['breadcrumb']['itemListElement'][0]['item']=registry['site']+registry['locales'][lang]['home']
    page['breadcrumb']['itemListElement'][-1]['item']=url;page['mainEntity']['headline']=copy['slots']['1']['text']
    schemas[0].string=json.dumps(page,ensure_ascii=False,indent=2).replace('<','\\u003c')
    faq=json.loads(schemas[1].string)
    candidates=[sec for sec in soup.select('main section') if sec.h2 and len(sec.select('h3'))==len(faq['mainEntity'])]
    if len(candidates)!=1:raise ValueError('Feast FAQ section is ambiguous')
    faq_section=candidates[0]
    if len(faq_section.select('p'))!=len(faq['mainEntity']):raise ValueError('Feast FAQ answer count changed')
    for item,h,p in zip(faq['mainEntity'],faq_section.select('h3'),faq_section.select('p')):
        item['name']=h.get_text();item['acceptedAnswer']['text']=p.get_text()
    schemas[1].string=json.dumps(faq,ensure_ascii=False,indent=2).replace('<','\\u003c')
    mapped={}
    for topic, topic_config in registry['topics'].items():
        if lang in topic_locales(registry, topic):
            mapped[topic_config['relatedEnglish'].strip('/')] = page_url(registry, lang, topic)
    for mirror in registry.get('authoredMirrors',{}).values():
        if lang in mirror['routes']:
            mapped[mirror['english'].strip('/')] = mirror['routes'][lang]
    for mirror in registry.get('domMirrors',{}).values():
        if lang in mirror['routes']:
            mapped[mirror['english'].strip('/')] = mirror['routes'][lang]
    # Prayer master redirects into this legacy guide cluster.
    if lang in topic_locales(registry, 'prayers'):
        mapped['en/prayers'] = page_url(registry, lang, 'prayers')
    mapped={key:value for key,value in mapped.items() if key in copy['localizedLinks']}
    for a in soup.select('a[href]'):
        href=a['href'];path=href.removeprefix('./')
        if path in mapped:a['href']=mapped[path]
        elif href.startswith('./'):a['href']='/'+path
        elif not href.startswith(('/','#','https://','http://')):a['href']='/'+href
    for tag in soup.select('script[src],link[href],img[src]'):
        attr='src' if tag.has_attr('src') else 'href';href=tag[attr]
        if href.startswith('./'):tag[attr]='/'+href[2:]
        elif not href.startswith(('/','#','https://','http://')):tag[attr]='/'+href
    en=read_json(root/'locales/en/mirrors/prayers.json');local=read_json(root/f'locales/{lang}/mirrors/prayers.json')
    chrome={v:local[k] for k,v in en.items() if k.startswith('header.') and k in local and isinstance(v,str)}
    chrome.update(copy.get('chrome',{}))
    for node in soup.select_one('header.topbar').find_all(string=True):
        old=str(node);key=old.strip()
        if key in chrome:node.replace_with(old.replace(key,chrome[key]))
    soup.select_one('header nav')['aria-label']=copy['primaryLabel'];soup.select_one('header a.brand')['href']=registry['locales'][lang]['home']
    soup.select_one('footer .site-shell').string=copy['footer']
    return {root/(config['routes'][lang].lstrip('/')+'.html'):str(soup)}


def render_feast(root=ROOT):
    registry=read_json(root/'locales/registry.json')
    result={}
    for lang in registry['domMirrors']['feast']['routes']:
        result.update(render_feast_locale(root,lang,registry))
    return result
