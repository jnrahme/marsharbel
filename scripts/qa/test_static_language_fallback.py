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
