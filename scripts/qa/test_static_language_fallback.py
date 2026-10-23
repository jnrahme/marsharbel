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

class GeneratedNavNegatives(unittest.TestCase):
    """The harness itself must reject the defects it guards against."""

    def setUp(self):
        text=(ROOT/'same-page-manifest.js').read_text()
        self.manifest=json.loads(text[len(PREFIX):].rstrip().rstrip(';'))
        self.registry=json.loads((ROOT/'locales/registry.json').read_text())
        self.copy=json.loads((ROOT/'locales/same-page-copy.json').read_text())
        fam=self.manifest['pages']['annaya-tour-travel-master-equivalence']
        self.verified={l:v for l,v in fam['variants'].items()}

    def _real_nav(self):
        from bs4 import BeautifulSoup
        text=(ROOT/'annaya-tour.html').read_text()
        return BeautifulSoup(GENERATED_NAV.findall(text)[0],'html.parser').nav,BeautifulSoup(text,'html.parser')

    def test_misplaced_nav_outside_footer_is_rejected(self):
        nav,soup=self._real_nav()
        # Move the marked fallback block out of the footer into <main>.
        page_nav=soup.select_one('nav[data-i18n-generated]')
        block=page_nav.find_parent('div',class_='site-shell')
        block.extract()
        soup.find('main').append(block)
        self.assertIsNotNone(footer_containment_violation(str(soup)))
        # and the real page must pass the same check
        self.assertIsNone(footer_containment_violation((ROOT/'annaya-tour.html').read_text()))

    def test_coexisting_forbidden_controls_are_rejected(self):
        real=(ROOT/'annaya-tour.html').read_text()
        with_twin=real.replace('<footer','<noscript><nav class="sc-static-language" aria-label="x"><a href="/ar/annaya-tour" hreflang="ar" lang="ar" dir="rtl">x</a></nav></noscript><footer',1)
        self.assertIsNotNone(exclusivity_violation(with_twin))
        self.assertIsNone(exclusivity_violation(real))

    def test_per_entry_missing_suffix_is_rejected(self):
        nav,_=self._real_nav()
        errors=nav_semantics_errors(nav,'en',self.verified,self.manifest,self.registry,self.copy,'fixture')
        self.assertEqual(errors,[],'real nav must pass its own semantics check')
        for a in nav.select('a[aria-disabled="true"]'):
            a.string=a.get_text().split(' (')[0]  # strip every suffix
            break
        self.assertTrue(any('suffix' in e for e in nav_semantics_errors(nav,'en',self.verified,self.manifest,self.registry,self.copy,'fixture')))


if __name__=='__main__':unittest.main()

GENERATED_NAV = re.compile(r'<!-- i18n-locale-nav:start -->\n<div class="site-shell">\n(<nav aria-label="[^"]*" class="locale-nav locale-fallback"(?=[^>]*\bdata-i18n-generated\b)(?=[^>]*\bdata-locale-fallback\b)[^>]*>[\s\S]*?</nav>)\n</div>\n<!-- i18n-locale-nav:end -->\n?')

def footer_containment_violation(text):
    """Strict: the generated fallback nav must be INSIDE the semantic footer."""
    from bs4 import BeautifulSoup
    soup=BeautifulSoup(text,'html.parser')
    nav=soup.select_one('nav[data-i18n-generated]')
    if nav is None:return None
    if nav.find_parent('footer') is None:
        return 'generated fallback nav is not contained in the page footer'
    return None


def exclusivity_violation(text):
    """Whole-page no-JS control exclusivity (original rule): a page carrying the
    ar2 noscript twin must carry NO locale-nav control at all - neither the
    authored exact-class nav nor a marked generated fallback."""
    if 'sc-static-language' not in text:return None
    if 'class="locale-nav"' in text:return 'carries both the ar2 twin and an authored locale-nav'
    if 'i18n-locale-nav:start' in text:return 'carries both the ar2 twin and a generated fallback'
    return None


