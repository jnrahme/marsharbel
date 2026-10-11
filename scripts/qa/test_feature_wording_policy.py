"""Exact feature producer exemption never covers copied/unregistered pages."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('feature_wording_policy',ROOT/'scripts/qa/check_i18n_policy.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class FeatureWording(unittest.TestCase):
    def setUp(self):
        t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup);self.root=Path(t.name)
        (self.root/'ar').mkdir();(self.root/'scripts').mkdir()
        self.text='<html lang="ar"><main><h1>نسخة مطابقة</h1></main></html>'
        self.target=self.root/'ar/charbel-film-premiere.html';self.target.write_text(self.text)
        self.producer=self.root/'scripts/build_film_news_ar.py'
        self.producer.write_text('def output(root):\n    return root/"ar/charbel-film-premiere.html", '+repr(self.text)+'\n')
    def test_exact_producer_accepted(self):self.assertEqual(m.check_registered_feature(self.root),[])
    def test_changed_bytes_or_wrong_destination_refused(self):
        self.target.write_text(self.text.replace('نسخة','تغيير'))
        self.assertTrue(m.check_registered_feature(self.root))
        self.target.write_text(self.text);self.producer.write_text('def output(root):\n    return root/"ar/other.html", '+repr(self.text)+'\n')
        self.assertTrue(m.check_registered_feature(self.root))
    def test_missing_producer_refused(self):
        self.producer.unlink();self.assertTrue(m.check_registered_feature(self.root))
    def test_unregistered_copy_retains_hardcoded_text_failure(self):
        (self.root/'ar/unregistered.html').write_text(self.text)
        registry={'locales':{'en':{},'ar':{}},'defaultLocale':'en'}
        with patch.object(m,'read_json',return_value=registry),patch.object(m,'locale_topics',return_value=[]),patch.object(m,'published_locales',return_value=[]):
            snap=m.snapshot(self.root)
        self.assertNotIn('ar/charbel-film-premiere.html',snap)
        self.assertIn('نسخة مطابقة',snap['ar/unregistered.html'])
        # Empty baseline leaves this exact copied string as a rejected addition.
        from collections import Counter
        self.assertTrue(Counter(snap['ar/unregistered.html'])-Counter())
    def test_no_route_no_effect(self):
        self.target.unlink();self.assertEqual(m.check_registered_feature(self.root),[])
if __name__=='__main__':unittest.main()
