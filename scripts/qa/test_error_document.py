"""Custom 404 contract. Run with --base-url to verify a deployed server."""
import argparse
import pathlib
import urllib.error
import urllib.request

root = pathlib.Path(__file__).resolve().parents[2]
parser = argparse.ArgumentParser()
parser.add_argument('--base-url')
args = parser.parse_args()
assert 'ErrorDocument 404 /404.html' in (root / '.htaccess').read_text()
html = (root / '404.html').read_text()
assert 'noindex, nofollow, noarchive' in html
assert 'href="/404.css"' in html
assert 'href="/"' in html
assert '<script' not in html
assert '404.html' not in (root / 'sitemap.xml').read_text()
if args.base_url:
    for path in ('/missing-security-page-20261002', '/ar/missing/deep', '/missing.css'):
        try:
            urllib.request.urlopen(args.base_url.rstrip('/') + path)
            raise AssertionError('Expected 404, got success: ' + path)
        except urllib.error.HTTPError as response:
            assert response.code == 404, (path, response.code)
            assert b'Page not found' in response.read(), path
            for header, value in (
                ('X-Content-Type-Options', 'nosniff'),
                ('X-Frame-Options', 'DENY'),
                ('Referrer-Policy', 'strict-origin-when-cross-origin'),
                ('X-Robots-Tag', 'noindex, nofollow, noarchive'),
                ('Cache-Control', 'no-store, max-age=0'),
            ):
                assert response.headers.get(header) == value, (path, header)
            assert "frame-ancestors 'none'" in response.headers.get('Content-Security-Policy', '')
            assert response.headers.get('Permissions-Policy')
            assert "default-src 'self'" in response.headers.get('Content-Security-Policy', '')
            if args.base_url.startswith('https:'):
                assert response.headers.get('Strict-Transport-Security') == 'max-age=31536000'
            print('PASS', path, response.code, 'custom body + security/cache/index headers')
print('PASS custom error document contract')
