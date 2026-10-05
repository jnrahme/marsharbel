import hashlib,json,sys,unittest
from pathlib import Path
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from i18n.page_mirror import render_page
from i18n.mirror_structure import check_pair
class HistoryMirrors(unittest.TestCase):
 def setUp(self):self.r=json.loads((ROOT/'locales/registry.json').read_text())
 def test_all_eight_full_masters_and_localized_schema(self):
  master=(ROOT/'history.html').read_text()
  for lang,route in self.r['pageMirrors']['history-master']['routes'].items():
   text=render_page(ROOT,self.r,lang,'history-master',route);s=BeautifulSoup(text,'html.parser')
   self.assertEqual(check_pair(master,text,'/history',route),[],lang)
   self.assertEqual(s.html['lang'],lang);self.assertEqual(s.main['tabindex'],'-1')
   self.assertEqual(s.select_one('link[rel=canonical]')['href'],self.r['site']+route)
   visit=s.select_one('#visit p').get_text(' ',strip=True)
   paragraph=s.select_one('#visit p')
   for link in paragraph.select('a'):
    after=link.next_sibling
    if after and str(after).lstrip()[:1].isalnum():self.assertTrue(str(after)[0].isspace(),(lang,str(after)))
   self.assertNotIn('[object Object]',visit);self.assertEqual(len(s.select('#visit p a')),3)
   self.assertTrue(all(a.get_text(strip=True) for a in s.select('#visit p a')),lang)
   copy=json.loads((ROOT/f'locales/{lang}/history-master-copy.json').read_text())
   schemas=[json.loads(x.string) for x in s.select('script[type="application/ld+json"]')]
   self.assertEqual(next(x for x in schemas if x['@type']=='Person')['name'],copy['history.header.saint-charbel'])
   self.assertEqual(next(x for x in schemas if x['@type']=='WebPage')['breadcrumb']['itemListElement'][0]['name'],copy['history.header.home'])
   faq=next(section for section in s.select('main section') if len(section.select('h3')) == 9)
   schema=next(json.loads(x.string) for x in s.select('script[type="application/ld+json"]') if json.loads(x.string)['@type']=='FAQPage')
   clean=lambda t:t.replace('\u2068','').replace('\u2069','')
   self.assertEqual([(q['name'],q['acceptedAnswer']['text']) for q in schema['mainEntity']],[(clean(h.get_text(' ',strip=True)),clean(p.get_text(' ',strip=True))) for h,p in zip(faq.select('h3'),faq.select('p'))])
 def test_missing_and_wrong_type_copy_fail(self):
  c=json.loads((ROOT/'locales/fr/history-master-copy.json').read_text());c.pop(next(iter(c)))
  with self.assertRaisesRegex(ValueError,'missing/extra'):render_page(ROOT,self.r,'fr','history-master','/fr/biographie',c)
  c=json.loads((ROOT/'locales/fr/history-master-copy.json').read_text());c[next(iter(c))]={}
  with self.assertRaisesRegex(ValueError,'unsafe'):render_page(ROOT,self.r,'fr','history-master','/fr/biographie',c)
 def test_arabic_latin_runs_are_bidi_isolated(self):
  s=BeautifulSoup(render_page(ROOT,self.r,'ar','history-master','/ar/biography'),'html.parser')
  self.assertIn('\u2068ora et labora\u2069',s.main.get_text())
  self.assertIn('\u2068CC BY-SA 4.0\u2069',s.main.get_text())
if __name__=='__main__':unittest.main()
