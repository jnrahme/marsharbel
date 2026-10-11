from i18n.encyclopedia_nav import finish_nav
"""Prepare exact-master locale renders without publishing or editing source files."""
import hashlib
import json
from pathlib import Path
from urllib.parse import urljoin, urlsplit
from bs4 import BeautifulSoup
from i18n.catalog import ROOT, read_json, leaves, page_url, topic_locales, home_url
from i18n.guarded_dom import translate_slots, translatable_nodes
from i18n.metadata import og_locales


def root_url(value, english_url, site):
    if value.startswith(('#', 'mailto:', 'tel:', 'data:', 'javascript:')):
        return value
    absolute = urljoin(english_url, value)
    parts = urlsplit(absolute)
    if absolute.startswith(site + '/'):
        return parts.path + ('?' + parts.query if parts.query else '') + ('#' + parts.fragment if parts.fragment else '')
    return absolute


def render_exact(root, registry, lang, name, route, catalog=None):
    """Reviewed route/catalog only. Returns HTML; has no publication side effects."""
    catalog = catalog or read_json(root/f'locales/{lang}/{name}-exact.json')
    master = Path(catalog['master'])
    if master.is_absolute() or '..' in master.parts or master.suffix != '.html':
        raise ValueError(f'{name}: unsafe master path')
    if not route.startswith(f'/{lang}/') or '..' in route or '?' in route or '#' in route:
        raise ValueError(f'{name}: unsafe reviewed locale route')
    for key in ('title', 'description', 'footer', 'translationNote'):
        leaves(catalog[key])
    source = (root/master).read_bytes()
    if hashlib.sha256(source).hexdigest() != catalog['masterSha256']:
        raise ValueError(f'{name}: complete master digest changed; refresh reviewed catalog')
    soup = BeautifulSoup(source, 'html.parser')
    translate_slots(soup.main, catalog['slots'], name)
    skip_links = soup.select('body > a.skip-link')
    if len(skip_links) != 1 or skip_links[0].get('href') != '#main-content':
        raise ValueError(f'{name}: expected one reviewed main-content skip link')
    if soup.main.get('id') != 'main-content' or soup.main.get('tabindex') != '-1':
        raise ValueError(f'{name}: skip target focus attributes changed')
    skip_label = read_json(root/f'locales/{lang}/common.json')['navigation.skip']
    leaves(skip_label)
    skip_links[0].string = skip_label
    chrome = catalog['chrome']
    leaves(chrome)
    for node in translatable_nodes(soup.header):
        key = str(node).strip()
        if key == '✦': continue
        if key not in chrome:
            raise ValueError(f'{name}: untranslated header {key}')
        old = str(node)
        node.replace_with(old.replace(key, chrome[key]))
    for selector, attrs in catalog['attributes'].items():
        found = soup.select(selector)
        if len(found) != 1: raise ValueError(f'{name}: ambiguous attribute target {selector}')
        for attr, value in attrs.items():
            if attr not in ('alt', 'aria-label', 'title', 'placeholder'):
                raise ValueError(f'{name}: disallowed translated attribute {attr}')
            leaves(value)
            found[0][attr] = value
        # Localized history tables may overflow at narrow widths. A keyed
        # accessible name also opts their scroll container into keyboard access.
        if 'history-table-wrap' in found[0].get('class', []) and attrs.get('aria-label'):
            found[0]['tabindex'] = '0'
            found[0]['role'] = 'region'
    for node in soup.select('main [aria-label], main [title], main img[alt]'):
        for attr in ('aria-label', 'title', 'alt'):
            if not node.get(attr): continue
            covered = any(node in soup.select(selector) and attr in attrs for selector,attrs in catalog['attributes'].items())
            if not covered: raise ValueError(f'{name}: untranslated accessible attribute {attr} on {node.name}')
    soup.select_one('footer .site-shell').string = catalog['footer']
    site = registry['site']
    english_url = soup.select_one('link[rel=canonical]')['href']
    local_url = site + route
    twins = {'': (home_url(registry, lang) or '/')}
    for topic, cfg in registry['topics'].items():
        if lang in topic_locales(registry, topic):
            twins[cfg['relatedEnglish'].rstrip('/')] = page_url(registry, lang, topic)
    for cfg in {**registry.get('authoredMirrors', {}), **registry.get('exactMirrors', {})}.values():
        if lang in cfg['routes']: twins[cfg['english'].rstrip('/')] = cfg['routes'][lang]
    if lang in topic_locales(registry, 'prayers'):
        twins['/en/prayers'] = page_url(registry, lang, 'prayers')
    if lang in registry['publicationSets']['eucharistic']:
        twins['/miracles/eucharistic'] = f'/{lang}/miracles/eucharistic/'
    twins[urlsplit(english_url).path.rstrip('/')] = route
    for node in soup.select('a[href],link[href],script[src],img[src]'):
        attr = 'src' if node.has_attr('src') else 'href'
        value = root_url(node[attr], english_url, site)
        if node.name == 'a' and not node.has_attr('hreflang') and value.startswith('/'):
            parts = urlsplit(value)
            if parts.path.rstrip('/') in twins:
                value = twins[parts.path.rstrip('/')] + ('?' + parts.query if parts.query else '') + ('#' + parts.fragment if parts.fragment else '')
        node[attr] = value
    runtime_path = root/f'locales/{lang}/runtime.json'
    if not runtime_path.exists(): raise ValueError(f'{name}: missing runtime chrome catalog')
    if runtime_path.exists():
        runtime = read_json(runtime_path)
        leaves(runtime)
        required_runtime = {'language.label','language.popular','language.all','install.label','install.link','install.ios','install.browser','footer.privacy','footer.terms','footer.accessibility'}
        if set(runtime) != required_runtime: raise ValueError(f'{name}: runtime chrome key mismatch')
        runtime['language.choose'] = read_json(root/f'locales/{lang}/common.json')['navigation.chooseLanguage']
        runtime['nativeNames'] = {code:cfg['nativeName'] for code,cfg in registry['locales'].items()}
        config = soup.new_tag('script', type='application/json', id='sc-runtime-labels')
        config.string = json.dumps(runtime,ensure_ascii=False).replace('<','\\u003c')
        soup.head.append(config)
    if soup.select('script[src*="share.js"]'):
        common = read_json(root/f'locales/{lang}/share.json')
        labels = {key:value for key,value in common.items() if key.startswith('share.')}
        leaves(labels)
        required_share = {'share.label','share.group.aria','share.trigger.aria','share.native.aria','share.target.aria','share.target.email.aria','share.target.email.label','share.copy.label','share.copy.aria','share.status.copied','share.status.failed','share.prompt.copy','share.fallbackTitle.gallery'}
        if set(labels) != required_share: raise ValueError(f'{name}: share label key mismatch')
        english_labels = read_json(root/'locales/en/share.json')
        import re
        for key,value in labels.items():
            if set(re.findall(r'\{([a-z]+)\}',value)) != set(re.findall(r'\{([a-z]+)\}',english_labels[key])):
                raise ValueError(f'{name}: share placeholders differ for {key}')
        config = soup.new_tag('script', type='application/json', id='sc-share-labels')
        config.string = json.dumps(labels,ensure_ascii=False).replace('<','\\u003c')
        soup.head.append(config)
    for stylesheet in soup.select('link[rel=stylesheet]'):
        if stylesheet.get('href','').split('?')[0] == '/styles.css': stylesheet['href'] = '/styles.css?v=20261002-locale-exact-1'
    soup.html['lang'] = lang
    soup.html['dir'] = registry['locales'][lang]['direction']
    soup.html['data-authored-mirror'] = name
    soup.title.string = catalog['title']
    for selector, value in [('link[rel=canonical]',local_url),('meta[name=description]',catalog['description']),('meta[property="og:title"]',catalog['title']),('meta[name="twitter:title"]',catalog['title']),('meta[property="og:description"]',catalog['description']),('meta[name="twitter:description"]',catalog['description']),('meta[property="og:url"]',local_url)]:
        node = soup.select_one(selector)
        if node: node['href' if node.name=='link' else 'content'] = value
    if soup.select_one('meta[property="og:locale"]'):
        soup.select_one('meta[property="og:locale"]')['content'] = og_locales(registry)[lang]
    for node in soup.select('meta[property="og:locale:alternate"]'):
        if node.get('content') == og_locales(registry)[lang]: node.decompose()
    # Alternate cluster is explicit reviewed input. Preserve reciprocal master
    # cluster until publishing owner updates both source and locale in one build.
    for node in soup.select('link[hreflang]'): node.decompose()
    if catalog['alternates'].get(lang) != local_url or catalog['alternates'].get('x-default') != english_url:
        raise ValueError(f'{name}: invalid self/default alternates')
    for code, url in catalog['alternates'].items():
        if not url.startswith(site + '/') or any(c in url for c in '<>\"'):
            raise ValueError(f'{name}: unsafe alternate URL')
        soup.head.append(soup.new_tag('link', rel='alternate', hreflang=code, href=url))
    faq_candidates = [section for section in soup.select('main section') if section.h2 and section.h2.get_text() == catalog['faqHeading']]
    if len(faq_candidates) != 1: raise ValueError(f'{name}: ambiguous FAQ section')
    faq = faq_candidates[0]
    headings, answers = faq.select('h3'), faq.select('p')
    if len(headings) != len(answers): raise ValueError(f'{name}: FAQ count differs')
    for script in soup.select('script[type="application/ld+json"]'):
        data = json.loads(script.string)
        if data['@type'] == 'FAQPage':
            if len(data['mainEntity']) != len(headings): raise ValueError(f'{name}: FAQ schema differs')
            for entry,h,p in zip(data['mainEntity'],headings,answers):
                entry['name'] = h.get_text(' ',strip=True)
                entry['acceptedAnswer']['text'] = p.get_text(' ',strip=True)
        else:
            data.update(name=catalog['title'],description=catalog['description'],url=local_url,inLanguage=lang)
            if 'alternateName' in data: data['alternateName'] = catalog['nameVariants']
            if 'breadcrumb' in data:
                items=data['breadcrumb']['itemListElement']
                if len(items)!=len(catalog['breadcrumbs']): raise ValueError(f'{name}: breadcrumb count differs')
                for item,label in zip(items,catalog['breadcrumbs']):
                    item['name']=label
                    path=urlsplit(item['item']).path.rstrip('/')
                    if path in twins:item['item']=site+twins[path]
                items[0]['item']=site+(home_url(registry, lang) or '/')
                items[-1]['item']=local_url
            if isinstance(data.get('mainEntity'),dict) and data['mainEntity'].get('@type')=='Article':
                data['mainEntity']['headline']=soup.h1.get_text(' ',strip=True)
        script.string=json.dumps(data,ensure_ascii=False,indent=2).replace('<','\\u003c')
    # This disclosure belongs with source attribution, not buried in notes.
    sources=[section for section in soup.select('main section') if section.h2 and section.h2.get_text()==catalog['sourcesHeading']]
    if len(sources)!=1: raise ValueError(f'{name}: source section differs')
    note=soup.new_tag('p',attrs={'class':'translation-note'});note.string=catalog['translationNote'];sources[0].append(note)
    for reference in catalog.get('translationSources', []):
        if set(reference) != {'url', 'label'} or not reference['url'].startswith('https://'):
            raise ValueError(f'{name}: invalid translation source')
        leaves(reference['label'])
        link=soup.new_tag('a',href=reference['url'],rel='noopener',attrs={'class':'translation-note'})
        link.string=reference['label']
        sources[0].append(link)

    return finish_nav(str(soup),root,lang)


def render_exact_set(root, registry):
    """Only explicitly registered, reviewed pairs publish; empty by default."""
    result = {}
    for name, config in registry.get('exactMirrors', {}).items():
        english = config['english']
        routes = config['routes']
        if routes.get('en') != english:
            raise ValueError(f'{name}: exact mirror English route differs')
        for lang, route in routes.items():
            if lang == 'en' or lang not in config.get('renderLocales', routes):
                continue
            if lang not in registry['locales']:
                raise ValueError(f'{name}: locale not registered')
            catalog = read_json(root/f'locales/{lang}/{name}-exact.json')
            expected = {code:registry['site']+url for code,url in routes.items()}
            expected['x-default'] = registry['site']+english
            if catalog['alternates'] != expected:
                raise ValueError(f'{name}: catalog alternate cluster differs')
            path = root/(route.lstrip('/')+'index.html' if route.endswith('/') else route.lstrip('/')+'.html')
            if path in result:
                raise ValueError(f'{name}: exact output collision')
            result[path] = render_exact(root, registry, lang, name, route, catalog)
    return result
