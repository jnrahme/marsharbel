#!/usr/bin/env python3
"""Build localized HTML, discovery links, routes and sitemap from strict catalogs."""
import argparse
from html import escape
import json
from pathlib import Path
import re
from string import Template

from i18n.catalog import ROOT, load_catalog, locale_topics, page_url, topic_locales


def alternate_links(registry, topic=None):
    languages = topic_locales(registry, topic) if topic else list(registry['locales'])
    links = {code: registry['site'] + page_url(registry, code, topic) for code in languages}
    default = registry['defaultLocale']
    if default not in links:
        # A topic authored only in some languages pairs with its existing English page.
        links = {default: registry['site'] + registry['topics'][topic]['relatedEnglish'], **links}
    links['x-default'] = links[default]
    return '\n'.join(f'<link rel="alternate" hreflang="{code}" href="{url}" />' for code, url in links.items())


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
        if path == '/' or (topic and language not in available and language == registry['defaultLocale']):
            path += '?lang=' + language
        current = ' aria-current="page"' if mark_current and language == code else ''
        links.append(f'<a href="{path}" lang="{language}" dir="{config["direction"]}"{current}>{escape(config["nativeName"])}</a>')
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
        related = ''.join(f'<li><a href="{page_url(registry, code, key)}">{escape(pages[key]["title"])}</a></li>' for key in locale_topics(registry, code) if key != topic)
        content = f'''<article><h1>{escape(page['title'])}</h1><p class="intro">{escape(page['intro'])}</p>
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
        brand=t('site.brand'), site=registry['site'], schema=schema_text, skip=t('navigation.skip'),
        home=page_url(registry, code) + ('?lang=en' if code == 'en' else ''),
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
            result[root / (page_url(registry, code, topic).lstrip('/') + '.html')] = render(registry, catalogs[code], code, template, topic)
        result[root / code / '.htaccess'] = '# Preserve language routes; never expose directory listings.\nOptions -Indexes\n'
    home = root / 'index.html'
    text = replace_block(home.read_text(), 'i18n-alternates', alternate_links(registry))
    # Existing pages already have the top selector; never generate a duplicate menu.
    text = replace_block(text, 'i18n-navigation', '')
    result[home] = text
    for topic, config in registry['topics'].items():
        related = config['relatedEnglish'].lstrip('/')
        path = root / (related + 'index.html' if related.endswith('/') else related + '.html')
        text = replace_block(path.read_text(), 'i18n-navigation', '')
        if registry['defaultLocale'] not in topic_locales(registry, topic):
            # The English page is this topic's English alternate, so it carries the same cluster.
            links = '\n'.join('  ' + line for line in alternate_links(registry, topic).split('\n'))
            text = replace_block(text, 'hreflang', links, begin='begin')
        result[path] = text
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
    def entry(url):
        lastmod = f'<lastmod>{lastmods[url]}</lastmod>' if url in lastmods else ''
        return f'  <url><loc>{url}</loc>{lastmod}</url>'
    text = text.replace('</urlset>', '\n' + '\n'.join(entry(url) for url in generated) + '\n</urlset>')
    result[sitemap] = text
    routing = {'homes':{code: cfg['home'] for code,cfg in registry['locales'].items()},
               'topics':{cfg['relatedEnglish']:{code:page_url(registry,code,topic) for code in topic_locales(registry,topic)} for topic,cfg in registry['topics'].items()}}
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
