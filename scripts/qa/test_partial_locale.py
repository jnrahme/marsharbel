"""Partial publication must never manufacture a locale home or topic fallback."""
import copy
import sys
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from i18n.catalog import read_json, validate_registry, home_url, page_url, published_home_locales

class PartialLocaleTests(unittest.TestCase):
    def setUp(self):
        self.registry = copy.deepcopy(read_json(ROOT / 'locales/registry.json'))
        self.registry['locales']['zz'] = {'nativeName': 'Test', 'direction': 'ltr', 'ogLocale': 'zz_ZZ', 'selectorAliases': [], 'slugs': {}, 'capabilities': {'home': False, 'topicGuides': [], 'mirrorTabs': [], 'runtime': True, 'selectorCopy': True}}
        self.registry['ogLocaleOrder'].append('zz')

    def test_partial_has_no_home_and_no_topic_fallback(self):
        validate_registry(self.registry)
        self.assertIsNone(home_url(self.registry, 'zz'))
        self.assertNotIn('zz', published_home_locales(self.registry))
        with self.assertRaisesRegex(ValueError, 'unpublished topic'):
            page_url(self.registry, 'zz', 'biography')

    def test_fake_home_rejected(self):
        self.registry['locales']['zz']['home'] = '/zz/'
        with self.assertRaisesRegex(ValueError, 'homepage capability'):
            validate_registry(self.registry)

    def test_unknown_capability_rejected(self):
        self.registry['locales']['zz']['capabilities']['fallback'] = True
        with self.assertRaisesRegex(ValueError, 'unknown capability'):
            validate_registry(self.registry)

    def test_topics_cannot_be_claimed_without_publication(self):
        self.registry['locales']['zz']['capabilities']['topicGuides'] = ['annaya']
        with self.assertRaisesRegex(ValueError, 'topic capability'):
            validate_registry(self.registry)

    def test_complete_travel_declaration_required(self):
        self.registry['locales']['zz']['capabilities']['mirrorTabs'] = ['travel']
        with self.assertRaisesRegex(ValueError, 'incomplete Travel'):
            validate_registry(self.registry)

    def test_runtime_required_for_published_tab(self):
        caps = self.registry['locales']['zz']['capabilities']
        caps['mirrorTabs'] = ['travel']
        for path in read_json(ROOT / 'locales/travel-routes.json')['destinations'] + ['/travel']:
            self.registry.setdefault('pageMirrors', {})['test' + path.replace('/', '-')] = {'english': path, 'routes': {'zz': '/zz' + path}, 'renderLocales': ['zz']}
        validate_registry(self.registry)
        caps['runtime'] = False
        with self.assertRaisesRegex(ValueError, 'requires runtime'):
            validate_registry(self.registry)

    def test_home_publication_needs_actual_build_output(self):
        outputs = {ROOT / ('index.html' if c == 'en' else c + '/index.html'): '' for c in self.registry['homePublicationLocales']}
        self.assertEqual(published_home_locales(self.registry, outputs, ROOT), self.registry['homePublicationLocales'])
        outputs.pop(ROOT / 'fr/index.html')
        with self.assertRaisesRegex(ValueError, 'missing from build output'):
            published_home_locales(self.registry, outputs, ROOT)

    def test_home_capability_without_membership_rejected(self):
        self.registry['locales']['zz']['capabilities']['home'] = True
        self.registry['locales']['zz']['home'] = '/zz/'
        with self.assertRaisesRegex(ValueError, 'homepage capability'):
            validate_registry(self.registry)

    def test_traditional_chinese_never_aliases_simplified(self):
        cfg=self.registry['locales'].pop('zz')
        cfg['ogLocale']='zh_CN';cfg['selectorAliases']=['zh-TW']
        self.registry['locales']['zh-Hans']=cfg
        self.registry['ogLocaleOrder']=[c for c in self.registry['ogLocaleOrder'] if c!='zz']
        if 'zh-Hans' not in self.registry['ogLocaleOrder']:self.registry['ogLocaleOrder'].append('zh-Hans')
        with self.assertRaisesRegex(ValueError, 'Traditional Chinese'):
            validate_registry(self.registry)

    def test_disclosure_cannot_hide_hostile_subtree(self):
        from i18n.mirror_structure import signature
        hostile='<header><a href="/" hreflang="en" aria-label="Home English"><span class="partial-home-language"><button>English</button></span></a></header><main></main>'
        with self.assertRaisesRegex(ValueError, 'text-only'):
            signature(hostile,'/zz/travel',('partial-home-disclosure',))

    def test_runtime_inventory_includes_partial_locale_without_home_or_proof(self):
        from i18n.same_page_injection import with_english_sources, _english_source_cache
        _english_source_cache.clear()
        seed = read_json(ROOT / 'locales/same-page-manifest.pending.json')
        result = with_english_sources(ROOT, seed)
        self.assertEqual(result['languages'], list(read_json(ROOT / 'locales/registry.json')['locales']))
        self.assertIn('zh-Hans', result['languages'])
        self.assertEqual(result['aliases']['zh-hans'], 'zh-Hans')
        self.assertNotIn('zh-Hans', result['publishedHomes'])
        self.assertEqual(result['pages'], seed['pages'])

    def test_existing_homes_unchanged(self):
        for c in self.registry['homePublicationLocales']:
            self.assertEqual(home_url(self.registry, c), '/' if c == 'en' else f'/{c}/')

if __name__ == '__main__':
    unittest.main()
