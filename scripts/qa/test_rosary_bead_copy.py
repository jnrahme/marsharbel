"""Catalog/source contract for the one-page bead specimen."""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

class BeadCopyTest(unittest.TestCase):
    def test_source_keys_are_catalogued_and_generated(self):
        source = (ROOT/'src/pages/rosary-prayer-coach.html').read_text()
        catalog = json.loads((ROOT/'locales/en/rosary-bead-copy.json').read_text())['copy']
        keys = re.findall(r'{{copy rosary-bead ([a-zA-Z0-9.]+)}}', source)
        self.assertGreater(len(keys), 10)
        self.assertTrue(all(key in catalog for key in keys))
        served = (ROOT/'rosary-prayer-coach.html').read_text()
        self.assertNotIn('{{copy rosary-bead', served)
        for key in keys:
            self.assertIn(catalog[key], served)

    def test_prayer_order_and_no_renderer(self):
        catalog = json.loads((ROOT/'locales/en/rosary-bead-copy.json').read_text())['copy']
        self.assertIn('if you wish', catalog['beads.completeStatus'])
        self.assertIn('{n}', catalog['beads.hailMaryStatus'])
        source = (ROOT/'src/pages/rosary-prayer-coach.html').read_text()
        self.assertEqual(len(re.findall(r'data-bead="\d+"', source)), 11)
        self.assertNotIn('<model-viewer', source)
        self.assertNotIn('<canvas', source)

if __name__ == '__main__':
    unittest.main()
