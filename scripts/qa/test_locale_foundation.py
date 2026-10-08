"""Fail-closed publication and locale identity regression gates."""
import importlib.util
from unittest.mock import patch
import copy
import json
from pathlib import Path
import sys
import unittest
from bs4 import BeautifulSoup
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from i18n.catalog import ROOT, read_json, validate_registry, topic_locales, load_catalog
from i18n.metadata import og_locales, published_locales, selector_aliases
from i18n.guarded_dom import translate_slots, translatable_nodes
from i18n.eucharistic_mirror import render_eucharistic

class FoundationTests(unittest.TestCase):
    def setUp(self):
        self.registry = copy.deepcopy(read_json(ROOT/'locales/registry.json'))

    def test_alias_identity_without_home_publication(self):
        self.assertEqual(selector_aliases(self.registry)['zh-cn'], 'zh-Hans')
        self.assertEqual(selector_aliases(self.registry)['zh-hans'], 'zh-Hans')
        self.assertNotIn('home', self.registry['locales']['zh-Hans'])
        self.assertNotIn('zh-Hans', topic_locales(self.registry, 'prayers'))
        self.assertNotIn('zh-Hans', published_locales(self.registry, 'eucharistic'))
        self.assertEqual(og_locales(self.registry)['zh-Hans'], 'zh_CN')

    def test_incomplete_locale_does_not_force_or_advertise_clusters(self):
        # Actual registered partial locale must not silently become a home.
        from i18n.catalog import published_home_locales, home_url
        self.assertNotIn('zh-Hans', published_home_locales(self.registry))
        self.assertIsNone(home_url(self.registry, 'zh-Hans'))
        self.assertFalse((ROOT/'zh-Hans/index.html').exists())
        sitemap=(ROOT/'sitemap.xml').read_text()
        self.assertNotIn('<loc>https://marsharbel.com/zh-Hans/</loc>', sitemap)
        self.assertNotIn('/zh-Hans/miracles/eucharistic', sitemap)

    def test_duplicate_alias_rejected(self):
        self.registry['locales']['de']['selectorAliases'] = ['EN']
        with self.assertRaisesRegex(ValueError, 'Duplicate selector alias'):
            validate_registry(self.registry)

    def test_metadata_required(self):
        del self.registry['locales']['de']['ogLocale']
        with self.assertRaisesRegex(ValueError, 'OG locale'):
            validate_registry(self.registry)

    def test_publication_sets_reject_unknown_and_duplicates(self):
        for subset in [['en','xx'], ['en','en'], ['ar']]:
            self.registry['publicationSets']['eucharistic'] = subset
            with self.assertRaisesRegex(ValueError, 'publication set'):
                validate_registry(self.registry)

    def test_dom_mirror_paths_cannot_escape_root(self):
        self.registry['domMirrors']['feast']['catalog'] = '../../private.json'
        with self.assertRaisesRegex(ValueError, 'unsafe DOM mirror catalog'):
            validate_registry(self.registry)

    def test_topics_cannot_silently_expand(self):
        del self.registry['topics']['biography']['locales']
        with self.assertRaisesRegex(ValueError, 'explicit publication'):
            validate_registry(self.registry)

    def test_partial_eucharistic_not_advertised(self):
        self.registry['publicationSets']['eucharistic'] = ['en', 'ar']
        pages = render_eucharistic(ROOT, self.registry)
        self.assertEqual(len(pages), 11)
        for text in pages.values():
            soup = BeautifulSoup(text, 'html.parser')
            self.assertEqual({a['hreflang'] for a in soup.select('link[hreflang]')}, {'en','ar','x-default'})

    def test_noncontent_and_explicit_hidden_nodes_preserved(self):
        soup = BeautifulSoup('<main><script>private()</script><style>.x{}</style><template>Template</template><noscript>Fallback</noscript><span hidden>Hidden</span><span inert>Inert</span><span aria-hidden="true">Decoration</span><p>Visible</p></main>', 'html.parser')
        self.assertEqual([str(n) for n in translatable_nodes(soup.main)], ['Visible'])
        translate_slots(soup.main, {'0': {'source': 'Visible', 'text': 'Sichtbar'}})
        for text in ['private()', '.x{}', 'Template', 'Fallback', 'Hidden', 'Inert', 'Decoration']:
            self.assertIn(text, str(soup))

    def test_guarded_dom_transaction_and_shape(self):
        soup = BeautifulSoup('<main><!-- keep:marker --><p> Hello <b>world</b> </p></main>', 'html.parser')
        slots = {'0': {'source':'Hello','text':'Hallo'}, '1': {'source':'world','text':'Welt'}}
        shape = [n.name for n in soup.select('main *')]
        translate_slots(soup.main, slots)
        self.assertEqual(shape, [n.name for n in soup.select('main *')])
        self.assertEqual(soup.main.p.contents[0], ' Hallo ')
        self.assertIn('<!-- keep:marker -->', str(soup))
        soup = BeautifulSoup('<main><p>Hello</p><p>world</p></main>', 'html.parser')
        original = str(soup)
        slots['1']['source'] = 'changed'
        with self.assertRaisesRegex(ValueError, 'master changed'):
            translate_slots(soup.main, slots)
        self.assertEqual(str(soup), original)
        slots['1'] = {'source':'world','text':'<b>Welt</b>'}
        with self.assertRaisesRegex(ValueError, 'Unsafe'):
            translate_slots(soup.main, slots)
        self.assertEqual(str(soup), original)

if __name__ == '__main__': unittest.main()
