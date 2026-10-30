"""Daily saint module source, provenance and paired book contract."""
import importlib.util,json,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('saintbuild',ROOT/'scripts/build_saint_of_day.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
def manifest():return json.loads((ROOT/'locales/saint-of-day.json').read_text())
class SaintDay(unittest.TestCase):
 def test_source_fresh(self):
  p,text=mod.output();self.assertEqual(p.read_text(),text)
 def test_locales_have_same_keys(self):
  en=json.loads((ROOT/'locales/en/saint-of-day.json').read_text())
  self.assertEqual(set(en),set(manifest()['entries']),'English copy dates must match the manifest window')
  for lang in json.loads((ROOT/'locales/registry.json').read_text())['homepageMirrors']['renderLocales']:
   local=json.loads((ROOT/f'locales/{lang}/saint-of-day.json').read_text())
   self.assertEqual(set(en),set(local),f'{lang} copy dates differ')
   for d in en:self.assertEqual(set(en[d]),set(local[d]),f'{lang} keys differ on {d}');self.assertTrue(all(v.strip() for v in local[d].values()))
 def test_sources_and_book_exist(self):
  m=manifest();self.assertEqual(m['timezone'],'America/New_York')
  for d,e in m['entries'].items():
   self.assertTrue(e['sources'],d);self.assertTrue(e['infoUrl'].startswith('https://'),d)
   if e.get('bookUrl'):
    self.assertTrue(e.get('bookImage'),d+' book is both or neither')
    self.assertNotIn('book',e,d+' book entry must not also carry "book": null')
    self.assertTrue((ROOT/(e['bookUrl'].strip('/')+'.html')).is_file(),d);self.assertTrue((ROOT/e['bookImage'].lstrip('/')).is_file(),d)
   else:
    self.assertIn('book',e,d+' no-book entry must carry explicit "book": null');self.assertIsNone(e['book'],d)
    self.assertFalse(e.get('bookImage'),d+' book is both or neither')
    if e.get('saintImage'): self.assertTrue((ROOT/e['saintImage'].lstrip('/')).is_file(),d+' saintImage file must exist')
 def test_section_and_ids(self):
  from bs4 import BeautifulSoup
  s=BeautifulSoup((ROOT/'index.html').read_text(),'html.parser')
  entries=manifest()['entries']
  sections=s.select('template[data-saint-date] #saint-of-the-day')
  self.assertEqual(len(sections),len(entries))
  for n in sections:
   d=n['data-saint-date']
   if entries[d].get('bookUrl'):
    self.assertEqual(len(n.select('.home-saint-pair > a')),2,d)
   else:
    self.assertEqual(len(n.select('.home-saint-pair')),0,d+' no-book renders no pair grid')
    self.assertEqual(len(n.select('a.home-saint-info')),1,d+' no-book renders the info card alone')
    if entries[d].get('saintImage'):
     self.assertEqual(len(n.select('img.home-saint-plate-img')),1,d+' image plate renders exactly one photo')
    else:
     self.assertEqual(len(n.select('img')),0,d+' no-book monogram/halo renders no image')
   self.assertIsNone(n.select_one('a a'))
 def test_date_is_generated_and_initial_state_fails_closed(self):
  from bs4 import BeautifulSoup
  from datetime import date
  m=manifest();s=BeautifulSoup((ROOT/'index.html').read_text(),'html.parser')
  templates=s.select('template[data-saint-date]')
  self.assertEqual(sorted(t['data-saint-date'] for t in templates),sorted(m['entries']))
  for t in templates:
   self.assertEqual(t.parent.name,'body');self.assertFalse(t.has_attr('hidden'))
   n=t.select_one('#saint-of-the-day');self.assertIsNotNone(n)
   self.assertEqual(''.join(str(c) for c in n.time.contents),date.fromisoformat(t['data-saint-date']).strftime('%d.%m.%Y'))
  en=json.loads((ROOT/'locales/en/saint-of-day.json').read_text())
  for d in en:self.assertNotIn('dateLabel',en[d])
 def test_missing_date_rejected(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp);(p/'locales').mkdir();(p/'locales/saint-of-day.json').write_text('{"entries":{"bad":{}}}')
   with self.assertRaises(ValueError):mod.output(p)
 def test_unsourced_entry_rejected(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp);(p/'locales').mkdir()
   (p/'locales/saint-of-day.json').write_text('{"entries":{"2026-10-15":{"saint":"x","calendar":"Maronite","infoUrl":"https://x","bookUrl":"/x","bookImage":"/x.jpg","sources":[],"translationStatus":"y"}}}')
   (p/'locales/en').mkdir();(p/'locales/en/saint-of-day.json').write_text('{"2026-10-15":{}}')
   with self.assertRaises(ValueError):mod.output(p)

class SaintDayBookContract(unittest.TestCase):
 def _root(self,tmp,entry,copy):
  p=Path(tmp)
  (p/'locales/en').mkdir(parents=True);(p/'templates/saint-of-day').mkdir(parents=True);(p/'src/pages').mkdir(parents=True)
  (p/'locales/saint-of-day.json').write_text(json.dumps({'timezone':'America/New_York','entries':{'2026-10-15':entry}}))
  (p/'locales/en/saint-of-day.json').write_text(json.dumps({'2026-10-15':copy}))
  (p/'templates/saint-of-day/home.html').write_text((ROOT/'templates/saint-of-day/home.html').read_text())
  (p/'templates/saint-of-day/home-nobook.html').write_text((ROOT/'templates/saint-of-day/home-nobook.html').read_text())
  (p/'templates/saint-of-day/home-nobook-mono.html').write_text((ROOT/'templates/saint-of-day/home-nobook-mono.html').read_text())
  (p/'templates/saint-of-day/home-nobook-image.html').write_text((ROOT/'templates/saint-of-day/home-nobook-image.html').read_text())
  (p/'src/pages/index.html').write_text('<!-- saint-of-day:start --><!-- saint-of-day:end -->')
  return p
 def _entry(self,**kw):
  e={'saint':'x','calendar':'Roman general','infoUrl':'https://x','sources':['https://x'],'translationStatus':'y'};e.update(kw);return e
 def _copy(self,**kw):
  c={'heading':'h','calendar':'c','name':'n','story':'s','provenance':'p','infoCta':'i','sourceLabel':'l'};c.update(kw);return c
 def test_book_null_renders_solo(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=self._root(tmp,self._entry(**{'book':None}),self._copy())
   _,text=mod.output(p)
   self.assertNotIn('<img',text);self.assertNotIn('home-saint-pair',text)
   self.assertIn('home-saint-plate',text,'solo card with derivable name renders the monogram plate')
   self.assertIn('data-saint-key="monogram">N<',text,'initial derived from the English name')
   self.assertIn('data-saint-key="dateShort">15 Oct<',text)
 def test_commemoration_is_text_only_without_saint_identity(self):
  with tempfile.TemporaryDirectory() as tmp:
   e=self._entry(kind='commemoration',commemoration='Faithful Departed',book=None);del e['saint']
   p=self._root(tmp,e,self._copy(heading='Commemoration',name='Commemoration of the Faithful Departed'))
   _,text=mod.output(p)
   self.assertNotIn('home-saint-plate',text);self.assertNotIn('home-saint-pair',text);self.assertNotIn('<img',text)
   self.assertIn('Commemoration of the Faithful Departed',text);self.assertIn('home-saint-info--text',text)
 def test_commemoration_rejects_invented_saint_book_or_art(self):
  for extra in ({'saint':'invented'},{'bookUrl':'/x','bookImage':'/x.jpg'},{'saintImage':'/x.jpg'}):
   with tempfile.TemporaryDirectory() as tmp:
    e=self._entry(kind='commemoration',commemoration='Faithful Departed',book=None);del e['saint'];e.update(extra)
    with self.assertRaises(ValueError):mod.output(self._root(tmp,e,self._copy()))
 def test_unknown_kind_and_missing_commemoration_rejected(self):
  for kind in ('commemoration','unexpected'):
   with tempfile.TemporaryDirectory() as tmp:
    e=self._entry(kind=kind,book=None);del e['saint']
    with self.assertRaises(ValueError):mod.output(self._root(tmp,e,self._copy()))
 def test_underivable_name_falls_back_to_halo(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=self._root(tmp,self._entry(**{'book':None}),self._copy(name='!!!'))
   _,text=mod.output(p)
   self.assertNotIn('home-saint-plate',text);self.assertIn('a class="home-news-lead home-saint-info"',text)
 def test_monogram_override_wins_in_render(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=self._root(tmp,self._entry(**{'book':None}),self._copy(monogram='Z'))
   _,text=mod.output(p)
   self.assertIn('data-saint-key="monogram">Z<',text)
 def test_saint_image_renders_photo_plate(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=self._root(tmp,self._entry(**{'book':None,'saintImage':'/x.jpg','saintImageSource':{'url':'https://commons.wikimedia.org/wiki/File:X.jpg','licence':'Public domain','credit':'Wikimedia Commons'}}),self._copy(imageAlt='a'))
   _,text=mod.output(p)
   self.assertIn('img class="home-saint-plate-img"',text);self.assertIn('src="/x.jpg"',text)
   self.assertNotIn('home-saint-plate-initial',text)
 def test_saint_image_without_alt_rejected(self):
  with tempfile.TemporaryDirectory() as tmp:
   with self.assertRaises(ValueError):mod.output(self._root(tmp,self._entry(**{'book':None,'saintImage':'/x.jpg'}),self._copy()))
 def test_saint_image_with_book_rejected(self):
  with tempfile.TemporaryDirectory() as tmp:
   with self.assertRaises(ValueError):mod.output(self._root(tmp,self._entry(bookUrl='/x-story',bookImage='/x.jpg',saintImage='/y.jpg'),self._copy(bookTitle='t',bookDek='d',bookCredit='c',bookCta='b',bookAlt='a',imageAlt='a')))
 def test_book_pair_renders_pair(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=self._root(tmp,self._entry(bookUrl='/x-story',bookImage='/x.jpg'),self._copy(bookTitle='t',bookDek='d',bookCredit='c',bookCta='b',bookAlt='a'))
   _,text=mod.output(p)
   self.assertIn('home-saint-pair',text);self.assertIn('<img',text)
 def test_xor_book_fields_rejected(self):
  for kw in ({'bookUrl':'/x-story'},{'bookImage':'/x.jpg'}):
   with tempfile.TemporaryDirectory() as tmp:
    with self.assertRaises(ValueError):mod.output(self._root(tmp,self._entry(**kw),self._copy()))
 def test_missing_book_without_null_rejected(self):
  with tempfile.TemporaryDirectory() as tmp:
   with self.assertRaises(ValueError):mod.output(self._root(tmp,self._entry(),self._copy()))
 def test_null_contradicting_book_fields_rejected(self):
  with tempfile.TemporaryDirectory() as tmp:
   with self.assertRaises(ValueError):mod.output(self._root(tmp,self._entry(bookUrl='/x-story',bookImage='/x.jpg',**{'book':None}),self._copy()))
