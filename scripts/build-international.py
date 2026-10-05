#!/usr/bin/env python3
"""Build localized HTML, discovery links, routes and sitemap from strict catalogs."""
import argparse
from html import escape
import json
from pathlib import Path
import re
from string import Template

from i18n.metadata import og_locales, published_locales, selector_aliases
from i18n.catalog import ROOT, load_catalog, locale_topics, page_url, topic_locales, read_json
from i18n.mirror import render_mirrors
from i18n.qadisha_mirror import render_qadisha
from i18n.travel_mirror import render_travel
from i18n.monastery_mirror import render_monasteries
from i18n.feast_mirror import render_feast
from i18n.litany_mirror import render_litany
from i18n.eucharistic_mirror import render_eucharistic
from i18n.chaplet_mirror import render_chaplet
from i18n.exact_master import render_exact_set
from i18n.tour_nav import tour_nav
from i18n.travel_components import travel_frame


def alternate_links(registry, topic=None):
    languages = topic_locales(registry, topic) if topic else list(registry['locales'])
    if topic in registry.get('exactMirrors', {}):
        languages=[c for c in languages if c not in registry['exactMirrors'][topic].get('renderLocales',[])]
    links = {code: registry['site'] + page_url(registry, code, topic) for code in languages}
    default = registry['defaultLocale']
    if default not in links and topic not in registry.get('exactMirrors', {}):
        # A topic authored only in some languages pairs with its existing English page.
        links = {default: registry['site'] + registry['topics'][topic]['relatedEnglish'], **links}
    links['x-default'] = links.get(default, next(iter(links.values())))
    return '\n'.join(f'<link rel="alternate" hreflang="{code}" href="{url}" />' for code, url in links.items())



def footer_locale_bar(registry):
    links = []
    for language, config in registry['locales'].items():
        path = page_url(registry, language)
        links.append(f'<a href="{path}" hreflang="{language}" lang="{language}" dir="{config["direction"]}">{escape(config["nativeName"])}</a>')
    return '<nav class="footer-locales" aria-label="Languages">' + ' <span aria-hidden="true">-</span> '.join(links) + '</nav>'

def og_locale_tags(registry, code):
    OG_LOCALE = og_locales(registry)
    tags = [f'<meta property="og:locale" content="{OG_LOCALE[code]}" />']
    for other in registry['locales']:
        if other != code:
            tags.append(f'<meta property="og:locale:alternate" content="{OG_LOCALE[other]}" />')
    return '\n'.join(tags)

def navigation(registry, code, topic=None, mark_current=True):
    links = []
    available = topic_locales(registry, topic) if topic else list(registry['locales'])
    for language, config in registry['locales'].items():
        if language in available:
            path = page_url(registry, language, topic)
        elif language == registry['defaultLocale']:
            path = registry['topics'][topic]['relatedEnglish']
        else:
            path = page_url(registry, language)
        current = ' aria-current="page"' if mark_current and language == code else ''
        links.append(f'<a href="{path}" hreflang="{language}" lang="{language}" dir="{config["direction"]}"{current}>{escape(config["nativeName"])}</a>')
    # Locale pages load no site JavaScript, but translate.js on an English
    # destination honors the stored sc_lang_pref and would bounce a visitor
    # back to their previous locale. A click on a language link is an explicit
    # choice, so persist it before navigation (the same key translate.js uses).
    links.append('<script defer src="/locale-pref.js"></script>')
    return '\n'.join(links)


