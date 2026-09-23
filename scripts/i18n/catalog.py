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
    for topic, config in registry['topics'].items():
        sections = config['sections']
        if not sections or len(sections) != len(set(sections)):
            raise ValueError(f'{topic}: section IDs must be nonempty and unique')
        if any(not re.fullmatch(r'[a-z][A-Za-z0-9]*', key) for key in [topic, *sections]):
            raise ValueError(f'{topic}: unsafe topic or section ID')
        if not re.fullmatch(r'/[a-z0-9]+(?:-[a-z0-9]+)*', config['relatedEnglish']):
            raise ValueError(f'{topic}: invalid related English route')
        if not config['sources'] or not set(config['sources']) <= registry['sources'].keys():
            raise ValueError(f'{topic}: unknown or missing source reference')


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
        expected_home = '/' if code == default else '/' + code
        if config['home'] != expected_home:
            raise ValueError(f'{code}: invalid homepage route')
        if set(config['slugs']) != set(registry['topics']):
            raise ValueError(f'{code}: missing or extra topic routes')
        for slug in config['slugs'].values():
            if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug):
                raise ValueError(f'{code}: unsafe or invalid slug {slug}')
            route = f'/{code}/{slug}'
            if route in paths:
                raise ValueError(f'Duplicate route: {route}')
            paths.add(route)
        catalogs[code] = {name: read_json(root / f'locales/{code}/{name}.json') for name in ('common', 'pages')}
        if set(catalogs[code]['pages']) != set(registry['topics']):
            raise ValueError(f'{code}: missing or extra page topics')
        for topic, page in catalogs[code]['pages'].items():
            if set(page) != {'title', 'description', 'intro', 'sections'}:
                raise ValueError(f'{code}/{topic}: invalid page fields')
            if set(page['sections']) != set(registry['topics'][topic]['sections']):
                raise ValueError(f'{code}/{topic}: section IDs do not match registry')
            for section in page['sections'].values():
                if set(section) != {'title', 'body'}:
                    raise ValueError(f'{code}/{topic}: invalid section fields')
    reference = leaves(catalogs[default])
    for code, catalog in catalogs.items():
        current = leaves(catalog)
        if current.keys() != reference.keys():
            missing = sorted(reference.keys() - current.keys())
            extra = sorted(current.keys() - reference.keys())
            raise ValueError(f'{code}: missing keys {missing}; extra keys {extra}')
        for key, text in current.items():
            if set(PLACEHOLDER.findall(text)) != set(PLACEHOLDER.findall(reference[key])):
                raise ValueError(f'{code}/{key}: placeholders differ from {default}')
    return registry, catalogs


def page_url(registry, code, topic=None):
    config = registry['locales'][code]
    return f'/{code}/{config["slugs"][topic]}' if topic else config['home']


def public_html_files(root=ROOT):
    registry = read_json(root / 'locales/registry.json')
    return sorted([*root.glob('*.html'), *root.glob('mysteries/*.html'),
                   *(p for code in registry['locales'] for p in root.glob(f'{code}/*.html'))])
