import json
from pathlib import Path
import sys,unittest
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from i18n.mirror_structure import check_pair, NORMALIZERS
from i18n.home_mirror import render_home

class MirrorStructure(unittest.TestCase):
    def test_translated_copy_does_not_change_structure(self):
        master='<header></header><main id="main"><section><h1>Hello</h1></section></main><footer></footer>'
        self.assertEqual(check_pair(master,master.replace('Hello','Bonjour'),'/','/fr/'),[])

    def test_section_and_stylesheet_mutations_fail(self):
        master='<link rel="stylesheet" href="/home.css"><main><section><h1>Hi</h1></section></main>'
        self.assertIn('main',check_pair(master,master.replace('<section>','<article>').replace('</section>','</article>'),'/','/fr/'))
        self.assertIn('styles',check_pair(master,master.replace('home.css','international.css'),'/','/fr/'))

    def test_launch_normalizer_preserves_unrelated_structure_checks(self):
        master='<header><nav></nav></header><main><section><h1>Hi</h1></section></main><footer></footer>'
        locale=master.replace('</nav>', '<span class="launch-english-qualifier">English</span></nav>').replace('</main>', '<aside class="launch-availability"><p>Launch note</p></aside></main>')
        normalizers=['launch-availability-annotations']
        self.assertIn('header',check_pair(master,locale,'/','/hi/'))
        self.assertIn('main',check_pair(master,locale,'/','/hi/'))
        self.assertEqual(check_pair(master,locale,'/','/hi/',normalizers),[])
        changed=locale.replace('<section>','<article>').replace('</section>','</article>')
        self.assertIn('main',check_pair(master,changed,'/','/hi/',normalizers))
        self.assertIn('header',check_pair(master,locale.replace('<nav>','<nav hidden>'),'/','/hi/',normalizers))
        other_aside=locale.replace('class="launch-availability"','class="other-note"')
        self.assertIn('main',check_pair(master,other_aside,'/','/hi/',normalizers))

    def test_english_nav_disclosure_normalizer_scoped_and_validated(self):
        master='<header><nav><a href="/stories">Stories</a></nav></header><main><section><h1>Hi</h1></section></main><footer></footer>'
        mark='<a hreflang="en" aria-label="Stories (English)" href="/stories">Stories <span class="enc-language">(English)</span></a>'
        locale=master.replace('<a href="/stories">Stories</a>',mark)
        normalizers=['english-nav-disclosure']
        # Unnormalized the marked header diverges; normalized it is equal to the master.
        self.assertIn('header',check_pair(master,locale,'/','/ar/'))
        self.assertEqual(check_pair(master,locale,'/','/ar/',normalizers),[])
        # The same marking inside <main> is out of scope and must still fail.
        in_main=master.replace('<h1>Hi</h1>','<h1>Hi</h1>'+mark)
        self.assertIn('main',check_pair(master,in_main,'/','/ar/',normalizers))
        # A mismatched aria-label raises instead of being stripped.
        bad_label=locale.replace('aria-label="Stories (English)"','aria-label="Other (English)"')
        self.assertRaises(ValueError,check_pair,master,bad_label,'/','/ar/',normalizers)
        # Marking a locale-prefixed href raises.
        prefixed=locale.replace('href="/stories"','href="/ar/stories"')
        self.assertRaises(ValueError,check_pair,master,prefixed,'/','/ar/',normalizers)
        # Any other tag/class change in the header still fails after normalizing.
        changed=locale.replace('<nav>','<nav hidden>')
        self.assertIn('header',check_pair(master,changed,'/','/ar/',normalizers))
        changed_class=locale.replace('class="enc-language"','class="enc-language extra"')
        self.assertRaises(ValueError,check_pair,master,changed_class,'/','/ar/',normalizers)

    def test_home_renderer_preserves_all_regions_and_assets(self):
        master=(ROOT/'index.html').read_text()
        registry=json.loads((ROOT/'locales/registry.json').read_text())
        copy=json.loads((ROOT/'locales/en/home-copy.json').read_text())
        locale=render_home(ROOT,registry,'de',copy)
        self.assertEqual(check_pair(master,locale,'/','/de/'),[])

    def test_published_home_mirrors_match_english(self):
        registry=json.loads((ROOT/'locales/registry.json').read_text())
        master=(ROOT/'index.html').read_text()
        policy=json.loads((ROOT/'config/locale-mirror-policy.json').read_text())
        for lang in registry.get('homepageMirrors',{}).get('renderLocales',[]):
            path=lang+'/index.html'
            entry=policy['pages'][path]
            self.assertEqual(entry['status'],'strict',lang)
            normalizers=entry.get('normalizers',[])
            for name in normalizers:
                self.assertIn(name,NORMALIZERS,f'{path}: unregistered normalizer {name}')
            self.assertEqual(check_pair(master,(ROOT/path).read_text(), '/',registry['locales'][lang]['home'],normalizers),[],lang)

if __name__=='__main__':unittest.main()
