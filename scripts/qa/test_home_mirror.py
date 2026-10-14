"""English-master home rendering rejects stale or incomplete translations."""
import copy
import json
from pathlib import Path
import sys
import unittest
from bs4 import BeautifulSoup
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from i18n.home_mirror import render_home, mark_home_prayer_disclosures, PRAYER_DISCLOSURE_CONTROLS
from i18n.catalog import published_home_locales

class HomeMirrorTests(unittest.TestCase):
    def setUp(self):
        self.registry = json.loads((ROOT/'locales/registry.json').read_text())
        self.copy = json.loads((ROOT/'locales/en/home-copy.json').read_text())
        # Explicit English-copy test fixture retains the reviewed DE handoff notice.
        qualifier = json.loads((ROOT/'locales/de/encyclopedia-trail.json').read_text())['englishQualifier']
        for _, key in PRAYER_DISCLOSURE_CONTROLS:
            self.copy[key] += ' ' + qualifier

    def test_main_structure_and_asset_paths_preserved(self):
        # English copy is an explicit test fixture, never a published locale.
        rendered = BeautifulSoup(render_home(ROOT, self.registry, 'de', self.copy), 'html.parser')
        source = BeautifulSoup((ROOT/'index.html').read_text(), 'html.parser')
        def structure(node):
            return [(n.name, n.get('class'), n.get('id')) for n in node.find_all()]
        self.assertEqual(structure(source.main), structure(rendered.main))
        self.assertEqual(rendered.html['lang'], 'de')
        self.assertEqual(rendered.select_one('link[rel=canonical]')['href'], 'https://marsharbel.com/de/')
        self.assertEqual(rendered.select_one('video')['data-src-mp4'], '/media/hero/home-hero-full.mp4?v=1')
        self.assertIn('/home.css', rendered.select_one('link[rel=stylesheet]')['href'])

    def test_localized_metadata_schema_and_reciprocal_home_cluster(self):
        title_key = next(key for key in self.copy if key.startswith('home.metadata.saint-charbel-mar-charbel-life-miracles'))
        self.copy[title_key] = 'Lokaler Seitentitel'
        rendered = BeautifulSoup(render_home(ROOT,self.registry,'de',self.copy),'html.parser')
        self.assertEqual(rendered.title.get_text(),'Lokaler Seitentitel')
        self.assertEqual(rendered.select_one('meta[property="og:title"]')['content'],'Lokaler Seitentitel')
        self.assertEqual(rendered.select_one('meta[property="og:locale"]')['content'],'de_DE')
        self.assertEqual({n['hreflang']:n['href'] for n in rendered.select('link[hreflang]')},
            {**{code:self.registry['site']+self.registry['locales'][code]['home'] for code in published_home_locales(self.registry)},'x-default':self.registry['site']+'/'})
        self.assertIsNone(rendered.select_one('link[hreflang="zh-Hans"]'))
        graph=json.loads(rendered.select_one('script[type="application/ld+json"]').string)['@graph']
        page=next(item for item in graph if item['@type']=='WebPage')
        self.assertEqual((page['name'],page['url'],page['inLanguage']),('Lokaler Seitentitel','https://marsharbel.com/de/','de'))

    def test_locale_home_links_use_published_twins(self):
        from i18n.catalog import page_url,topic_locales
        for lang in self.registry['homepageMirrors']['renderLocales']:
            rendered=BeautifulSoup(render_home(ROOT,self.registry,lang),'html.parser')
            links={a['href'] for a in rendered.select('a[href]') if not a.has_attr('hreflang')}
            for topic,cfg in self.registry['topics'].items():
                if lang not in topic_locales(self.registry,topic): continue
                master=cfg['relatedEnglish']
                source=BeautifulSoup((ROOT/'index.html').read_text(),'html.parser')
                from urllib.parse import urljoin,urlsplit
                master_links={urlsplit(urljoin('/',a['href'])).path.rstrip('/') for a in source.select('a[href]') if not a.has_attr('hreflang')}
                if master.rstrip('/') not in master_links:continue
                expected=page_url(self.registry,lang,topic)
                for config in self.registry.get('exactMirrors',{}).values():
                    if config['english']==master and lang in config['routes']:expected=config['routes'][lang]
                self.assertIn(expected,links,f'{lang}: missing {topic} twin')
                self.assertNotIn(master,links,f'{lang}: English {topic} leaked instead of its twin')
            routes=json.loads((ROOT/'locale-routes.js').read_text().split('=',1)[1].strip().rstrip(';'))['topics']
            self.assertIn(routes.get('/gallery',{}).get(lang,'/gallery'),links,'Gallery link must be the published twin, else the English destination')

    def test_reviewed_prayer_controls_and_hindi_thai_unchanged(self):
        for lang in self.registry['homepageMirrors']['renderLocales']:
            rendered = BeautifulSoup(render_home(ROOT, self.registry, lang), 'html.parser')
            catalog = json.loads((ROOT/f'locales/{lang}/home-copy.json').read_text())
            qualifier = json.loads((ROOT/f'locales/{lang}/encyclopedia-trail.json').read_text())['englishQualifier']
            for selector, key in PRAYER_DISCLOSURE_CONTROLS:
                anchor = rendered.select_one(selector)
                self.assertEqual(anchor['href'], '/mystery-meditation')
                self.assertEqual(catalog[key].count(qualifier), 1)
                if lang in ('hi', 'th'):
                    self.assertNotIn('hreflang', anchor.attrs)
                    self.assertNotIn('aria-label', anchor.attrs)
                else:
                    self.assertEqual(anchor['hreflang'], 'en')
                    self.assertEqual(anchor['aria-label'], catalog[key])
            youtube = rendered.select('a.promo-link[href*="#pray-along"]')
            self.assertEqual(len(youtube), 1)

    def test_prayer_disclosure_negative_controls(self):
        catalog = json.loads((ROOT/'locales/de/home-copy.json').read_text())
        qualifier = json.loads((ROOT/'locales/de/encyclopedia-trail.json').read_text())['englishQualifier']
        rendered = render_home(ROOT, self.registry, 'de')
        for mutation in ('target', 'missing', 'duplicate', 'label', 'qualifier', 'double'):
            with self.subTest(mutation=mutation):
                soup = BeautifulSoup(rendered, 'html.parser')
                changed = dict(catalog)
                anchor = soup.select_one('a.home-hero-cta2')
                if mutation == 'target': anchor['href'] = '/rosary-intro'
                elif mutation == 'missing': anchor.decompose()
                elif mutation == 'duplicate': anchor.insert_after(copy.deepcopy(anchor))
                elif mutation == 'label': anchor.string = 'Wrong label'
                elif mutation == 'qualifier': changed[PRAYER_DISCLOSURE_CONTROLS[0][1]] = 'No notice'
                elif mutation == 'double': changed[PRAYER_DISCLOSURE_CONTROLS[0][1]] += ' ' + qualifier
                with self.assertRaises(ValueError):
                    mark_home_prayer_disclosures(soup, 'de', changed, qualifier)

    def test_new_meditation_twin_requires_review(self):
        registry = copy.deepcopy(self.registry)
        registry['pageMirrors']['test-meditation'] = {
            'english': '/mystery-meditation', 'routes': {'de': '/de/meditation'},
            'renderLocales': ['de']}
        with self.assertRaisesRegex(ValueError, 'twin now exists'):
            render_home(ROOT, registry, 'de')

    def test_missing_key_fails(self):
        self.copy.pop(next(iter(self.copy)))
        with self.assertRaisesRegex(ValueError, 'missing/extra'): render_home(ROOT, self.registry, 'de', self.copy)

    def test_html_and_placeholder_drift_fail(self):
        key='home.runtime.monthly.next'
        self.copy[key]='Bad markup <b>text</b>'
        with self.assertRaisesRegex(ValueError, 'unsafe'):render_home(ROOT,self.registry,'de',self.copy)
        self.copy[key]='No month parameter'
        with self.assertRaisesRegex(ValueError, 'placeholders'):render_home(ROOT,self.registry,'de',self.copy)

if __name__ == '__main__': unittest.main()
