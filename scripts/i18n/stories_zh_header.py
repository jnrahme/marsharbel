"""Stories-only Chinese header routing; no global locale-policy change."""
import re,xml.etree.ElementTree as ET
from urllib.parse import urlsplit
from bs4 import BeautifulSoup, NavigableString
from i18n.catalog import read_json
from i18n.page_mirror import twin_routes
from i18n.encyclopedia_trail import load_trail

def finish_stories_zh_header(text, root, family, lang):
    if family!='stories-master' or lang!='zh-Hans':
        raise ValueError('Stories ZH header routing requires exact family and locale')
    m=re.search(r'<header\b[\s\S]*?</header>',text)
    if not m:raise ValueError('Missing Stories header')
    from i18n.stories_shelf_copy import reject_duplicate_attributes
    reject_duplicate_attributes(m[0])
    registry=read_json(root/'locales/registry.json')
    sitemap=ET.fromstring((root/'sitemap.xml').read_bytes())
    published={urlsplit(x.text).path.rstrip('/') or '/' for x in sitemap.iter() if x.tag.endswith('}loc') and x.text}
    twins=twin_routes(registry,lang)
    soup=BeautifulSoup(m[0],'html.parser')
    catalog_qualifier=load_trail(root,lang)['englishQualifier']
    for a in soup.select('a[href]'):
        href=a['href'];parts=urlsplit(href)
        if 'TR006-ISOLATED' in href:
            raise ValueError('Synthetic preview route cannot ship')
        if parts.netloc or parts.scheme or not parts.path.startswith('/') or parts.path.startswith('/zh-Hans/'):continue
        hints=a.select(':scope > span.enc-language, :scope > span.partial-home-language')
        if hints:
            if len(hints)!=1 or len(hints[0].contents)!=1 or not isinstance(hints[0].contents[0],NavigableString) or not str(hints[0].contents[0]).strip() or a.get('hreflang')!='en':
                raise ValueError('Malformed or duplicate Stories disclosure')
            visible=''.join(t for t in a.find_all(string=True) if t.find_parent('span',class_=['enc-language','partial-home-language']) is None).strip()
            incoming_qualifier=hints[0].get_text(strip=True)
            if incoming_qualifier != catalog_qualifier:
                raise ValueError('Stories disclosure differs from trusted catalog qualifier')
            if hints[0].get('class')==['partial-home-language'] and href!='/':
                raise ValueError('Old Home disclosure must target exact root')
            expected_label=a.get_text(' ',strip=True) if hints[0].get('class')==['partial-home-language'] else visible+' '+catalog_qualifier
            if hints[0].get('class') not in (['enc-language'],['partial-home-language']) or a.get('aria-label')!=expected_label:
                raise ValueError('Stories disclosure accessible text mismatch')
        elif a.has_attr('hreflang') or a.has_attr('aria-label'):
            raise ValueError('Incomplete Stories English disclosure')
        key=parts.path.rstrip('/') or '/';twin=twins.get(key)
        if twin and twin!='/' and twin.startswith('/zh-Hans/') and (twin.rstrip('/') or '/') in published:
            a['href']=twin+('?' +parts.query if parts.query else '')+('#'+parts.fragment if parts.fragment else '')
            for hint in a.select(':scope > span.enc-language, :scope > span.partial-home-language'):hint.decompose()
            a.attrs.pop('hreflang',None);a.attrs.pop('aria-label',None)
        elif a.select(':scope > span.partial-home-language'):
            hints=a.select(':scope > span.partial-home-language')
            if len(hints)!=1 or a.get('hreflang')!='en' or len(hints[0].contents)!=1:raise ValueError('Unexpected old Home disclosure')
            hints[0].decompose();a.attrs.pop('hreflang',None);a.attrs.pop('aria-label',None)
    # Apply the same exact disclosure contract without the generic regex helper,
    # which treats protocol-relative external links as local English routes.
    for a in soup.select('a[href]'):
        parts=urlsplit(a['href'])
        if parts.scheme or parts.netloc or not parts.path.startswith('/') or re.match(r'^/(ar|de|es|fr|hi|it|pl|pt|ru|th|zh-Hans)(/|$)',parts.path):continue
        if a.select(':scope > span.enc-language'):continue
        visible=a.get_text('',strip=False).strip()
        a['hreflang']='en';a['aria-label']=visible+' '+catalog_qualifier
        hint=soup.new_tag('span',attrs={'class':'enc-language'});hint.string=catalog_qualifier
        a.append(' ');a.append(hint)
    candidate=text[:m.start()]+str(soup.header)+text[m.end():]
    from i18n.mirror_structure import _strip_english_nav_disclosure
    _strip_english_nav_disclosure(BeautifulSoup(candidate,'html.parser'))
    return candidate
