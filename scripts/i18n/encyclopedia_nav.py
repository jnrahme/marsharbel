"""Header-only destination disclosure; never reserialize a page's MAIN."""
from html import escape
import re
from i18n.encyclopedia_trail import load_trail


def nav_twin_hrefs(registry, lang):
    """renderLocales-gated header hrefs for the locale's registered twins."""
    from i18n.page_mirror import twin_routes
    return twin_routes(registry, lang)


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
    # Arabic launch routing: links with a registered Arabic twin route to it without
    # the English-destination disclosure; links that stay English keep the disclosure.
    reroute={}
    if lang=='ar':
        twins=nav_twin_hrefs(registry,lang)
        for destination in ('/saint-charbel-encyclopedia','/history'):
            if destination in twins:reroute[destination]=twins[destination]
    for path in history_paths:
        if path==biography and '/history' in reroute:continue
        header_text=header_text.replace('href="'+path+'"','href="/history"')
    destinations=r'(?:\./|/)saint-charbel-encyclopedia|/history'
    if '/history' in reroute:destinations+='|'+re.escape(biography)
    pattern=r'<a\b([^>]*\bhref=["\'](?:'+destinations+r')["\'][^>]*)>([\s\S]*?)</a>'
    matches=list(re.finditer(pattern,header_text))
    if len(matches)!=3:raise ValueError('Expected Legacy parent, Encyclopedia child and Full History')
    def replace(m):
        attrs,body=m.groups()
        if 'hreflang=' in attrs or 'enc-language' in body:raise ValueError('Duplicate destination disclosure')
        dest=re.search(r'href=["\']([^"\']+)["\']',attrs).group(1).lstrip('.')
        key=dest if dest=='/' else dest.rstrip('/')
        if key==biography.rstrip('/') and '/history' in reroute:return m[0]
        if key in reroute:
            attrs=re.sub(r'href=["\'][^"\']*["\']','href="'+reroute[key]+'"',attrs,count=1)
            return '<a'+attrs+'>'+body+'</a>'
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


def route_nav_hrefs(text, root, lang):
    """Route plain header nav hrefs to the locale's registered twins.

    Arabic launch only: the newly registered twins are Arabic, and rerouting other
    locales' reviewed English links is out of scope for this change.
    """
    if lang!='ar':return text
    header=re.search(r'<header\b[\s\S]*?</header>',text)
    if not header:raise ValueError('Missing navigation header')
    from i18n.catalog import read_json
    registry=read_json(root/'locales/registry.json')
    twins=nav_twin_hrefs(registry,lang)
    block=header[0]
    from urllib.parse import urlsplit
    def replace(m):
        tag=m[0]
        if 'hreflang=' in tag:return tag
        href=m[1]
        if href.startswith(('#','mailto:','tel:')):return tag
        parts=urlsplit(href)
        if parts.scheme:return tag
        path=parts.path.lstrip('.')
        key=path if path=='/' else path.rstrip('/')
        if key not in twins:return tag
        new=twins[key]+('?'+parts.query if parts.query else '')+('#'+parts.fragment if parts.fragment else '')
        return tag.replace('href="'+href+'"','href="'+new+'"',1)
    block=re.sub(r'<a\b[^>]*\bhref="([^"]*)"[^>]*>',replace,block)
    return text[:header.start()]+block+text[header.end():]


def finish_nav(text, root, lang):
    from i18n.tour_nav import tour_nav
    return route_nav_hrefs(disclose_nav(tour_nav(text, root, lang), root, lang), root, lang)
