"""Inject the same resolver/control in runtime and static generated pages.

This preparation is explicit: pending variants stay unavailable without JS too.
Reviewed manifest and UI copy must be supplied by the integration gate.
"""
from bs4 import BeautifulSoup
from html import escape
import re,json,subprocess
from i18n.catalog import read_json


_english_source_cache = {}

def with_english_sources(root, manifest):
    key = str(root)
    if key in _english_source_cache:
        return _english_source_cache[key]
    result = dict(manifest)
    sources = {}
    for item in manifest['pages'].values():
        path = root / item['sourcePath']
        if not path.exists():
            continue
        page = BeautifulSoup(path.read_text(), 'html.parser')
        canonical = page.select_one('link[rel=canonical]')
        english = page.select_one('link[rel=alternate][hreflang=en]')
        if canonical and english:
            from urllib.parse import urlsplit
            target = urlsplit(english['href'])
            if target.netloc == 'marsharbel.com' and target.scheme == 'https':
                sources[urlsplit(canonical['href']).path.rstrip('/') or '/'] = target.path
    result['englishSources'] = sources
    registry = read_json(root/'locales/registry.json')
    result['publishedHomes'] = {code: cfg['home'] for code,cfg in registry['locales'].items()
        if (root / cfg['home'].strip('/') / 'index.html').exists()}
    _english_source_cache[key] = result
    return result

def place_footer_navigation(text):
    """Move existing managed locale navigation to the semantic page-end footer."""
    soup=BeautifulSoup(text,'html.parser')
    bars=soup.select('nav.footer-locales')
    if not bars:return text
    if len(bars)!=1:raise ValueError('Expected one footer language bar')
    if bars[0].find_parent('footer'):return text
    pattern=r'<!-- i18n-navigation:start -->[\s\S]*?<!-- i18n-navigation:end -->'
    match=re.search(pattern,text)
    if not match:
        match=re.search(r'<nav\b[^>]*class=["\']footer-locales["\'][\s\S]*?</nav>',text)
    if not match:raise ValueError('Cannot locate misplaced footer language bar')
    block=match[0];text=text[:match.start()].rstrip(' \t')+text[match.end():]
    container='<div class="site-shell">\n'+block+'\n</div>\n'
    if '</footer>' in text:
        return text.replace('</footer>',container+'</footer>',1)
    if text.count('</main>')!=1:raise ValueError('Missing unique page end for locale footer')
    return text.replace('</main>','</main>\n<footer class="footer">\n'+container+'</footer>',1)

