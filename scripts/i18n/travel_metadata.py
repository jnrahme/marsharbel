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
        canonical = re.search(r'<link\b[^>]*rel=["\']canonical["\'][^>]*href=["\']([^"\']+)', text)
        cluster = owners.get(urlsplit(canonical[1]).path) if canonical else None
        if cluster is None:
            continue
        end = text.index('</head>')
        head = re.sub(r'<link\b[^>]*\bhreflang=["\'][^>]*>\s*', '', text[:end])
        links = '\n'.join('<link rel="alternate" hreflang="' + code + '" href="' + registry['site'] + route + '" />' for code, route in cluster.items())
        texts[file] = head + links + '\n' + text[end:]
    return texts
