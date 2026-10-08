"""Preserve the exact committed metadata/preload bytes at fragment boundaries."""
import re
import json
from unittest.mock import patch
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def resolve_copy(source):
    """Match build-pages.mjs: resolve and HTML-escape copy before parsing includes."""
    catalogs = {}
    def replace(match):
        name, key = match.groups()
        if name not in catalogs:
            catalogs[name] = json.loads((ROOT / f'locales/en/{name}-copy.json').read_text())['copy']
        value = catalogs[name][key]  # Missing catalog/key is a failure, never a fallback.
        return str(value).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
    return re.sub(r'\{\{copy ([a-z0-9-]+) ([a-zA-Z0-9.-]+)\}\}', replace, source)


class HeadFragmentTest(unittest.TestCase):
    def test_copy_resolution_escapes_like_builder_and_rejects_missing_keys(self):
        with patch.object(Path, 'read_text', return_value=json.dumps({'copy': {'sample': 'A & <B> "C"'}})):
            self.assertEqual(resolve_copy('{{copy sample sample}}'), 'A &amp; &lt;B&gt; &quot;C&quot;')
            with self.assertRaises(KeyError):
                resolve_copy('{{copy sample missing}}')

    def test_changed_fragment_is_still_rejected(self):
        original = Path.read_text
        def changed(path, *args, **kwargs):
            text = original(path, *args, **kwargs)
            if path == ROOT / 'partials/fragments/head-social.html':
                return text.replace('og:description', 'og:description-tampered', 1)
            return text
        with patch.object(Path, 'read_text', changed):
            with self.assertRaisesRegex(AssertionError, 'head-social changed bytes'):
                self.test_head_fragments_match_served_bytes()

    def test_head_fragments_match_served_bytes(self):
        counts = {}
        for source in (ROOT / 'src/pages').rglob('*.html'):
            served = (ROOT / source.relative_to(ROOT / 'src/pages')).read_text()
            for marker in re.finditer(
                r'\{\{> (head-[a-z-]+)((?: "(?:[^"\\]|\\.)*")*)\}\}',
                resolve_copy(source.read_text()),
            ):
                name, raw = marker.groups()
                args = [m[1] for m in re.finditer(r' "((?:[^"\\]|\\.)*)"', raw)]
                fragment = (ROOT / 'partials/fragments' / (name + '.html')).read_text().removesuffix('\n')
                rendered = re.sub(r'\{\{(\d+)\}\}', lambda m: args[int(m[1]) - 1], fragment)
                self.assertIn('  ' + rendered, served, f'{source.name}: {name} changed bytes')
                counts[name] = counts.get(name, 0) + 1
        self.assertEqual(counts, {
            'head-og-locales': 92,
            'head-social': 113,
            'head-font-preloads': 82,
            'head-font-preloads-legacy': 16,
        })


if __name__ == '__main__':
    unittest.main()
