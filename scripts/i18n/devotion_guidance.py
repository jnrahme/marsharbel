"""Render optional, sourced reading guidance without changing prayer text."""
from html import escape
from urllib.parse import urlsplit
from i18n.catalog import read_json, leaves


def load_guidance(root, code, topic):
    path = root / f'locales/{code}/oct22-guidance.json'
    if not path.exists():
        return None
    catalog = read_json(path)
    if set(catalog) != {'twentySecond', 'annaya', 'prayers'}:
        raise ValueError('Devotion guidance topic mismatch')
    for name, entry in catalog.items():
        if set(entry) != {'lead', 'sectionLinks'}:
            raise ValueError('Devotion guidance entry mismatch')
        if set(entry['lead']) != {'heading', 'steps', 'links'} or not entry['lead']['steps']:
            raise ValueError('Devotion guidance lead mismatch')
        leaves(entry['lead']['heading'])
        for step in entry['lead']['steps']:
            leaves(step)
        for links in [entry['lead']['links'], *entry['sectionLinks'].values()]:
            for link in links:
                if set(link) != {'href', 'label'}:
                    raise ValueError('Devotion guidance link mismatch')
                leaves(link)
                parts = urlsplit(link['href'])
                internal = link['href'].startswith(f'/{code}/') and not parts.netloc and '..' not in parts.path
                external = parts.scheme == 'https' and parts.netloc in {'saintcharbel.com', 'cnewa.org'}
                if not (internal or external):
                    raise ValueError('Unsafe devotion guidance destination')
    return catalog.get(topic)


def render_links(links):
    return '<p class="devotion-reading-links">' + ' · '.join(
        f'<a href="{escape(link["href"], quote=True)}">{escape(link["label"])}</a>' for link in links) + '</p>'


def render_lead(entry):
    if entry is None:
        return ''
    lead = entry['lead']
    steps = ''.join(f'<li>{escape(step)}</li>' for step in lead['steps'])
    return '<aside class="related devotion-guidance prayer-card card"><h2>' + escape(lead['heading']) + '</h2><ol>' + steps + '</ol>' + render_links(lead['links']) + '</aside>'
