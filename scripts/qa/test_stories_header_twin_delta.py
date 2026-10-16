"""Real25-output amendment controls, retaining original full-file candidates."""
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from i18n.stories_header_twin_delta import inverse,set_outputs,PAIRS
from i18n.header_marking_delta import strip_for_locale
from i18n.travel_variant_evidence import blob,without_ru,validate_variant

class StoriesHeaderTwinTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.groups=json.loads((ROOT/'locales/travel-equivalence.json').read_text())['groups']
        cls.outputs={ROOT/(c+'/stories.html'):(ROOT/(c+'/stories.html')).read_text() for c in ('de','ru','hi')}
        set_outputs(cls.outputs)

    def candidates(self):
        for family,code in sorted(PAIRS):
            group=self.groups[family];v=group['variants'][code]
            candidate=(ROOT/v['file']).read_text() if group['evidenceSchema']=='annaya-hero-v1' else blob(ROOT,v['reviewEvidence']['preparedRevision'],v['file'])
            # Annaya's on-disk output has already been built with the new target;
            # its original candidate is immutable stage HEAD, not generated output.
            if group['evidenceSchema']=='annaya-hero-v1':candidate=blob(ROOT,'194b3cb965173162e0890833013760ed6b4f0573',v['file'])
            candidate=strip_for_locale(ROOT,code,candidate)
            current=(ROOT/v['file']).read_text()
            yield family,code,v,group,candidate,current

    def test_all25_real_outputs(self):
        n=0
        for family,code,v,group,candidate,current in self.candidates():
            restored=inverse(ROOT,family,code,strip_for_locale(ROOT,code,current),candidate)
            slug=family.removesuffix('-travel-master')
            self.assertEqual(without_ru(restored,slug),without_ru(candidate,slug),(family,code))
            n+=1
        self.assertEqual(n,25)

    def test_hostile_deltas_still_fail_full_file_equality(self):
        count=0
        for family,code,v,group,candidate,current in self.candidates():
            target='/'+code+'/stories'
            text=strip_for_locale(ROOT,code,current)
            changes=[text.replace('<main','<main data-hostile="1"',1),text.replace('href="'+target+'"','href="/ar/wrong"',1),text.replace('href="'+target+'"','href="'+target+'?x=1"',1),text.replace('href="'+target+'"','href="'+target+'#x"',1),text.replace('href="'+target+'"','data-extra="1" href="'+target+'"',1),text.replace('</header>','<a href="'+target+'">duplicate</a></header>',1),text.replace('</body>','hostile</body>',1),text.replace('</header>','<div>new</div></header>',1)]
            for changed in changes:
                with self.subTest(family=family,code=code,count=count):
                    try:restored=inverse(ROOT,family,code,changed,candidate)
                    except ValueError:pass
                    else:self.assertNotEqual(without_ru(restored,family.removesuffix('-travel-master')),without_ru(candidate,family.removesuffix('-travel-master')))
                count+=1
        self.assertEqual(count,200)

    def test_unrendered_destination_refused(self):
        family,code,v,g,candidate,current=next(self.candidates())
        set_outputs({})
        real=Path.is_file
        try:
            with patch.object(Path,'is_file',lambda p: False if str(p).endswith('/'+code+'/stories.html') else real(p)), self.assertRaisesRegex(ValueError,'not rendered'):
                inverse(ROOT,family,code,strip_for_locale(ROOT,code,current),candidate)
        finally:set_outputs(self.outputs)

if __name__=='__main__':unittest.main()
