"""Header-only destination disclosure; never reserialize a page's MAIN."""
from html import escape
import re
from i18n.encyclopedia_trail import load_trail

# Locales whose header nav links are routed to registered twins and marked
# English with the localized qualifier where no twin exists. The single gate
# for the marking mechanism: adding a locale's nav drop means adding its code
# here (plus its registry twins and reviewed qualifier catalog), never editing
# per-call-site literals. QA mirrors import this constant.
MARKING_LOCALES=frozenset({'ar','de','ru','fr'})


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

    Arabic launch, then de (locale-drop PR 2): twins are looked up per locale from
    the registry, so marking only touches links that have no registered twin.
    """
    if lang not in MARKING_LOCALES:return text
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


def mark_english_nav_hrefs(text, root, lang, label=True):
    """Header-only: mark links that still land on English with hreflang/aria + a visible qualifier.

    Runs after twin routing; anything left unrouted has no registered twin. Adds
    hreflang="en" and an aria-label carrying the localized English qualifier, plus
    (when label=True) a visible <span class="enc-language"> qualifier inside the
    anchor so the destination language is never a surprise. Idempotent per build.
    """
    if lang == 'en':
        return text
    m = re.search(r'<header\b[\s\S]*?</header>', text)
    if not m:
        return text
    from urllib.parse import urlsplit
    from html import escape, unescape
    qualifier = load_trail(root, lang)['englishQualifier']
    block = m[0]
    def replace(mm):
        pre, href, post, body = mm.group(1), mm.group(2), mm.group(3), mm.group(4)
        if 'hreflang=' in pre + post or 'enc-language' in body:
            return mm[0]
        if href.startswith(('#', 'mailto:', 'tel:')):
            return mm[0]
        parts = urlsplit(href)
        if parts.scheme or not parts.path.startswith('/'):
            return mm[0]
        if re.match(r'^/(ar|de|es|fr|hi|it|pl|pt|ru|th|zh-Hans)(/|$)', parts.path):
            return mm[0]
        visible = unescape(re.sub(r'<[^>]+>', '', body)).strip()
        clean = pre.strip()
        new_attrs = (' ' + clean if clean else '') + f' hreflang="en" aria-label="{escape(visible + " " + qualifier, quote=True)}"'
        new_body = body + (f' <span class="enc-language">{escape(qualifier)}</span>' if label else '')
        return '<a' + new_attrs + f' href="{href}"' + post + '>' + new_body + '</a>'
    block = re.sub(r'<a\b([^>]*?)href="([^"]*)"([^>]*)>([\s\S]*?)</a>', replace, block)
    return text[:m.start()] + block + text[m.end():]


def route_and_mark_nav(text, root, lang, label=True):
    """Locale launch: route header links to registered twins, mark the rest as English.

    Gated per locale as each locale's nav PR lands (ar, then de); every locale uses
    its own registry twin map and its own reviewed qualifier catalog."""
    if lang not in MARKING_LOCALES:
        return text
    if not re.search(r'<header\b', text):
        return text
    return mark_english_nav_hrefs(route_nav_hrefs(text, root, lang), root, lang, label)
