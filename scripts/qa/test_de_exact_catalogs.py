"""Prepared German catalogs remain tied to the complete English masters."""
import hashlib
import json
from pathlib import Path
import sys
import unittest
from bs4 import BeautifulSoup
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from i18n.catalog import ROOT, read_json, leaves
from i18n.guarded_dom import translate_slots
class GermanPreparedCatalogTests(unittest.TestCase):
    def test_full_master_and_dom_parity(self):
        for name in ['biography','novena','feast','miracles']:
            c=read_json(ROOT/f'locales/de/{name}-exact.json')
            source=(ROOT/c['master']).read_bytes()
            self.assertEqual(hashlib.sha256(source).hexdigest(), c['masterSha256'])
            for slot in c['slots'].values(): leaves(slot)
            soup=BeautifulSoup(source,'html.parser')
            before=[(n.name,n.attrs.copy()) for n in soup.select('main *')]
            translate_slots(soup.main,c['slots'],name)
            self.assertEqual(before,[(n.name,n.attrs.copy()) for n in soup.select('main *')])
            if b'<!-- i18n-navigation:start -->' in source:
                self.assertIn('<!-- i18n-navigation:start -->',str(soup))
            self.assertIn('Häufige Fragen',soup.main.get_text())
            if name in ('biography','novena'):
                self.assertIn('kein offizieller deutscher Klostertext',c['translationNote'])
            if name=='miracles':
                self.assertIn('förmlich anerkanntes Wunder',soup.main.get_text())
                self.assertIn('Klosterregister',soup.main.get_text())
            if name=='novena':
                days=soup.select('#nine-days h3')
                self.assertEqual([d.get_text() for d in days],[f'Tag {i}' for i in range(1,10)])
                self.assertIn('Kein Gebet garantiert automatisch Heilung',soup.main.get_text())
if __name__=='__main__':unittest.main()
