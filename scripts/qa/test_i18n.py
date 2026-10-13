import copy
import importlib.util
import json
import re
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from string import Template

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'scripts'))
from i18n.catalog import load_catalog, locale_topics, read_json, page_url
from i18n.tour_nav import tour_nav
from i18n.travel_components import travel_frame
from i18n.runtime_labels import ensure_runtime_labels
from i18n.same_page_injection import inject_control
from i18n.travel_metadata import compose_travel_clusters
from bs4 import BeautifulSoup
from i18n.catalog import read_json as _read_json_fc
def fc(t):
    canonical=BeautifulSoup(t,'html.parser').select_one('link[rel=canonical]')['href'].removeprefix('https://marsharbel.com')
    path=ROOT/(canonical.lstrip('/')+'.html')
    t=compose_travel_clusters(ROOT,_read_json_fc(ROOT/'locales/registry.json'),{path:t})[path]
    return inject_control(t,ROOT,_read_json_fc(ROOT/'locales/same-page-manifest.pending.json'),_read_json_fc(ROOT/'locales/same-page-copy.json'))
from check_i18n_policy import check, extract_html

spec = importlib.util.spec_from_file_location('international_builder', ROOT/'scripts/build-international.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


def external_page_hrefs(text):
    """External source links a page offers its readers (site-internal excluded)."""
    return {u for u in re.findall(r'<a [^>]*href="(https?://[^"]+)"', text)
            if 'marsharbel.com' not in u}


def assert_hreflang_reciprocity(case, en_path, ar_path, en_url, ar_url):
    """Authored AR-2 twins carry their own alternate links: exactly one ar
    alternate per side, and the EN master and AR twin point at each other."""
    en = (ROOT/en_path).read_text(encoding='utf8')
    ar = (ROOT/ar_path).read_text(encoding='utf8')
    case.assertEqual(en.count('<link rel="alternate" hreflang="ar"'), 1)
    case.assertEqual(ar.count('<link rel="alternate" hreflang="ar"'), 1)
    case.assertIn(f'<link rel="alternate" hreflang="ar" href="{ar_url}"', en)
    case.assertIn(f'<link rel="alternate" hreflang="en" href="{en_url}"', ar)


def assert_external_sources_mirrored(case, en_path, ar_path, count):
    """The AR twin must offer the same external sources as the EN master."""
    en = external_page_hrefs((ROOT/en_path).read_text(encoding='utf8'))
    ar = external_page_hrefs((ROOT/ar_path).read_text(encoding='utf8'))
    case.assertEqual(en, ar)
    case.assertEqual(len(ar), count)


class CatalogTests(unittest.TestCase):
    def test_english_monasteries_share_navigation_renderer(self):
        import re
        import subprocess
        from i18n.monastery_mirror import render_monasteries
        registry = json.loads((ROOT / 'locales/registry.json').read_text())
        outputs = render_monasteries(ROOT, registry)
        driver = "import fs from 'node:fs';import {renderPrimaryNav} from './scripts/lib/primary-nav.mjs';process.stdout.write(renderPrimaryNav(fs.readFileSync('partials/primary-navigation.html','utf8').trim(),process.argv[1]));"
        for name in ('qannoubine', 'qozhaya'):
            file = name + '-monastery.html'
            nav = re.search(r'<nav\b[^>]*class=["\']links["\'][^>]*>[\s\S]*?</nav>', outputs[ROOT / file])[0]
            expected = subprocess.check_output(['node', '--input-type=module', '-e', driver, file], cwd=ROOT, text=True)
            self.assertEqual(nav, expected)

    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        shutil.copytree(ROOT/'locales', self.root/'locales')
        # Minimal policy fixture tests unrelated hardcoded strings, not full mirror rendering.
        registry=json.loads((self.root/'locales/registry.json').read_text())
        registry['exactMirrors']={}
        # The film family has its own strict gate (test_film_master_family); keep it out of this string-policy fixture.
        registry.get('pageMirrors',{}).pop('film-premiere-master',None)
        (self.root/'locales/registry.json').write_text(json.dumps(registry))
        shutil.copyfile(ROOT/'same-page-copy.js', self.root/'same-page-copy.js')
        # Mirror capability validation needs real source masters in this fixture.
        for cfg in registry.get('pageMirrors',{}).values():
            master=cfg['master']
            if not (self.root/master).exists():
                (self.root/master).parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(ROOT/master,self.root/master)

    def edit(self, file, update):
        path = self.root/'locales'/file
        data = read_json(path)
        update(data)
        path.write_text(json.dumps(data))

    def test_arabic_22nd_attribution_and_home_devotion_limits(self):
        registry, _ = load_catalog(ROOT)
        self.assertEqual(registry['topics']['twentySecond']['sources'], ['cnewaMonthly', 'monastery'])
        html = builder.outputs(ROOT)[ROOT/'ar/22nd-of-the-month.html']
        self.assertIn('href="https://cnewa.org/magazine/lebanons-beloved-saint/"', html)
        self.assertIn('وردت في مقابلة، وليست عددًا ثابتًا', html)
        self.assertIn('إن سمح الطقس', html)
        self.assertIn('كلا. الأعياد الليتورجية هي 24 تموز في التقويم اللاتيني', html)
        self.assertIn('والزيت المبارك والحج والصلاة لا تحلّ محلّ الرعاية الطبية', html)
        self.assertIn('لا موعد ولا صيغة تضمن نتيجة', html)
        self.assertNotIn('تضمن الشفاء', html)

    def test_arabic_raymond_story_distinguishes_reporter_from_medical_record(self):
        # Authored AR-2 twin (PR #769): read the real page, not generator output.
        ar = (ROOT/'ar/miracles/raymond-nader.html').read_text(encoding='utf8')
        self.assertIn('ولم تعلنه الكنيسة عجيبة', ar)
        assert_hreflang_reciprocity(self, 'miracles/raymond-nader.html', 'ar/miracles/raymond-nader.html',
                                    'https://marsharbel.com/miracles/raymond-nader', 'https://marsharbel.com/ar/miracles/raymond-nader')
        assert_external_sources_mirrored(self, 'miracles/raymond-nader.html', 'ar/miracles/raymond-nader.html', 2)

    def test_arabic_dafne_story_anchors_eparchy_statement_without_roman_approval(self):
        ar = (ROOT/'ar/miracles/dafne-gutierrez.html').read_text(encoding='utf8')
        self.assertIn('لا إعلان صادر عن الفاتيكان؛ فلم تُرفع الحالة إلى روما', ar)
        assert_hreflang_reciprocity(self, 'miracles/dafne-gutierrez.html', 'ar/miracles/dafne-gutierrez.html',
                                    'https://marsharbel.com/miracles/dafne-gutierrez', 'https://marsharbel.com/ar/miracles/dafne-gutierrez')
        assert_external_sources_mirrored(self, 'miracles/dafne-gutierrez.html', 'ar/miracles/dafne-gutierrez.html', 3)

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
        self.assertEqual(fc(travel_frame(tour_nav(pages[ROOT / 'qadisha-valley.html'], ROOT, 'en'),ROOT,'en','/qadisha-valley',read_json(ROOT/'locales/registry.json'))), (ROOT / 'qadisha-valley.html').read_text())
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
        # fc composes after its input, but the generator composes BEFORE runtime labels;
        # the two orders are byte-visible, so this chain is written explicitly.
        expected_fr = ensure_runtime_labels(compose_travel_clusters(ROOT,read_json(ROOT/'locales/registry.json'),{ROOT / 'fr/vallee-qadisha.html':travel_frame(tour_nav(fr,ROOT,'fr'),ROOT,'fr','/fr/vallee-qadisha',read_json(ROOT/'locales/registry.json'))})[ROOT / 'fr/vallee-qadisha.html'],ROOT,'fr',read_json(ROOT/'locales/registry.json'))
        self.assertEqual(inject_control(expected_fr,ROOT,read_json(ROOT/'locales/same-page-manifest.pending.json'),read_json(ROOT/'locales/same-page-copy.json')), (ROOT / 'fr/vallee-qadisha.html').read_text())
        es = pages[ROOT / 'es/valle-qadisha.html']
        self.assertEqual(Shape(es).sections, Shape(en).sections)
        self.assertEqual(Shape(es).images, Shape(en).images)
        self.assertEqual(Shape(es).headings, Shape(en).headings)
        self.assertIn('lang="es" dir="ltr"', es)
        self.assertIn('hreflang="es" href="https://marsharbel.com/es/valle-qadisha"', es)
        self.assertIn('no es un tercer bien incluido', es)
        self.assertIn('href="/es/biografia"', es)
        self.assertIn('href="/es/annaya"', es)
        self.assertIn('href="/es/valle-qadisha"', es)
        self.assertNotIn('href="/es/saint-charbel-trail"', es)
        # fc composes after its input, but the generator composes BEFORE runtime labels;
        # the two orders are byte-visible, so this chain is written explicitly.
        expected_es = ensure_runtime_labels(compose_travel_clusters(ROOT,read_json(ROOT/'locales/registry.json'),{ROOT / 'es/valle-qadisha.html':travel_frame(tour_nav(es,ROOT,'es'),ROOT,'es','/es/valle-qadisha',read_json(ROOT/'locales/registry.json'))})[ROOT / 'es/valle-qadisha.html'],ROOT,'es',read_json(ROOT/'locales/registry.json'))
        self.assertEqual(inject_control(expected_es,ROOT,read_json(ROOT/'locales/same-page-manifest.pending.json'),read_json(ROOT/'locales/same-page-copy.json')), (ROOT / 'es/valle-qadisha.html').read_text())


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

    def test_monastery_mirrors_have_matched_shape_and_faq_schema(self):
        from html.parser import HTMLParser
        from i18n.monastery_mirror import render_monasteries

        class Probe(HTMLParser):
            def __init__(self):
                super().__init__(convert_charrefs=True)
                self.main_depth = 0
                self.main_tags = []
                self.ldjson = []
                self._in_ld = False
                self._buf = []
                self.raw = []

            def handle_starttag(self, tag, attrs):
                a = dict(attrs)
                self.raw.append((tag, a))
                if tag == 'main':
                    self.main_depth += 1
                elif self.main_depth:
                    self.main_tags.append((tag, a))
                if tag == 'script' and a.get('type') == 'application/ld+json':
                    self._in_ld = True
                    self._buf = []

            def handle_startendtag(self, tag, attrs):
                a = dict(attrs)
                self.raw.append((tag, a))
                if self.main_depth and tag != 'main':
                    self.main_tags.append((tag, a))

            def handle_endtag(self, tag):
                if tag == 'main' and self.main_depth:
                    self.main_depth -= 1
                if tag == 'script' and self._in_ld:
                    self._in_ld = False
                    self.ldjson.append(''.join(self._buf))

            def handle_data(self, data):
                if self._in_ld:
                    self._buf.append(data)

        registry = read_json(ROOT/'locales/registry.json')
        pages = render_monasteries(ROOT)
        for name in ('qannoubine', 'qozhaya'):
            routes = registry['authoredMirrors'][name]['routes']
            other = 'qozhaya' if name == 'qannoubine' else 'qannoubine'
            other_routes = registry['authoredMirrors'][other]['routes']
            en = Probe(); en.feed(pages[ROOT/f'{name}-monastery.html'])
            # Navigation-only English places must never enter article prose.
            for slug in ('our-lady-of-lebanon-harissa', 'cedars-of-god-lebanon', 'bkerke-maronite-patriarchate'):
                self.assertEqual(pages[ROOT/f'{name}-monastery.html'].count(f'href="./{slug}"'), 1)
                self.assertFalse(any(a.get('href') == f'./{slug}' for t, a in en.main_tags))
            for code, route in routes.items():
                if code == 'en':
                    continue
                page = pages[ROOT/(route.lstrip('/') + '.html')]
                probe = Probe(); probe.feed(page)
                for tag in ('section', 'h1', 'h2', 'h3', 'img', 'figure'):
                    self.assertEqual(len([t for t, a in en.main_tags if t == tag]),
                                     len([t for t, a in probe.main_tags if t == tag]),
                                     f'{name}/{code} {tag} count')
                self.assertEqual([a['src'].lstrip('.') for t, a in en.main_tags if t == 'img'],
                                 [a['src'] for t, a in probe.main_tags if t == 'img'])
                self.assertEqual([s['@type'] for s in [json.loads(body) for body in probe.ldjson]],
                                 ['WebPage', 'FAQPage', 'TouristAttraction'])
                faq = json.loads(probe.ldjson[1])['mainEntity']
                catalog = read_json(ROOT/f'locales/{code}/mirrors/{name}-monastery.json')
                self.assertEqual([(q['name'], q['acceptedAnswer']['text']) for q in faq],
                                 [(catalog[f'faq.question{i}'], catalog[f'faq.text{i}']) for i in range(1,7)])
                self.assertIn(f'href="{other_routes[code]}"', page)
            self.assertEqual(fc(travel_frame(tour_nav(pages[ROOT/f'{name}-monastery.html'], ROOT, 'en'),ROOT,'en',f'/{name}-monastery',read_json(ROOT/'locales/registry.json'))), (ROOT/f'{name}-monastery.html').read_text())

    def test_letters_catalog_does_not_hide_new_copy(self):
        catalog=read_json(ROOT/'locales/en/letters-display.json')['values']
        self.assertEqual(catalog['index.html']['Write a Letter to Saint Charbel'],1)
        self.assertEqual(catalog['home-letter.js']['This browser could not carry your letter to the next page. Keep a copy before continuing.'],1)
        self.assertEqual(catalog['submit-testimony.html']['Send letter for review'],1)
        self.assertNotIn('testimony-admin.js',catalog)

    def test_all_registered_languages_have_all_topics(self):
        registry, catalogs = load_catalog(self.root)
        self.assertEqual(set(catalogs), set(registry['locales']))
        for code,catalog in catalogs.items():
            self.assertEqual(set(catalog['pages']),set(locale_topics(registry,code)))
        self.assertTrue({'biography','prayers','novena','rosary','annaya'} <= set(catalogs['pl']['pages']))

    def test_directory_english_related_page_is_generated_in_index(self):
        # The eucharistic hub is the surviving directory-routed fixture: a
        # directory route maps to a real index.html, never a hidden ".html"
        # file inside the directory.
        generated = builder.outputs(ROOT)
        self.assertIn(ROOT/'ar/miracles/eucharistic/index.html', generated)
        self.assertNotIn(ROOT/'ar/miracles/eucharistic/.html', generated)
        # The English related page is served as the directory index too.
        self.assertTrue((ROOT/'miracles/eucharistic/index.html').exists())

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
        registry, _ = load_catalog(ROOT)
        hub = ROOT/'ar/miracles/eucharistic'
        generated = builder.outputs(ROOT)
        self.assertIn(hub/'index.html', generated)
        self.assertIn(hub/'.htaccess', generated)
        self.assertIn('DirectoryIndex index.html', generated[hub/'.htaccess'])
        self.assertNotIn(ROOT/'ar/miracles/eucharistic.html', generated)
        # Nested story routes live under the hub directory.
        self.assertIn(ROOT/'ar/miracles/eucharistic/lanciano.html', generated)
        # Unsafe slugs stay rejected.
        self.edit('registry.json', lambda d: d['locales']['ar']['slugs'].update({'annaya': 'miracles/../private'}))
        with self.assertRaisesRegex(ValueError, 'unsafe'):
            load_catalog(self.root)

    def test_miracle_story_related_links_start_with_hub(self):
        for slug in ('raymond-nader', 'dafne-gutierrez', 'nohad-el-shami'):
            html = (ROOT/f'ar/miracles/{slug}.html').read_text(encoding='utf8')
            related = html.split('<div class="cta-row">', 1)[1]
            self.assertIn('href="/ar/miracles/"', related)
        nohad = (ROOT/'ar/miracles/nohad-el-shami.html').read_text(encoding='utf8')
        self.assertIn('ولم تفحصها محكمة طبية', nohad)
        self.assertIn('وليس عجيبة أعلنتها الكنيسة', nohad)
        assert_hreflang_reciprocity(self, 'miracles/nohad-el-shami.html', 'ar/miracles/nohad-el-shami.html',
                                    'https://marsharbel.com/miracles/nohad-el-shami', 'https://marsharbel.com/ar/miracles/nohad-el-shami')
        assert_external_sources_mirrored(self, 'miracles/nohad-el-shami.html', 'ar/miracles/nohad-el-shami.html', 5)

    def test_arabic_miracle_hub_anchors_approval_and_separates_testimony(self):
        ar = (ROOT/'ar/miracles/index.html').read_text(encoding='utf8')
        self.assertIn('والتسجيل في الدير ليس هو الاعتراف الرسمي من الكنيسة', ar)
        self.assertIn('٥ كانون الأول ١٩٦٥', ar)
        self.assertIn('٩ تشرين الأول ١٩٧٧', ar)
        assert_hreflang_reciprocity(self, 'miracles/index.html', 'ar/miracles/index.html',
                                    'https://marsharbel.com/miracles/', 'https://marsharbel.com/ar/miracles/')
        assert_external_sources_mirrored(self, 'miracles/index.html', 'ar/miracles/index.html', 11)
        # The rosary-intro <-> ar/rosary pair must survive a build-pages regen:
        # exactly one ar alternate per side, pointing at each other.
        assert_hreflang_reciprocity(self, 'rosary-intro.html', 'ar/rosary.html',
                                    'https://marsharbel.com/rosary-intro', 'https://marsharbel.com/ar/rosary')

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
                d['locales'][code]['capabilities']['topicGuides'].append('sampleTopic')
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
        # Canonical English URL carries no language parameter (P0: parameter URLs
        # are crawlable duplicates).
        self.assertIn('href="/sample-topic"',navigation)
        self.assertNotIn('?lang=',navigation)
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
        with self.assertRaisesRegex(ValueError,'locales must be|topic capability differs from publication'):
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
