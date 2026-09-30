"""Pillar copy has counted locale ownership and schema/visible parity."""
import json,re,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
sys.path.insert(0,str(ROOT/'scripts/qa'))
from apply_seo_tags import faq_pairs
from check_i18n_policy import extract_html
class PillarTests(unittest.TestCase):
 def test_faq_matches_visible_copy(self):
  for name in('massabki-brothers','abouna-yaacoub'):
   html=(ROOT/(name+'.html')).read_text()
   blocks=[json.loads(x)for x in re.findall(r'<script type="application/ld\+json">\s*(.*?)\s*</script>',html,re.S)]
   faqs=[x for x in blocks if x.get('@type')=='FAQPage']
   self.assertEqual(len(faqs),1)
   self.assertEqual([(x['name'],x['acceptedAnswer']['text'])for x in faqs[0]['mainEntity']],faq_pairs(html))
 def test_new_pages_not_grandfathered(self):
  baseline=json.loads((ROOT/'locales/legacy-text-baseline.json').read_text())
  catalog=json.loads((ROOT/'locales/en/saint-pillars-copy.json').read_text())['values']
  for file in('massabki-brothers.html','abouna-yaacoub.html'):
   self.assertNotIn(file,baseline)
   self.assertEqual(dict(extract_html((ROOT/file).read_text())),catalog[file])
