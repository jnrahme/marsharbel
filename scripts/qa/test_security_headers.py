"""Static production-header contract. Live checks remain required after deploy."""
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]


class SecurityHeaderTests(unittest.TestCase):
    def setUp(self):
        self.config = (ROOT / '.htaccess').read_text()

    def header(self, name):
        values = re.findall(r'Header always set ' + re.escape(name) + r' "([^"]+)"', self.config)
        self.assertTrue(values, name)
        return values[0]

    def test_baseline(self):
        self.assertEqual(self.header('X-Content-Type-Options'), 'nosniff')
        self.assertEqual(self.header('X-Frame-Options'), 'DENY')
        self.assertEqual(self.header('Referrer-Policy'), 'strict-origin-when-cross-origin')
        for feature in ('camera', 'microphone', 'geolocation', 'payment', 'usb'):
            self.assertIn(feature + '=()', self.header('Permissions-Policy'))

    def test_csp_safe_rollout(self):
        enforcing = self.header('Content-Security-Policy')
        for directive in ("frame-ancestors 'none'", "object-src 'none'", "base-uri 'self'", 'upgrade-insecure-requests'):
            self.assertIn(directive, enforcing)
        self.assertNotIn('script-src', enforcing)
        report = self.header('Content-Security-Policy-Report-Only')
        for host in ('alxccoizzksyitxvqhpv.supabase.co', 'www.googletagmanager.com', 'cdn.jsdelivr.net', 'js.hcaptcha.com', 'challenges.cloudflare.com', 'www.youtube-nocookie.com', 'translate.googleapis.com'):
            self.assertIn(host, report)
        self.assertNotIn("'unsafe-inline'", report.split('script-src ')[1].split(';')[0])
        self.assertNotIn('YOUR_PROJECT', report)

    def test_hsts_one_year_without_subdomain_commitment(self):
        self.assertEqual(self.header('Strict-Transport-Security'), 'max-age=31536000')
        self.assertIn('"expr=%{HTTPS} == \'on\'"', self.config)

    def test_private_pages(self):
        self.assertIn('(?:account|submit-testimony|testimony-review|feedback|feedback-review)', self.config)
        self.assertIn('Header always set Cache-Control "no-store, max-age=0"', self.config)
        self.assertIn('Header always set X-Robots-Tag "noindex, nofollow, noarchive"', self.config)

    def test_supabase_cdn_integrity(self):
        for filename in ('account.html', 'submit-testimony.html', 'testimonies.html', 'testimony-review.html'):
            text = (ROOT / filename).read_text()
            self.assertRegex(text, r'src="https://cdn\.jsdelivr\.net/npm/@supabase/supabase-js@2\.57\.4" integrity="sha384-AkNSQdptcXlJ0/NBZc4qGk86cDVXcCevwoWgEKIpHOEfbvlXGLlIkimQtONt8KNf" crossorigin="anonymous"')

    def test_no_inline_objects_or_external_base_in_pages(self):
        # These must stay absent while the lightweight policy is enforced.
        for path in ROOT.rglob('*.html'):
            if any(part in ('node_modules', '.git', 'test-results') for part in path.parts):
                continue
            text = path.read_text(errors='replace')
            self.assertIsNone(re.search(r'<(?:object|embed)\b', text, re.I), str(path))
            self.assertIsNone(re.search(r'<base\b[^>]*href=["\']https?://', text, re.I), str(path))


if __name__ == '__main__':
    unittest.main()
