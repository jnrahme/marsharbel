"""Pure Travel hub renderer with one template and complete keyed locale copy."""
from html import escape
import re
from i18n.catalog import read_json
from i18n.metadata import og_locales
from i18n.travel_components import directory, travel_frame
from i18n.encyclopedia_nav import finish_nav
SLOT = re.compile(r'\{\{([a-z][A-Za-z0-9]*(?:\.[a-z][A-Za-z0-9]*)+)\}\}')
def render_travel(root, registry):
    template = (root / 'templates/mirrors/travel.html').read_text()
    config = registry['authoredMirrors']['travel']
    alternates = '\n'.join(f'<link rel="alternate" hreflang="{lang}" href="{registry["site"]+route}" />' for lang,route in [('x-default',config['english']),*config['routes'].items()])
    result = {}
    for lang, route in config['routes'].items():
        travel = read_json(root/f'locales/{lang}/travel.json')
        if set(travel) != set(read_json(root/'locales/en/travel.json')):
            raise ValueError(f'Travel {lang}: catalog keys differ')
        header = read_json(root/f'locales/{lang}/mirrors/prayers.json')
        common = read_json(root/f'locales/{lang}/common.json')
        values = {**header, **{'travel.'+key:value for key,value in travel.items()},
                  'common.footer':common['site.footer'], 'common.skip':common['navigation.skip'],
                  'locale.code':lang, 'locale.direction':registry['locales'][lang]['direction'],
                  'locale.canonical':registry['site']+route, 'locale.alternates':alternates,
                  'locale.ogLocale':og_locales(registry)[lang],
                  'locale.destinationDirectory':directory(root,registry,lang),
                  'locale.ogLocaleAlternates':'\n'.join(f'<meta property="og:locale:alternate" content="{val}" />' for code,val in og_locales(registry).items() if code != lang)}
        def replace(m):
            key=m.group(1)
            if key not in values: raise ValueError(f'Travel {lang}: missing {key}')
            return values[key] if key in ('locale.alternates','locale.ogLocaleAlternates','locale.destinationDirectory') else escape(values[key],quote=True)
        text=SLOT.sub(replace,template)
        targets={cfg['english']:cfg['routes'][lang] for cfg in registry['authoredMirrors'].values() if lang in cfg['routes']}
        # Only published routes are localized; other destinations stay on existing English URLs.
        text=re.sub(r'(<a\b[^>]*\bhref=["\'])(/[^"\']*)(["\'])',lambda m:m[1]+targets.get(m[2],m[2])+m[3],text)
        if lang=='en':
            # English chrome is the shared navigation; the nav-sync checker owns it.
            nav=(root/'partials/primary-navigation.html').read_text().strip()
            nav=nav.replace('class="nav-parent" href="./travel"','class="active nav-parent" href="./travel"').replace('<a href="./travel">','<a class="active" href="./travel" aria-current="page">')
            text=re.sub(r'<nav class="links".*?</nav>',lambda m:nav,text,flags=re.S)
        result[root/(route.lstrip('/')+'.html')]=travel_frame(finish_nav(text,root,lang),root,lang,route,registry)
    return result
