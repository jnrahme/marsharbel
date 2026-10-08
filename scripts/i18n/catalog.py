"""Strict, side-effect-free loading of plain-text localization catalogs."""
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[2]
PLACEHOLDER = re.compile(r'\{([A-Za-z][A-Za-z0-9_]*)\}')


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'Duplicate catalog key: {key}')
        result[key] = value
    return result


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=unique_object)


def leaves(value, prefix=''):
    if isinstance(value, dict) and value:
        result = {}
        for key, child in value.items():
            result.update(leaves(child, f'{prefix}.{key}' if prefix else key))
        return result
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{prefix}: expected a nonempty plain-text string')
    if re.search(r'<\s*/?\s*[a-zA-Z!]', value):
        raise ValueError(f'{prefix}: HTML belongs in the template, not the catalog')
    return {prefix: value}


def validate_registry(registry):
    if registry.get('version') != 1:
        raise ValueError('Unsupported locale registry version')
    for label, url in {'site': registry['site'], **registry['sources']}.items():
        parts = urlsplit(url)
        if parts.scheme != 'https' or not parts.hostname or parts.username or parts.password or re.search(r'[\s<>"\']', url):
            raise ValueError(f'{label}: expected a safe HTTPS source URL')
    if registry['site'] != 'https://marsharbel.com':
        raise ValueError('Site origin must match the published canonical origin')
    order = registry.get('ogLocaleOrder', [])
    if len(order) != len(set(order)) or set(order) != set(registry['locales']):
        raise ValueError('OG locale order must list each registered language once')
    if len(registry.get('homePublicationLocales', [])) != len(set(registry.get('homePublicationLocales', []))) or not set(registry.get('homePublicationLocales', [])) <= registry['locales'].keys():
        raise ValueError('Invalid homepage publication membership')
    aliases = {}
    for code, config in registry['locales'].items():
        if not re.fullmatch(r'[a-z]{2,3}(?:-[A-Za-z]{2,4})?', code):
            raise ValueError(f'Invalid locale code: {code}')
        if not re.fullmatch(r'[a-z]{2,3}_[A-Z]{2}', config.get('ogLocale', '')):
            raise ValueError(f'{code}: invalid or missing OG locale')
        validate_capabilities(registry, code)
        values = config.get('selectorAliases')
        if not isinstance(values, list):
            raise ValueError(f'{code}: selectorAliases must be a list')
        for alias in [code, *values]:
            if not isinstance(alias, str) or not re.fullmatch(r'[a-zA-Z]{2,3}(?:-[a-zA-Z]{2,4})?', alias):
                raise ValueError(f'{code}: invalid selector alias')
            key = alias.lower()
            if key in aliases:
                raise ValueError(f'Duplicate selector alias: {alias}')
            if key == 'zh-tw' and code == 'zh-Hans':
                raise ValueError('Traditional Chinese cannot alias Simplified Chinese')
            aliases[key] = code
    sets = registry.get('publicationSets', {})
    if set(sets) != {'prayers', 'eucharistic'}:
        raise ValueError('Missing or unknown publication sets')
    for name, subset in sets.items():
        if (not isinstance(subset, list) or not subset or len(subset) != len(set(subset))
                or not set(subset) <= registry['locales'].keys()
                or registry['defaultLocale'] not in subset):
            raise ValueError(f'{name}: invalid publication set')
    for name, config in registry.get('domMirrors', {}).items():
        if not re.fullmatch(r'[a-z][A-Za-z0-9]*', name):
            raise ValueError('Unsafe DOM mirror name')
        if not re.fullmatch(r'[a-z0-9-]+\.json', config.get('catalog', '')):
            raise ValueError(f'{name}: unsafe DOM mirror catalog')
        routes = config.get('routes', {})
        if not routes or not set(routes) <= registry['locales'].keys():
            raise ValueError(f'{name}: invalid DOM mirror publication')
        matching = [topic for topic, value in registry['topics'].items() if value['relatedEnglish'] == config['english']]
        if len(matching) != 1:
            raise ValueError(f'{name}: DOM mirror needs one registered topic')
        for code, route in routes.items():
            if code not in topic_locales(registry, matching[0]) or page_url(registry, code, matching[0]) != route:
                raise ValueError(f'{name}: DOM mirror route is not published by its topic')
        for route in [config['english'], *routes.values()]:
            if not re.fullmatch(r'/[a-zA-Z0-9-]+(?:/[a-z0-9-]+)*/?', route):
                raise ValueError(f'{name}: unsafe DOM mirror route')
    for topic, config in registry['topics'].items():
        sections = config['sections']
        if not sections or len(sections) != len(set(sections)):
            raise ValueError(f'{topic}: section IDs must be nonempty and unique')
        if any(not re.fullmatch(r'[a-z][A-Za-z0-9]*', key) for key in [topic, *sections]):
            raise ValueError(f'{topic}: unsafe topic or section ID')
        if not re.fullmatch(r'/[a-z0-9]+(?:-[a-z0-9]+)*(?:/[a-z0-9]+(?:-[a-z0-9]+)*)*/?', config['relatedEnglish']):
            raise ValueError(f'{topic}: invalid related English route')
        if not config['sources'] or not set(config['sources']) <= registry['sources'].keys():
            raise ValueError(f'{topic}: unknown or missing source reference')
        if 'locales' not in config:
            raise ValueError(f'{topic}: explicit publication locales required')
        if 'locales' in config:
            subset = config['locales']
            if not subset or len(subset) != len(set(subset)) or not set(subset) <= registry['locales'].keys():
                raise ValueError(f'{topic}: locales must be a nonempty list of registered languages')


