import json
from pathlib import Path
import sys,unittest
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from i18n.mirror_structure import check_pair
from i18n.home_mirror import render_home

class MirrorStructure(unittest.TestCase):
    def test_translated_copy_does_not_change_structure(self):
        master='<header></header><main id="main"><section><h1>Hello</h1></section></main><footer></footer>'
        self.assertEqual(check_pair(master,master.replace('Hello','Bonjour'),'/','/fr/'),[])

    def test_section_and_stylesheet_mutations_fail(self):
        master='<link rel="stylesheet" href="/home.css"><main><section><h1>Hi</h1></section></main>'
        self.assertIn('main',check_pair(master,master.replace('<section>','<article>').replace('</section>','</article>'),'/','/fr/'))
        self.assertIn('styles',check_pair(master,master.replace('home.css','international.css'),'/','/fr/'))

    def test_home_renderer_preserves_all_regions_and_assets(self):
        master=(ROOT/'index.html').read_text()
        registry=json.loads((ROOT/'locales/registry.json').read_text())
        copy=json.loads((ROOT/'locales/en/home-copy.json').read_text())
        locale=render_home(ROOT,registry,'de',copy)
        self.assertEqual(check_pair(master,locale,'/','/de/'),[])

    def test_published_home_mirrors_match_english(self):
        registry=json.loads((ROOT/'locales/registry.json').read_text())
        master=(ROOT/'index.html').read_text()
        for lang in registry.get('homepageMirrors',{}).get('renderLocales',[]):
            self.assertEqual(check_pair(master,(ROOT/lang/'index.html').read_text(), '/',registry['locales'][lang]['home']),[],lang)

if __name__=='__main__':unittest.main()
