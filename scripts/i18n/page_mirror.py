"""Render keyed English-master page families with strict structural parity."""
import json
import re
from bs4 import NavigableString, Comment
from urllib.parse import urljoin,urlsplit
from i18n.catalog import read_json,page_url,topic_locales
from i18n.keyed_master import apply_keyed_master
from i18n.metadata import og_locales
from i18n.mirror_structure import check_pair


def twin_routes(registry,lang):
    routes={'/':registry['locales'][lang]['home']}
    for topic,cfg in registry['topics'].items():
        if lang in topic_locales(registry,topic):routes[cfg['relatedEnglish'].rstrip('/')]=page_url(registry,lang,topic)
    for name in ('authoredMirrors','exactMirrors','domMirrors'):
        for cfg in registry.get(name,{}).values():
            if lang in cfg['routes']:routes[cfg['english'].rstrip('/')]=cfg['routes'][lang]
    if '/saint-charbel-prayers' in routes:routes['/en/prayers']=routes['/saint-charbel-prayers']
    if lang in registry.get('publicationSets',{}).get('eucharistic',[]):routes['/miracles/eucharistic']=f'/{lang}/miracles/eucharistic/'
    return routes


def render_page(root,registry,lang,family,route,catalog=None):
    raw,soup,copy=apply_keyed_master(root,family,lang,catalog)
    source=read_json(root/f'locales/en/{family}-bindings.json')['master']
    master_route='/' + source.removesuffix('.html')
    twins=twin_routes(registry,lang);twins[master_route]=route
    for node in soup.select('[href],[src],[srcset],[action]'):
        for attr in ('href','src','action'):
            if node.has_attr(attr) and not node[attr].startswith(('#','mailto:','tel:','data:','javascript:')):
                node[attr]=urljoin('/',node[attr])
        if node.has_attr('srcset'):
            node['srcset']=', '.join(urljoin('/',p.strip().split()[0])+(' '+' '.join(p.strip().split()[1:]) if len(p.strip().split())>1 else '') for p in node['srcset'].split(','))
    for a in soup.select('a[href]'):
        if a.has_attr('hreflang') or a['href'].startswith('#'):continue
        parts=urlsplit(a['href']);key=parts.path.rstrip('/') or '/'
        if not parts.scheme and key in twins:a['href']=twins[key]+('?' +parts.query if parts.query else '')+('#'+parts.fragment if parts.fragment else '')
    canonical=registry['site']+route
    soup.html['lang']=lang;soup.html['dir']=registry['locales'][lang]['direction'];soup.html['data-authored-mirror']=family
    soup.select_one('link[rel=canonical]')['href']=canonical
    soup.select_one('meta[property="og:url"]')['content']=canonical
    soup.select_one('meta[property="og:locale"]')['content']=og_locales(registry)[lang]
    for node in soup.select('meta[property="og:locale:alternate"]'):node.decompose()
    for code,value in og_locales(registry).items():
        if code!=lang:soup.head.append(soup.new_tag('meta',property='og:locale:alternate',content=value))
    for node in soup.select('link[hreflang]'):node.decompose()
    clusters={'en':master_route,**registry['pageMirrors'][family]['routes'],'x-default':master_route}
    for code,path in clusters.items():soup.head.append(soup.new_tag('link',rel='alternate',hreflang=code,href=registry['site']+path))
    title=soup.title.get_text();description=soup.select_one('meta[name=description]')['content']
    for script in soup.select('script[type="application/ld+json"]'):
        data=json.loads(script.string)
        if data.get('@type')=='FAQPage':
            # Source questions/answers have exact text nodes bound to the same
            # catalog. Resolve by source text, not another authored schema copy.
            lookup={b['source']:copy[b['key']] for b in read_json(root/f'locales/en/{family}-bindings.json')['bindings'] if b['kind']=='text'}
            for entry in data['mainEntity']:
                for obj,key in [(entry,'name'),(entry['acceptedAnswer'],'text')]:
                    if obj[key] not in lookup:raise ValueError(f'{family}: FAQ schema text has no keyed visible equivalent')
                    obj[key]=lookup[obj[key]]
            data['inLanguage']=lang
        else:
            data.update(url=canonical,inLanguage=lang,description=description)
            if data.get('@type')=='WebPage':data['name']=title
            if data.get('@type')=='Person':data['name']=copy['history.header.saint-charbel']
            if 'breadcrumb' in data:
                items=data['breadcrumb']['itemListElement']
                items[0].update(name=copy['history.header.home'],item=registry['site']+registry['locales'][lang]['home'])
                items[-1].update(name=soup.h1.get_text(' ',strip=True),item=canonical)
                # Intermediate navigation label is translated in the same header.
                for item in items[1:-1]:
                    path=urlsplit(item['item']).path
                    a=soup.select_one('header a[href="'+path+'"]')
                    if a:item['name']=a.get_text(' ',strip=True)
        script.string=json.dumps(data,ensure_ascii=False).replace('<','\\u003c')
    runtime=read_json(root/f'locales/{lang}/runtime.json');runtime['language.choose']=read_json(root/f'locales/{lang}/common.json')['navigation.chooseLanguage'];runtime['nativeNames']={c:cfg['nativeName'] for c,cfg in registry['locales'].items()}
    node=soup.new_tag('script',type='application/json',id='sc-runtime-labels');node.string=json.dumps(runtime,ensure_ascii=False).replace('<','\\u003c');soup.head.append(node)
    if registry['locales'][lang]['direction'] == 'rtl':
        # Unicode isolates preserve the exact element tree while containing
        # embedded Latin names, mottoes and license codes within Arabic prose.
        for text in list(soup.main.find_all(string=True)):
            if isinstance(text, Comment) or text.parent.name in ('script','style'): continue
            isolated = re.sub(r'[A-Za-z][A-Za-z0-9]*(?:[ .:/\-][A-Za-z0-9]+)*', lambda m: '\u2068' + m[0] + '\u2069', str(text))
            if isolated != str(text): text.replace_with(isolated)
    rendered=str(soup);diff=check_pair(raw.decode('utf-8'),rendered,master_route,route)
    if diff:raise ValueError(f'{family} {lang}: mirror structure diverged: {diff}')
    return rendered


def render_page_set(root,registry):
    result={}
    for family,cfg in registry.get('pageMirrors',{}).items():
        for lang in cfg.get('renderLocales',[]):
            route=cfg['routes'][lang];result[root/(route.lstrip('/')+'.html')]=render_page(root,registry,lang,family,route)
    return result
