"""Inactive strict film family gate. Activation and pins require independent review."""
import html,json,re
from datetime import date
from urllib.parse import urljoin,urlsplit
from xml.etree import ElementTree as ET
from bs4 import BeautifulSoup
from i18n.feature_mirror import adapted,digest,one,shell_digest
from i18n.keyed_master import apply_keyed_master
FAMILY='film-premiere-master'
SLUG='charbel-film-premiere'
ID='charbel-premiere-release-2026-10'
RULE='.film-news-article p a{text-decoration:underline;text-underline-offset:.15em}'
FONT="body{font-family:'Manrope','Segoe UI',sans-serif}h1,h2{font-family:'Cormorant Garamond',serif}html[lang=\"ar\"] body{font-family:'Noto Sans Arabic','Manrope',sans-serif}html[lang=\"ar\"] h1,html[lang=\"ar\"] h2{font-family:'Noto Naskh Arabic','Noto Sans Arabic',serif}"
def style_for(code):return RULE if code=='en' else RULE+FONT
def registered(root):
    path=root/'locales/registry.json'
    if not path.is_file():return False
    return FAMILY in json.loads(path.read_text()).get('pageMirrors',{})
def validate_discovery(root,registry,routes):
    site=registry['site']
    ns={'s':'http://www.sitemaps.org/schemas/sitemap/0.9'}
    sitemap=ET.parse(root/'sitemap.xml')
    entries=sitemap.findall('s:url',ns)
    for code,route in sorted(routes.items()):
        matches=[e for e in entries if e.findtext('s:loc',namespaces=ns)==site+route]
        if len(matches)!=1:raise ValueError('film: sitemap URL must occur exactly once '+code)
        modified=matches[0].findtext('s:lastmod',namespaces=ns)
        try:
            if not modified or not re.fullmatch(r'\d{4}-\d{2}-\d{2}',modified):raise ValueError()
            date.fromisoformat(modified)
        except ValueError:raise ValueError('film: valid sitemap lastmod required '+code)
    def crawlable_link(soup,selector,base,target):
        for a in soup.select(selector):
            raw=a.get('href','')
            if not raw or urlsplit(raw).scheme not in ('','http','https'):continue
            if urljoin(base,raw)==target and a.get_text(strip=True) and not any(a.has_attr(k) for k in ('hidden','inert')) and a.get('aria-hidden')!='true' and 'nofollow' not in a.get('rel',[]):return True
        return False
    for code,cfg in sorted(registry['locales'].items()):
        home=cfg.get('home')
        if not home:continue
        file='index.html' if home=='/' else home.lstrip('/')+'index.html'
        soup=BeautifulSoup((root/file).read_text(),'html.parser')
        if not crawlable_link(soup,'a.home-news-lead--film[href]',site+home,site+routes[code]):raise ValueError('film: home lead must reach own locale article '+code)
    news=BeautifulSoup((root/'news.html').read_text(),'html.parser')
    if not crawlable_link(news,'article#'+ID+' a.card-cover[href]',site+'/news',site+routes['en']):raise ValueError('film: news card must reach EN article')
def validate_family(root):
    registry=json.loads((root/'locales/registry.json').read_text())
    if FAMILY not in registry.get('pageMirrors',{}):return []
    cfg=registry['pageMirrors'][FAMILY];codes=set(registry['locales'])
    if len(codes)!=12 or registry['defaultLocale']!='en':raise ValueError('film: active locale set must contain exactly 12 including EN')
    routes={code:('/'+SLUG if code=='en' else '/'+code+'/'+SLUG) for code in codes}
    if cfg.get('master')!=SLUG+'.html' or cfg.get('english')!=routes['en']:raise ValueError('film: strict EN master identity mismatch')
    if cfg.get('routes')!={c:p for c,p in routes.items() if c!='en'} or set(cfg.get('renderLocales',[]))!=codes-{'en'} or len(cfg.get('renderLocales',[]))!=11:raise ValueError('film: locale membership/routes must be exactly all 12 once')
    contract=json.loads((root/'config/film-master-family.json').read_text())
    if contract.get('family')!=FAMILY or set(contract.get('shellSha256',{}))!=codes:raise ValueError('film: independent shell pins must cover all 12')
    template=(root/'templates/news-desk/cards.html').read_text();raw=one(BeautifulSoup(template,'html.parser'),'article#'+ID)
    keys=set(re.findall(r'\$\{([^}]+)\}',str(raw)))
    if not keys or any(not k.startswith('premiere.') for k in keys):raise ValueError('film: source feature key scope mismatch')
    english=json.loads((root/'locales/en/news-desk.json').read_text());values={k:english[k] for k in sorted(keys)}
    rendered=re.sub(r'\$\{([^}]+)\}',lambda m:html.escape(english[m[1]],quote=True),str(raw))
    source=one(BeautifulSoup((root/'news.html').read_text(),'html.parser'),'article#'+ID)
    if str(source)!=str(BeautifulSoup(rendered,'html.parser').article):raise ValueError('film: served news source differs from keyed source')
    for name,value in {'templateSha256':digest(str(raw)),'englishCatalogSha256':digest(json.dumps(values,ensure_ascii=False,sort_keys=True)),'sourceFeatureSha256':digest(str(source))}.items():
        if contract.get(name)!=value:raise ValueError('film: stale source provenance '+name)
    master=BeautifulSoup((root/(SLUG+'.html')).read_text(),'html.parser')
    if str(one(master,'main > article.film-news-article'))!=str(adapted(source)):raise ValueError('film: EN article differs from adapted news feature')
    alternates={**{c:registry['site']+p for c,p in routes.items()},'x-default':registry['site']+routes['en']}
    for code,route in sorted(routes.items()):
        file=SLUG+'.html' if code=='en' else code+'/'+SLUG+'.html';text=(root/file).read_text();soup=BeautifulSoup(text,'html.parser')
        if soup.html.get('lang')!=code or soup.html.get('dir')!=registry['locales'][code]['direction']:raise ValueError('film: locale identity mismatch '+code)
        if one(soup,'link[rel=canonical]').get('href')!=registry['site']+route:raise ValueError('film: canonical mismatch '+code)
        links=soup.select('link[rel=alternate][hreflang]')
        if len(links)!=13 or {a['hreflang']:a.get('href') for a in links}!=alternates:raise ValueError('film: reciprocal cluster/x-default mismatch '+code)
        styles=soup.select('head style')
        if len(styles)!=1 or styles[0].get_text()!=style_for(code):raise ValueError('film: exactly one exact underline rule required '+code)
        if len(soup.select('h1'))!=1 or len(soup.select('main article'))!=1:raise ValueError('film: standalone article shape mismatch '+code)
        _,keyed,_=apply_keyed_master(root,FAMILY,code)
        if str(one(soup,'main > article.film-news-article'))!=str(one(keyed,'main > article.film-news-article')):raise ValueError('film: article differs from keyed output '+code)
        if contract['shellSha256'][code]!=shell_digest(text,route):raise ValueError('film: independent final shell drift '+code)
        switcher=soup.select('nav.film-locale-switcher a[href][hreflang]')
        if len(switcher)!=12 or {a['hreflang']:a['href'] for a in switcher}!=routes:raise ValueError('film: crawlable 12-locale switcher required '+code)
    validate_discovery(root,registry,routes)
    return []
