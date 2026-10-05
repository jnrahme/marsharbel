"""Render homepages from the English master, never a separate locale layout."""
import hashlib
import json
import re
from urllib.parse import urljoin, urlsplit
from i18n.metadata import og_locales
from i18n.mirror_structure import check_pair
from bs4 import BeautifulSoup, NavigableString
from i18n.catalog import read_json, page_url, topic_locales


def render_home(root, registry, lang, catalog=None):
    contract = read_json(root / 'locales/en/home-bindings.json')
    raw = (root / contract['master']).read_bytes()
    if hashlib.sha256(raw).hexdigest() != contract['masterSha256']:
        raise ValueError('Home master changed: update bindings and reviewed locale catalogs')
    english = read_json(root / 'locales/en/home-copy.json')
    copy = catalog if catalog is not None else read_json(root / f'locales/{lang}/home-copy.json')
    if set(copy) != set(english):
        raise ValueError(f'Home {lang}: missing/extra message keys: {sorted(set(english) ^ set(copy))}')
    for key, value in copy.items():
        if not isinstance(value, str) or not value.strip() or re.search(r'<\s*/?\s*[A-Za-z!]', value):
            raise ValueError(f'Home {lang}: unsafe or empty message {key}')
        if set(re.findall(r'\{([A-Za-z]+)\}', value)) != set(re.findall(r'\{([A-Za-z]+)\}', english[key])):
            raise ValueError(f'Home {lang}: placeholders differ for {key}')
    soup = BeautifulSoup(raw, 'html.parser')
    for binding in contract['bindings']:
        nodes = soup.select(binding['selector'])
        if len(nodes) != 1:
            raise ValueError(f'Home: ambiguous binding {binding["key"]}')
        node = nodes[0]
        if binding['kind'] == 'attribute':
            attr = binding['attribute']
            if node.get(attr) != binding['source']:
                raise ValueError(f'Home: changed attribute {binding["key"]}')
            node[attr] = copy[binding['key']]
        else:
            text = node.contents[binding['nodeIndex']]
            if not isinstance(text, NavigableString) or ' '.join(str(text).split()) != binding['source']:
                raise ValueError(f'Home: changed text {binding["key"]}')
            old = str(text)
            text.replace_with(old[:len(old)-len(old.lstrip())] + copy[binding['key']] + old[len(old.rstrip()):])
    # Preserve asset paths, srcsets, forms and JS navigation from a nested route.
    for node in soup.select('[href], [src], [srcset], [action], [data-src-mp4]'):
        for attr in ('href', 'src', 'action', 'data-src-mp4'):
            if node.has_attr(attr) and not node[attr].startswith(('#', 'mailto:', 'tel:', 'data:', 'javascript:')):
                node[attr] = urljoin('/', node[attr])
        if node.has_attr('srcset'):
            node['srcset'] = ', '.join(urljoin('/', p.strip().split()[0]) + (' ' + ' '.join(p.strip().split()[1:]) if len(p.strip().split()) > 1 else '') for p in node['srcset'].split(','))
    route = registry['locales'][lang]['home']
    canonical = registry['site'] + route
    soup.html['lang'] = lang
    soup.html['dir'] = registry['locales'][lang]['direction']
    soup.html['data-authored-mirror'] = 'home'
    soup.select_one('link[rel=canonical]')['href'] = canonical
    soup.select_one('meta[property="og:url"]')['content'] = canonical
    soup.select_one('meta[property="og:locale"]')['content'] = og_locales(registry)[lang]
    for node in soup.select('meta[property="og:locale:alternate"]'):
        node.decompose()
    for code, value in og_locales(registry).items():
        if code != lang:
            soup.head.append(soup.new_tag('meta', property='og:locale:alternate', content=value))
    for a in soup.select('header a[href="/"],header a[href="/index.html"]'):
        a['href'] = route
    # Route existing controls to published twins without changing their structure.
    twins = {cfg['english']:cfg['routes'][lang] for cfg in registry.get('authoredMirrors',{}).values() if lang in cfg['routes']}
    for topic, cfg in registry['topics'].items():
        if lang in topic_locales(registry, topic):
            twins[cfg['relatedEnglish'].rstrip('/')] = page_url(registry, lang, topic)
    for cfg in registry.get('exactMirrors', {}).values():
        if lang in cfg['routes']:
            twins[cfg['english'].rstrip('/')] = cfg['routes'][lang]
    # English app links can use the old /en guide alias for the full prayer master.
    if '/saint-charbel-prayers' in twins:
        twins['/en/prayers'] = twins['/saint-charbel-prayers']
    if lang in registry.get('publicationSets', {}).get('eucharistic', []):
        twins['/miracles/eucharistic'] = f'/{lang}/miracles/eucharistic/'
    for a in soup.select('a[href]'):
        if a.has_attr('hreflang'): continue
        parts = urlsplit(a['href'])
        if not parts.scheme and parts.path.rstrip('/') in twins:
            a['href'] = twins[parts.path.rstrip('/')] + ('?' + parts.query if parts.query else '') + ('#' + parts.fragment if parts.fragment else '')
    for script in soup.select('script[type="application/ld+json"]'):
        data = json.loads(script.string)
        for item in data.get('@graph', []):
            if item.get('@type') == 'WebPage':
                item.update(url=canonical, inLanguage=lang, name=soup.title.get_text(), description=soup.select_one('meta[name=description]')['content'])
        script.string = json.dumps(data, ensure_ascii=False).replace('<', '\\u003c')
    runtime = read_json(root / f'locales/{lang}/runtime.json')
    required_runtime = {'language.label','language.popular','language.all','install.label','install.link','install.ios','install.browser','footer.privacy','footer.terms','footer.accessibility'}
    if set(runtime) != required_runtime or any(not isinstance(v,str) or not v.strip() for v in runtime.values()):
        raise ValueError(f'Home {lang}: incomplete runtime chrome catalog')
    runtime['language.choose'] = read_json(root / f'locales/{lang}/common.json')['navigation.chooseLanguage']
    runtime['nativeNames'] = {code:cfg['nativeName'] for code,cfg in registry['locales'].items()}
    for ident, data in [('sc-runtime-labels', runtime), ('sc-home-labels', {k:v for k,v in copy.items() if k.startswith('home.runtime.')})]:
        node = soup.new_tag('script', type='application/json', id=ident)
        node.string = json.dumps(data, ensure_ascii=False).replace('<', '\\u003c')
        soup.head.append(node)
    rendered = str(soup)
    # Match the existing Travel frame serializer's canonical indentation so
    # reprocessing a generated home is byte-idempotent, not just DOM-equal.
    travel = registry.get('authoredMirrors', {}).get('travel', {}).get('routes', {}).get(lang)
    if travel:
        rendered = re.sub(r'(?m)^([ \t]*)(<a href="' + re.escape(travel) + r'">[^<]*</a>)$',
                          lambda match: '        ' + match[2], rendered)
    mismatches = check_pair(raw.decode('utf-8'), rendered, '/', route)
    if mismatches:
        raise ValueError(f'Home {lang}: mirror structure diverged: {mismatches}')
    return rendered


def render_home_set(root, registry):
    return {root / lang / 'index.html': render_home(root, registry, lang)
            for lang in registry.get('homepageMirrors', {}).get('renderLocales', [])}