def topic_locales(registry, topic):
    """Languages that publish a topic. Topics without a list exist in every language."""
    return [code for code in registry['locales'] if code in registry['topics'][topic].get('locales', registry['locales'])]


def locale_topics(registry, code):
    return [topic for topic in registry['topics'] if code in topic_locales(registry, topic)]


def load_catalog(root=ROOT):
    registry = read_json(root / 'locales/registry.json')
    validate_registry(registry)
    locales = registry['locales']
    default = registry['defaultLocale']
    if default not in locales:
        raise ValueError('Default locale is not registered')
    catalogs = {}
    paths = set()
    for code, config in locales.items():
        if not re.fullmatch(r'[a-z]{2,3}(?:-[A-Za-z]{2,4})?', code):
            raise ValueError(f'Invalid locale code: {code}')
        leaves(config['nativeName'], f'{code}.nativeName')
        if config['direction'] not in ('ltr', 'rtl'):
            raise ValueError(f'{code}: invalid text direction')
        expected_home = '/' if code == default else f'/{code}/'
        if config['capabilities']['home'] and config.get('home') != expected_home:
            raise ValueError(f'{code}: invalid homepage route')
        if set(config['slugs']) != set(locale_topics(registry, code)):
            raise ValueError(f'{code}: missing or extra topic routes')
        for slug in config['slugs'].values():
            if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*(?:/[a-z0-9]+(?:-[a-z0-9]+)*)*/?', slug):
                raise ValueError(f'{code}: unsafe or invalid slug {slug}')
            route = f'/{code}/{slug}'
            if route.rstrip('/') in paths:
                raise ValueError(f'Duplicate route: {route}')
            paths.add(route.rstrip('/'))
        catalogs[code] = {name: read_json(root / f'locales/{code}/{name}.json') for name in ('common', 'pages')}
        if set(catalogs[code]['pages']) != set(locale_topics(registry, code)):
            raise ValueError(f'{code}: missing or extra page topics')
        for topic, page in catalogs[code]['pages'].items():
            if set(page) - {'fullGuide'} != {'title', 'description', 'intro', 'sections'}:
                raise ValueError(f'{code}/{topic}: invalid page fields')
            if set(page['sections']) != set(registry['topics'][topic]['sections']):
                raise ValueError(f'{code}/{topic}: section IDs do not match registry')
            for section in page['sections'].values():
                if set(section) != {'title', 'body'}:
                    raise ValueError(f'{code}/{topic}: invalid section fields')
    # Each message is compared with the default language when the default publishes it.
    # Topics outside the default language are held to the registry structure checked above.
    for code, catalog in catalogs.items():
        pages = {topic: page for topic, page in catalog['pages'].items() if topic in catalogs[default]['pages']}
        base_pages = {topic: catalogs[default]['pages'][topic] for topic in pages}
        current = leaves({'common': catalog['common'], **({'pages': pages} if pages else {})})
        reference = leaves({'common': catalogs[default]['common'], **({'pages': base_pages} if base_pages else {})})
        if current.keys() != reference.keys():
            missing = sorted(reference.keys() - current.keys())
            extra = sorted(current.keys() - reference.keys())
            raise ValueError(f'{code}: missing keys {missing}; extra keys {extra}')
        for key, text in current.items():
            if set(PLACEHOLDER.findall(text)) != set(PLACEHOLDER.findall(reference[key])):
                raise ValueError(f'{code}/{key}: placeholders differ from {default}')
    validate_mirror_capabilities(root, registry)
    return registry, catalogs


