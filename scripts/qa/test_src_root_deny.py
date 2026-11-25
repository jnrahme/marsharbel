"""Source tree (src/) and root build/agent files must be denied with 403. Run with --base-url to verify a deployed server.

Live finding 2026-10-14: /src/pages/news answered 200 with the raw template, and
package.json, package-lock.json, README.md and AGENTS.md were public. Files stay in git;
the server answers 403. Public routes (/news, /) must keep answering 200.
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
dir_rule = re.search(r'^RewriteRule (\^\(\?:[^ ]*\)\(\?:/\|\$\)) - \[F,L\]$', htaccess, re.M)
assert dir_rule, '.htaccess must carry the 403 [F,L] directory deny rule'
dir_re = re.compile(dir_rule.group(1))
file_rule = re.search(r'^RewriteRule (\^\(\?:package[^ ]*\)\$) - \[F,L\]$', htaccess, re.M)
assert file_rule, '.htaccess must carry the 403 [F,L] root-file deny rule'
file_re = re.compile(file_rule.group(1))

DENIED = ['src', 'src/', 'src/pages/news', 'src/pages/', 'src/partials/head.html',
          'package.json', 'package-lock.json', 'README.md', 'AGENTS.md']
ALLOWED = ['', 'news', 'ar/', 'source-code-of-faith', 'srcset-guide', 'package-deal', 'readme-prayer']
for path in DENIED:
    assert dir_re.match(path) or file_re.match(path), f'{path!r} must be denied'
for path in ALLOWED:
    assert not dir_re.match(path) and not file_re.match(path), f'{path!r} must NOT be denied'
assert (root / 'src' / 'pages').is_dir(), 'src/ must stay in git (deny, not delete)'

if args.base_url:
    base = args.base_url.rstrip('/')
    for path in ('/src/pages/news', '/src/pages/', '/package.json', '/package-lock.json', '/README.md', '/AGENTS.md'):
        try:
            urllib.request.urlopen(base + path)
            raise AssertionError('Expected 403, got success: ' + base + path)
        except urllib.error.HTTPError as response:
            assert response.code == 403, (path, response.code)
            print('PASS', path, response.code)
    for path in ('/', '/news'):
        assert urllib.request.urlopen(base + path).status == 200, path
        print('PASS', path, 200)
print('PASS src and root-file 403 deny contract')
