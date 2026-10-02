"""Shared Travel routing, navigation and page frame, with no IO side effects."""
from html import escape
import re
import json
from bs4 import BeautifulSoup
from i18n.catalog import read_json,page_url,topic_locales

def route_for(root,registry,english,code):
    if code=='en':return english
    for config in registry.get('authoredMirrors',{}).values():
        if config['english']==english and code in config['routes']:return config['routes'][code]
    if english in read_json(root/'locales/travel-routes.json')['destinations']:return english
    for topic,config in registry['topics'].items():
        if config['relatedEnglish']==english and code in topic_locales(registry,topic):return page_url(registry,code,topic)
    return english

def directory(root,registry,code):
    config=read_json(root/'locales/travel-routes.json');copy=read_json(root/f'locales/{code}/travel.json')
    images={'qadisha':('/media/annaya/qadisha-valley-aerial.webp','Evan Williams / CC BY-SA 4.0'),'qannoubine':('/media/annaya/qannoubine-church.webp','Hussein Sabboury / CC0'),'qozhaya':('/media/annaya/qozhaya-monastery.webp','Yellaban / Wikimedia Commons')}

    chunks=[]
    for group,keys in config['groups'].items():
        ident='planning' if group=='planning' else 'destinations-'+group
        chunks.append(f'<section class="travel-directory" id="{ident}"><h2>{escape(copy[group+"Group"])}</h2>')
        photo_keys=[key for key in keys if key in images]
        plain_keys=[key for key in keys if key not in images]
        chunks.append('<div class="travel-destination-list">' if photo_keys else '<div class="travel-link-list">')
        keys=photo_keys+plain_keys
        for key in keys:
            if photo_keys and plain_keys and key==plain_keys[0]:chunks.append('</div><div class="travel-link-list">')
            route=route_for(root,registry,config['routes'][key],code);label=escape(copy[key]);image=images.get(key)
            picture=f'<figure><img src="{image[0]}" alt="" loading="lazy" decoding="async" width="1200" height="750" /></figure>' if image else ''
            credit=f'<p class="travel-credit">{escape(image[1])}</p>' if image else ''
            chunks.append(f'<div><a class="travel-place{ " travel-place-text" if not image else ""}" href="{route}">{picture}<h3>{label}</h3></a>{credit}</div>')
        chunks.append('</div></section>')
    return '<div id="destinations">'+''.join(chunks)+'</div>'

