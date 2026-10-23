"""No-JS static en<->ar fallback: every recomputed AR-2 twin ships one <noscript> link to its twin."""
import json,re,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PREFIX='window.SC_SAME_PAGE_MANIFEST = '
BLOCK=re.compile(r'<noscript><nav class="sc-static-language" aria-label="[^"]*"><a href="([^"]+)" hreflang="(ar|en)" lang="\2" dir="(rtl|ltr)">[^<]+</a></nav></noscript>')

def route_file(route):
    if route=='/':return ROOT/'index.html'
    if route.endswith('/'):return ROOT/route.strip('/')/'index.html'
    return ROOT/(route.strip('/')+'.html')

class StaticLanguageFallback(unittest.TestCase):
    def setUp(self):
        text=(ROOT/'same-page-manifest.js').read_text()
        self.manifest=json.loads(text[len(PREFIX):].rstrip().rstrip(';'))

    def test_every_ar2_twin_links_to_its_twin_and_nothing_else_does(self):
        ar2=[p for k,p in self.manifest['pages'].items() if k.startswith('ar2-')]
        self.assertGreaterEqual(len(ar2),20)
        linked=set()
        for fam in ar2:
            en,ar=fam['variants']['en']['path'],fam['variants']['ar']['path']
            if en=='/':continue  # published-home route, never a static exact-twin link
            for here,there,code,direction in ((en,ar,'ar','rtl'),(ar,en,'en','ltr')):
                f=route_file(here);text=f.read_text()
                found=BLOCK.findall(text)
                self.assertEqual(len(found),1,f.name+' needs exactly one static fallback')
                self.assertEqual(found[0],('https://marsharbel.com'+there,code,direction),f.name)
                self.assertLess(text.index('<noscript><nav class="sc-static-language"'),text.index('<main'),f.name)
                linked.add(f)
        for f in ROOT.rglob('*.html'):
            if any(p in {'node_modules','.git','src','templates','docs'} for p in f.relative_to(ROOT).parts):continue
            if f not in linked:
                self.assertNotIn('sc-static-language',f.read_text(),str(f.relative_to(ROOT))+' must not carry an unpaired static fallback')

    def test_certified_rosary_guide_family_survives_control_composition(self):
        """The control build must keep composing the reviewed A1 rosary-guide family (a rebase once dropped its producer)."""
        fam=self.manifest['pages'].get('rosary-guide-equivalence')
        self.assertIsNotNone(fam,'rosary-guide-equivalence family missing from the composed manifest')
        self.assertEqual(sorted(fam['variants']),sorted(['en','ar','fr','es','pt','it','de','pl']))
        self.assertEqual(fam['sourcePath'],'en/rosary.html')
        self.assertEqual(fam['variants']['ar']['path'],'/ar/rosary-guide')
        self.assertEqual(fam['variants']['en']['path'],'/en/rosary')
        # Fallback scope stays AR-2 only: the rosary-guide family carries no static fallback block.
        for v in fam['variants'].values():
            self.assertNotIn('sc-static-language',route_file(v['path']).read_text())

if __name__=='__main__':unittest.main()

GENERATED_NAV = re.compile(r'<!-- i18n-locale-nav:start -->\n<div class="site-shell">\n(<nav aria-label="Choose language" class="locale-nav">[\s\S]*?</nav>)\n</div>\n<!-- i18n-locale-nav:end -->\n?')

