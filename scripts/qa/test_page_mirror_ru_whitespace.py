"""Actual render_page replaces RU source tag without inheriting its whitespace."""
import json,sys,unittest
from pathlib import Path
from unittest.mock import patch
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts'))
from i18n import page_mirror as m
class RuWhitespaceTests(unittest.TestCase):
 def render(self,raw,family="travel-travel-master",lang="de"):
  registry={'site':'https://marsharbel.com','locales':{'en':{'direction':'ltr','nativeName':'English','home':'/'},'de':{'direction':'ltr','nativeName':'Deutsch','home':'/de/'},'ru':{'direction':'ltr','nativeName':'Russian','home':'/ru/'}},'topics':{},'pageMirrors':{family:{'english':'/fixture','routes':{'de':'/de/fixture'},'discoveryRoutes':{'en':'/fixture','de':'/de/fixture','ru':'/ru/fixture','x-default':'/fixture'}}}}
  contract={'master':'fixture.html','bindings':[]}
  def read(path):
   if str(path).endswith(family+'-bindings.json'):return contract
   if str(path).endswith('runtime.json'):return {'language.label':'Language'}
   if str(path).endswith('common.json'):return {'navigation.chooseLanguage':'Choose'}
   raise AssertionError(path)
  with patch.object(m,'apply_keyed_master',return_value=(raw.encode(),BeautifulSoup(raw,'html.parser'),{'fixture.title':'Title'})),patch.object(m,'read_json',side_effect=read),patch.object(m,'og_locales',return_value={'en':'en_US','de':'de_DE','ru':'ru_RU'}),patch.object(m,'home_url',side_effect=lambda registry,code:registry['locales'][code]['home']),patch.object(m,'check_pair',return_value=None),patch('i18n.launch_availability.apply_launch_availability',side_effect=lambda text,*args:text):
   return m.render_page(ROOT,registry,lang,family,'/de/fixture')
 def source(self):
  return '<html><head><title>Title</title><meta name="description" content="Description"/><link rel="canonical" href="https://marsharbel.com/fixture"/><meta property="og:url" content="https://marsharbel.com/fixture"/><meta property="og:locale" content="en_US"/>\n<link rel="alternate" hreflang="en" href="https://marsharbel.com/fixture"/>\n</head><body><main><h1>Title</h1></main></body></html>'
 def ru_source(self):
  return self.source().replace('</head>','<link rel="alternate" hreflang="ru" href="https://marsharbel.com/ru/fixture"/>\n</head>')
 def test_ru_scoped_renderer_matches_same_master_without_ru(self):
  for lang in ('de','ru'):
   # Model the pre-RU-source renderer while keeping identical family identity.
   # Only disable the new RU guard for the historical no-RU baseline.
   with patch('i18n.travel_variant_evidence.SLUGS',set()):
    baseline=self.render(self.source(),lang=lang)
   self.assertEqual(baseline,self.render(self.ru_source(),lang=lang))
 def test_non_ru_trailing_whitespace_is_retained(self):
  before=self.ru_source();extra=before.replace('</head>','<link rel="alternate" hreflang="fr" href="https://marsharbel.com/fr/fixture"/>\n</head>')
  a,b=self.render(before),self.render(extra)
  self.assertNotEqual(a,b)
  self.assertEqual(b,a.replace('<meta content="en_US" property="og:locale:alternate"/>','\n<meta content="en_US" property="og:locale:alternate"/>',1))
 def test_wrong_duplicate_missing_ru_and_newline_shape_refuse(self):
  raw=self.ru_source();tag='<link rel="alternate" hreflang="ru" href="https://marsharbel.com/ru/fixture"/>'
  for bad in [self.source(),raw.replace('/ru/fixture','/ru/wrong'),raw.replace(tag,tag+tag),raw.replace(tag+'\n',tag+' '),raw.replace(tag+'\n',tag+'<!--comment-->\n')]:
   with self.subTest(raw=bad),self.assertRaises(ValueError):self.render(bad)
 def test_out_of_scope_families_keep_ru_whitespace(self):
  before=self.source();after=self.ru_source()
  for family in ('fixture','travel-zh-travel-master','travel-th-travel-master'):
   a,b=self.render(before,family),self.render(after,family)
   self.assertNotEqual(a,b)
if __name__=='__main__':unittest.main()
