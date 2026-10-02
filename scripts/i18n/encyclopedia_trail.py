"""Render reviewed visible trail copy with explicit English destination qualifier."""
from html import escape
from i18n.catalog import leaves

STANDARD={'before','encyclopedia','middle','history','after','historyAfter','englishQualifier'}

def render_trail(copy, history_url='/history', history_variant=False):
    expected=STANDARD if history_variant else STANDARD-{'historyAfter'}
    if set(copy) not in (expected, STANDARD):raise ValueError('Encyclopedia trail key mismatch')
    leaves(copy)
    if not history_url.startswith('/') or any(x in history_url for x in '<>"\'?#'):
        raise ValueError('Unsafe trail history route')
    title=copy['encyclopedia'];qualifier=copy['englishQualifier']
    # The translated anchor text and qualifier retain the page's language.
    # Only the destination is English; lang=en would mispronounce the label.
    anchor='<a href="/saint-charbel-encyclopedia" hreflang="en" aria-label="'+escape(title+' '+qualifier,quote=True)+'">'+escape(title)+'</a>'
    hint=' <span class="enc-language">'+escape(qualifier)+'</span>'
    suffix=escape(copy['historyAfter']) if history_variant else escape(copy['middle'])+'<a href="'+escape(history_url,quote=True)+'">'+escape(copy['history'])+'</a>'+escape(copy['after'])
    return '<p class="enc-trail">'+escape(copy['before'])+anchor+hint+suffix+'</p>'


def load_trail(root, lang):
    """Missing reviewed locale copy is a hard gate, never English fallback."""
    from i18n.catalog import read_json
    return read_json(root/f'locales/{lang}/encyclopedia-trail.json')


def apply_trail(soup, root, lang, history_url='/history'):
    """Replace only the exact reviewed English trail, after MAIN slot validation."""
    from bs4 import BeautifulSoup
    trails=soup.select('main p.enc-trail')
    if len(trails)!=1:raise ValueError('Expected exactly one Encyclopedia trail')
    anchors=trails[0].select('a')
    if len(anchors) not in (1,2):raise ValueError('Encyclopedia trail anchor count changed')
    if anchors[0].get('href') not in ('./saint-charbel-encyclopedia','/saint-charbel-encyclopedia'):
        raise ValueError('Encyclopedia destination changed')
    if len(anchors)==2 and anchors[1].get('href') not in ('./history','/history',history_url):
        raise ValueError('Encyclopedia history destination changed')
    rendered=BeautifulSoup(render_trail(load_trail(root,lang),history_url,len(anchors)==1),'html.parser').p
    trails[0].replace_with(rendered)
