from i18n.encyclopedia_nav import finish_nav
"""Render Qannoubine and Qozhaya from their keyed English masters and locale catalogs."""
from i18n.metadata import og_locales, published_locales

def og_alternates(code, registry=None):
    return '\n'.join(f'<meta property="og:locale:alternate" content="{v}" />' for k, v in og_locales(registry).items() if k != code)

from html import escape
import json
from pathlib import Path
import re
import subprocess

from i18n.catalog import ROOT, leaves, page_url, read_json, topic_locales

SITE = 'https://marsharbel.com'
SLOT = re.compile(r'\{\{([a-z][A-Za-z0-9]*(?:\.[a-z][A-Za-z0-9]*)+)\}\}')
RESERVED = {'locale.code', 'locale.direction', 'locale.canonical', 'locale.alternates', 'locale.ogLocale', 'locale.ogLocaleAlternates'}


def render_monasteries(root=ROOT, registry=None):
    """Pure generated HTML; fail if a published catalog is incomplete or unsafe."""
    registry = registry or read_json(root / 'locales/registry.json')
    result = {}
    for name in ('qannoubine', 'qozhaya'):
        config = registry['authoredMirrors'][name]
        routes = config['routes']
        if routes.get('en') != config['english']:
            raise ValueError(f'{name} English master route mismatch')
        template = (root / f'templates/mirrors/{name}-monastery.html').read_text(encoding='utf-8')
        found = SLOT.findall(template)
        if template.count('{{') != len(found) or template.count('}}') != len(found):
            raise ValueError(f'{name}: invalid template slots')
        expected = set(found) - RESERVED
        alternates = '\n'.join(f'  <link rel="alternate" hreflang="{code}" href="{SITE + route}" />'
                               for code, route in [('x-default', config['english']), *routes.items()])
        for code, route in routes.items():
            catalog = read_json(root / f'locales/{code}/mirrors/{name}-monastery.json')
            if set(catalog) != expected:
                raise ValueError(f'{name}/{code}: catalog mismatch, missing {sorted(expected-set(catalog))}; extra {sorted(set(catalog)-expected)}')
            leaves(catalog)
            tokens = {**catalog, 'locale.code': code, 'locale.direction': registry['locales'][code]['direction'],
                      'locale.canonical': SITE + route, 'locale.alternates': alternates,
                  'locale.ogLocale': og_locales(registry)[code], 'locale.ogLocaleAlternates': og_alternates(code, registry)}
            def substitute(match):
                key = match.group(1)
                if key in ('locale.alternates', 'locale.ogLocaleAlternates'):
                    return tokens[key]
                before = template[:match.start()]
                if before.rfind('<script type="application/ld+json">') > before.rfind('</script>'):
                    return json.dumps(tokens[key], ensure_ascii=False)[1:-1].replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
                return escape(tokens[key], quote=key.startswith(('meta.', 'images.', 'header.primaryLabel', 'locale.')))
            text = SLOT.sub(substitute, template)
            if '{{' in text or '}}' in text:
                raise ValueError(f'{name}/{code}: unresolved slot')
            if code == 'en':
                # English generated pages share the same navigation renderer as
                # sync-navigation/build-pages. A template's old header must not
                # undo later shared-nav changes during international rebuilds.
                nav = subprocess.run(
                    ['node', '--input-type=module', '-e',
                     "import fs from 'node:fs'; import {renderPrimaryNav} from './scripts/lib/primary-nav.mjs'; "
                     "process.stdout.write(renderPrimaryNav(fs.readFileSync('partials/primary-navigation.html','utf8').trim(),process.argv[1]));",
                     name + '-monastery.html'],
                    cwd=root, check=True, capture_output=True, text=True).stdout
                pattern = r'<nav\b[^>]*class=[\"\']links[\"\'][^>]*>[\s\S]*?</nav>'
                if len(re.findall(pattern, text)) != 1:
                    raise ValueError(f'{name}: expected one primary navigation')
                text = re.sub(pattern, lambda _: nav, text, count=1)
                text = text.replace('src="/app.js"', 'src="app.js"').replace('src="/translate.js?', 'src="translate.js?')
                text = re.sub(r'(<a\b[^>]*\bhref=["\'])/(?!/)([^"\']*)(["\'])', r'\1./\2\3', text)
                text = text.replace('href="./miracles"', 'href="./miracles/"')
            else:
                targets = {config['relatedEnglish'].rstrip('/') or '/': page_url(registry, code, topic)
                           for topic, config in registry['topics'].items()
                           if code in topic_locales(registry, topic)}
                targets.update({mirror['english']: mirror['routes'][code] for mirror in registry['authoredMirrors'].values()
                                if code in mirror['routes']})
                # The retired prayer master 301s to the English guide; locale
                # pages point prayer links at their own authored mirror.
                targets.update({page_url(registry, 'en', topic).rstrip('/') or '/': page_url(registry, code, topic)
                                for topic in registry['topics']
                                if 'en' in topic_locales(registry, topic) and code in topic_locales(registry, topic)})
                text = re.sub(r'((?:href|src)=["\'])\./(?!/)([^"\']*)(["\'])', r'\1/\2\3', text)
                text = text.replace('href="styles.css', 'href="/styles.css')
                text = re.sub(r'(<a\b[^>]*\bhref=["\'])(/[^"\']*)(["\'])',
                              lambda m: m[1] + targets.get(m[2].rstrip('/') or '/', m[2]) + m[3], text)
            result[root / (route.lstrip('/') + '.html')] = finish_nav(text,root,code)
    return result