def nav_semantics_errors(nav, lang, verified, manifest, registry, copy, fname):
    """Per-entry generated-nav semantics; returns a list of errors (empty = pass)."""
    errors=[]
    linked={a['hreflang']:a for a in nav.select('a[hreflang]')}
    if set(linked)!=set(manifest['languages']):
        errors.append(fname+' lists '+str(sorted(linked))+' not every registered language')
        return errors
    for code,a in linked.items():
        native=registry['locales'][code]['nativeName']
        expected=native if code in verified else native+' ('+copy[lang]['suffix']+')'
        if a.get_text()!=expected:
            errors.append(fname+' '+code+' must render the full native name with the localized suffix per entry')
        if a.get('lang')!=code:errors.append(fname+' '+code+' lang attribute')
        if code in verified:
            if a.get('href')!='https://marsharbel.com'+verified[code]['path']:errors.append(fname+' '+code+' twin href')
            if a.get('aria-disabled')=='true':errors.append(fname+' '+code+' must stay enabled')
        else:
            if a.get('href') is not None:errors.append(fname+' unavailable '+code+' must never link')
            if a.get('aria-disabled')!='true':errors.append(fname+' '+code+' aria-disabled')
        if code==lang:
            if a.get('aria-current')!='page':errors.append(fname+' aria-current')
        elif a.get('aria-current') is not None:errors.append(fname+' aria-current only on current')
    return errors


class GeneratedLocaleNav(unittest.TestCase):
    """PR3 four-way exclusivity, page-level: ar2 noscript twins; the certified
    A1 family keeps its authored nav; published homes keep footer-locales; the
    47 authored-footer-locales guides keep their authored control; only the 50
    verified-equivalence pages with no authored locale chrome gain the marked
    generated footer fallback. Mirrors scripts/i18n/same_page_injection.py
    control_outputs eligibility exactly; the two must never drift apart."""

    def setUp(self):
        text=(ROOT/'same-page-manifest.js').read_text()
        self.manifest=json.loads(text[len(PREFIX):].rstrip().rstrip(';'))
        import sys
        sys.path.insert(0,str(ROOT/'scripts'))
        from i18n.catalog import published_home_locales, home_url
        registry=json.loads((ROOT/'locales/registry.json').read_text())
        self.homes={(home_url(registry,code) or '/').rstrip('/') for code in published_home_locales(registry)}

    def eligible(self):
        out={}
        for key,fam in self.manifest['pages'].items():
            if key.startswith('ar2-'):continue
            verified={l:v for l,v in fam.get('variants',{}).items() if v.get('status')=='verified'}
            if len(verified)<2:continue
            pages={}
            for l,v in verified.items():
                path=(v.get('path','').rstrip('/') or '/')
                if path in self.homes:continue
                text=route_file(v['path']).read_text()
                if 'class="locale-nav"' in text:continue
                if 'sc-static-language' in text:continue
                from bs4 import BeautifulSoup
                if BeautifulSoup(text,'html.parser').select_one('nav.footer-locales'):continue
                pages[l]=v
            if pages:out[key]=pages
        return out

    def test_whole_families_carry_one_marked_nav_with_exact_verified_hreflangs(self):
        seen=set()
        for key,verified in sorted(self.eligible().items()):
            for lang,v in verified.items():
                f=route_file(v['path']);text=f.read_text();seen.add(f)
                blocks=GENERATED_NAV.findall(text)
                self.assertEqual(len(blocks),1,f.name+' needs exactly one marked generated locale-nav')
                self.assertIsNone(exclusivity_violation(text),f.name)
                self.assertIsNone(footer_containment_violation(text),f.name+' fallback must live strictly inside the footer')
                from bs4 import BeautifulSoup
                nav=BeautifulSoup(blocks[0],'html.parser').nav
                registry=json.loads((ROOT/'locales/registry.json').read_text())
                copy=json.loads((ROOT/'locales/same-page-copy.json').read_text())
                self.assertEqual(nav.get('aria-label'),copy[lang]['choose'],f.name+' localized aria-label')
                self.assertEqual(nav_semantics_errors(nav,lang,verified,self.manifest,registry,copy,f.name),[])
        total=sum(len(pages) for pages in self.eligible().values())
        self.assertEqual(total,50,'exact authorized eligible inventory (50 zero-authored-chrome pages; 47 footer-locales guides excluded)')
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
            violation=exclusivity_violation(text)
            self.assertIsNone(violation,str(f.relative_to(ROOT))+' '+str(violation))
            containment=footer_containment_violation(text)
            self.assertIsNone(containment,str(f.relative_to(ROOT))+' '+str(containment))

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
        marked='<!-- i18n-locale-nav:start -->\n<div class="site-shell">\n<nav aria-label="Choose a language" class="locale-nav locale-fallback" data-locale-fallback="" data-i18n-generated=""><a hreflang="en" lang="en">English</a>\n</nav>\n</div>\n<!-- i18n-locale-nav:end -->\n'
        self.assertEqual(strip_generated_locale_nav(('a\n'+marked+'b\n').encode()),b'a\nb\n','marked generated block must strip cleanly')
        self.assertEqual(strip_generated_locale_nav(b'plain bytes, no markers'),b'plain bytes, no markers')
