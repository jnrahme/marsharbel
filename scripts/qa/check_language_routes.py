#!/usr/bin/env python3
"""Check language routes against Apache/LiteSpeed (not the simpler Node preview)."""
import sys
import json
from pathlib import Path
from urllib.request import build_opener, HTTPRedirectHandler
from urllib.error import HTTPError
from urllib.parse import urlsplit

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args):
        return None

if __name__ == '__main__':
    base = sys.argv[1].rstrip('/') if len(sys.argv) > 1 else 'http://127.0.0.1:4192'
    opener = build_opener(NoRedirect)
    registry = json.loads((Path(__file__).resolve().parents[2]/'locales/registry.json').read_text())
    cases = [('/en',301,'/'),('/en/',301,'/')]
    for code, config in registry['locales'].items():
        if code != registry['defaultLocale']:
            cases.extend([(f'/{code}',200,None),(f'/{code}/',301,f'/{code}'),(f'/{code}.html',301,f'/{code}')])
        for slug in config['slugs'].values():
            route=f'/{code}/{slug}'
            cases.extend([(route,200,None),(route+'/',301,route),(route+'.html',301,route)])
    for path, status, target in cases:
        try:
            response = opener.open(base+path,timeout=15)
        except HTTPError as error:
            response = error
        assert response.code == status, (path, response.code, status)
        if target:
            assert urlsplit(response.headers['Location']).path == target, (path,response.headers)
        print(path, response.code)
    print(f'Language route checks passed: {len(cases)}')
