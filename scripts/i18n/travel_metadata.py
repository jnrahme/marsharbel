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


def compose_travel_clusters(root, registry, texts):
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
        texts[file] = splice_travel_alternates(text, cluster, registry['site'])
    return texts


def splice_travel_alternates(text, cluster, site):
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
    if not actual:
        # Initial source composition has no block to preserve. Existing blocks
        # NEVER use this bootstrap branch.
        block='\n'.join('<link rel="alternate" hreflang="'+code+'" href="'+href+'" />' for code,href in expected.items())
        return head+block+'\n'+text[end:]
    if set(expected)-set(actual)!={'ru'} or 'ru' in actual:
        raise ValueError('Existing Travel block has non-RU discovery gap')
    # Reviewed compact candidates place RU immediately before x-default with
    # href/hreflang/rel order. Locate that raw tag, not a soup reserialization.
    tokens=[t for t in Tokens(head).tokens if t[0]=='tag' and t[3]=='link' and dict(t[4]).get('hreflang')=='x-default']
    if len(tokens)!=1:raise ValueError('Missing unique x-default insertion anchor')
    position=tokens[0][1]
    tag='<link href="'+expected['ru']+'" hreflang="ru" rel="alternate"/>'
    return text[:position]+tag+text[position:]
