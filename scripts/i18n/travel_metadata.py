"""Reciprocal Travel discovery heads from actual registered route ownership.

Discovery is not same-page review evidence. English source composers and the
international writer call the same head-only transform to remain idempotent.
"""
import re
from urllib.parse import urlsplit
from i18n.catalog import read_json


def travel_clusters(root, registry):
    routes = read_json(root / 'locales/travel-routes.json')
    clusters = {route: {'en': route} for route in [routes['hub'], *routes['destinations']]}
    for group in ('authoredMirrors', 'exactMirrors', 'domMirrors', 'pageMirrors'):
        for cfg in registry.get(group, {}).values():
            english = cfg['english']
            if english not in clusters:
                continue
            for code, route in cfg.get('routes', {}).items():
                old = clusters[english].get(code)
                if old is not None and old != route:
                    raise ValueError('Ambiguous Travel discovery route: ' + english + ' ' + code)
                clusters[english][code] = route
    for english, cluster in clusters.items():
        cluster['x-default'] = english
    return clusters


# Explicit served paths from the approved authored-mirror producer boundary.
# Nineteen explicitly reviewed authored-mirror producer files.
PARTIAL_AUTHORED_FILES = frozenset({
    'ar/qadisha-valley.html','fr/vallee-qadisha.html','es/valle-qadisha.html',
    'ar/qannoubine-monastery.html','fr/monastere-qannoubine.html','es/monasterio-qannoubine.html',
    'ar/qozhaya-monastery.html','fr/monastere-qozhaya.html','es/monasterio-qozhaya.html',
    'travel.html','ar/travel.html','es/travel.html','fr/travel.html','it/travel.html','pl/travel.html','pt/travel.html',
    'qadisha-valley.html','qannoubine-monastery.html','qozhaya-monastery.html',
})


SOURCE_STUB_FILES = frozenset({
    # Eight EN source composers carry valid en/x-default discovery stubs.
    'our-lady-of-lebanon-harissa.html','bekaa-kafra.html',
    'bkerke-maronite-patriarchate.html','annaya-tour.html',
    'saint-charbel-trail.html','saint-charbel-places-lebanon.html',
    'cedars-of-god-lebanon.html','saint-charbel-hermitage.html',
})


def compose_travel_clusters(root, registry, texts, source_inputs=False):
    clusters = travel_clusters(root, registry)
    owners = {route: cluster for cluster in clusters.values() for route in cluster.values()}
    for file, text in list(texts.items()):
        if file.suffix != '.html':
            continue
        # Read attributes independently of serializer order. Never reserialize
        # body/head to discover identity; the existing transform remains head-only.
        from bs4 import BeautifulSoup
        heads = BeautifulSoup(text[:text.index('</head>')], 'html.parser')
        canonical = heads.select('link[rel="canonical"]')
        if len(canonical) > 1:raise ValueError('Ambiguous Travel canonical')
        cluster = owners.get(urlsplit(canonical[0].get('href','')).path) if canonical else None
        if cluster is None:
            continue
        texts[file] = splice_travel_alternates(text, cluster, registry['site'], file.relative_to(root).as_posix(), source_inputs=source_inputs)
    return texts


def splice_travel_alternates(text, cluster, site, file=None, source_inputs=False):
    """No serialization of an existing discovery block. Missing RU only."""
    from bs4 import BeautifulSoup
    from i18n.travel_scoped_delta import Tokens
    end=text.index('</head>');head=text[:end]
    soup=BeautifulSoup(head,'html.parser');links=soup.select('link[hreflang]')
    expected={code:site+route for code,route in cluster.items()}
    actual={}
    for link in links:
        code=link.get('hreflang')
        if code in actual or link.get('rel')!=['alternate'] or link.get('href')!=expected.get(code):
            raise ValueError('Malformed/duplicate/unexpected Travel alternate')
        actual[code]=link['href']
    if actual==expected:return text
    if not actual:raise ValueError('Travel bootstrap forbidden: missing discovery block')
    missing=set(expected)-set(actual)
    if missing!={'ru'}:
        source_stub=(source_inputs and file in SOURCE_STUB_FILES and set(actual)=={'en','x-default'})
        if not (file in PARTIAL_AUTHORED_FILES or source_stub) or not set(actual)<set(expected):
            raise ValueError('Existing Travel block has non-RU discovery gap')
        # Exact old composer serialization, bounded to the declared partial
        # producer files. Raw replacement remains HEAD-only and unchanged MAIN.
        head=re.sub(r'<link\b[^>]*\bhreflang=["\'][^>]*>\s*','',head)
        block='\n'.join('<link rel="alternate" hreflang="'+code+'" href="'+href+'" />' for code,href in expected.items())
        return head+block+'\n'+text[end:]
    # Reviewed compact candidates place RU immediately before x-default with
    # href/hreflang/rel order. Locate that raw tag, not a soup reserialization.
    tokens=[t for t in Tokens(head).tokens if t[0]=='tag' and t[3]=='link' and dict(t[4]).get('hreflang')=='x-default']
    if len(tokens)!=1:raise ValueError('Missing unique x-default insertion anchor')
    position=tokens[0][1]
    tag='<link href="'+expected['ru']+'" hreflang="ru" rel="alternate"/>'
    return text[:position]+tag+text[position:]