class GeneratedLocaleNav(unittest.TestCase):
    """PR3 four-way exclusivity: ar2 noscript twins, >=2-variant equivalence
    families gain one marked generated locale-nav (EN+mirrors together), the
    certified A1 family keeps its authored nav, everything else gets neither."""

    def setUp(self):
        text=(ROOT/'same-page-manifest.js').read_text()
        self.manifest=json.loads(text[len(PREFIX):].rstrip().rstrip(';'))

    def eligible(self):
        out={}
        for key,fam in self.manifest['pages'].items():
            if key.startswith('ar2-') or key=='rosary-guide-equivalence':continue
            verified={l:v for l,v in fam.get('variants',{}).items() if v.get('status')=='verified'}
            if len(verified)>=2:out[key]=verified
        return out

    def test_whole_families_carry_one_marked_nav_with_exact_verified_hreflangs(self):
        seen=set()
        for key,verified in sorted(self.eligible().items()):
            for lang,v in verified.items():
                f=route_file(v['path']);text=f.read_text();seen.add(f)
                blocks=GENERATED_NAV.findall(text)
                self.assertEqual(len(blocks),1,f.name+' needs exactly one marked generated locale-nav')
                self.assertNotIn('sc-static-language',text,f.name+' must not also carry the ar2 noscript twin')
                self.assertLess(text.index('i18n-locale-nav:start'),text.index('</header>'),f.name)
                from bs4 import BeautifulSoup
                nav=BeautifulSoup(blocks[0],'html.parser').nav
                linked={a['hreflang']:a for a in nav.select('a[hreflang]')}
                self.assertEqual(set(linked),set(self.manifest['languages']),f.name+' lists every registered language')
                for code,a in linked.items():
                    if code in verified:
                        self.assertEqual(a.get('href'),'https://marsharbel.com'+verified[code]['path'],f.name+' '+code)
                        self.assertNotEqual(a.get('aria-disabled'),'true',f.name+' '+code)
                    else:
                        self.assertIsNone(a.get('href'),f.name+' unavailable '+code+' must never link')
                        self.assertEqual(a.get('aria-disabled'),'true',f.name+' '+code)
                    if code==lang:self.assertEqual(a.get('aria-current'),'page',f.name+' aria-current')
                    else:self.assertIsNone(a.get('aria-current'),f.name+' aria-current only on current')
        self.assertEqual(len(self.eligible()),18,'exact current-stage eligible inventory (18 families, A1 excluded)')
        return seen

    def test_no_page_outside_the_release_carries_the_marked_nav(self):
        eligible_files=set()
        for verified in self.eligible().values():
            for v in verified.values():eligible_files.add(route_file(v['path']))
        for f in ROOT.rglob('*.html'):
            if any(p in {'node_modules','.git','src','templates','docs','test-results','playwright-report'} for p in f.relative_to(ROOT).parts):continue
            text=f.read_text()
            if f not in eligible_files:
                self.assertNotIn('i18n-locale-nav:start',text,str(f.relative_to(ROOT))+' outside the release carries the marked nav')
            if 'sc-static-language' in text:
                self.assertNotIn('class="locale-nav"',text,str(f.relative_to(ROOT))+' carries both no-JS controls')

    def test_authored_nav_and_content_never_strip(self):
        """The marked-block stripper must leave authored bytes (A1 rosary nav and
        all unmarked content) untouched; only generated markers strip."""
        import sys
        sys.path.insert(0,str(ROOT/'scripts'))
        from i18n.keyed_master import strip_static_fallback_text, strip_generated_locale_nav
        authored=(ROOT/'en/rosary.html').read_text()
        self.assertIn('class="locale-nav"',authored)
        self.assertNotIn('i18n-locale-nav:start',authored,'A1 authored nav must stay unmarked')
        self.assertEqual(strip_static_fallback_text(authored),authored,'authored A1 nav bytes must never strip')
        marked='<!-- i18n-locale-nav:start -->\n<div class="site-shell">\n<nav aria-label="Choose language" class="locale-nav"><a hreflang="en">English</a>\n</nav>\n</div>\n<!-- i18n-locale-nav:end -->\n'
        self.assertEqual(strip_generated_locale_nav(('a\n'+marked+'b\n').encode()),b'a\nb\n','marked generated block must strip cleanly')
        self.assertEqual(strip_generated_locale_nav(b'plain bytes, no markers'),b'plain bytes, no markers')
