"""Render the corrected Qadisha master and published locale mirrors from one template."""
from html import escape
import json
from pathlib import Path
import re

from i18n.catalog import ROOT, leaves, page_url, read_json, topic_locales

SLOT = re.compile(r'\{\{([a-z][A-Za-z0-9]*(?:\.[a-z][A-Za-z0-9]*)+)\}\}')
SITE = 'https://marsharbel.com'
RESERVED = {'locale.code', 'locale.direction', 'locale.canonical', 'locale.alternates'}


def render_qadisha(root=ROOT, registry=None):
    """Return all authored pages without writes; reject missing/extra copy or routes."""
    registry = registry or read_json(root / 'locales/registry.json')
    mirror = registry['authoredMirrors']['qadisha']
    routes = mirror['routes']
    if routes.get('en') != mirror['english']:
        raise ValueError('Qadisha mirror: English route differs from master')
    template = (root / 'templates/mirrors/qadisha.html').read_text(encoding='utf-8')
    found = SLOT.findall(template)
    if template.count('{{') != len(found) or template.count('}}') != len(found):
        raise ValueError('Qadisha mirror: malformed slot')
    expected = set(found) - RESERVED
    alternates = '\n'.join(f'  <link rel="alternate" hreflang="{lang}" href="{SITE + route}" />'
                            for lang, route in [('x-default', mirror['english']), *routes.items()])
    result = {}
    for code, route in routes.items():
        catalog = read_json(root / f'locales/{code}/mirrors/qadisha.json')
        if set(catalog) != expected:
            raise ValueError(f'Qadisha {code} catalog mismatch: missing {sorted(expected-set(catalog))}, extra {sorted(set(catalog)-expected)}')
        leaves(catalog)
        tokens = {**catalog, 'locale.code': code, 'locale.direction': registry['locales'][code]['direction'],
                  'locale.canonical': SITE + route, 'locale.alternates': alternates}
        def substitute(match):
            key = match.group(1)
            if key == 'locale.alternates':
                return tokens[key]
            before = template[:match.start()]
            if before.rfind('<script type="application/ld+json">') > before.rfind('</script>'):
                return json.dumps(tokens[key], ensure_ascii=False)[1:-1].replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
            return escape(tokens[key], quote=key.startswith(('meta.', 'images.', 'header.primaryLabel', 'locale.')))
        text = SLOT.sub(substitute, template)
        if '{{' in text or '}}' in text:
            raise ValueError('Qadisha mirror: unresolved slot')
        # The English managed nav spells this label with a raw ampersand.
        # Do not unescape arbitrary catalog text in the nav.
        if code == 'en':
            text = text.replace('>Miracles &amp; Reports</a>', '>Miracles & Reports</a>')
        # Only known, published locale routes are rewritten. Other English
        # resources retain their canonical target, with no imaginary Arabic URL.
        if code == 'en':
            nav = re.search(r'<nav class="links".*?</nav>', text, flags=re.S)
            if nav:
                text = text[:nav.start()] + re.sub(r'(<a\b[^>]*\bhref=["\'])/(?!/)([^"\']*)(["\'])', r'\1./\2\3', nav.group(0)) + text[nav.end():]
        else:
            targets = {config['relatedEnglish'].rstrip('/') or '/': page_url(registry, code, topic)
                       for topic, config in registry['topics'].items()
                       if code in topic_locales(registry, topic)}
            targets[mirror['english']] = route
            text = re.sub(r'(<a\b[^>]*\bhref=["\'])(/[^"\']*)(["\'])',
                          lambda m: m[1] + targets.get(m[2].rstrip('/') or '/', m[2]) + m[3], text)
        if code == 'en':
            text = text.replace('  <script defer src="/app.js">', '  <script defer src="app.js">').replace('  <script defer src="/translate.js?', '  <script defer src="translate.js?')
        result[root / (route.lstrip('/') + '.html')] = text
    return result