def inject_control(text, root, manifest, copy):
    manifest = with_english_sources(root, manifest)
    # English guide routes are live destinations, including the legacy prayer redirect.
    page=BeautifulSoup(text,'html.parser')
    canonical=page.select_one('link[rel=canonical]')
    registry=read_json(root/'locales/registry.json')
    english_guides={registry['site']+'/en/'+slug for slug in registry['locales']['en']['slugs'].values()}
    if canonical and canonical.get('href') in english_guides and not page.select_one('nav.footer-locales'):
        if '</footer>' not in text:raise ValueError('English guide missing semantic footer')
        links=' '.join('<a href="'+escape(cfg['home'])+'" hreflang="'+code+'" lang="'+code+'" dir="'+cfg['direction']+'">'+escape(cfg['nativeName'])+'</a>' for code,cfg in registry['locales'].items())
        block='<nav class="footer-locales" aria-label="Languages">'+links+'</nav>'
        text=text.replace('</footer>',block+'\n</footer>',1)
    text=place_footer_navigation(text)
    # Deterministic rebuilding: remove only our generated control resources.
    text=re.sub(r'<script\b[^>]*src=["\']/same-page-(?:manifest|copy|resolver|switcher)\.js["\'][^>]*></script>\s*','',text)
    text=re.sub(r'<link\b[^>]*id=["\']sc-language-css["\'][^>]*>\s*','',text)
    soup=BeautifulSoup(text,'html.parser')
    lang=soup.html.get('lang','en') if soup.html else 'en'
    if lang not in copy:raise ValueError('Missing reviewed selector copy '+lang)
    canonical=soup.select_one('link[rel=canonical]')
    if not canonical:raise ValueError('Language control requires canonical identity')
    href=canonical['href']
    # Use the JS resolver itself: no second, weaker availability predicate.
    driver="const fs=require('fs');const api=require(process.argv[1]);const d=JSON.parse(fs.readFileSync(0,'utf8'));let out={};for(const lang of d.manifest.languages)out[lang]=api.resolve(d.manifest,d.href,lang,d.actual);process.stdout.write(JSON.stringify(out));"
    choices=json.loads(subprocess.check_output(['node','-e',driver,str(root/'same-page-resolver.js')],input=json.dumps({'manifest':manifest,'href':href,'actual':lang}),text=True))
    # No-JS static choices must not retain guide/home substitutions.
    # Mutate only language nav blocks, never MAIN or ordinary editorial anchors.
    def static_nav(match):
        nav=BeautifulSoup(match[0],'html.parser').nav
        registry=read_json(root/'locales/registry.json')
        home=registry['locales'][lang]['home']
        if href.rstrip('/') == (registry['site']+home).rstrip('/'):
            nav['data-locale-section-navigation']=''
            for helper in nav.select('.sc-language-helper,.sc-unavailable-suffix'):helper.decompose()
            for a in nav.select('a[hreflang]'):
                code=a['hreflang'];cfg=registry['locales'][code]
                a['href']=cfg['home'];a['lang']=code;a['dir']=cfg['direction'];a.string=cfg['nativeName']
                for attr in ('aria-disabled','tabindex','aria-label','data-language-switch'):a.attrs.pop(attr,None)
            nav.attrs.pop('aria-describedby',None)
            return str(nav)
        for helper in nav.select('.sc-language-helper'):helper.decompose()
        unavailable=False
        for a in nav.select('a[hreflang]'):
            code=a['hreflang'];choice=choices.get(code,{})
            a.attrs.pop('lang',None)
            a.string=copy[lang]['names'].get(code,code)
            if choice.get('available'):
                a['href']=choice['href']
                for attr in ('aria-disabled','tabindex','aria-label'):a.attrs.pop(attr,None)
            else:
                unavailable=True
                a.attrs.pop('href',None);a['aria-disabled']='true';a['tabindex']='-1'
                a.string=copy[lang]['names'].get(code,code)+' ('+copy[lang]['suffix']+')'
        if unavailable:
            helper=BeautifulSoup('<span class="sc-language-helper"></span>','html.parser').span
            helper.string=copy[lang]['helper'];nav.append(helper)
        return str(nav)
    # Footer language links are locale-section navigation, never exact-page choices.
    def footer_nav(match):
        nav=BeautifulSoup(match[0],'html.parser').nav
        homes=read_json(root/'locales/registry.json')['locales']
        nav.attrs.pop('aria-describedby',None)
        for helper in nav.select('.sc-language-helper,.sc-unavailable-suffix'):helper.decompose()
        for a in nav.select('a[hreflang]'):
            code=a['hreflang']
            if code not in homes:raise ValueError('Unregistered footer locale '+code)
            a['href']=homes[code]['home']
            a.string=homes[code]['nativeName']
            a['lang']=code
            a['dir']=homes[code]['direction']
            for attr in ('aria-disabled','tabindex','aria-label','data-language-switch','style'):a.attrs.pop(attr,None)
        return str(nav)
    text=re.sub(r'<nav\b[^>]*class=["\']footer-locales["\'][\s\S]*?</nav>',footer_nav,text)
    text=re.sub(r'<nav\b[^>]*class=["\']locale-nav["\'][\s\S]*?</nav>',static_nav,text)
    text=text.replace('</head>','<link id="sc-language-css" rel="stylesheet" href="/same-page-switcher.css" />\n</head>')
    scripts='\n'.join('<script defer src="/'+name+'"></script>' for name in ['same-page-manifest.js','same-page-copy.js','same-page-resolver.js','same-page-switcher.js'])
    if text.count('</body>')!=1:raise ValueError('Missing unique body end')
    return text.replace('</body>',scripts+'\n</body>')


def control_outputs(root, texts, manifest, copy):
    import json
    from i18n.reviewed_history import history_manifest
    manifest = history_manifest(root,texts,manifest)
    from i18n.reviewed_travel import travel_manifest
    manifest = travel_manifest(root,texts,manifest)
    from i18n.reviewed_prayers import prayer_manifest
    manifest = prayer_manifest(root,texts,manifest)
    out={}
    for path,text in texts.items():
        if path.suffix=='.html' and 'https://marsharbel.com/' in text:out[path]=inject_control(text,root,manifest,copy)
    manifest = with_english_sources(root, manifest)
    out[root/'same-page-manifest.js']='window.SC_SAME_PAGE_MANIFEST = '+json.dumps(manifest,ensure_ascii=False,separators=(',',':'))+';\n'
    out[root/'same-page-copy.js']='window.SC_SAME_PAGE_COPY = '+json.dumps(copy,ensure_ascii=False,separators=(',',':'))+';\n'
    return out
