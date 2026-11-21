"""Render homepages from the English master, never a separate locale layout."""
import hashlib
import os
import json
import re
from urllib.parse import urljoin, urlsplit
from i18n.metadata import og_locales
from i18n.keyed_master import apply_keyed_master
from i18n.mirror_structure import check_pair
from bs4 import BeautifulSoup, NavigableString
from i18n.catalog import read_json, page_url, topic_locales, published_home_locales

HEADER_NAV_LABELS = {'Media': 'navigation.media', 'Music': 'navigation.music', 'Video': 'navigation.video', 'Gallery': 'navigation.gallery'}


# Only the reviewed home hero, meditation promo, and storybook promo. Other English
# links retain their existing behavior and markup.
PRAYER_DISCLOSURE_LOCALES = frozenset({'ar', 'de', 'es', 'fr', 'hi', 'it', 'pl', 'pt', 'ru', 'th'})
PRAYER_DISCLOSURE_CONTROLS = (
    ('a.home-hero-cta2', '/mystery-meditation', 'home.home-cinematic-hero.pray-today-s-rosary'),
    ('a.promo-link[href="/mystery-meditation"]', '/mystery-meditation', 'home.section.start-today-s-meditation'),
    ('a.promo-link[href="/story"]', '/story', 'home.section.open-the-storybook'),
)


def mark_home_prayer_disclosures(soup, lang, copy, qualifier):
    """Validate the exact reviewed controls before marking their English target."""
    if lang not in PRAYER_DISCLOSURE_LOCALES:
        return
    if not qualifier or qualifier != qualifier.strip():
        raise ValueError(f'Home {lang}: invalid prayer English qualifier')
    for selector, href, key in PRAYER_DISCLOSURE_CONTROLS:
        matches = soup.select(selector)
        if len(matches) != 1:
            raise ValueError(f'Home {lang}: prayer control missing or duplicated: {key}')
        anchor = matches[0]
        label = copy[key]
        if (anchor.get('href') != href or
                not label.endswith(' ' + qualifier) or label.count(qualifier) != 1):
            raise ValueError(f'Home {lang}: prayer target or qualifier changed: {key}')
        # Ignore only the existing decorative arrow; all readable text must
        # match the complete catalog message, not a label assembled at runtime.
        visible = ''.join(str(t) for t in anchor.find_all(string=True)
                          if not any(p.get('aria-hidden') == 'true' for p in t.parents)).strip()
        if visible != label:
            raise ValueError(f'Home {lang}: prayer visible label differs: {key}')
        anchor['hreflang'] = 'en'
        anchor['aria-label'] = label