def page_url(registry, code, topic=None):
    config = registry['locales'][code]
    if topic is None:
        return home_url(registry, code)
    if topic not in locale_topics(registry, code):
        raise ValueError(f'{code}: unpublished topic {topic}')
    return f'/{code}/{config["slugs"][topic]}'


def public_html_files(root=ROOT):
    registry = read_json(root / 'locales/registry.json')
    return sorted([*root.glob('*.html'), *root.glob('mysteries/*.html'), *root.glob('miracles/*.html'), *root.glob('miracles/eucharistic/*.html'),
                   *(p for code in registry['locales'] for p in root.glob(f'{code}/**/*.html'))])


CAPABILITY_FIELDS = {'home', 'topicGuides', 'mirrorTabs', 'runtime', 'selectorCopy'}

def validate_capabilities(registry, code):
    config = registry['locales'][code]
    caps = config.get('capabilities')
    if not isinstance(caps, dict) or set(caps) != CAPABILITY_FIELDS:
        raise ValueError(f'{code}: missing or unknown capability fields')
    for field in ('home', 'runtime', 'selectorCopy'):
        if type(caps[field]) is not bool:
            raise ValueError(f'{code}: {field} capability must be boolean')
    for field in ('topicGuides', 'mirrorTabs'):
        if not isinstance(caps[field], list) or len(caps[field]) != len(set(caps[field])):
            raise ValueError(f'{code}: invalid {field} capability')
    if set(caps['topicGuides']) != set(locale_topics(registry, code)):
        raise ValueError(f'{code}: topic capability differs from publication')
    if not set(caps['mirrorTabs']) <= {'travel'}:
        raise ValueError(f'{code}: unknown mirror tab')
    membership = code in registry.get('homePublicationLocales', [])
    if caps['home'] != membership or (not caps['home'] and 'home' in config):
        raise ValueError(f'{code}: homepage capability/publication mismatch')
    if caps['home'] and config.get('home') != ('/' if code == registry['defaultLocale'] else f'/{code}/'):
        raise ValueError(f'{code}: missing or invalid published homepage')
    if 'travel' in caps['mirrorTabs']:
        expected = {'/travel', '/visit-annaya', '/bekaa-kafra', '/qadisha-valley', '/qannoubine-monastery', '/qozhaya-monastery', '/saint-charbel-hermitage', '/saint-charbel-trail', '/saint-charbel-places-lebanon', '/our-lady-of-lebanon-harissa', '/cedars-of-god-lebanon', '/bkerke-maronite-patriarchate', '/saint-charbel-pilgrimage', '/annaya-tour'}
        declared = {cfg['english'] for group in ('authoredMirrors', 'pageMirrors', 'exactMirrors') for cfg in registry.get(group, {}).values() if code in cfg.get('routes', {}) and (group != 'pageMirrors' or code in cfg.get('renderLocales', []))}
        if not expected <= declared:
            raise ValueError(f'{code}: incomplete Travel tab: {sorted(expected - declared)}')
    if caps['mirrorTabs'] and not (caps['runtime'] and caps['selectorCopy']):
        raise ValueError(f'{code}: published mirror requires runtime and selector copy')


def published_home_locales(registry, outputs=None, root=ROOT):
    """Homes require explicit membership and a generator, optionally actual outputs.

    The legacy generator owns every nondefault publication member not handled by
    home_mirror; English is the source index. Files lying on disk prove nothing.
    """
    result = []
    keyed = registry.get('homepageMirrors', {}).get('renderLocales', [])
    for code in registry.get('homePublicationLocales', []):
        config = registry['locales'][code]
        if not config['capabilities']['home']:
            raise ValueError(f'{code}: advertised homepage without capability')
        # Legacy topic-home renderer is selected by explicit publication membership;
        # keyed home renderer additionally validates its route contract below.
        if code in keyed and code == registry['defaultLocale']:
            raise ValueError('English home is owned by the source-index generator')
        if outputs is not None:
            path = root / ('index.html' if code == registry['defaultLocale'] else code + '/index.html')
            if path not in outputs:
                raise ValueError(f'{code}: published homepage missing from build output')
        result.append(code)
    return result


def home_url(registry, code):
    return registry['locales'][code]['home'] if code in published_home_locales(registry) else None


RUNTIME_KEYS = {'language.label', 'language.popular', 'language.all', 'install.label', 'install.link', 'install.ios', 'install.browser', 'footer.privacy', 'footer.terms', 'footer.accessibility'}

