"""Preserve the exact committed metadata/preload bytes at fragment boundaries."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class HeadFragmentTest(unittest.TestCase):
    def test_head_fragments_match_served_bytes(self):
        counts = {}
        for source in (ROOT / 'src/pages').rglob('*.html'):
            served = (ROOT / source.relative_to(ROOT / 'src/pages')).read_text()
            for marker in re.finditer(
                r'\{\{> (head-[a-z-]+)((?: "(?:[^"\\]|\\.)*")*)\}\}',
                source.read_text(),
            ):
                name, raw = marker.groups()
                args = [m[1] for m in re.finditer(r' "((?:[^"\\]|\\.)*)"', raw)]
                fragment = (ROOT / 'partials/fragments' / (name + '.html')).read_text().removesuffix('\n')
                rendered = re.sub(r'\{\{(\d+)\}\}', lambda m: args[int(m[1]) - 1], fragment)
                self.assertIn('  ' + rendered, served, f'{source.name}: {name} changed bytes')
                counts[name] = counts.get(name, 0) + 1
        self.assertEqual(counts, {
            'head-og-locales': 90,
            'head-social': 108,
            'head-font-preloads': 77,
            'head-font-preloads-legacy': 16,
        })


if __name__ == '__main__':
    unittest.main()