def render(registry, catalog, code, template, topic=None):
    common, pages = catalog['common'], catalog['pages']
    t = lambda key: escape(common[key])
    if topic:
        page = pages[topic]
        section_ids = registry['topics'][topic]['sections']
        contents = ''.join(f'<li><a href="#section-{key}">{escape(page["sections"][key]["title"])}</a></li>' for key in section_ids)
        sections = ''.join(f'<section id="section-{key}" class="section"><h2>{escape(page["sections"][key]["title"])}</h2><p>{escape(page["sections"][key]["body"])}</p></section>' for key in section_ids)
        sources = ''.join(f'<li><a href="{escape(registry["sources"][key])}">{t("sources." + key)}</a></li>' for key in registry['topics'][topic]['sources'])
        full = page.get('fullGuide')
        full_href = registry['topics'][topic]['relatedEnglish'] + ('' if code == 'en' else '?lang=en')
        full_attrs = '' if code == 'en' else ' lang="en" dir="ltr"'
        full_guide = (f'<p class="full-guide">{escape(full["lead"])} <a href="{full_href}"{full_attrs}>{escape(full["label"])}</a>.</p>' if full else '')
        related_topics = [key for key in locale_topics(registry, code) if key != topic]
        # Readers of story leaves should get back to the hub before the broader
        # catalog; homepage cards still expose every topic for discovery.
        if topic.endswith('Story') and 'miracles' in related_topics:
            related_topics.remove('miracles')
            related_topics.insert(0, 'miracles')
        related = ''.join(f'<li><a href="{page_url(registry, code, key)}">{escape(pages[key]["title"])}</a></li>' for key in related_topics)
        content = f'''<article><h1>{escape(page['title'])}</h1><p class="intro">{escape(page['intro'])}</p>{full_guide}
<nav class="contents" aria-label="{t('navigation.contents')}"><h2>{t('navigation.contents')}</h2><ol>{contents}</ol></nav>
{sections}<section class="section"><h2>{t('navigation.sources')}</h2><ul>{sources}</ul></section></article>
<aside class="related"><h2>{t('navigation.related')}</h2><ul>{related}</ul><a href="{registry['topics'][topic]['relatedEnglish']}?lang=en">{t('navigation.englishResource')}</a></aside>'''
        title, description = page['title'], page['description']
    else:
        cards = ''.join(f'<section class="section"><h2><a href="{page_url(registry, code, key)}">{escape(pages[key]["title"])}</a></h2><p>{escape(pages[key]["intro"])}</p><a href="{page_url(registry, code, key)}">{t("navigation.openGuide")}</a></section>' for key in locale_topics(registry, code))
        content = f'<h1>{t("home.heading")}</h1><p class="intro">{t("home.intro")}</p>{cards}<aside class="related"><h2>{t("home.availabilityHeading")}</h2><p>{t("home.availability")}</p></aside>'
        title, description = common['home.title'], common['home.description']
    url = registry['site'] + page_url(registry, code, topic)
    schema = {'@context':'https://schema.org', '@type':'WebPage', 'name':title, 'description':description,
              'url':url, 'inLanguage':code, 'isPartOf':{'@id':registry['site']+'/#website'}}
    # Catalogs are plain text; escape JSON script delimiters separately from HTML.
    schema_text = json.dumps(schema, ensure_ascii=False).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
    return template.substitute(language=code, direction=registry['locales'][code]['direction'], title=escape(title),
        description=escape(description), canonical=url, alternates=alternate_links(registry, topic),
        oglocale=og_locale_tags(registry, code),
        brand=t('site.brand'), site=registry['site'], schema=schema_text, skip=t('navigation.skip'),
        home=page_url(registry, code),
        chooseLanguage=t('navigation.chooseLanguage'), navigation=navigation(registry, code, topic),
        homeLabel=t('navigation.home'), content=content, footer=t('site.footer'))


def replace_block(text, name, content, begin='start'):
    start, end = f'<!-- {name}:{begin} -->', f'<!-- {name}:end -->'
    pattern = re.escape(start) + r'.*?' + re.escape(end)
    if len(re.findall(pattern, text, flags=re.S)) != 1:
        raise ValueError(f'Expected one managed block: {name}')
    return re.sub(pattern, lambda _: start + '\n' + content + '\n' + end, text, flags=re.S)


