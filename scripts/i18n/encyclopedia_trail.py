"""Render reviewed visible trail copy with explicit English destination qualifier."""
from html import escape
from i18n.catalog import leaves

STANDARD={'before','encyclopedia','middle','history','after','historyAfter','englishQualifier'}

def render_trail(copy, history_url='/history', history_variant=False):
    if set(copy)!=STANDARD:raise ValueError('Encyclopedia trail key mismatch')
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
