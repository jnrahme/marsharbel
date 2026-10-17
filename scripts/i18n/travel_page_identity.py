"""Source-validated Travel candidate groups, not attested same-page promotions."""
import hashlib
from pathlib import Path
from bs4 import BeautifulSoup
from i18n.catalog import read_json

def candidate_travel_groups(root):
    registry=read_json(root/'locales/registry.json');data=read_json(root/'locales/travel-routes.json')
    routes=[data['hub'],*data['destinations']]
    authored={cfg['english']:cfg['routes'] for cfg in registry.get('authoredMirrors',{}).values()}
    groups={};paths=set()
    for master in routes:
        variants={'en':master,**authored.get(master,{})}
        aliases=[alias for alias,destination in data['englishAliases'].items() if destination==master]
        for lang,route in variants.items():
            file=root/(route.lstrip('/')+('index.html' if route.endswith('/') else '.html'))
            soup=BeautifulSoup(file.read_text(),'html.parser')
            canonical=soup.select_one('link[rel=canonical]')
            if not canonical or canonical['href']!='https://marsharbel.com'+route or soup.html.get('lang')!=lang:
                raise ValueError('Travel candidate canonical/language mismatch '+route)
            if route in paths:raise ValueError('Duplicate Travel identity '+route)
            paths.add(route)
        groups['travel-'+master.lstrip('/')]=dict(master=master,candidateVariants=variants,englishAliases=aliases,status='pending_exact_source_content_native_render_review')
    # Explicitly reject shorter Annaya guides from this full-master group.
    if groups['travel-visit-annaya']['candidateVariants']!={'en':'/visit-annaya'}:
        raise ValueError('Full Annaya master cannot use shorter guide substitutes')
    return groups
