"""Header-only destination disclosure; never reserialize a page's MAIN."""
from html import escape
import re
from i18n.encyclopedia_trail import load_trail

def disclose_nav(text, root, lang):
    if lang=='en':return text
    catalog=load_trail(root,lang)
    header=re.search(r'<header\b[\s\S]*?</header>',text)
    if not header:raise ValueError('Missing Encyclopedia navigation header')
    from i18n.catalog import read_json, page_url
    registry=read_json(root/'locales/registry.json')
    from i18n.catalog import locale_topics
    biography=page_url(registry,lang,'biography') if 'biography' in locale_topics(registry,lang) else '/history'
    history_paths=['./history','/history',biography]
    header_text=header[0]
    for path in history_paths:
        header_text=header_text.replace('href="'+path+'"','href="/history"')
    pattern=r'<a\b([^>]*\bhref=["\'](?:(?:\./|/)saint-charbel-encyclopedia|/history)["\'][^>]*)>([\s\S]*?)</a>'
    matches=list(re.finditer(pattern,header_text))
    if len(matches)!=3:raise ValueError('Expected Legacy parent, Encyclopedia child and Full History')
    def replace(m):
        attrs,body=m.groups()
        if 'hreflang=' in attrs or 'enc-language' in body:raise ValueError('Duplicate destination disclosure')
        visible=re.sub(r'<span\b[\s\S]*?</span>','',body).strip()
        # Retain separately reviewed nav title, especially Polish nominative.
        from html import unescape
        label=unescape(visible)+' '+catalog['englishQualifier']
        attrs+=' hreflang="en" aria-label="'+escape(label,quote=True)+'"'
        anchor='<a'+attrs+'>'+body+'</a>'
        if 'nav-parent' in attrs:return anchor
        return '<div class="enc-nav-item">'+anchor+' <span class="enc-language">'+escape(catalog['englishQualifier'])+'</span></div>'
    result=re.sub(pattern,replace,header_text)
    return text[:header.start()]+result+text[header.end():]


def finish_nav(text, root, lang):
    from i18n.tour_nav import tour_nav
    return disclose_nav(tour_nav(text, root, lang), root, lang)
