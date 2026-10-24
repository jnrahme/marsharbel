"""Keyed context fidelity and fail-closed projection controls."""
import json,sys,unittest
from pathlib import Path
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from build_nader_context import project,TARGETS
class NaderContext(unittest.TestCase):
 def test_catalogs_match_projected_copy(self):
  for lang,pages in TARGETS.items():
   copy=json.loads((ROOT/f'locales/{lang}/nader-context-copy.json').read_text())['copy']
   for rel,heading in pages.items():
    source=(ROOT/rel).read_text();soup=BeautifulSoup(source,'html.parser');nodes=soup.select('[data-nader-reported-context]')
    self.assertEqual(len(nodes),1,rel);self.assertEqual(nodes[0].get_text(),copy['text']);self.assertEqual(nodes[0].find_next_sibling('p').a['href'],copy['href']);self.assertEqual(nodes[0].find_next_sibling('p').a.get_text(),copy['link_text']);self.assertEqual(project(source,heading,copy),source)
 def test_german_exact_translation_matches_keyed_copy(self):
  copy=json.loads((ROOT/'locales/de/nader-context-copy.json').read_text())['copy'];soup=BeautifulSoup((ROOT/'de/miracles/index.html').read_text(),'html.parser');self.assertEqual(soup.select_one('[data-nader-reported-context]').get_text(),copy['text'])
 def test_english_scope_and_no_authorship_or_recognition(self):
  copy=json.loads((ROOT/'locales/en/nader-context-copy.json').read_text())['copy'];self.assertIn('not as the saint\'s surviving writings or Church-recognized miracles',copy['text']);self.assertIn('Raymond Nader attributes',copy['text']);self.assertEqual(copy['href'],'https://www.familyofsaintsharbel.org/experiences.html')
 def test_negative_duplicate_markers_rejected(self):
  source='<!-- nader-reported-context:begin -->a<!-- nader-reported-context:end -->'*2
  with self.assertRaisesRegex(ValueError,'Duplicate'):project(source,'Heading',{'text':'x','href':'https://example.invalid','link_text':'y'})
 def test_negative_missing_anchor_rejected_and_html_escaped(self):
  copy={'text':'<script>bad</script>','href':'https://example.invalid','link_text':'<img>'}
  with self.assertRaisesRegex(ValueError,'Missing'):project('<main></main>','Missing',copy)
  result=project('<h2>Heading</h2><p>existing</p>','Heading',copy);self.assertNotIn('<script>',result);self.assertIn('&lt;script&gt;',result)
if __name__=='__main__':unittest.main()
