"""Generate the Arabic Chaplet from the current English master and keyed copy."""
from bs4 import BeautifulSoup
from pathlib import Path
import json
from i18n.catalog import ROOT, read_json

EN = '/saint-charbel-chaplet'
AR = '/ar/saint-charbel-chaplet'
SITE = 'https://marsharbel.com'


def render_chaplet(root=ROOT):
    catalog = read_json(root/'locales/ar/chaplet.json')
    required = {'hero.kicker','hero.title','hero.intro','hero.caption',*(f'hero.action{i}' for i in range(1,4)),
                'what.title','what.body1before','what.link','what.body1after','what.body2',
                'steps.title','steps.intro','prayers.title','prayers.fatherTitle','prayers.father',
                'prayers.fatherContext','prayers.gracesTitle','prayers.graces','when.title',
                'when.before1','when.link1','when.between1','when.link2','when.between2','when.link3','when.after3',
                'faq.title','continue.title','continue.before1','continue.link1','continue.between1',
                'continue.link2','continue.between2','continue.link3','continue.after3','sources.title',
                *(f'sources.{i}' for i in range(1,5)),
                *(f'faq.{kind}{i}' for kind in ('q','a') for i in range(1,6)),
                *(f'steps.{i}.{part}' for i in range(1,7) for part in ('title','before','strong','after'))}
    if set(catalog) != required or any(not isinstance(v,str) or not v.strip() or '<' in v for v in catalog.values()):
        raise ValueError('Arabic chaplet catalog missing/extra/unsafe values')
    soup = BeautifulSoup((root/'saint-charbel-chaplet.html').read_text(), 'html.parser')
    skip=soup.select_one('.skip-link')
    if skip is not None: skip.string=read_json(root/'locales/ar/common.json')['navigation.skip']
    soup.html['lang']='ar';soup.html['dir']='rtl';soup.html['data-authored-mirror']='chaplet'
    def one(selector):
        matches=soup.select(selector)
        if len(matches)!=1:raise ValueError(f'Chaplet master changed at {selector}: {len(matches)}')
        return matches[0]
    def text(selector,key):one(selector).string=catalog[key]
    def mixed(selector,keys):
        tag=one(selector)
        nodes=[n for n in tag.contents if getattr(n,'name',None)=='a']
        if len(nodes)!=len(keys)//2:raise ValueError(f'Chaplet master links changed at {selector}')
        tag.clear()
        for i,node in enumerate(nodes):
            tag.append(catalog[keys[2*i]])
            node.string=catalog[keys[2*i+1]]
            tag.append(node)
        tag.append(catalog[keys[-1]])
    # Keep the English layout, DOM structure, all media and links. Only replace text nodes.
    for selector,key in [('main .hero .kicker','hero.kicker'),('main h1','hero.title'),('main .hero > p','hero.intro'),
                         ('main .hero figcaption','hero.caption'),('main .section:nth-of-type(2) h2','what.title'),
                         ('main .section:nth-of-type(3) h2','steps.title'),('main .section:nth-of-type(3) .section-sub','steps.intro'),
                         ('main .section:nth-of-type(4) h2','prayers.title'),('main .section:nth-of-type(5) h2','when.title'),
                         ('main .section:nth-of-type(6) h2','faq.title'),('main .section:nth-of-type(7) h2','continue.title'),
                         ('main .section:nth-of-type(8) h2','sources.title')]:text(selector,key)
    for i,a in enumerate(one('main .hero .cta-row').select('a'),1):
        if i>3:raise ValueError('Extra chaplet CTA')
        a.string=catalog[f'hero.action{i}']
    text('main .section:nth-of-type(2) .story p:nth-of-type(2)','what.body2')
    mixed('main .section:nth-of-type(2) .story p:nth-of-type(1)',('what.body1before','what.link','what.body1after'))
    steps=soup.select('main .section:nth-of-type(3) article')
    if len(steps)!=6:raise ValueError('Chaplet bead step count changed')
    for i,card in enumerate(steps,1):
        card.h3.string=catalog[f'steps.{i}.title']
        para=card.p;strong=para.strong
        para.clear();para.append(catalog[f'steps.{i}.before']);strong.string=catalog[f'steps.{i}.strong'];para.append(strong);para.append(catalog[f'steps.{i}.after'])
    prayer=one('main .section:nth-of-type(4) .story')
    heads=prayer.select('h3');paras=prayer.select('p')
    if len(heads)!=2 or len(paras)!=3 or not paras[0].em or not paras[2].em:raise ValueError('Chaplet prayer structure changed')
    heads[0].string=catalog['prayers.fatherTitle'];heads[1].string=catalog['prayers.gracesTitle']
    paras[0].em.string=catalog['prayers.father'];paras[1].string=catalog['prayers.fatherContext'];paras[2].em.string=catalog['prayers.graces']
    mixed('main .section:nth-of-type(5) .story p',('when.before1','when.link1','when.between1','when.link2','when.between2','when.link3','when.after3'))
    faq=one('main .section:nth-of-type(6) .story');heads=faq.select('h3');paras=faq.select('p')
    if len(heads)!=5 or len(paras)!=5:raise ValueError('Chaplet FAQ changed')
    for i,(h,p) in enumerate(zip(heads,paras),1):h.string=catalog[f'faq.q{i}'];p.string=catalog[f'faq.a{i}']
    mixed('main .section:nth-of-type(7) .story p',('continue.before1','continue.link1','continue.between1','continue.link2','continue.between2','continue.link3','continue.after3'))
    sources=one('main .section:nth-of-type(8) ul').select('li a')
    if len(sources)!=4:raise ValueError('Chaplet source list changed')
    for i,a in enumerate(sources,1):a.string=catalog[f'sources.{i}']
    one('main .hero img')['alt']='الصورة التقليدية لمار شربل مخلوف مرتديًا قلنسوة الرهبان'
    # Head copy and FAQ schema from the same keyed source; leave English photo provenance untouched.
    title=catalog['hero.title']+' | طريقة صلاة مسبحة مار شربل'
    description=catalog['hero.intro']
    soup.title.string=title
    for selector,value in [('meta[name="description"]',description),('meta[property="og:title"]',title),
                           ('meta[property="og:description"]',description),('meta[name="twitter:title"]',title),
                           ('meta[name="twitter:description"]',description)]:one(selector)['content']=value
    canonical=SITE+AR
    og=soup.select_one('meta[property="og:locale"]')
    if og:og['content']='ar_AR'
    for tag in soup.select('meta[property="og:locale:alternate"]'):
        if tag.get('content')=='ar_AR':tag['content']='en_US'
    one('link[rel="canonical"]')['href']=canonical;one('meta[property="og:url"]')['content']=canonical
    # The build's managed hreflang pass rewrites this block from registry routes.
    # It starts from the already-updated English master, which includes Arabic.
    schemas=soup.select('script[type="application/ld+json"]')
    if len(schemas)!=2:raise ValueError('Chaplet schema count changed')
    article=json.loads(schemas[0].string);faq_schema=json.loads(schemas[1].string)
    article['name']=title;article['description']=description;article['url']=canonical
    article['breadcrumb']['itemListElement'][-1]['name']=catalog['hero.title'];article['breadcrumb']['itemListElement'][-1]['item']=canonical
    article['mainEntity']['headline']=catalog['hero.title'];article['inLanguage']='ar'
    for i,item in enumerate(faq_schema['mainEntity'],1):
        item['name']=catalog[f'faq.q{i}'];item['acceptedAnswer']['text']=catalog[f'faq.a{i}']
    for tag,obj in zip(schemas,(article,faq_schema)):
        tag.string=json.dumps(obj,ensure_ascii=False,indent=2).replace('<','\\u003c')
    # Absolute internal paths prevent /ar/ relative resolution errors. Map only authored destinations.
    mapped={'saint-charbel-novena':'/ar/novena','./saint-charbel-novena':'/ar/novena',
            'prayer-library':'/prayer-library','./prayer-library#find-a-prayer':'/prayer-library#find-a-prayer',
            'visit-annaya':'/ar/annaya','22nd-of-the-month':'/ar/22nd-of-the-month',
            'saint-charbel-feast-day':'/ar/feast-day','./en/prayers':'/ar/prayers'}
    for a in soup.select('a[href]'):
        href=a['href']
        if href in mapped:a['href']=mapped[href]
        elif href.startswith('./'):a['href']='/'+href[2:]
    for tag in soup.select('script[src],link[href],img[src]'):
        attr='src' if tag.has_attr('src') else 'href';url=tag[attr]
        if url.startswith('./'):tag[attr]='/'+url[2:]
        elif not url.startswith(('/','#','https://','http://')):tag[attr]='/'+url
    # Shared navigation chrome is keyed in the existing authored prayer mirror.
    english_header=read_json(root/'locales/en/mirrors/prayers.json')
    arabic_header=read_json(root/'locales/ar/mirrors/prayers.json')
    chrome={value:arabic_header[key] for key,value in english_header.items()
            if key.startswith('header.') and key in arabic_header and isinstance(value,str)}
    chrome.update({'Saint Charbel':'مار شربل','Primary':'التنقل الرئيسي'})
    for node in one('header.topbar').find_all(string=True):
        original=str(node)
        stripped=original.strip()
        if stripped in chrome:node.replace_with(original.replace(stripped,chrome[stripped]))
    one('header.topbar nav')['aria-label']='التنقل الرئيسي'
    one('header.topbar a.brand')['href']='/ar/'
    article['breadcrumb']['itemListElement'][0]['name']='الرئيسية'
    article['breadcrumb']['itemListElement'][1]['name']='الصلاة'
    schemas[0].string=json.dumps(article,ensure_ascii=False,indent=2).replace('<','\\u003c')
    footer=one('footer .site-shell');footer.string=catalog['hero.title']+'. الكاتب: صلّ من أجل من أنشأ هذا الموقع.'
    return {root/'ar/saint-charbel-chaplet.html':str(soup)}
