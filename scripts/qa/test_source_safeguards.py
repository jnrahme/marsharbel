import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class SourceSafeguards(unittest.TestCase):
 def test_calendar_and_home_slots(self):
  key='saint-charbel-novena.when-to-pray-it.the-feast-falls-on-the-third-sunday-of-july-in-the-maronite'
  for lang in ('en','ar','de','fr','es','pt','it','pl','ru'):
   novena=json.loads((ROOT/f'locales/{lang}/saint-charbel-novena-master-copy.json').read_text())
   self.assertIn('28',novena[key],lang)
  en=json.loads((ROOT/'locales/en/home-copy.json').read_text())
  self.assertIn('not a Church declaration',en['home.monthly-prayer.why-the-22nd-this-monthly-devotion-recalls-nouhad-el'])
  self.assertIn('reports seeing',en['home.accessibility.an-artistic-rendition-of-saint-charbel-in-a-black'])
