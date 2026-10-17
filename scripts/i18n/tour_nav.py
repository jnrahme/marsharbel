"""Scoped reviewed tour-nav insertion without changing MAIN or other locales."""
import re
from html import escape
from i18n.catalog import read_json,leaves

def tour_nav(text, root, code):
    def header(match):
        markup=match[0]
        if not re.search(r'<nav\b[^>]*class=["\']links["\']',markup):return markup
        existing=re.compile(r'\s*<a\b[^>]*href=["\'](?:\.\.?/|/)?annaya-tour["\'][^>]*>[^<]*</a>')
        if code not in ('en','ar'):
            return existing.sub('',markup)
        copy=read_json(root/f'locales/{code}/nav-tour.json');leaves(copy)
        if set(copy)!={'header.annayaTour'}:raise ValueError('Tour nav key mismatch')
        visit=re.compile(r'<a\b[^>]*href=["\']((?:\.\.?/|/)?visit-annaya|/ar/annaya)["\'][^>]*>[^<]*</a>')
        matches=[m for m in visit.finditer(markup) if 'aria-haspopup' not in m[0]]
        if len(matches)!=1:raise ValueError('Tour nav requires one Annaya Travel item')
        markup=existing.sub('',markup)
        matches=[m for m in visit.finditer(markup) if 'aria-haspopup' not in m[0]]
        found=matches[0];prefix=found[1].removesuffix('visit-annaya') if code=='en' else '/'
        current=' class="active"' if re.search(r'<link rel="canonical" href="https://marsharbel.com/annaya-tour"',text) else ''
        aria=' aria-current="page"' if current else ''
        new=f'\n        <a{current} href="{prefix}annaya-tour"{aria}>{escape(copy["header.annayaTour"])}</a>'
        return markup[:found.end()]+new+markup[found.end():]
    return re.sub(r'<header\b[\s\S]*?</header>',header,text,count=1)