def validate_mirror_capabilities(root, registry):
    """Capability grants require real catalog and emitted family contracts."""
    used = {}
    for group in ('authoredMirrors', 'pageMirrors', 'exactMirrors'):
        for name, family in registry.get(group, {}).items():
            routes = family.get('routes', {})
            for code, route in routes.items():
                if code not in registry['locales']:
                    raise ValueError(f'{name}: unknown route locale {code}')
                if not isinstance(route, str) or not re.fullmatch(r'/[A-Za-z0-9-]+(?:/[a-z0-9-]+)*/?', route):
                    raise ValueError(f'{name}: malformed mirror route')
                if code == 'en':
                    continue
                if group == 'pageMirrors' and code not in family.get('renderLocales', []):
                    continue
                key = route.rstrip('/')
                if key in used and registry['locales'][code]['capabilities']['mirrorTabs'] and family.get('english') in {'/travel','/visit-annaya','/bekaa-kafra','/qadisha-valley','/qannoubine-monastery','/qozhaya-monastery','/saint-charbel-hermitage','/saint-charbel-trail','/saint-charbel-places-lebanon','/our-lady-of-lebanon-harissa','/cedars-of-god-lebanon','/bkerke-maronite-patriarchate','/saint-charbel-pilgrimage','/annaya-tour'}:
                    raise ValueError(f'Duplicate mirror route: {route}')
                used[key] = (group, name, code)
    for code, config in registry['locales'].items():
        caps = config['capabilities']
        if caps['runtime'] and caps['mirrorTabs']:
            runtime = read_json(root / f'locales/{code}/runtime.json')
            if set(runtime) != RUNTIME_KEYS:
                raise ValueError(f'{code}: incomplete runtime catalog')
            leaves(runtime)
        if caps['selectorCopy'] and caps['mirrorTabs']:
            selectors = read_json(root / 'locales/same-page-copy.json')
            if code not in selectors or set(selectors[code]) != {'language','choose','unavailable','suffix','helper','names'}:
                raise ValueError(f'{code}: incomplete selector catalog')
            leaves(selectors[code])
            if set(selectors[code]['names']) != set(registry['locales']):
                raise ValueError(f'{code}: selector language names incomplete')
        if not caps['home']:
            if code in registry.get('homepageMirrors', {}).get('renderLocales', []) or code in registry.get('limitedLaunchLocales', []):
                raise ValueError(f'{code}: undeclared home output')
            if any(code in values for values in registry['publicationSets'].values()):
                raise ValueError(f'{code}: partial mirror locale cannot gain prayer/eucharistic output')
        if 'travel' in caps['mirrorTabs']:
            for route, (group, name, owner) in used.items():
                if owner != code:
                    continue
                cfg = registry[group][name]
                english = cfg['english']
                if english not in {'/travel','/visit-annaya','/bekaa-kafra','/qadisha-valley','/qannoubine-monastery','/qozhaya-monastery','/saint-charbel-hermitage','/saint-charbel-trail','/saint-charbel-places-lebanon','/our-lady-of-lebanon-harissa','/cedars-of-god-lebanon','/bkerke-maronite-patriarchate','/saint-charbel-pilgrimage','/annaya-tour'}:
                    continue
                source = cfg.get('master', english.lstrip('/') + '.html')
                if not (root / source).is_file():
                    raise ValueError(f'{code}/{name}: missing mirror master')
                if group != 'pageMirrors':
                    raise ValueError(f'{code}/{name}: partial tab requires explicit keyed master family')
                contract = read_json(root / f'locales/en/{name}-bindings.json')
                if contract['master'] != source:
                    raise ValueError(f'{code}/{name}: family/master linkage differs')
                import hashlib
                if contract['masterSha256'] != hashlib.sha256((root / source).read_bytes()).hexdigest():
                    raise ValueError(f'{code}/{name}: stale mirror master')
                base = read_json(root / f'locales/en/{name}-copy.json')
                local = read_json(root / f'locales/{code}/{name}-copy.json')
                if set(base) != set(local):
                    raise ValueError(f'{code}/{name}: incomplete keyed catalog')
                leaves(local)


def validate_partial_outputs(root, registry, outputs):
    """Declared partial tab routes and generated HTML must be a bijection."""
    for code, config in registry['locales'].items():
        if config['capabilities']['home']:
            continue
        expected = {root / (route.lstrip('/') + '.html')
            for family in registry.get('pageMirrors', {}).values()
            for owner, route in family.get('routes', {}).items()
            if owner == code and owner in family.get('renderLocales', [])}
        actual = {path for path in outputs
            if path.suffix == '.html' and path.relative_to(root).parts[0] == code}
        if actual != expected:
            raise ValueError(f'{code}: partial capability/output mismatch')
