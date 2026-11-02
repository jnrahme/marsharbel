"""Fail-closed tests for the Stories-only Chinese header adapter."""
import sys,tempfile,json,unittest
from pathlib import Path
from unittest.mock import patch
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts'))
from i18n.stories_zh_header import finish_stories_zh_header
from i18n.mirror_structure import _strip_english_nav_disclosure
class StoriesChineseHeader(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        (self.root/'locales/zh-Hans').mkdir(parents=True)
        (self.root/'locales/registry.json').write_text('{}')
        (self.root/'locales/zh-Hans/encyclopedia-trail.json').write_text(json.dumps({'englishQualifier':'(英文)'}))
        (self.root/'sitemap.xml').write_text('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://marsharbel.com/zh-Hans/existing</loc></url></urlset>')
        self.mock=patch('i18n.stories_zh_header.twin_routes',return_value={'/existing':'/zh-Hans/existing','/unpublished':'/zh-Hans/unpublished'});self.mock.start()
    def tearDown(self):self.mock.stop();self.tmp.cleanup()
    def run_header(self,body,family='stories-master',lang='zh-Hans'):
        text='<html><header>'+body+'</header>\n<main data-byte="unchanged">  Main &amp; text </main>\n<footer> Footer  </footer></html>'
        out=finish_stories_zh_header(text,self.root,family,lang)
        self.assertEqual(text.split('</header>',1)[1],out.split('</header>',1)[1])
        _strip_english_nav_disclosure(BeautifulSoup(out,'html.parser'))
        return BeautifulSoup(out,'html.parser')
    def test_registered_unpublished_absent_query_fragment_and_invariance(self):
        s=self.run_header('<a href="/existing?q=1#part">甲</a><a href="/unpublished?q=2#x">乙</a><a href="/absent">丙</a>')
        a,b,c=s.header.select('a');self.assertEqual(a['href'],'/zh-Hans/existing?q=1#part');self.assertFalse(a.select('span'))
        self.assertEqual(b['href'],'/unpublished?q=2#x');self.assertEqual(c['href'],'/absent')
        for n in (b,c):self.assertEqual(n['hreflang'],'en');self.assertEqual(n['aria-label'],n.get_text(' ',strip=True))
    def test_stale_valid_disclosure_removed_for_twin_and_idempotent(self):
        s=self.run_header('<a href="/existing" hreflang="en" aria-label="甲 (英文)">甲 <span class="enc-language">(英文)</span></a>')
        self.assertFalse(s.a.select('span'));self.assertNotIn('hreflang',s.a.attrs)
        original='<html><header><a href="/absent">甲</a></header><main> x </main><footer> y </footer></html>'
        once=finish_stories_zh_header(original,self.root,'stories-master','zh-Hans')
        self.assertEqual(once,finish_stories_zh_header(once,self.root,'stories-master','zh-Hans'))
    def test_malformed_duplicate_disclosure_rejected(self):
        cases=('<a href="/absent" hreflang="en">甲</a>',
               '<a href="/existing" hreflang="en" aria-label="甲 X">甲 <span class="enc-language">(英文)</span></a>',
               '<a href="/existing" hreflang="en" aria-label="甲 X">甲 <span class="enc-language"><b>X</b></span></a>',
               '<a href="/existing" hreflang="en" aria-label="甲 X">甲 <span class="enc-language">X</span><span class="enc-language">X</span></a>',
               '<a href="/existing" href="/ATTACK">甲</a>')
        for body in cases:
            with self.subTest(body=body),self.assertRaises(ValueError):self.run_header(body)
    def test_already_localized_external_hash_unchanged(self):
        body='<a href="/zh-Hans/existing">甲</a><a href="https://example.org/a">乙</a><a href="//example.org/a">丙</a><a href="#a">丁</a><a href="mailto:x@example.org">戊</a>'
        s=self.run_header(body)
        for a in s.header.select('a'):self.assertFalse(a.select('span'));self.assertNotIn('hreflang',a.attrs)
    def test_wrong_context_missing_header_synthetic_route(self):
        for f,l in (('other','zh-Hans'),('stories-master','ar')):
            with self.assertRaises(ValueError):self.run_header('<a href="/absent">甲</a>',f,l)
        with self.assertRaises(ValueError):finish_stories_zh_header('<main>x</main>',self.root,'stories-master','zh-Hans')
        with self.assertRaises(ValueError):self.run_header('<a href="/zh-Hans/TR006-ISOLATED-STORIES-PREVIEW">甲</a>')
    def test_consistent_but_wrong_qualifier_cannot_poison_later_or_earlier_link(self):
        for route in ('/existing','/absent','/'):
            for old_class in ('enc-language','partial-home-language'):
                malicious='<a href="'+route+'" hreflang="en" aria-label="甲 WRONG">甲 <span class="'+old_class+'">WRONG</span></a>'
                untouched='<a href="/absent">乙</a>'
                for body in (malicious+untouched,untouched+malicious):
                    with self.subTest(route=route,old_class=old_class,body=body),self.assertRaises(ValueError):self.run_header(body)

    def test_trusted_disclosure_is_order_independent_and_old_home_scope_exact(self):
        valid='<a href="/existing" hreflang="en" aria-label="甲 (英文)">甲 <span class="enc-language">(英文)</span></a>'
        untouched='<a href="/absent">乙</a>'
        for body in (valid+untouched,untouched+valid):
            s=self.run_header(body);a=s.select_one('a[href="/absent"]')
            self.assertEqual(a.select_one('span').get_text(),'(英文)');self.assertEqual(a['aria-label'],'乙 (英文)')
        self.run_header('<a href="/" hreflang="en" aria-label="首页 (英文)">首页<span class="partial-home-language"> (英文)</span></a>')
        with self.assertRaises(ValueError):self.run_header('<a href="/absent" hreflang="en" aria-label="甲 (英文)">甲<span class="partial-home-language"> (英文)</span></a>')

if __name__=='__main__':unittest.main()
