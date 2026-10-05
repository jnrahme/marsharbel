"""English-master home rendering rejects stale or incomplete translations."""
import copy
import json
from pathlib import Path
import sys
import unittest
from bs4 import BeautifulSoup
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from i18n.home_mirror import render_home

class HomeMirrorTests(unittest.TestCase):
    def setUp(self):
        self.registry = json.loads((ROOT/'locales/registry.json').read_text())
        self.copy = json.loads((ROOT/'locales/en/home-copy.json').read_text())

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
            {**{code:self.registry['site']+cfg['home'] for code,cfg in self.registry['locales'].items()},'x-default':self.registry['site']+'/'})
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
            self.assertIn('/gallery',links,'Unpublished gallery twin must retain English destination')

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
