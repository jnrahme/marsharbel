import importlib.util,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];spec=importlib.util.spec_from_file_location('repin',ROOT/'scripts/i18n/repin_media_nav_hotfix.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class RepinTests(unittest.TestCase):
 def test_exact_placeholder_class_and_refusals(self):
  old={'old':'value'};new={**old,**{'family.header.'+s:s.title()for s in ('media','music','video')}};self.assertTrue(m.placeholder_delta(old,new,'family'))
  for k,value in [('family.header.music','translated'),('old','changed')]:
   bad=new.copy();bad[k]=value
   with self.subTest(key=k):self.assertFalse(m.placeholder_delta(old,bad,'family'))
  bad=new.copy();bad.pop('old');self.assertFalse(m.placeholder_delta(old,bad,'family'))
  bad=new.copy();bad['extra']='key';self.assertFalse(m.placeholder_delta(old,bad,'family'));self.assertFalse(m.placeholder_delta(old,new,'wrong'))
 def test_non_header_changes_detected(self):
  a='<html><header>old</header><main>body</main></html>';b='<html><header>new</header><main>body</main></html>';self.assertEqual(m.outside_header(a),m.outside_header(b));self.assertNotEqual(m.outside_header(a),m.outside_header(b.replace('body','changed')))
if __name__=='__main__':unittest.main()
