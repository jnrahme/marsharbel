"""Inject the same resolver/control in runtime and static generated pages.

This preparation is explicit: pending variants stay unavailable without JS too.
Reviewed manifest and UI copy must be supplied by the integration gate.
"""
from bs4 import BeautifulSoup
from html import escape
import re,json,subprocess
from i18n.catalog import read_json

def inject_control(text, root, manifest, copy):
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
    text=re.sub(r'<nav\b[^>]*class=["\'](?:locale-nav|footer-locales)["\'][\s\S]*?</nav>',static_nav,text)
    text=text.replace('</head>','<link id="sc-language-css" rel="stylesheet" href="/same-page-switcher.css" />\n</head>')
    scripts='\n'.join('<script defer src="/'+name+'"></script>' for name in ['same-page-manifest.js','same-page-copy.js','same-page-resolver.js','same-page-switcher.js'])
    if text.count('</body>')!=1:raise ValueError('Missing unique body end')
    return text.replace('</body>',scripts+'\n</body>')


def control_outputs(root, texts, manifest, copy):
    import json
    out={}
    for path,text in texts.items():
        if path.suffix=='.html' and 'https://marsharbel.com/' in text:out[path]=inject_control(text,root,manifest,copy)
    out[root/'same-page-manifest.js']='window.SC_SAME_PAGE_MANIFEST = '+json.dumps(manifest,ensure_ascii=False,separators=(',',':'))+';\n'
    out[root/'same-page-copy.js']='window.SC_SAME_PAGE_COPY = '+json.dumps(copy,ensure_ascii=False,separators=(',',':'))+';\n'
    return out
