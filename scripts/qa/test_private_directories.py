"""Non-public directories must be denied with 410 Gone. Run with --base-url to verify a deployed server.

Covers source-pages/ and book-pages/ (phone photos of a printed modern devotional
book - standing copyright exposure, rights audit 2026-10-13) and story-production/
(799 orphaned render source-kit files, zero references from pages, sitemap, or
manifests). Files stay in git; the web server answers 410.
"""
import argparse
import pathlib
import re
import urllib.error
import urllib.request

root = pathlib.Path(__file__).resolve().parents[2]
parser = argparse.ArgumentParser()
parser.add_argument('--base-url')
args = parser.parse_args()

htaccess = (root / '.htaccess').read_text()
rule = re.search(r'^RewriteRule \^\(\?\:([^)]*)\)\(\?\:/\|\$\) - \[G,L\]$', htaccess, re.M)
assert rule, '.htaccess must carry a 410 [G,L] directory deny rule'
denied = set(rule.group(1).split('|'))
for directory in ('source-pages', 'book-pages', 'story-production'):
    assert directory in denied, f'{directory}/ missing from the 410 deny rule'
    assert (root / directory).is_dir(), f'{directory}/ must stay in git (deny, not delete)'

SAMPLES = {
    'source-pages': '/source-pages/WhatsApp%20Image%202026-03-02%20at%2012.33.45%20(1).jpeg',
    'book-pages': '/book-pages/page-01.jpeg',
    'story-production': '/story-production/anthony-padua/art-plan.md',
}
if args.base_url:
    for directory, path in SAMPLES.items():
        url = args.base_url.rstrip('/') + path
        try:
            urllib.request.urlopen(url)
            raise AssertionError('Expected 410, got success: ' + url)
        except urllib.error.HTTPError as response:
            assert response.code == 410, (url, response.code)
            print('PASS', url, response.code)
print('PASS private directory 410 deny contract')
