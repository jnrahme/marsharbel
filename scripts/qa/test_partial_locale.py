"""Partial publication must never manufacture a locale home or topic fallback."""
import copy
import sys
import unittest
from unittest.mock import patch
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

    def prayer_fixture(self):
        from i18n.catalog import PRAYER_FAMILIES
        self.registry['locales']['zz']['capabilities']['mirrorTabs'] = ['prayers']
        for name in PRAYER_FAMILIES:
            cfg = self.registry['pageMirrors'][name]
            cfg['routes']['zz'] = '/zz' + cfg['english']
            cfg['renderLocales'].append('zz')
        selectors = copy.deepcopy(read_json(ROOT / 'locales/same-page-copy.json'))
        selectors['zz'] = copy.deepcopy(selectors['de'])
        for values in selectors.values():
            values['names']['zz'] = 'Test'
        def fixture_read(path):
            if path == ROOT / 'locales/same-page-copy.json':
                return selectors
            if path.parent == ROOT / 'locales/zz':
                return read_json(ROOT / 'locales' / ('de' if path.name == 'runtime.json' else 'en') / path.name)
            return read_json(path)
        return fixture_read

    def test_prayer_allowlist_pins_and_exact_outputs_without_home(self):
        from i18n.catalog import validate_mirror_capabilities, validate_partial_outputs, PRAYER_FAMILIES
        reader = self.prayer_fixture()
        validate_registry(self.registry)
        with patch('i18n.catalog.read_json', side_effect=reader):
            validate_mirror_capabilities(ROOT, self.registry)
        outputs = {ROOT / (route.lstrip('/') + '.html'): ''
                   for cfg in self.registry['pageMirrors'].values()
                   for code, route in cfg['routes'].items()
                   if code in ('zz', 'zh-Hans') and code in cfg.get('renderLocales', [])}
        validate_partial_outputs(ROOT, self.registry, outputs)
        self.assertIsNone(home_url(self.registry, 'zz'))
        for path in (ROOT / 'zz/index.html', ROOT / 'zz/history.html'):
            with self.assertRaisesRegex(ValueError, 'output mismatch'):
                validate_partial_outputs(ROOT, self.registry, {**outputs, path: ''})
        with self.assertRaisesRegex(ValueError, 'output mismatch'):
            validate_partial_outputs(ROOT, self.registry, {})

    def test_unlisted_tab_and_prayer_master_rejected(self):
        from i18n.catalog import validate_mirror_capabilities
        reader = self.prayer_fixture()
        self.registry['locales']['zz']['capabilities']['mirrorTabs'].append('media')
        with self.assertRaisesRegex(ValueError, 'unknown mirror tab'):
            validate_registry(self.registry)
        self.registry['locales']['zz']['capabilities']['mirrorTabs'] = ['prayers']
        cfg = self.registry['pageMirrors']['history-master']
        cfg['routes']['zz'] = '/zz/history'
        cfg['renderLocales'].append('zz')
        with patch('i18n.catalog.read_json', side_effect=reader):
            with self.assertRaisesRegex(ValueError, 'lacks declared mirror'):
                validate_mirror_capabilities(ROOT, self.registry)

    def test_prayer_served_and_pinned_master_linkages_rejected(self):
        from i18n.catalog import validate_mirror_capabilities
        reader = self.prayer_fixture()
        cfg = self.registry['pageMirrors']['saint-charbel-prayers-master']
        cfg['master'] = 'history.html'
        with patch('i18n.catalog.read_json', side_effect=reader):
            with self.assertRaisesRegex(ValueError, 'served master linkage'):
                validate_mirror_capabilities(ROOT, self.registry)
        cfg['master'] = 'saint-charbel-prayers.html'
        def bad_pin(path):
            data = copy.deepcopy(reader(path))
            if path.name == 'saint-charbel-prayers-master-bindings.json':
                data['master'] = 'history.html'
            return data
        with patch('i18n.catalog.read_json', side_effect=bad_pin):
            with self.assertRaisesRegex(ValueError, 'family/master linkage'):
                validate_mirror_capabilities(ROOT, self.registry)

    def test_prayer_grant_cannot_enable_legacy_publication_sets(self):
        from i18n.catalog import validate_mirror_capabilities
        reader = self.prayer_fixture()
        for name in ('prayers', 'eucharistic'):
            self.registry['publicationSets'][name].append('zz')
            with patch('i18n.catalog.read_json', side_effect=reader):
                with self.assertRaisesRegex(ValueError, 'cannot gain prayer/eucharistic'):
                    validate_mirror_capabilities(ROOT, self.registry)
            self.registry['publicationSets'][name].remove('zz')

    def test_prayer_allowlist_exactly_three_names_and_routes(self):
        from i18n.catalog import PRAYER_FAMILIES
        self.assertEqual(PRAYER_FAMILIES, {
            'saint-charbel-prayers-master': ('/saint-charbel-prayers', 'templates/masters/saint-charbel-prayers.html'),
            'saint-charbel-novena-master': ('/saint-charbel-novena', 'templates/masters/saint-charbel-novena.html'),
            'twenty-second-master': ('/22nd-of-the-month', '22nd-of-the-month.html'),
        })

    def test_prayer_bypass_paths_rejected(self):
        from i18n.catalog import validate_mirror_capabilities
        cases = ('wrong-english', 'renamed-family', 'authored', 'exact', 'novena-stale', '22nd-stale', 'missing-template')
        for case in cases:
            with self.subTest(case=case):
                self.setUp()
                reader = self.prayer_fixture()
                name = 'saint-charbel-prayers-master'
                if case == 'wrong-english':
                    self.registry['pageMirrors'][name]['english'] = '/history'
                if case == 'renamed-family':
                    self.registry['pageMirrors']['unlisted-prayer-master'] = self.registry['pageMirrors'].pop(name)
                if case in ('authored', 'exact'):
                    self.registry[case + 'Mirrors']['unlisted-prayer-master'] = {
                        'english': '/saint-charbel-prayers', 'routes': {'zz': '/zz/other-prayer'}}
                def fixture_read(path):
                    data = copy.deepcopy(reader(path))
                    target = ('saint-charbel-novena-master' if case == 'novena-stale' else 'twenty-second-master')
                    if case.endswith('stale') and path.name == target + '-bindings.json':
                        data['masterSha256'] = '0' * 64
                    return data
                original_is_file = Path.is_file
                def file_exists(path):
                    if case == 'missing-template' and path == ROOT / 'templates/masters/saint-charbel-prayers.html':
                        return False
                    return original_is_file(path)
                with patch('i18n.catalog.read_json', side_effect=fixture_read), patch.object(Path, 'is_file', file_exists):
                    with self.assertRaises(ValueError):
                        validate_mirror_capabilities(ROOT, self.registry)

    def test_gradual_prayers_only_subset_valid(self):
        from i18n.catalog import validate_mirror_capabilities, PRAYER_FAMILIES
        reader = self.prayer_fixture()
        for name in ('saint-charbel-novena-master', 'twenty-second-master'):
            cfg = self.registry['pageMirrors'][name]
            cfg['routes'].pop('zz')
            cfg['renderLocales'].remove('zz')
        validate_registry(self.registry)
        with patch('i18n.catalog.read_json', side_effect=reader):
            validate_mirror_capabilities(ROOT, self.registry)
        self.assertEqual(self.registry['locales']['zz']['capabilities']['mirrorTabs'], ['prayers'])

    def test_history_only_partial_exact_allowlist_and_no_home(self):
        from i18n.catalog import validate_mirror_capabilities, validate_partial_outputs, HISTORY_FAMILY
        self.assertEqual(HISTORY_FAMILY, ('history-master', '/history', 'history.html'))
        reader = self.prayer_fixture()
        for name in ('saint-charbel-prayers-master', 'saint-charbel-novena-master', 'twenty-second-master'):
            cfg = self.registry['pageMirrors'][name]
            cfg['routes'].pop('zz')
            cfg['renderLocales'].remove('zz')
        self.registry['locales']['zz']['capabilities']['mirrorTabs'] = ['history']
        cfg = self.registry['pageMirrors']['history-master']
        cfg['routes']['zz'] = '/zz/history'
        cfg['renderLocales'].append('zz')
        validate_registry(self.registry)
        with patch('i18n.catalog.read_json', side_effect=reader):
            validate_mirror_capabilities(ROOT, self.registry)
        self.assertIsNone(home_url(self.registry, 'zz'))
        for case in ('wrong-english', 'wrong-name', 'wrong-master', 'authored', 'exact', 'unlisted-tab', 'prayer-without-grant'):
            with self.subTest(case=case):
                bad = copy.deepcopy(self.registry)
                if case == 'wrong-english': bad['pageMirrors']['history-master']['english'] = '/history-extra'
                if case == 'wrong-name': bad['pageMirrors']['history-extra'] = bad['pageMirrors'].pop('history-master')
                if case == 'wrong-master': bad['pageMirrors']['history-master']['master'] = 'music.html'
                if case in ('authored', 'exact'):
                    bad[case + 'Mirrors']['extra'] = {'english': '/history', 'routes': {'zz': '/zz/history-extra'}}
                if case == 'unlisted-tab': bad['locales']['zz']['capabilities']['mirrorTabs'] = ['history-extra']
                if case == 'prayer-without-grant':
                    bad['pageMirrors']['saint-charbel-prayers-master']['routes']['zz'] = '/zz/prayers'
                    bad['pageMirrors']['saint-charbel-prayers-master']['renderLocales'].append('zz')
                with patch('i18n.catalog.read_json', side_effect=reader):
                    with self.assertRaises(ValueError):
                        validate_registry(bad)
                        validate_mirror_capabilities(ROOT, bad)

    def film_fixture(self):
        import hashlib
        from tempfile import TemporaryDirectory
        from i18n.catalog import FILM_FAMILY
        temp=TemporaryDirectory(); self.addCleanup(temp.cleanup); root=Path(temp.name)
        name,english,master=FILM_FAMILY
        self.registry['locales']['zz']['capabilities']['mirrorTabs']=['film']
        self.registry['pageMirrors'][name]={'english':english,'master':master,'routes':{'zz':'/zz'+english},'renderLocales':['zz']}
        selectors=copy.deepcopy(read_json(ROOT/'locales/same-page-copy.json'));selectors['zz']=copy.deepcopy(selectors['de'])
        for value in selectors.values():value['names']['zz']='Test'
        source='<html><main>Film fixture</main></html>';(root/master).write_text(source)
        def reader(path):
            if path.name=='same-page-copy.json':return selectors
            if path.name==name+'-bindings.json':return {'master':master,'masterSha256':hashlib.sha256(source.encode()).hexdigest()}
            if path.name==name+'-copy.json':return {'film.body':'Fixture'}
            if path.parent.name=='zz' and path.name=='runtime.json':return read_json(ROOT/'locales/de/runtime.json')
            return read_json(ROOT/path.relative_to(root))
        for cfg in self.registry['pageMirrors'].values():
            other_master=cfg.get('master')
            if other_master and (ROOT/other_master).is_file() and not (root/other_master).exists():
                target=root/other_master;target.parent.mkdir(parents=True,exist_ok=True);target.symlink_to(ROOT/other_master)
        return root,reader

    def test_exact_film_partial_grant_without_home_or_topics(self):
        from i18n.catalog import validate_mirror_capabilities,validate_partial_outputs,mirror_tab,FILM_FAMILY
        root,reader=self.film_fixture();name,english,master=FILM_FAMILY
        self.assertEqual(mirror_tab('pageMirrors',name,self.registry['pageMirrors'][name]),'film')
        validate_registry(self.registry)
        with patch('i18n.catalog.read_json',side_effect=reader):validate_mirror_capabilities(root,self.registry)
        outputs={root/(route.lstrip('/')+'.html'):'' for cfg in self.registry['pageMirrors'].values() for code,route in cfg['routes'].items() if code in ('zz','zh-Hans') and code in cfg.get('renderLocales',[])}
        validate_partial_outputs(root,self.registry,outputs)
        for extra in ('zz/index.html','zz/history.html'):
            with self.assertRaisesRegex(ValueError,'output mismatch'):validate_partial_outputs(root,self.registry,{**outputs,root/extra:''})
        self.assertIsNone(home_url(self.registry,'zz'))
        tabs=self.registry['locales']['zh-Hans']['capabilities']['mirrorTabs']
        if 'film' not in tabs:tabs.append('film')
        self.assertEqual(tabs,['travel','film'])
        self.registry['pageMirrors'][name]['routes']['zh-Hans']='/zh-Hans'+english
        self.registry['pageMirrors'][name]['renderLocales'].append('zh-Hans')
        validate_registry(self.registry)
        self.assertIsNone(home_url(self.registry,'zh-Hans'))
        self.assertEqual(self.registry['locales']['zh-Hans']['capabilities']['topicGuides'],[])
        self.assertEqual(self.registry['locales']['zz']['capabilities']['topicGuides'],[])

    def test_film_exact_identity_group_and_missing_grant_refuse(self):
        from i18n.catalog import validate_mirror_capabilities,mirror_tab,FILM_FAMILY
        for case in ('name','english','master','authored','exact','missing-grant','media'):
            with self.subTest(case=case):
                self.setUp();root,reader=self.film_fixture();name=FILM_FAMILY[0]
                family=self.registry['pageMirrors'][name]
                if case=='name':name='film-other';self.registry['pageMirrors'][name]=self.registry['pageMirrors'].pop(FILM_FAMILY[0])
                if case=='english':family['english']='/film-other'
                if case=='master':family['master']='history.html'
                group='pageMirrors'
                if case in ('authored','exact'):
                    group=case+'Mirrors';self.registry[group][name]=self.registry['pageMirrors'].pop(name)
                if case in ('name','english','master','authored','exact'):self.assertIsNone(mirror_tab(group,name,family))
                if case=='missing-grant':self.registry['locales']['zz']['capabilities']['mirrorTabs']=[]
                if case=='media':
                    self.registry['locales']['zz']['capabilities']['mirrorTabs']=['media']
                    with self.assertRaisesRegex(ValueError,'unknown mirror tab'):validate_registry(self.registry)
                    continue
                with patch('i18n.catalog.read_json',side_effect=reader):
                    with self.assertRaisesRegex(ValueError,'lacks declared mirror capability'):validate_mirror_capabilities(root,self.registry)

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