def travel_frame(text,root,code,route,registry):
    """Idempotent frame: nav has correct route/current state; content is preserved."""
    # A synthetic/unpublished locale has no Travel chrome or catalog requirement.
    if code not in registry.get('authoredMirrors',{}).get('travel',{}).get('routes',{}):return text
    cfg=read_json(root/'locales/travel-routes.json');copy=read_json(root/f'locales/{code}/travel.json');common=read_json(root/f'locales/{code}/common.json')
    hub=route_for(root,registry,cfg['hub'],code)
    def header(m):
        s=m[0]
        # Only Travel group parents change, never ordinary visit links.
        s=re.sub(r'(<a\b[^>]*class=["\'][^"\']*nav-parent[^"\']*["\'][^>]*href=["\'])([^"\']*(?:visit-annaya|annaya|travel))(["\'])',lambda x:x[1]+hub+x[3],s)
        # Locate the Travel group by the now canonical hub parent.
        pattern=r'(<div class="nav-group">\s*<a\b[^>]*href=["\']'+re.escape(hub)+r'["\'][^>]*>.*?</a>\s*<div class="nav-sub">)(.*?)(</div></div>)'
        def group(g):
            parent=g[1];body=g[2]
            body=re.sub(r' class="active"| aria-current="page"','',body)
            body=re.sub(r'\s*<a\b[^>]*href=["\']'+re.escape(hub)+r'["\'][^>]*>.*?</a>','',body)
            current=' class="active" aria-current="page"' if route==hub else ''
            body=f'\n        <a{current} href="{hub}">{escape(copy["hubLabel"])}</a>'+body
            if route!=hub:body=re.sub(r'(<a)( href=["\']'+re.escape(route)+r'["\'])',r'\1 class="active" aria-current="page"\2',body)
            parent=re.sub(r'class="(?:active )?nav-parent"','class="active nav-parent"' if route in travel_routes(root,registry,code) else 'class="nav-parent"',parent)
            return parent+body+g[3]
        s=re.sub(pattern,group,s,flags=re.S)
        return s
    if code!='en':text=re.sub(r'<header\b.*?</header>',header,text,count=1,flags=re.S)
    standalone=route==registry['locales'][code]['home'] or (code in registry['topics']['annaya'].get('locales',[]) and route==page_url(registry,code,'annaya'))
    if route not in travel_routes(root,registry,code) and not standalone:return text
    # Standalone language-home/guide chrome keeps its existing single language control.
    if 'class="locale-nav"' in text:
        link=f'<a class="travel-hub-return" href="{hub}">{escape(copy["hubLabel"])}</a>'
        if 'class="travel-hub-return"' not in text:text=text.replace('</header>','<div class="shell" style="padding-block:.8rem">'+link+'</div></header>',1)
        return text
    if standalone:return text
    if route==hub or route.endswith('/travel') or '/annaya-tour' not in route:
        if '/travel.css?' not in text:text=text.replace('</head>','<link rel="stylesheet" href="/travel.css?v=20261002-2" />\n</head>',1)
        text=re.sub(r'(href=["\']/travel.css\?)[^"\']+',r'\g<1>v=20261002-2',text)
        def body_class(m):
            attrs=m[1]
            if 'travel-page' not in attrs:
                if re.search(r'class=["\']',attrs):attrs=re.sub(r'(class=["\'])([^"\']*)',r'\1\2 travel-page travel-destination',attrs,count=1)
                else:attrs+=' class="travel-page travel-destination"'
            return '<body'+attrs+'>'
        text=re.sub(r'<body([^>]*)>',body_class,text,count=1)
    # Promote the existing lead photograph without inventing content or changing catalog text.
    hero_match=re.search(r'<section class="hero">(.*?)</section>',text,re.S)
    if hero_match and '/annaya-tour' not in route:
        hero=hero_match[1]
        figure=re.search(r'<figure class="hero-figure">.*?</figure>',hero,re.S)
        if figure:
            picture=figure[0].replace('loading="lazy"','loading="eager" fetchpriority="high"')
            remaining=re.sub(r'(?m)^[ \t]+$', '', hero[:figure.start()]+hero[figure.end():])
            text=text[:hero_match.start()]+ '<section class="hero travel-split-hero">'+picture+'<div class="travel-summary">'+remaining+'</div></section>'+text[hero_match.end():]
    # One generated breadcrumb uses cataloged home/Travel labels and the page's existing H1.
    soup=BeautifulSoup(text,'html.parser');title=soup.h1.get_text(' ',strip=True) if soup.h1 else ''
    crumb=f'<!-- i18n-travel-frame:start -->\n<nav class="travel-breadcrumb" aria-label="{escape(common["navigation.contents"])}"><a href="{registry["locales"][code]["home"]}">{escape(common["navigation.home"])}</a><span aria-hidden="true">/</span>'
    if route!=hub:crumb+=f'<a href="{hub}">{escape(copy["hubLabel"])}</a><span aria-hidden="true">/</span>'
    crumb+=f'<span aria-current="page">{escape(copy["hubLabel"] if route==hub else title)}</span></nav>\n<!-- i18n-travel-frame:end -->'
    text=re.sub(r'<!-- i18n-travel-frame:start -->.*?<!-- i18n-travel-frame:end -->\s*','',text,flags=re.S)
    text=re.sub(r'(<main\b[^>]*>)',lambda m:m[1]+'\n'+crumb,text,count=1)
    schema={'@context':'https://schema.org','@type':'BreadcrumbList','itemListElement':[
        {'@type':'ListItem','position':1,'name':common['navigation.home'],'item':registry['site']+registry['locales'][code]['home']},
        {'@type':'ListItem','position':2,'name':copy['hubLabel'],'item':registry['site']+hub}]}
    if route!=hub:schema['itemListElement'].append({'@type':'ListItem','position':3,'name':title,'item':registry['site']+route})
    text=re.sub(r'<!-- i18n-travel-schema:start -->.*?<!-- i18n-travel-schema:end -->\s*','',text,flags=re.S)
    nested=False
    def update_schema(m):
        nonlocal nested
        try:data=json.loads(m[2])
        except ValueError:return m[0]
        def replace_trail(node):
            nonlocal nested
            if isinstance(node,dict):
                if 'breadcrumb' in node:
                    node['breadcrumb']={k:v for k,v in schema.items() if k!='@context'};nested=True
                for key,value in node.items():
                    if key!='breadcrumb':replace_trail(value)
            elif isinstance(node,list):
                for value in node:replace_trail(value)
        replace_trail(data)
        if '"breadcrumb"' not in m[2]:return m[0]
        return m[1]+('\n' if code=='en' else re.match(r'\s*',m[2])[0])+json.dumps(data,ensure_ascii=code=='en',indent=2).replace('<','\\u003c')+('\n  ' if code=='en' else re.search(r'\s*$',m[2])[0])+m[3]
    text=re.sub(r'(<script\b[^>]*type="application/ld\+json"[^>]*>)(.*?)(</script>)',update_schema,text,flags=re.S)
    if not nested:
        script='<!-- i18n-travel-schema:start --><script type="application/ld+json">'+json.dumps(schema,ensure_ascii=False).replace('<','\\u003c')+'</script><!-- i18n-travel-schema:end -->'
        text=text.replace('</head>',script+'\n</head>',1)
    return re.sub(r'(?m)^[ \t]+$', '', text)

def travel_routes(root,registry,code):
    cfg=read_json(root/'locales/travel-routes.json')
    return {route_for(root,registry,path,code) for path in [cfg['hub'],*cfg['destinations']]}
