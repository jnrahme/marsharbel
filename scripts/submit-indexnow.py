#!/usr/bin/env python3
"""Preview or submit published sitemap URLs; never submit local/unverified drafts."""
import argparse
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SITE = 'https://marsharbel.com'

def payload_for(urls, key):
    if not re.fullmatch(r'[a-zA-Z0-9-]{8,128}', key):
        raise ValueError('Invalid public IndexNow ownership key')
    if not urls or len(urls) > 10000:
        raise ValueError('Submit between 1 and 10000 URLs')
    for url in urls:
        parsed = urlsplit(url)
        if parsed.scheme != 'https' or parsed.netloc != 'marsharbel.com' or parsed.query or parsed.fragment:
            raise ValueError('Only canonical HTTPS marsharbel.com URLs may be submitted')
    return {'host':'marsharbel.com','key':key,'keyLocation':SITE+'/indexnow-key.txt','urlList':list(dict.fromkeys(urls))}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--submit', action='store_true', help='Notify IndexNow after deployment approval and live verification')
    parser.add_argument('--url', action='append', help='Published canonical URL; default: sitemap URLs')
    args = parser.parse_args()
    sitemap_urls = [node.text for node in ET.parse(ROOT/'sitemap.xml').iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
    urls = args.url or sitemap_urls
    if set(urls) - set(sitemap_urls):
        raise SystemExit('Only indexable sitemap URLs can be submitted.')
    key = (ROOT/'indexnow-key.txt').read_text().strip()
    payload = payload_for(urls, key)
    if not args.submit:
        print(json.dumps(payload, indent=2))
        print('Preview only. No network submission made.', file=sys.stderr)
        return
    # Prevent accidental notification before the approved batch is deployed.
    from qa.verify_deployment import frontend_files, verify_file
    with urlopen(SITE+'/indexnow-key.txt',timeout=20) as response:
        if response.read().decode().strip() != key:
            raise SystemExit('Live ownership key differs; deploy and verify the approved batch first.')
    for url in urls:
        with urlopen(url,timeout=20) as response:
            if response.status != 200 or response.url != url:
                raise SystemExit('URL is not live at its canonical address: '+url)
    for path in frontend_files(ROOT):
        error = verify_file(ROOT,path,SITE,'indexnow-preflight')
        if error: raise SystemExit(error)
    request = Request('https://api.indexnow.org/indexnow',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'})
    with urlopen(request,timeout=30) as response:
        print(f'IndexNow HTTP {response.status}; submission does not guarantee indexing.')

if __name__ == '__main__': main()
