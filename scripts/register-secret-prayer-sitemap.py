#!/usr/bin/env python3
"""Register the four English prayer masters, preserving all other sitemap bytes."""
import argparse,json
from pathlib import Path
from sitemap_lastmod import last_changed
ROOT=Path(__file__).resolve().parents[1]
FAMILIES=('powerful-secret-prayers-master','mary-who-goes-ahead-prayer-master','lebanese-mountain-prayers-master','terco-da-batalha-master')
def outputs(root=ROOT):
    registry=json.loads((root/'locales/registry.json').read_text())
    text=(root/'sitemap.xml').read_text()
    for family in FAMILIES:
        mirror=registry['pageMirrors'][family]
        route=mirror['english'];url=registry['site']+route
        if '<loc>'+url+'</loc>' not in text:
            source=root/(route.lstrip('/')+'.html')
            if not source.is_file():raise ValueError('Missing prayer master '+route)
            date=last_changed(root,source)
            entry='  <url><loc>'+url+'</loc><lastmod>'+date+'</lastmod></url>\n'
            text=text.replace('</urlset>',entry+'</urlset>')
    return text
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');args=parser.parse_args()
    expected=outputs();path=ROOT/'sitemap.xml'
    if args.check and path.read_text()!=expected:raise SystemExit('Secret prayer sitemap registration is stale')
    if not args.check:path.write_text(expected)
    print('Four English prayer sitemap entries '+('checked' if args.check else 'registered'))