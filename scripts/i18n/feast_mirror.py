"""Arabic feast mirror: preserve the English DOM and fail on untranslated master edits."""
from bs4 import BeautifulSoup
import json
from i18n.catalog import ROOT, read_json


def render_feast(root=ROOT):
    copy=read_json(root/'locales/ar/feast-mirror.json')
    soup=BeautifulSoup((root/'saint-charbel-feast-day.html').read_text(),'html.parser')
    skip=soup.select_one('.skip-link')
    if skip is not None: skip.string=read_json(root/'locales/ar/common.json')['navigation.skip']
    nodes=[n for n in soup.main.find_all(string=True) if n.strip()]
    if set(copy['slots'])!={str(i) for i in range(len(nodes))}:raise ValueError('Feast slot count changed')
    for i,node in enumerate(nodes):
        slot=copy['slots'][str(i)]
        if ' '.join(str(node).split())!=slot['source']:raise ValueError(f'Feast master changed at slot {i}')
        if not isinstance(slot['text'],str) or not slot['text'].strip() or '<' in slot['text']:raise ValueError(f'Unsafe feast slot {i}')
        old=str(node)
        leading=old[:len(old)-len(old.lstrip())];trailing=old[len(old.rstrip()):]
        node.replace_with(leading+slot['text']+trailing)
    soup.html['lang']='ar';soup.html['dir']='rtl';soup.html['data-authored-mirror']='feast'
    title=copy['title'];description=soup.select_one('main .hero > p').get_text(' ',strip=True);url='https://marsharbel.com/ar/feast-day'
    soup.title.string=title
    for selector,value in [('meta[name=description]',description),('meta[property="og:title"]',title),('meta[property="og:description"]',description),('meta[name="twitter:title"]',title),('meta[name="twitter:description"]',description),('meta[property="og:url"]',url)]:soup.select_one(selector)['content']=value
    soup.select_one('link[rel=canonical]')['href']=url
    for tag in soup.select('meta[property="og:locale:alternate"]'):
        if tag.get('content')=='ar_AR':tag['content']='en_US'
    og=soup.select_one('meta[property="og:locale"]')
    if og:og['content']='ar_AR'
    soup.select_one('main img')['alt']=copy['alt']
    schemas=soup.select('script[type="application/ld+json"]')
    if len(schemas)!=2:raise ValueError('Feast schema count changed')
    page=json.loads(schemas[0].string)
    page.update(name=title,description=description,url=url,inLanguage='ar')
    for item,name in zip(page['breadcrumb']['itemListElement'],('الرئيسية','الصلاة',copy['slots']['1']['text'])):item['name']=name
    page['breadcrumb']['itemListElement'][0]['item']='https://marsharbel.com/ar/'
    page['breadcrumb']['itemListElement'][-1]['item']=url;page['mainEntity']['headline']=copy['slots']['1']['text']
    schemas[0].string=json.dumps(page,ensure_ascii=False,indent=2).replace('<','\\u003c')
    faq=json.loads(schemas[1].string)
    faq_section=next(sec for sec in soup.select('main section') if sec.h2 and sec.h2.get_text()=='أسئلة شائعة')
    for item,h,p in zip(faq['mainEntity'],faq_section.select('h3'),faq_section.select('p')):
        item['name']=h.get_text();item['acceptedAnswer']['text']=p.get_text()
    schemas[1].string=json.dumps(faq,ensure_ascii=False,indent=2).replace('<','\\u003c')
    mapped={'saint-charbel-novena':'/ar/novena','22nd-of-the-month':'/ar/22nd-of-the-month','saint-charbel-feast-day':'/ar/feast-day','en/prayers':'/ar/prayers','visit-annaya':'/ar/annaya','history':'/ar/biography','miracles':'/ar/miracles/'}
    # Resolve a queued Chaplet only when its authored route exists in this checkout.
    mirrors=read_json(root/'locales/registry.json').get('authoredMirrors',{})
    if 'chaplet' in mirrors and 'ar' in mirrors['chaplet']['routes']:
        mapped['saint-charbel-chaplet']=mirrors['chaplet']['routes']['ar']
    for a in soup.select('a[href]'):
        href=a['href'];path=href.removeprefix('./')
        if path in mapped:a['href']=mapped[path]
        elif href.startswith('./'):a['href']='/'+path
        elif not href.startswith(('/','#','https://','http://')):a['href']='/'+href
    for tag in soup.select('script[src],link[href],img[src]'):
        attr='src' if tag.has_attr('src') else 'href';href=tag[attr]
        if href.startswith('./'):tag[attr]='/'+href[2:]
        elif not href.startswith(('/','#','https://','http://')):tag[attr]='/'+href
    en=read_json(root/'locales/en/mirrors/prayers.json');ar=read_json(root/'locales/ar/mirrors/prayers.json')
    chrome={v:ar[k] for k,v in en.items() if k.startswith('header.') and k in ar and isinstance(v,str)}
    chrome.update({'Saint Charbel':'مار شربل','Primary':'التنقل الرئيسي'})
    chrome.update(copy.get('chrome',{}))
    for node in soup.select_one('header.topbar').find_all(string=True):
        old=str(node);key=old.strip()
        if key in chrome:node.replace_with(old.replace(key,chrome[key]))
    soup.select_one('header nav')['aria-label']='التنقل الرئيسي';soup.select_one('header a.brand')['href']='/ar/'
    soup.select_one('footer .site-shell').string='عيد مار شربل. الكاتب: صلّ من أجل من أنشأ هذا الموقع.'
    return {root/'ar/feast-day.html':str(soup)}
