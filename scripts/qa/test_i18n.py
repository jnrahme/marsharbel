import copy
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from string import Template

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'scripts'))
from i18n.catalog import load_catalog, locale_topics, read_json, page_url
from check_i18n_policy import check, extract_html

spec = importlib.util.spec_from_file_location('international_builder', ROOT/'scripts/build-international.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class CatalogTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        shutil.copytree(ROOT/'locales', self.root/'locales')

    def edit(self, file, update):
        path = self.root/'locales'/file
        data = read_json(path)
        update(data)
        path.write_text(json.dumps(data))

    def test_all_registered_languages_have_all_topics(self):
        registry, catalogs = load_catalog(self.root)
        self.assertEqual(set(catalogs), {'en','ar','fr','es','pt','it','de','pl'})
        for code,catalog in catalogs.items():
            self.assertEqual(set(catalog['pages']),set(locale_topics(registry,code)))
        self.assertTrue({'biography','prayers','novena','rosary','annaya'} <= set(catalogs['pl']['pages']))

    def test_missing_key_is_rejected(self):
        self.edit('pl/common.json', lambda d:d.pop('navigation.skip'))
        with self.assertRaisesRegex(ValueError,'missing keys'):
            load_catalog(self.root)

    def test_empty_translation_is_rejected(self):
        self.edit('de/common.json',lambda d:d.update({'navigation.home':' '}))
        with self.assertRaisesRegex(ValueError,'nonempty'):
            load_catalog(self.root)

    def test_duplicate_keys_are_rejected(self):
        path=self.root/'locales/es/common.json'
        path.write_text('{"label":"uno","label":"dos"}')
        with self.assertRaisesRegex(ValueError,'Duplicate'):
            read_json(path)

    def test_placeholder_mismatch_is_rejected(self):
        self.edit('it/common.json',lambda d:d.update({'navigation.home':'Casa {name}'}))
        with self.assertRaisesRegex(ValueError,'placeholders differ'):
            load_catalog(self.root)

    def test_missing_section_is_rejected(self):
        self.edit('pt/pages.json',lambda d:d['novena']['sections'].pop('day9'))
        with self.assertRaisesRegex(ValueError,'section IDs'):
            load_catalog(self.root)

    def test_unsafe_route_is_rejected(self):
        self.edit('registry.json',lambda d:d['locales']['es']['slugs'].update({'prayers':'../../account'}))
        with self.assertRaisesRegex(ValueError,'unsafe'):
            load_catalog(self.root)

    def test_duplicate_route_is_rejected(self):
        self.edit('registry.json',lambda d:d['locales']['es']['slugs'].update({'prayers':'biografia'}))
        with self.assertRaisesRegex(ValueError,'Duplicate route'):
            load_catalog(self.root)

    def test_executable_source_link_is_rejected(self):
        self.edit('registry.json',lambda d:d['sources'].update({'biography':'javascript:alert(1)'}))
        with self.assertRaisesRegex(ValueError,'safe HTTPS'):
            load_catalog(self.root)

    def test_unsafe_section_id_is_rejected(self):
        self.edit('registry.json',lambda d:d['topics']['biography']['sections'].append('bad"id'))
        with self.assertRaisesRegex(ValueError,'unsafe topic or section'):
            load_catalog(self.root)

    def test_unknown_source_reference_is_rejected(self):
        self.edit('registry.json',lambda d:d['topics']['prayers']['sources'].append('missing'))
        with self.assertRaisesRegex(ValueError,'unknown or missing source'):
            load_catalog(self.root)

    def test_html_in_catalog_is_rejected(self):
        self.edit('fr/common.json',lambda d:d.update({'navigation.home':'<script>alert(1)</script>'}))
        with self.assertRaisesRegex(ValueError,'HTML belongs'):
            load_catalog(self.root)

    def test_render_escapes_html_and_script_boundaries(self):
        registry,catalogs=load_catalog(self.root)
        catalog=copy.deepcopy(catalogs['en'])
        catalog['pages']['prayers']['title']='Prayer <script> & "text"'
        template=Template((ROOT/'templates/international/page.html').read_text())
        html=builder.render(registry,catalog,'en',template,'prayers')
        self.assertIn('Prayer &lt;script&gt; &amp; &quot;text&quot;',html)
        self.assertIn('\\u003cscript\\u003e',html)
        self.assertNotIn('Prayer <script>',html)

    def add_partial_topic(self, locales=('ar',)):
        def registry(d):
            d['topics']['sampleTopic']={'sections':['date'],'relatedEnglish':'/sample-topic','sources':['monastery'],'locales':list(locales)}
            for code in locales:
                d['locales'][code]['slugs']['sampleTopic']='sample-topic'
        self.edit('registry.json',registry)
        for code in locales:
            self.edit(f'{code}/pages.json',lambda d:d.update({'sampleTopic':{'title':'Feast','description':'Feast day guide','intro':'Intro text','sections':{'date':{'title':'Date','body':'Body text'}}}}))

    def test_partial_topic_is_published_only_in_its_languages(self):
        self.add_partial_topic()
        registry,catalogs=load_catalog(self.root)
        self.assertIn('sampleTopic',catalogs['ar']['pages'])
        self.assertNotIn('sampleTopic',catalogs['fr']['pages'])
        links=builder.alternate_links(registry,'sampleTopic')
        self.assertIn('hreflang="ar" href="https://marsharbel.com/ar/sample-topic"',links)
        self.assertIn('hreflang="en" href="https://marsharbel.com/sample-topic"',links)
        self.assertIn('hreflang="x-default" href="https://marsharbel.com/sample-topic"',links)
        self.assertNotIn('hreflang="fr"',links)
        navigation=builder.navigation(registry,'ar','sampleTopic')
        self.assertIn('href="/fr/"',navigation)
        self.assertIn('href="/sample-topic?lang=en"',navigation)
        template=Template((ROOT/'templates/international/page.html').read_text())
        self.assertNotIn('/ar/sample-topic',builder.render(registry,catalogs['fr'],'fr',template))
        self.assertIn('/ar/sample-topic',builder.render(registry,catalogs['ar'],'ar',template))

    def test_partial_topic_rejects_missing_page(self):
        self.add_partial_topic()
        self.edit('ar/pages.json',lambda d:d.pop('sampleTopic'))
        with self.assertRaisesRegex(ValueError,'missing or extra page topics'):
            load_catalog(self.root)

    def test_partial_topic_rejects_page_in_other_language(self):
        self.add_partial_topic()
        self.edit('fr/pages.json',lambda d:d.update({'sampleTopic':{'title':'F','description':'D','intro':'I','sections':{'date':{'title':'T','body':'B'}}}}))
        with self.assertRaisesRegex(ValueError,'missing or extra page topics'):
            load_catalog(self.root)

    def test_partial_topic_rejects_unknown_language(self):
        self.edit('registry.json',lambda d:d['topics']['prayers'].update({'locales':['xx']}))
        with self.assertRaisesRegex(ValueError,'locales must be'):
            load_catalog(self.root)

    def test_legacy_guard_detects_new_visible_text(self):
        old=extract_html('<button>Old button</button>')
        new=extract_html('<button>Old button</button><p>New hardcoded wording</p>')
        self.assertEqual(list(new-old),['New hardcoded wording'])

    def test_policy_rejects_hardcoded_new_page(self):
        (self.root/'new-page.html').write_text('<button>New hardcoded button</button>')
        errors=check(self.root)
        self.assertTrue(any('new-page.html: new hardcoded wording' in error for error in errors), errors)

    def test_policy_rejects_literal_template_label(self):
        template=self.root/'templates/international/page.html'
        template.parent.mkdir(parents=True)
        template.write_text('<nav aria-label="Hardcoded language menu">$navigation</nav>')
        errors=check(self.root)
        self.assertTrue(any('literal display text' in error for error in errors), errors)

    def test_no_generated_file_is_stale(self):
        for path,expected in builder.outputs(ROOT).items():
            self.assertEqual(path.read_text(),expected,str(path.relative_to(ROOT)))


if __name__=='__main__':unittest.main()
