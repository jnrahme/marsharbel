"""Render keyed English-master page families with strict structural parity."""
import json
import re
from bs4 import NavigableString, Comment
from urllib.parse import urljoin,urlsplit
from i18n.catalog import read_json,page_url,topic_locales,home_url
from i18n.keyed_master import apply_keyed_master
from i18n.metadata import og_locales
from i18n.mirror_structure import check_pair


def twin_routes(registry,lang,page_families=True):
    routes={'/':home_url(registry, lang) or '/'}
    for topic,cfg in registry['topics'].items():
        if lang in topic_locales(registry,topic):routes[cfg['relatedEnglish'].rstrip('/')]=page_url(registry,lang,topic)
    for name in ('authoredMirrors','exactMirrors','domMirrors','pageMirrors'):
        if name=='pageMirrors' and not page_families:continue
        for cfg in registry.get(name,{}).values():
            if lang in cfg['routes']:routes[cfg['english'].rstrip('/')]=cfg['routes'][lang]
    if '/saint-charbel-prayers' in routes:routes['/en/prayers']=routes['/saint-charbel-prayers']
    if lang in registry.get('publicationSets',{}).get('eucharistic',[]):routes['/miracles/eucharistic']=f'/{lang}/miracles/eucharistic/'
    return routes


def render_page(root,registry,lang,family,route,catalog=None):
    raw,soup,copy=apply_keyed_master(root,family,lang,catalog)
    source=read_json(root/f'locales/en/{family}-bindings.json')['master']
    master_route=registry['pageMirrors'][family].get('english','/' + source.removesuffix('.html'))
    prefix=next(iter(copy)).split('.')[0]
    # The reviewed history bytes are pinned, so history keeps its reviewed links.
    twins=twin_routes(registry,lang)
    if not family.endswith('-travel-master'):
        # Existing reviewed families keep their established publication links.
        # Adding exact Travel twins is not permission to re-pin unrelated bodies.
        for name,cfg in registry.get('pageMirrors',{}).items():
            if name.endswith('-travel-master') and lang in cfg.get('renderLocales',[]):
                twins.pop(cfg['english'].rstrip('/'),None)
        for topic,cfg in registry['topics'].items():
            if lang in topic_locales(registry,topic):
                twins[cfg['relatedEnglish'].rstrip('/')]=page_url(registry,lang,topic)
        legacy=registry.get('travelPreviousRoutes',{}).get(lang,{})
        twins.update(legacy)
    # Bounded DE Annaya href-only correction, no translated text change.
    if family == 'annaya-master' and lang == 'de':
        all_twins=twin_routes(registry,lang)
        for destination in ('/saint-charbel-hermitage','/saint-charbel-places-lebanon','/qadisha-valley','/qannoubine-monastery','/qozhaya-monastery','/saint-charbel-trail'):
            if destination in all_twins:twins[destination]=all_twins[destination]
    twins[master_route]=route
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
    clusters=registry['pageMirrors'][family].get('discoveryRoutes',{'en':master_route,**registry['pageMirrors'][family]['routes'],'x-default':master_route})
    for code,path in clusters.items():soup.head.append(soup.new_tag('link',rel='alternate',hreflang=code,href=registry['site']+path))
    if home_url(registry, lang) is None:
        qualifier=read_json(root/f'locales/{lang}/encyclopedia-trail.json')['englishQualifier']
        for a in soup.select('a[href="/"]'):
            a['hreflang']='en'
            a['aria-label']=a.get_text(' ',strip=True)+' '+qualifier
            if not a.find('span',class_='partial-home-language'):
                hint=soup.new_tag('span',attrs={'class':'partial-home-language'})
                hint.string=' '+qualifier;a.append(hint)
    title=soup.title.get_text();description=soup.select_one('meta[name=description]')['content']
    contract=read_json(root/f'locales/en/{family}-bindings.json')
    schema_copy={}
    for binding in contract['bindings']:
        source=binding['source'];value=copy[binding['key']]
        if source in schema_copy and schema_copy[source] != value:
            schema_copy[source]=None
        elif source not in schema_copy:
            schema_copy[source]=value
    def translate_schema(node):
        if isinstance(node,dict):
            for key,value in list(node.items()):
                if key in ('name','headline','description','text') and isinstance(value,str) and schema_copy.get(value) is not None:
                    node[key]=schema_copy[value]
                else:translate_schema(value)
        elif isinstance(node,list):
            for value in node:translate_schema(value)
    schema_path=root/f'locales/{lang}/{family}-schema-bindings.json'
    schema_contract=read_json(schema_path) if schema_path.exists() else None
    for ordinal,script in enumerate(soup.select('script[type="application/ld+json"]')):
        data=json.loads(script.string)
        if schema_contract is not None:
            for binding in schema_contract['bindings']:
                if binding['scriptOrdinal'] != ordinal:continue
                tokens=[x.replace('~1','/').replace('~0','~') for x in binding['jsonPointer'].lstrip('/').split('/')]
                target=data
                for token in tokens[:-1]:target=target[int(token)] if isinstance(target,list) else target[token]
                token=int(tokens[-1]) if isinstance(target,list) else tokens[-1]
                if target[token] != binding['source']:raise ValueError(f'{family}: changed schema pointer')
                target[token]=binding['translation']
        if data.get('@type')=='FAQPage' and not (schema_contract and any(b['scriptOrdinal']==ordinal for b in schema_contract['bindings'])):
            # Source questions/answers have exact text nodes bound to the same
            # catalog. Resolve by source text, not another authored schema copy.
            lookup={b['source']:copy[b['key']] for b in read_json(root/f'locales/en/{family}-bindings.json')['bindings'] if b['kind']=='text'}
            for entry in data['mainEntity']:
                if entry['name'] not in lookup:raise ValueError(f'{family}: FAQ schema text has no keyed visible equivalent')
                entry['name']=lookup[entry['name']]
                answer=entry['acceptedAnswer']
                if answer['text'] in lookup:answer['text']=lookup[answer['text']];continue
                # Authored short answers can differ from the visible answer. The
                # structured answer then mirrors the localized visible paragraph
                # that follows the matching question heading, never other text.
                heading=next((h for h in soup.select('main h3, main p > strong:first-child') if ' '.join(h.get_text().split())==entry['name']),None)
                paragraph=None
                if heading is not None:paragraph=heading.parent if heading.name=='strong' else heading.find_next_sibling('p')
                if paragraph is None:raise ValueError(f'{family}: FAQ schema answer has no keyed visible equivalent')
                text=' '.join(paragraph.get_text().split())
                if heading.name=='strong':text=text[len(entry['name']):].lstrip()
                answer['text']=text
            data['inLanguage']=lang
        else:
            data.update(url=canonical,inLanguage=lang,description=description)
            if data.get('@type')=='WebPage':data['name']=title
            if data.get('@type')=='Person':data['name']=copy[prefix+'.header.saint-charbel']
            if 'breadcrumb' in data:
                items=data['breadcrumb']['itemListElement']
                items[0].update(name=copy[prefix+'.header.home'],item=registry['site']+(home_url(registry, lang) or '/'))
                items[-1].update(name=soup.h1.get_text(' ',strip=True),item=canonical)
                # Intermediate navigation label is translated in the same header.
                for item in items[1:-1]:
                    path=urlsplit(item['item']).path
                    a=soup.select_one('header a[href="'+path+'"]')
                    if a:item['name']=a.get_text(' ',strip=True)
        if family.endswith('-travel-master'):
            translate_schema(data)
        if family.endswith('-travel-master'):
            def localize_schema_routes(node):
                if isinstance(node,dict):
                    for key,value in list(node.items()):
                        if key == 'item' and isinstance(value,str) and value.startswith(registry['site']):
                            path=value.removeprefix(registry['site']).rstrip('/') or '/'
                            if path in twins:node[key]=registry['site']+twins[path]
                        else:localize_schema_routes(value)
                elif isinstance(node,list):
                    for value in node:localize_schema_routes(value)
            localize_schema_routes(data)
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
    rendered=str(soup);master_text=raw.decode('utf-8')
    if family in ('saint-charbel-prayers-master','saint-charbel-novena-master'):
        from i18n.prayer_runtime import share_head
        hub=family=='saint-charbel-prayers-master'
        rendered=share_head(rendered,root,lang,hub)
        master_text=share_head(master_text,root,'en',hub)
    diff=check_pair(master_text,rendered,master_route,route, normalizers=('partial-home-disclosure',) if home_url(registry, lang) is None else ())
    if diff:raise ValueError(f'{family} {lang}: mirror structure diverged: {diff}')
    if lang in registry.get('limitedLaunchLocales', []):
        from i18n.prayer_runtime import share_head
        rendered=share_head(rendered,root,lang)
    from i18n.launch_availability import apply_launch_availability
    if family == 'music-master':
        labels = read_json(root / f'locales/{lang}/music-playlist.json')
        expected = {'playlist.upNext', 'playlist.lastTrack', 'playlist.nowPlaying', 'playlist.selected'}
        if set(labels) != expected or any(not isinstance(value, str) or not value.strip() for value in labels.values()):
            raise ValueError(f'{family} {lang}: incomplete playlist runtime labels')
        config = '<script type="application/json" id="sc-playlist-labels">' + json.dumps(labels, ensure_ascii=False).replace('<', '\\u003c') + '</script>\n'
        rendered = rendered.replace('</head>', config + '</head>', 1)
    from i18n.ru_travel_chrome import localize_travel_chrome
    return localize_travel_chrome(apply_launch_availability(rendered, root, registry, lang), registry, lang, family)


def render_page_set(root,registry):
    result={}
    for family,cfg in registry.get('pageMirrors',{}).items():
        for lang in cfg.get('renderLocales',[]):
            route=cfg['routes'][lang];result[root/(route.lstrip('/')+'.html')]=render_page(root,registry,lang,family,route)
    return result
