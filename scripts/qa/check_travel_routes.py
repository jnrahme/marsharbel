#!/usr/bin/env python3
"""Verify Travel routes, aliases, links, fragment targets, discovery and locale parity."""
import json,sys
from pathlib import Path
from urllib.parse import urljoin,urlsplit,unquote
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from i18n.catalog import read_json

def check(root=ROOT):
 cfg=read_json(root/'locales/travel-routes.json');registry=read_json(root/'locales/registry.json');errors=[]
 def resolve(path):
  p=root/path.lstrip('/');return next((x for x in [p,p.with_suffix('.html'),p/'index.html'] if x.is_file()),None)
 sources={p:BeautifulSoup(p.read_text(),'html.parser') for p in root.rglob('*.html') if not any(x in p.relative_to(root).parts for x in ('node_modules','.git','src','templates','partials','tmp','test-results','playwright-report'))}
 sitemap={x.get_text() for x in BeautifulSoup((root/'sitemap.xml').read_text(),'xml').select('loc')}
 travel_routes=set([cfg['hub'],*cfg['destinations']])
 for name in ('travel','qadisha','qannoubine','qozhaya'):
  travel_routes.update(registry['authoredMirrors'][name]['routes'].values())
 inbound={}
 broken=[]
 for p,soup in sources.items():
  canonical=soup.select_one('link[rel=canonical]');base=canonical['href'] if canonical else registry['site']+'/'+str(p.relative_to(root))
  for a in soup.select('a[href]'):
   u=urlsplit(urljoin(base,a['href']))
   if u.netloc!='marsharbel.com' or u.scheme not in ('http','https'):continue
   if u.path in cfg['englishAliases']:u=urlsplit(registry['site']+cfg['englishAliases'][u.path]+('#'+u.fragment if u.fragment else ''))
   target=resolve(unquote(u.path))
   if not target:
    if not u.path.startswith('/api/'):broken.append((str(p.relative_to(root)),a['href']))
    continue
   inbound.setdefault(target,set()).add(p)
   if p in [resolve(r) for r in travel_routes] and u.fragment and u.fragment!='install-app':
    dest=sources.get(target)
    if dest and not dest.find(id=unquote(u.fragment)) and not dest.find(attrs={'name':unquote(u.fragment)}):errors.append(f'{p.name}: missing fragment {a["href"]}')
 for route in sorted(travel_routes):
  p=resolve(route)
  if not p:errors.append(f'Missing Travel route {route}');continue
  soup=sources[p]
  if registry['site']+route not in sitemap:errors.append(f'Not in sitemap: {route}')
  if not inbound.get(p):errors.append(f'Orphan Travel page: {route}')
  if len(soup.select('main'))!=1 or not soup.h1:errors.append(f'No real page body: {route}')
  for alt in soup.select('link[hreflang]'):
   dest=resolve(urlsplit(alt['href']).path)
   if not dest:errors.append(f'Broken alternate: {route} -> {alt["href"]}');continue
   if alt['hreflang']!='x-default' and not any(a['href']==registry['site']+route for a in sources[dest].select('link[hreflang]')):errors.append(f'Nonreciprocal alternate: {route} -> {alt["href"]}')
  if not soup.select('.travel-breadcrumb') and route!='/annaya-tour':errors.append(f'No breadcrumb: {route}')
  for resource in soup.select('main img[src],link[rel=stylesheet][href],script[src]'):
   value=resource.get('src',resource.get('href'));u=urlsplit(urljoin(registry['site']+route,value))
   if u.netloc=='marsharbel.com' and not resolve(u.path):errors.append(f'Missing resource: {route} -> {value}')
 errors.extend(f'Broken internal link: {p} -> {href}' for p,href in broken)
 report={'travelRoutes':len(travel_routes),'htmlPages':len(sources),'brokenInternalLinks':broken,'errors':errors}
 return report
if __name__=='__main__':
 report=check();print(json.dumps(report,indent=2));sys.exit(bool(report['errors']))
