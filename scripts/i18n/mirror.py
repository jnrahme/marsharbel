from i18n.encyclopedia_nav import finish_nav
"""Render reviewed prayer locale pages from one DOM skeleton and strict text slots."""
from i18n.devotion_guidance import load_guidance, render_lead
from i18n.metadata import og_locales, published_locales

def og_alternates(code, registry=None):
    return '\n'.join(f'<meta property="og:locale:alternate" content="{v}" />' for k, v in og_locales(registry).items() if k != code and k in published_locales(registry, "prayers"))

from html import escape
import json
from pathlib import Path
import re

from i18n.catalog import leaves, read_json, page_url, topic_locales

SLOT = re.compile(r'\{\{([a-z][A-Za-z0-9]*(?:\.[a-z][A-Za-z0-9]*)+)\}\}')
SITE = 'https://marsharbel.com'
ROOT = Path(__file__).resolve().parents[2]


def render_mirrors(root=ROOT, registry=None, retired_routes=()):
    """Return rendered prayer pages without writes; fail on missing or extra text."""
    if registry is None:
        registry = read_json(root / 'locales/registry.json')
    template = (root / 'templates/mirrors/prayers.html').read_text(encoding='utf-8')
    expected = set(SLOT.findall(template)) - {'locale.code', 'locale.direction', 'locale.canonical', 'locale.alternates', 'locale.currentRoute', 'locale.prayerLibraryUrl', 'locale.homeUrl', 'locale.robotsContent', 'locale.ogLocale', 'locale.ogLocaleAlternates', 'locale.prayerLinks'}
    if template.count('{{') != len(SLOT.findall(template)) or template.count('}}') != len(SLOT.findall(template)):
        raise ValueError('Prayer mirror: invalid slot syntax')
    result = {}
    english_path = (root / registry['topics']['prayers']['relatedEnglish'].lstrip('/')).with_suffix('.html')
    english_guide_path = root / 'en' / (registry['locales']['en']['slugs']['prayers'] + '.html')
    # Add a locale only when its full catalog and page have passed parity review.
    mirror_locales = published_locales(registry, 'prayers')
    catalogs = {code: read_json(root / f'locales/{code}/mirrors/prayers.json')
                for code in mirror_locales}
    routes = [(code, catalogs[code], root / code /
               (registry['locales'][code]['slugs']['prayers'] + '.html'))
              for code in mirror_locales]
    guide_meta = read_json(root / 'locales/en/mirrors/prayers-guide.json')
    if set(guide_meta) != {'title', 'description'}:
        raise ValueError('English prayer guide metadata needs title and description')
    leaves(guide_meta)
    for code, catalog in catalogs.items():
        if set(catalog) != expected:
            raise ValueError(f'Prayer mirror {code} slot mismatch: missing {sorted(expected - set(catalog))}; extra {sorted(set(catalog) - expected)}')
    for code, catalog, path in [('en', catalogs['en'], english_path), *routes]:
        if path in retired_routes: continue
        # The mirror catalogs are separate from the legacy short-guide catalogs.
        leaves(catalog)
        is_english_master = path == english_path
        canonical = SITE + (registry['topics']['prayers']['relatedEnglish'] if is_english_master else page_url(registry, code, 'prayers'))
        # Keep the original cluster and ordering byte-for-byte. The builder owns
        # managed hreflang on English and all other guides.
        if is_english_master:
            alternates = '\n'.join(f'  <link rel="alternate" hreflang="{lang}" href="{canonical}" />'
                                   for lang in ('x-default', 'en'))
        else:
            language_urls = {lang: SITE + page_url(registry, lang, 'prayers')
                             for lang in topic_locales(registry, 'prayers')}
            language_urls['x-default'] = language_urls['en']
            alternates = '\n'.join(f'<link rel="alternate" hreflang="{lang}" href="{url}" />'
                                   for lang, url in language_urls.items())
        page_text = {**catalog, **({'meta.title': guide_meta['title'], 'meta.description': guide_meta['description']}
                                    if path == english_guide_path else {})}
        prayer_links = '\n'.join(
            f'          <li><a class="locale-prayer-link" href="{page_url(registry, lang, "prayers")}" hreflang="{lang}" lang="{lang}" dir="{registry["locales"][lang]["direction"]}">{escape(catalogs[lang]["meta.title"].split(" | ")[0])}</a></li>'
            for lang in mirror_locales if lang != code)
        tokens = {**page_text, 'locale.prayerLinks': prayer_links, 'locale.code': code, 'locale.direction': registry['locales'][code]['direction'],
                  'locale.robotsContent': 'noindex' if is_english_master else 'index,follow,max-image-preview:large',
                  'locale.canonical': canonical, 'locale.alternates': alternates,
                  'locale.currentRoute': registry['topics']['prayers']['relatedEnglish'] if is_english_master else page_url(registry, code, 'prayers'),
                  'locale.prayerLibraryUrl': SITE + '/prayer-library', 'locale.homeUrl': SITE + '/',
                  'locale.ogLocale': og_locales(registry)[code], 'locale.ogLocaleAlternates': og_alternates(code, registry)}
        def replace(match):
            key = match.group(1)
            if key not in tokens:
                raise ValueError(f'Prayer mirror: missing {key}')
            if key in ('locale.alternates', 'locale.ogLocaleAlternates', 'locale.prayerLinks'):
                return tokens[key]
            if key.startswith('locale.'):
                return escape(tokens[key], quote=True)
            # Inside JSON-LD, escape quotes and script delimiters as JSON, not HTML.
            before = template[:match.start()]
            if before.rfind('<script type="application/ld+json">') > before.rfind('</script>'):
                return json.dumps(tokens[key], ensure_ascii=False)[1:-1].replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
            return escape(tokens[key], quote=True)
        text = SLOT.sub(replace, template)
        if '{{' in text or '}}' in text:
            raise ValueError('Prayer mirror: unresolved slot')
        # The shared primary navigation is managed byte-for-byte by
        # sync-navigation.mjs, whose canonical form keeps authored label text
        # raw. Normalize entity escaping inside the nav block only, so the
        # generated pair matches the managed navigation exactly.
        nav_match = re.search(r'<nav class="links".*?</nav>', text, flags=re.S)
        if nav_match:
            from html import unescape
            text = text.replace(nav_match.group(0), unescape(nav_match.group(0)))
        # Only authored routes move to the same locale. Unmapped English
        # resources retain their canonical route; the existing selector handles
        # language preference at runtime. No localized URL is invented.
        if code != 'en':
            related = {config['relatedEnglish'].rstrip('/') or '/': page_url(registry, code, topic)
                       for topic, config in registry['topics'].items()
                       if code in topic_locales(registry, topic)}
            # Unmapped English resources keep their canonical absolute route;
            # relative ./ hrefs only exist in the English master's managed nav.
            text = re.sub(r'(<a\b[^>]*\bhref=["\'])\.?(/[^"\']*)(["\'])',
                          lambda match: match.group(1) + related.get(match.group(2), match.group(2)) + match.group(3), text)
        elif is_english_master:
            nav_match = re.search(r'<nav class="links".*?</nav>', text, flags=re.S)
            if nav_match:
                block = nav_match.group(0)
                text = text.replace(block, re.sub(r'(<a\b[^>]*\bhref=["\'])/(?!/)([^"\']*)(["\'])', r'\1./\2\3', block))
        else:
            # Locale-prefixed English guide (/en/...): the managed relative
            # nav links only resolve from the root master, so absolutize them.
            nav_match = re.search(r'<nav class="links".*?</nav>', text, flags=re.S)
            if nav_match:
                block = nav_match.group(0)
                text = text.replace(block, re.sub(r'(<a\b[^>]*\bhref=["\'])\./([^"\']*)(["\'])', r'\1/\2\3', block))
        guidance = load_guidance(root, code, 'prayers')
        if guidance:
            marker = '    <section class="section">'
            if text.count(marker) < 1:
                raise ValueError('Prayer guidance insertion target missing')
            text = text.replace(marker, render_lead(guidance) + '\n' + marker, 1)
        result[path] = finish_nav(text,root,code)
    return result


def render_pair(root=ROOT, registry=None):
    """Compatibility wrapper for the first English-master/Arabic pilot tests."""
    rendered = render_mirrors(root, registry)
    english_master = (root / 'saint-charbel-prayers.html')
    arabic_mirror = root / 'ar/prayers.html'
    return {path: rendered[path] for path in (english_master, arabic_mirror)}
