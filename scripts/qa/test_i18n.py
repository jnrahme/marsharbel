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

    def test_qadisha_correction_tracks_visible_copy_and_faq_schema(self):
        from i18n.qadisha_copy import validate as validate_qadisha
        page = validate_qadisha(ROOT)
        self.assertIn('Annaya monastery, not in the Qadisha Valley', page)
        self.assertNotIn('hermitage above Bsharri', page)
        self.assertNotIn('monastery of Annaya on the ridge above', page)

    def test_qadisha_mirror_parity_and_unesco_distinction(self):
        from html.parser import HTMLParser
        from i18n.qadisha_mirror import render_qadisha
        class Shape(HTMLParser):
            def __init__(self, source):
                super().__init__(); self.sections = []; self.images = []; self.headings = []
                self.feed(source)
            def handle_starttag(self, tag, attrs):
                attrs = dict(attrs)
                if tag == 'section': self.sections.append(attrs.get('class'))
                if tag == 'img': self.images.append(attrs.get('src'))
                if tag in ('h1', 'h2', 'h3'): self.headings.append(tag)
        pages = render_qadisha(ROOT)
        en, ar = (pages[ROOT / path] for path in ('qadisha-valley.html', 'ar/qadisha-valley.html'))
        self.assertEqual(Shape(en).sections, Shape(ar).sections)
        self.assertEqual(Shape(en).images, Shape(ar).images)
        self.assertEqual(Shape(en).headings, Shape(ar).headings)
        self.assertIn('not a third property in the UNESCO inscription', en)
        self.assertNotIn('three World Heritage neighbors', en)
        self.assertIn('ليس موقعًا ثالثًا', ar)
        self.assertIn('hreflang="ar" href="https://marsharbel.com/ar/qadisha-valley"', en)
        self.assertIn('href="/ar/biography"', ar)
        self.assertIn('href="/ar/annaya"', ar)
        self.assertNotIn('href="/ar/saint-charbel-trail"', ar)
        self.assertEqual(pages[ROOT / 'qadisha-valley.html'], (ROOT / 'qadisha-valley.html').read_text())
        fr = pages[ROOT / 'fr/vallee-qadisha.html']
        self.assertEqual(Shape(fr).sections, Shape(en).sections)
        self.assertEqual(Shape(fr).images, Shape(en).images)
        self.assertEqual(Shape(fr).headings, Shape(en).headings)
        self.assertIn('lang="fr" dir="ltr"', fr)
        self.assertIn('hreflang="fr" href="https://marsharbel.com/fr/vallee-qadisha"', fr)
        self.assertIn('ne constitue pas un troisième bien inscrit', fr)
        self.assertIn('href="/fr/biographie"', fr)
        self.assertIn('href="/fr/annaya"', fr)
        self.assertIn('href="/fr/vallee-qadisha"', fr)
        self.assertNotIn('href="/fr/saint-charbel-trail"', fr)
        self.assertIn('"@type": "TouristAttraction"', fr)
        self.assertEqual(fr, (ROOT / 'fr/vallee-qadisha.html').read_text())

    def test_qadisha_mirror_rejects_missing_keys_and_escapes_text(self):
        from i18n.qadisha_mirror import render_qadisha
        import tempfile
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(ROOT / 'locales', root / 'locales')
            (root / 'templates/mirrors').mkdir(parents=True)
            shutil.copyfile(ROOT / 'templates/mirrors/qadisha.html', root / 'templates/mirrors/qadisha.html')
            ar = root / 'locales/ar/mirrors/qadisha.json'
            data = read_json(ar)
            data['meta.title'] = 'عنوان خطير &'
            ar.write_text(json.dumps(data, ensure_ascii=False))
            text = render_qadisha(root)[root / 'ar/qadisha-valley.html']
            self.assertIn('عنوان خطير &amp;', text)
            data['meta.title'] = 'عنوان <script>'
            ar.write_text(json.dumps(data, ensure_ascii=False))
            with self.assertRaisesRegex(ValueError, 'HTML belongs'):
                render_qadisha(root)
            data['meta.title'] = 'عنوان'
            ar.write_text(json.dumps(data, ensure_ascii=False))
            del data['faq.question6']
            ar.write_text(json.dumps(data, ensure_ascii=False))
            with self.assertRaisesRegex(ValueError, 'catalog mismatch'):
                render_qadisha(root)

    def test_letters_catalog_does_not_hide_new_copy(self):
        catalog=read_json(ROOT/'locales/en/letters-display.json')['values']
        self.assertEqual(catalog['index.html']['Write a Letter to Saint Charbel'],1)
        self.assertEqual(catalog['home-letter.js']['This browser could not carry your letter to the next page. Keep a copy before continuing.'],1)
        self.assertEqual(catalog['submit-testimony.html']['Send letter for review'],1)
        self.assertNotIn('testimony-admin.js',catalog)

    def test_all_registered_languages_have_all_topics(self):
        registry, catalogs = load_catalog(self.root)
        self.assertEqual(set(catalogs), {'en','ar','fr','es','pt','it','de','pl'})
        for code,catalog in catalogs.items():
            self.assertEqual(set(catalog['pages']),set(locale_topics(registry,code)))
        self.assertTrue({'biography','prayers','novena','rosary','annaya'} <= set(catalogs['pl']['pages']))

    def test_directory_english_related_page_is_generated_in_index(self):
        registry, _ = load_catalog(self.root)
        self.assertEqual(registry['topics']['miracles']['relatedEnglish'], '/miracles/')
        self.assertEqual(builder.alternate_links(registry, 'miracles').count('https://marsharbel.com/miracles/'), 2)
        # The real project's output maps the directory route to index.html,
        # never to a hidden ".html" file inside the directory.
        self.assertIn(ROOT/'miracles/index.html', builder.outputs())
        self.assertNotIn(ROOT/'miracles/.html', builder.outputs())

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

    def test_nested_locale_route_and_directory_hub(self):
        registry, catalogs = load_catalog(ROOT)
        self.assertEqual(page_url(registry, 'ar', 'miracles'), '/ar/miracles/')
        self.assertEqual(page_url(registry, 'ar', 'nohadStory'), '/ar/miracles/nohad-el-shami')
        generated = builder.outputs(ROOT)
        self.assertIn(ROOT/'ar/miracles/index.html', generated)
        self.assertIn(ROOT/'ar/miracles/.htaccess', generated)
        self.assertIn('DirectoryIndex index.html', generated[ROOT/'ar/miracles/.htaccess'])
        self.assertIn(ROOT/'ar/miracles/nohad-el-shami.html', generated)
        self.assertNotIn(ROOT/'ar/miracles.html', generated)
        self.assertIn('https://marsharbel.com/ar/miracles/', builder.alternate_links(registry, 'miracles'))
        self.edit('registry.json',lambda d:d['locales']['ar']['slugs'].update({'nohadStory':'miracles/../private'}))
        with self.assertRaisesRegex(ValueError, 'unsafe'):
            load_catalog(self.root)

    def test_miracle_story_related_links_start_with_hub(self):
        registry, catalogs = load_catalog(ROOT)
        template = Template((ROOT/'templates/international/page.html').read_text())
        html = builder.render(registry, catalogs['ar'], 'ar', template, 'raymondStory')
        related = html.split('<aside class="related">', 1)[1]
        self.assertIn('<li><a href="/ar/miracles/">', related)
        self.assertLess(related.index('href="/ar/miracles/"'),
                        related.index('href="/ar/biography"'))

    def test_arabic_miracle_hub_anchors_approval_and_separates_testimony(self):
        registry, catalogs = load_catalog(ROOT)
        html = builder.outputs(ROOT)[ROOT/'ar/miracles/index.html']
        self.assertIn('href="https://www.sharbel.org/st-sharbel"', html)
        self.assertIn('٥ كانون الأول ١٩٦٥', html)
        self.assertIn('٩ تشرين الأول ١٩٧٧', html)
        self.assertIn('ليست ضمن الحالات الثلاث', html)
        self.assertEqual(builder.alternate_links(registry, 'miracles').count('hreflang="ar"'), 1)

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