def outputs(root=ROOT):
    registry, catalogs = load_catalog(root)
    template = Template((root / 'templates/international/page.html').read_text())
    result = {}
    for code in registry['locales']:
        if code != registry['defaultLocale']:
            result[root / code / 'index.html'] = render(registry, catalogs[code], code, template)
        for topic in locale_topics(registry, code):
            route = page_url(registry, code, topic)
            output_path = root / (route.lstrip('/') + 'index.html' if route.endswith('/') else route.lstrip('/') + '.html')
            result[output_path] = render(registry, catalogs[code], code, template, topic)
        result[root / code / '.htaccess'] = '# Preserve language routes; never expose directory listings.\nOptions -Indexes\n'
        # A nested localized hub is a real directory with its own index; the
        # parent locale's Options -Indexes must not hide that index.
        for topic in locale_topics(registry, code):
            route = page_url(registry, code, topic)
            if route.endswith('/'):
                result[root / route.lstrip('/') / '.htaccess'] = (
                    '# Canonical localized directory hub.\nOptions -Indexes\nDirectoryIndex index.html\n')
    # The reviewed pair shares one skeleton; other guide locales remain unchanged.
    mirrors = render_mirrors(root, registry)
    # The English master receives its existing managed hreflang from the loop
    # below; only the Arabic mirror is handed to the generated-page set here.
    english_mirror = mirrors.pop(root / 'saint-charbel-prayers.html')
    result.update(mirrors)
    qadisha = render_qadisha(root, registry)
    english_qadisha = qadisha.pop(root / 'qadisha-valley.html')
    result.update(qadisha)
    result.update(render_travel(root, registry))
    monasteries = render_monasteries(root, registry)
    english_monasteries = {path: monasteries.pop(path) for path in (root / 'qannoubine-monastery.html', root / 'qozhaya-monastery.html')}
    result.update(monasteries)
    result.update(render_litany(root))
    eucharistic = render_eucharistic(root, registry)
    result.update(eucharistic)
    result.update(render_chaplet(root))
    result.update(render_feast(root))
    # Master cluster composition happens below before exact-source rendering.
    # Nested localized directory indexes must be explicit; Options -Indexes
    # otherwise hides hubs on some hosts.
    for code in published_locales(registry, 'eucharistic'):
        if code != registry['defaultLocale']:
            result[root/code/'miracles/eucharistic/.htaccess'] = (
                '# Canonical localized Eucharistic directory hub.\nOptions -Indexes\nDirectoryIndex index.html\n')
    home = root / 'index.html'
    text = replace_block(home.read_text(), 'i18n-alternates', alternate_links(registry))
    # Crawlable cross-locale links for English pages live in the footer block; the
    # top selector stays JS-only.
    text = replace_block(text, 'i18n-navigation', footer_locale_bar(registry))
    result[home] = text
    for topic, config in registry['topics'].items():
        related = config['relatedEnglish'].lstrip('/')
        path = root / (related + 'index.html' if related.endswith('/') else related + '.html')
        text = (english_mirror if path == root / 'saint-charbel-prayers.html' else
                english_qadisha if path == root / 'qadisha-valley.html' else
                english_monasteries[path] if path in english_monasteries else
                result.get(path, path.read_text()))
        if related != 'saint-charbel-feast-day':
            text = replace_block(text, 'i18n-navigation', footer_locale_bar(registry))
        if registry['defaultLocale'] not in topic_locales(registry, topic):
            # The English page is this topic's English alternate, so it carries the same cluster.
            links = '\n'.join('  ' + line for line in alternate_links(registry, topic).split('\n'))
            text = replace_block(text, 'hreflang', links, begin='begin')
        result[path] = text
    # Declared discovery clusters are composed reciprocally; they do not enable
    # the same-page selector or certify independent content/native review.
    for cfg in registry.get('exactMirrors', {}).values():
        master=root/(cfg['english'].lstrip('/')+'index.html' if cfg['english'].endswith('/') else cfg['english'].lstrip('/')+'.html')
        master_text=master.read_text()
        block=re.search(r'<!-- hreflang:begin -->[\s\S]*?<!-- hreflang:end -->',master_text)
        for route in cfg['routes'].values():
            path=root/(route.lstrip('/')+'index.html' if route.endswith('/') else route.lstrip('/')+'.html')
            text=result.get(path,path.read_text())
            if route==cfg['english'] and block:
                text=re.sub(r'<!-- hreflang:begin -->[\s\S]*?<!-- hreflang:end -->',lambda _:block[0],text,count=1)
            elif route!=cfg['english'] and route not in [cfg['routes'].get(c) for c in cfg.get('renderLocales',[])]:
                if block and '<!-- hreflang:begin -->' in text:
                    from bs4 import BeautifulSoup
                    existing={(n.get('hreflang'),n.get('href')) for n in BeautifulSoup(text,'html.parser').select('head link[hreflang]')}
                    target={(code,registry['site']+url) for code,url in {**cfg['routes'],'x-default':cfg['english']}.items()}
                    if existing==target:continue
                    text=re.sub(r'<!-- hreflang:begin -->[\s\S]*?<!-- hreflang:end -->',lambda _:block[0],text,count=1)
                else:
                    head_end=text.index('</head>')
                    head=re.sub(r'<link\b[^>]*\bhreflang=["\'][^>]*>\s*','',text[:head_end])
                    links='\n'.join(f'<link rel="alternate" hreflang="{code}" href="{registry["site"]+url}" />' for code,url in {**cfg['routes'],'x-default':cfg['english']}.items())
                    text=head+links+'\n'+text[head_end:]
            result[path]=text
    result.update(render_exact_set(root, registry))
    # Keep the English homepage and legacy canonical URLs stable.
    sitemap = root / 'sitemap.xml'
    text = sitemap.read_text()
    pattern = '|'.join(re.escape(code) for code in registry['locales'])
    localized = re.compile(r'\s*<url>\s*<loc>(https://marsharbel.com/(?:' + pattern + r')(?:/[^<]*)?)</loc>(?:\s*<lastmod>([^<]*)</lastmod>)?\s*</url>')
    # lastmod is owned by scripts/sitemap_lastmod.py (git history); keep it stable here.
    lastmods = {match.group(1): match.group(2) for match in localized.finditer(text) if match.group(2)}
    text = localized.sub('', text)
    generated = [registry['site'] + page_url(registry, code) for code in registry['locales'] if code != registry['defaultLocale']]
    generated += [registry['site'] + page_url(registry, code, topic) for code in registry['locales'] for topic in locale_topics(registry, code)]
    generated += [registry['site'] + '/' + code + '/miracles/eucharistic/' + ('' if slug=='index' else slug)
                  for code in published_locales(registry, 'eucharistic') if code != registry['defaultLocale']
                  for slug in ('index','lanciano','bolsena-orvieto','siena','santarem','sokolka','legnica','ludbreg','amsterdam','ivorra','faverney')]
    generated += [registry['site'] + route for mirror in {**registry.get('authoredMirrors', {}), **registry.get('exactMirrors', {})}.values()
                  for route in mirror['routes'].values() if route != mirror['english']]
    def entry(url):
        lastmod = f'<lastmod>{lastmods[url]}</lastmod>' if url in lastmods else ''
        return f'  <url><loc>{url}</loc>{lastmod}</url>'
    text = text.replace('</urlset>', '\n' + '\n'.join(entry(url) for url in dict.fromkeys(generated)) + '\n</urlset>')
    text = re.sub(r'\n[ \t]*\n(?:[ \t]*\n)+', '\n\n', text)
    result[sitemap] = text
    routing = {'aliases':selector_aliases(registry), 'homes':{code: cfg['home'] for code,cfg in registry['locales'].items()},
               'topics':{cfg['relatedEnglish']:{code:page_url(registry,code,topic) for code in topic_locales(registry,topic)} for topic,cfg in registry['topics'].items()}}
    for mirror in {**registry.get('authoredMirrors', {}), **registry.get('exactMirrors', {})}.values():
        routing['topics'][mirror['english']] = mirror['routes']
    routing['topics']['/saint-charbel-feast-day']['en']='/saint-charbel-feast-day'
    for slug in ('', 'lanciano', 'bolsena-orvieto', 'siena', 'santarem', 'sokolka', 'legnica','ludbreg','amsterdam','ivorra','faverney'):
        english = '/miracles/eucharistic/' + slug
        routing['topics'][english] = {code:('/' + code if code != 'en' else '') + english
                                       for code in published_locales(registry, 'eucharistic')}
    # The English Chaplet remains the master; add only the authored Arabic alternate.
    chaplet = root / 'saint-charbel-chaplet.html'
    chaplet_text = chaplet.read_text()
    chaplet_alt = '  <link rel="alternate" hreflang="ar" href="https://marsharbel.com/ar/saint-charbel-chaplet" />'
    chaplet_text = re.sub(r'(<!-- hreflang:begin -->).*?(<!-- hreflang:end -->)',
                          lambda m: m[1] + '\n  <link rel="alternate" hreflang="x-default" href="https://marsharbel.com/saint-charbel-chaplet" />\n  <link rel="alternate" hreflang="en" href="https://marsharbel.com/saint-charbel-chaplet" />\n' + chaplet_alt + '\n  ' + m[2],
                          chaplet_text, count=1, flags=re.S)
    result[chaplet] = chaplet_text
    result[root / 'qadisha-valley.html'] = english_qadisha
    result.update(english_monasteries)
    result[root / 'locale-routes.js'] = '// Generated by npm run i18n:build. Edit locales/registry.json.\nwindow.SC_LOCALE_ROUTES = ' + json.dumps(routing, ensure_ascii=False, separators=(',', ':')) + ';\n'
    htaccess = root / '.htaccess'
    start, end = '# i18n-routes:start', '# i18n-routes:end'
    # Localized hubs use real directory indexes. This avoids file/directory name
    # collisions on LiteSpeed and gives every non-English homepage one canonical URL.
    nondefault = '|'.join(code for code in registry['locales'] if code != registry['defaultLocale'])
    rules = (f'{start}\n'
             f'RewriteRule ^en/?$ / [R=301,L]\n'
             f'RewriteRule ^({nondefault})/index(?:\\.html)?$ /$1/ [R=301,L]\n'
             f'RewriteRule ^({nondefault})\\.html$ /$1/ [R=301,L]\n'
             f'RewriteRule ^({nondefault})$ /$1/ [R=301,L]\n'
             f'{end}')
    updated, count = re.subn(re.escape(start)+r'.*?'+re.escape(end), lambda _:rules, htaccess.read_text(), flags=re.S)
    if count != 1:
        raise ValueError('Expected exactly one managed i18n-routes block in .htaccess')
    result[htaccess] = updated
    for route in json.loads((root/'locales/travel-routes.json').read_text())['destinations']:
        path=root/(route.lstrip('/')+'.html')
        result.setdefault(path,path.read_text())
    for path,text in list(result.items()):
        if path.suffix == '.html' and '<header' in text:
            import re as _re
            match = _re.search(r'<html[^>]*lang=["\']([^"\']+)',text)
            if match:
                code=match[1]
                route='/' + str(path.relative_to(root)).removesuffix('.html')
                route=route.removesuffix('index') if route.endswith('/index') else route
                result[path] = travel_frame(tour_nav(text,root,code),root,code,route,registry)
    from i18n.same_page_injection import control_outputs
    manifest=read_json(root/'locales/same-page-manifest.pending.json')
    control_copy=read_json(root/'locales/same-page-copy.json')
    result.update(control_outputs(root,{path:text for path,text in result.items() if path.suffix=='.html'},manifest,control_copy))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    generated = outputs()
    stale = []
    for path, expected in generated.items():
        if not path.exists() or path.read_text() != expected:
            if args.check:
                stale.append(str(path.relative_to(ROOT)))
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(expected, encoding='utf-8')
    if stale:
        raise SystemExit('Stale generated files; run npm run i18n:build: ' + ', '.join(stale))
    registry, _ = load_catalog()
    languages = len(registry['locales'])
    guides = sum(len(locale_topics(registry, code)) for code in registry['locales'])
    print(f'Localization {"checked" if args.check else "built"}: {languages} languages, {guides} guides, {languages - 1} language homepages.')


if __name__ == '__main__':
    main()
