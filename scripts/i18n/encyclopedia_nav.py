"""Header-only destination disclosure; never reserialize a page's MAIN."""
from html import escape
import re
from i18n.encyclopedia_trail import load_trail

def disclose_nav(text, root, lang):
    if lang=='en':return text
    catalog=load_trail(root,lang)
    header=re.search(r'<header\b[\s\S]*?</header>',text)
    if not header:raise ValueError('Missing Encyclopedia navigation header')
    pattern=r'<a\b([^>]*\bhref=["\'](?:\./|/)saint-charbel-encyclopedia["\'][^>]*)>([\s\S]*?)</a>'
    matches=list(re.finditer(pattern,header[0]))
    if len(matches)!=2:raise ValueError('Expected Legacy parent and Encyclopedia child')
    def replace(m):
        attrs,body=m.groups()
        if 'hreflang=' in attrs or 'enc-language' in body:raise ValueError('Duplicate destination disclosure')
        visible=re.sub(r'<span\b[\s\S]*?</span>','',body).strip()
        # Retain separately reviewed nav title, especially Polish nominative.
        from html import unescape
        label=unescape(visible)+' '+catalog['englishQualifier']
        attrs+=' hreflang="en" aria-label="'+escape(label,quote=True)+'"'
        body+=' <span class="enc-language">'+escape(catalog['englishQualifier'])+'</span>'
        return '<a'+attrs+'>'+body+'</a>'
    result=re.sub(pattern,replace,header[0])
    return text[:header.start()]+result+text[header.end():]
