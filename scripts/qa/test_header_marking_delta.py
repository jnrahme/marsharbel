"""Pinned pages may carry English-destination header marking and nothing else after review."""
import json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from i18n.header_marking_delta import strip_marking,strip_for_locale
from i18n.encyclopedia_nav import mark_english_nav_hrefs
import i18n.annaya_hero_evidence as ah
import i18n.travel_variant_evidence as tv

Q='(Englisch)'
PLAIN='<html><body><header><nav><a class="nav-parent" href="/saint-charbel-encyclopedia">Erbe<span aria-hidden="true" class="nav-chev"></span></a><a href="/testimonies">Briefe</a><a href="/de/">Start</a></nav></header><main><p>Text</p></main></body></html>'
class StripMarking(unittest.TestCase):
 def marked(self):return mark_english_nav_hrefs(PLAIN,ROOT,'de')
 def test_marked_differs_and_roundtrips(self):
  m=self.marked();self.assertNotEqual(m,PLAIN);self.assertIn('enc-language',m)
  self.assertEqual(strip_marking(m,Q),PLAIN)
 def test_unmarked_passes_through(self):self.assertEqual(strip_marking(PLAIN,Q),PLAIN)
 def test_wrong_qualifier_survives(self):
  m=self.marked().replace('(Englisch)','(English)');self.assertNotEqual(strip_marking(m,Q),PLAIN)
 def test_changed_label_is_rejected(self):
  m=self.marked().replace('aria-label="Briefe (Englisch)"','aria-label="Post (Englisch)"')
  with self.assertRaises(ValueError):strip_marking(m,Q)
 def test_extra_header_edit_survives(self):
  m=self.marked().replace('>Start<','>Beginn<');self.assertNotEqual(strip_marking(m,Q),PLAIN)
 def test_extra_attribute_survives(self):
  m=self.marked().replace('hreflang="en" aria-label="Briefe','data-x="1" hreflang="en" aria-label="Briefe');self.assertNotEqual(strip_marking(m,Q),PLAIN)
 def test_body_edit_survives(self):
  m=self.marked().replace('<p>Text</p>','<p>Other</p>');self.assertNotEqual(strip_marking(m,Q),PLAIN)
 def test_non_marking_locale_untouched(self):
  m=self.marked();self.assertEqual(strip_for_locale(ROOT,'fr',m),m)
class PinnedGates(unittest.TestCase):
 """Real pinned files through the real final gates: marking passes, any other delta fails."""
 def groups(self):return json.loads((ROOT/'locales/travel-equivalence.json').read_text())['groups']
 def run_gate(self,family,group,code,text):
  v=group['variants'][code]
  if group.get('evidenceSchema')=='annaya-hero-v1':return ah.validate_variant(ROOT,family,code,v,text,final=True)
  return tv.validate_variant(ROOT,family,code,v,text,final=True,schema=group['evidenceSchema'])
 def test_marking_passes_other_delta_fails_every_pinned_de_page(self):
  checked=0
  for family,group in self.groups().items():
   if group.get('evidenceSchema') not in ('scoped-variants-v1','annaya-hero-v1') or 'de' not in group['variants']:continue
   file=ROOT/group['variants']['de']['file'];disk=file.read_text()
   from i18n.encyclopedia_nav import PINNED_MARKING_LOCALES
   base=strip_for_locale(ROOT,'de',disk)  # candidate form (unmarked) whether or not disk is marked
   marked=mark_english_nav_hrefs(base,ROOT,'de')
   self.run_gate(family,group,'de',marked)
   header_tamper=marked.replace('</nav>',' </nav>',1)
   with self.assertRaises(ValueError):self.run_gate(family,group,'de',header_tamper)
   body_tamper=marked.replace('<main','<main data-x="1"',1)
   with self.assertRaises(ValueError):self.run_gate(family,group,'de',body_tamper)
   checked+=1
  self.assertGreaterEqual(checked,12)
if __name__=='__main__':unittest.main()
