import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from i18n.exact_master import render_exact_set
from i18n.catalog import ROOT,read_json
class ExactWiring(unittest.TestCase):
    def test_no_registered_output(self):
        self.assertEqual(render_exact_set(ROOT,read_json(ROOT/'locales/registry.json')), {})
    def test_english_route_guard(self):
        r=read_json(ROOT/'locales/registry.json')
        r['exactMirrors']={'test':{'english':'/history','routes':{'en':'/other'}}}
        with self.assertRaisesRegex(ValueError,'English route'):render_exact_set(ROOT,r)
    def test_unregistered_locale_guard(self):
        r=read_json(ROOT/'locales/registry.json')
        r['exactMirrors']={'test':{'english':'/history','routes':{'en':'/history','xx':'/xx/history'}}}
        with self.assertRaisesRegex(ValueError,'locale not registered'):render_exact_set(ROOT,r)
