"""Inject the same resolver/control in runtime and static generated pages.

This preparation is explicit: pending variants stay unavailable without JS too.
Reviewed manifest and UI copy must be supplied by the integration gate.
"""
from bs4 import BeautifulSoup
from html import escape
import re
from i18n.catalog import read_json

def inject_control(text, root, manifest, copy):
    soup=BeautifulSoup(text,'html.parser')
    lang=soup.html.get('lang','en') if soup.html else 'en'
    if lang not in copy:raise ValueError('Missing reviewed selector copy '+lang)
    # No-JS static choices must not retain guide/home substitutions.
    # Mutate only language nav blocks, never MAIN or ordinary editorial anchors.
    def static_nav(match):
        nav=BeautifulSoup(match[0],'html.parser').nav
        for a in nav.select('a[hreflang]'):
            code=a['hreflang']
            if code==lang:continue
            a.attrs.pop('href',None);a.attrs.pop('lang',None)
            a['aria-disabled']='true';a['tabindex']='-1'
            a.string=copy[lang]['names'].get(code,code)+' ('+copy[lang]['suffix']+')'
        helper=BeautifulSoup('<span class="sc-language-helper"></span>','html.parser').span
        helper.string=copy[lang]['helper'];nav.append(helper)
        return str(nav)
    text=re.sub(r'<nav\b[^>]*class=["\'](?:locale-nav|footer-locales)["\'][\s\S]*?</nav>',static_nav,text)
    text=text.replace('</head>','<link id="sc-language-css" rel="stylesheet" href="/same-page-switcher.css" />\n</head>')
    scripts='\n'.join('<script defer src="/'+name+'"></script>' for name in ['same-page-manifest.js','same-page-copy.js','same-page-resolver.js','same-page-switcher.js'])
    if 'src="/same-page-resolver.js"' in text:raise ValueError('Duplicate control injection')
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