def render_home(root, registry, lang, catalog=None):
    if lang not in published_home_locales(registry):
        raise ValueError(f'{lang}: unpublished homepage renderer')
    raw, soup, copy = apply_keyed_master(root, 'home', lang, catalog)
    # Preserve asset paths, srcsets, forms and JS navigation from a nested route.
    for node in soup.select('[href], [src], [srcset], [action], [data-src-mp4]'):
        for attr in ('href', 'src', 'action', 'data-src-mp4'):
            if node.has_attr(attr) and not node[attr].startswith(('#', 'mailto:', 'tel:', 'data:', 'javascript:')):
                node[attr] = urljoin('/', node[attr])
        if node.has_attr('srcset'):
            node['srcset'] = ', '.join(urljoin('/', p.strip().split()[0]) + (' ' + ' '.join(p.strip().split()[1:]) if len(p.strip().split()) > 1 else '') for p in node['srcset'].split(','))
    # Registry discovery changes are metadata-only, not authored content.
    for node in soup.select('link[rel=alternate][hreflang]'):node.decompose()
    for code,path in {**{c:registry['locales'][c]['home'] for c in published_home_locales(registry)},'x-default':'/'}.items():
        soup.head.append(soup.new_tag('link',rel='alternate',hreflang=code,href=registry['site']+path))
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
    for cfg in registry.get('pageMirrors', {}).values():
        if lang in cfg['routes'] and (lang in registry.get('limitedLaunchLocales', []) or cfg['english'] == '/travel' or (lang == 'ar' and lang in cfg.get('renderLocales', []))):
            twins[cfg['english'].rstrip('/')] = cfg['routes'][lang]
    # The reviewed film lead points at the EN canonical page on the master home;
    # repoint it to the released locale article wherever the strict family renders.
    film = registry.get('pageMirrors', {}).get('film-premiere-master')
    if film and lang in film.get('renderLocales', []):
        leads = soup.select('a.home-news-lead--film[href="/charbel-film-premiere"]')
        if len(leads) != 1:
            raise ValueError('Film lead source destination changed ' + lang)
        leads[0]['href'] = film['routes'][lang]
    # Same repoint for the home medal card: the medal master's locale twin is
    # the card destination wherever the family renders (mirrors the film lead).
    medal = registry.get('pageMirrors', {}).get('saint-charbel-medal-master')
    if medal and lang in medal.get('renderLocales', []):
        cards = soup.select('section.home-medal a[href="/saint-charbel-medal"]')
        if len(cards) != 1:
            raise ValueError('Medal card source destination changed ' + lang)
        cards[0]['href'] = medal['routes'][lang]
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
    if lang in PRAYER_DISCLOSURE_LOCALES:
        for english in {href for _, href, _ in PRAYER_DISCLOSURE_CONTROLS}:
            if any(lang in cfg.get('routes', {}) for cfg in registry.get('pageMirrors', {}).values()
                   if cfg.get('english') == english):
                raise ValueError(f'Home {lang}: prayer twin now exists; review the English handoff')
        qualifier = read_json(root / f'locales/{lang}/encyclopedia-trail.json')['englishQualifier']
        mark_home_prayer_disclosures(soup, lang, copy, qualifier)
    # The daily-rosary YouTube promo resolves to the locale's own rosary twin
    # #pray-along section when the locale publishes one; homes without a twin
    # keep the English target (marked English by launch availability on hi/th,
    # inline qualifier in the label on ru).
    promo = soup.select('a.promo-link[href="/rosary-visual-guide#pray-along"]')
    if len(promo) != 1:
        raise ValueError(f'Home {lang}: YouTube promo anchor missing or duplicated')
    if lang in topic_locales(registry, 'rosary'):
        promo[0]['href'] = page_url(registry, lang, 'rosary') + '#pray-along'
    # Keep the hand-authored intro twin (same-page AR-2 pair, e.g. /ar/rosary)
    # reachable from home after the promo retarget above: when the twin file
    # exists and is not the guide page itself, add a promo link labelled with
    # the twin's own H1 so no untranslated link text is invented.
    twin_path = root / lang / 'rosary.html'
    guide_file = root / (page_url(registry, lang, 'rosary').strip('/').replace('/', os.sep) + '.html') if lang in topic_locales(registry, 'rosary') else None
    if twin_path.exists() and (guide_file is None or twin_path.resolve() != guide_file.resolve()):
        twin_h1 = BeautifulSoup(twin_path.read_text(encoding='utf-8'), 'html.parser').find('h1').get_text(strip=True)
        arrow = soup.new_tag('span', **{'aria-hidden': 'true'})
        arrow.string = '\u2192'
        twin_link = soup.new_tag('a', **{'class': 'promo-link intro-twin-link', 'href': '/' + lang + '/rosary'})
        twin_link.string = twin_h1 + ' '
        twin_link.append(arrow)
        promo[0].insert_before(twin_link)
    for script in soup.select('script[type="application/ld+json"]'):
        data = json.loads(script.string)
        for item in data.get('@graph', []):
            if item.get('@type') == 'WebPage':
                item.update(url=canonical, inLanguage=lang, name=soup.title.get_text(), description=soup.select_one('meta[name=description]')['content'])
        script.string = json.dumps(data, ensure_ascii=False).replace('<', '\\u003c')
    # Shared Media/Music/Video/Gallery header chrome uses the locale's reviewed common.json label; never new text.
    common_nav = read_json(root / f'locales/{lang}/common.json')
    for link in soup.select('header nav a'):
        key = HEADER_NAV_LABELS.get(link.get_text(strip=True))
        if not key: continue
        chev = link.find('span', class_='nav-chev')
        if chev: chev.extract()
        link.clear(); link.append(common_nav[key])
        if chev: link.append(chev)
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
    mismatches = check_pair(raw.decode('utf-8'), rendered, '/', route, normalizers=('home-intro-twin-link',))
    if mismatches:
        raise ValueError(f'Home {lang}: mirror structure diverged: {mismatches}')
    if lang in registry.get('limitedLaunchLocales', []):
        from i18n.prayer_runtime import share_head
        rendered=share_head(rendered,root,lang)
    from i18n.launch_availability import apply_launch_availability
    rendered = apply_launch_availability(rendered, root, registry, lang, home=True)
    # Match the existing Travel frame serializer's canonical indentation so
    # reprocessing a generated home is byte-idempotent, not just DOM-equal.
    # This runs last: launch-availability re-serializes through BeautifulSoup,
    # which normalizes the indentation back out of the header.
    travel = registry.get('authoredMirrors', {}).get('travel', {}).get('routes', {}).get(lang)
    if not travel:
        travel = next((cfg['routes'][lang] for cfg in registry.get('pageMirrors', {}).values() if cfg['english'] == '/travel' and lang in cfg.get('renderLocales', [])), None)
    if travel:
        rendered = re.sub(r'(?m)^([ \t]*)(<a href="' + re.escape(travel) + r'">[^<]*</a>)$',
                          lambda match: '        ' + match[2], rendered)
    from i18n.ru_travel_chrome import localize_travel_chrome
    from i18n.encyclopedia_nav import route_and_mark_nav
    return localize_travel_chrome(route_and_mark_nav(rendered, root, lang), registry, lang, 'home')


def render_home_set(root, registry):
    return {root / lang / 'index.html': render_home(root, registry, lang)
            for lang in registry.get('homepageMirrors', {}).get('renderLocales', [])}
