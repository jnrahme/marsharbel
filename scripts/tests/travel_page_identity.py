from pathlib import Path
import sys,unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from i18n.travel_page_identity import candidate_travel_groups
class TravelIdentity(unittest.TestCase):
 def test_exact_candidate_groups_not_promotions(self):
  root=Path(__file__).resolve().parents[2];groups=candidate_travel_groups(root)
  self.assertEqual(len(groups),14)
  self.assertEqual(set(groups['travel-travel']['candidateVariants']),{'en','ar','fr','es','pt','it','de','pl'})
  for name in ['qadisha-valley','qannoubine-monastery','qozhaya-monastery']:
   self.assertEqual(set(groups['travel-'+name]['candidateVariants']),{'en','ar','fr','es'})
  for name,g in groups.items():
   if name not in ['travel-travel','travel-qadisha-valley','travel-qannoubine-monastery','travel-qozhaya-monastery']:self.assertEqual(set(g['candidateVariants']),{'en'})
   self.assertTrue(g['status'].startswith('pending'))
  self.assertEqual(groups['travel-visit-annaya']['englishAliases'],['/en/visit-annaya'])
if __name__=='__main__':unittest.main()
