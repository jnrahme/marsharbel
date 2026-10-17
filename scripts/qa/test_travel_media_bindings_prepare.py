"""Synthetic append/refusal tests for Travel Media preparation."""
import copy
import importlib.util
from pathlib import Path
import unittest
ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('media_prepare', ROOT/'scripts/i18n/prepare_travel_media_bindings.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class TravelMediaPreparationTests(unittest.TestCase):
    def records(self):
        sels = ['header > div > nav > div:nth-of-type(6) > a',
                *['header > div > nav > div:nth-of-type(6) > div > a:nth-of-type(%d)' % i for i in (1,2,3)]]
        return [dict(key=k, source=v, kind='text', nodeIndex=0, selector=s)
                for k,v,s in zip(m.KEYS,m.VALUES['en'],sels)]

    def test_catalog_append_preserves_old_values_and_repeats(self):
        prior = {'other':'original'}
        expected = m.append_catalog(prior, prior, m.VALUES['ru'])
        self.assertEqual(expected['other'], 'original')
        self.assertEqual(m.append_catalog(prior,expected,m.VALUES['ru']),expected)
        self.assertEqual(prior, {'other':'original'})

    def test_partial_wrong_and_old_catalog_mutation_refused(self):
        prior = {'other':'original'}
        for current in [dict(prior, **{m.KEYS[0]:'Медиа'}), {'other':'changed'},
                        dict(prior, **dict(zip(m.KEYS,m.VALUES['en'])))]:
            with self.subTest(current=current), self.assertRaises(ValueError):
                m.append_catalog(prior,current,m.VALUES['ru'])
        with self.assertRaises(ValueError):
            m.append_catalog({m.KEYS[0]:'old'}, {}, m.VALUES['en'])

    def test_contract_append_preserves_metadata_messages_bindings(self):
        prior = {'masterSha256':'same','bindings':[{'key':'old'}],'messages':{'old':'text'}}
        expected = m.append_contract(prior,prior,self.records())
        self.assertEqual(expected['bindings'][:1],prior['bindings'])
        self.assertEqual(expected['masterSha256'],'same')
        self.assertEqual(m.append_contract(prior,expected,self.records()),expected)

    def test_contract_old_edits_and_duplicate_refused(self):
        prior = {'masterSha256':'same','bindings':[],'messages':{'old':'text'}}
        for field,value in [('masterSha256','new'),('messages',{'old':'changed'})]:
            bad=copy.deepcopy(prior);bad[field]=value
            with self.assertRaises(ValueError):m.append_contract(prior,bad,self.records())
        prior['messages'][m.KEYS[0]]='Media'
        with self.assertRaises(ValueError):m.append_contract(prior,prior,self.records())

    def raw(self):
        return '<header><div><nav>' + '<div></div>'*5 + '<div><a href="./music">Media<span></span></a><div><a href="./music">Music</a><a href="./videos">Video</a><a href="./gallery">Gallery</a></div></div></nav></div></header>'

    def test_exact_parent_three_children(self):
        m.validate_nodes(self.raw(),self.records())

    def test_duplicate_child_wrong_href_wrong_source_refused(self):
        for raw in [self.raw().replace('>Music<','>Media<'),
                    self.raw().replace('./videos','./other'),
                    self.raw().replace('>Gallery<','>Galerie<')]:
            with self.assertRaises(ValueError):m.validate_nodes(raw,self.records())


if __name__ == '__main__':
    unittest.main()
