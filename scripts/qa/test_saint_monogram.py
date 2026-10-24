"""Saint plate monogram derivation: titles per locale, Arabic article, override, fallback."""
import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from i18n.saint_plate import saint_image_rejection, derive_monogram,date_short,plate_fields

class Derivation(unittest.TestCase):
 def test_titles_stripped_per_locale(self):
  cases=[
   ('Saint Teresa of Jesus (Avila)','en','T'),('St. Jude','en','J'),('Blessed Carlo Acutis','en','C'),
   ('Bl. Pier Giorgio Frassati','en','P'),('Pope Saint John Paul II','en','J'),
   ('Venerable Anne','en','A'),('Ven. Anne','en','A'),('Servant of God Maria','en','M'),
   ('Heiliger Judas Thaddäus, Apostel','de','J'),('Heilige Hedwig von Schlesien','de','H'),('Selige Anna','de','A'),
   ('Sainte Thérèse de Jésus','fr','T'),('Bienheureux Charles','fr','C'),
   ('Santa Teresa de Jesús','es','T'),('San Juan','es','J'),('Beata María','es','M'),
   ('Santa Chiara','it','C'),('São Francisco','pt','F'),('Santo António','pt','A'),
   ('Święta Jadwiga','pl','J'),('Błogosławiony Karol','pl','K'),
   ('Святой Иуда, апостол','ru','И'),('Святая Тереза от Иисуса (Авила)','ru','Т'),('Блаженный Августин','ru','А'),
   ('संत तेरेसा ऑफ जीसस (आविला)','hi','त'),('นักบุญเทเรซาแห่งเยซู (อาวิลา)','th','ท'),
  ]
  for name,lang,want in cases:
   with self.subTest(lang=lang,name=name): self.assertEqual(derive_monogram(name,lang),want)
 def test_arabic_article_and_tashkeel_stripped(self):
  self.assertEqual(derive_monogram('القديسة تريزا من يسوع (آفيلا)','ar'),'ت')
  self.assertEqual(derive_monogram('القديس شربل','ar'),'ش')
  self.assertEqual(derive_monogram('الطوباوي يعقوب الكبازي','ar'),'ي')
  self.assertEqual(derive_monogram('القديسة رفقا','ar'),'ر')
  self.assertEqual(derive_monogram('شَرْبَل','ar'),'ش')
 def test_thai_preposed_vowel_skipped(self):
  self.assertEqual(derive_monogram('นักบุญเทเรซา','th'),'ท')
  self.assertEqual(derive_monogram('นักบุญยูดา','th'),'ย')
 def test_override_wins(self):
  self.assertEqual(derive_monogram('Saint Thomas','ar',override='ت'),'ت')
  self.assertEqual(derive_monogram('Anything','en',override='Z'),'Z')
  self.assertEqual(derive_monogram('Saint Jude','en',override=' '),'J')
 def test_fallback_when_nothing_derivable(self):
  self.assertIsNone(derive_monogram('!!!','en'))
  self.assertIsNone(derive_monogram('','en'))
  self.assertIsNone(derive_monogram('123','fr'))
  self.assertIsNone(plate_fields('!!!','en','2026-10-15'))
 def test_uppercase_stays_single_glyph(self):
  self.assertEqual(derive_monogram('hedwig','en'),'H')
  self.assertEqual(derive_monogram('ñandú','es'),'Ñ')

class DateShort(unittest.TestCase):
 def test_formats(self):
  self.assertEqual(date_short('2026-10-15','en'),'15 Oct')
  self.assertEqual(date_short('2026-10-15','ar'),'15 تشرين الأول')
  self.assertEqual(date_short('2026-01-05','de'),'5. Jan.')
  self.assertEqual(date_short('2026-03-22','ru'),'22 мар.')
  self.assertEqual(date_short('2026-12-25','th'),'25 ธ.ค.')
  self.assertEqual(date_short('2026-02-14','pl'),'14 lut')
  self.assertEqual(date_short('2026-07-04','fr'),'4 juil.')
 def test_no_year_anywhere(self):
  for lang in ('en','ar','fr','es','pt','it','de','pl','ru','hi','th'):
   with self.subTest(lang=lang): self.assertNotIn('2026',date_short('2026-10-15',lang))
 def test_unknown_locale_falls_back_to_en_months(self):
  self.assertEqual(date_short('2026-10-15','xx'),'15 Oct')


class SaintImageGate(unittest.TestCase):
 def test_book_illustration_path_rejected(self):
  e={'saintImage':'/media/storybook-jude/images/page-01.jpg','saintImageSource':{'url':'https://example.com','licence':'CC0','credit':'X'}}
  self.assertIsNotNone(saint_image_rejection(e))
 def test_missing_credit_rejected(self):
  e={'saintImage':'/media/saints/teresa-avila.jpg','saintImageSource':{'url':'https://commons.wikimedia.org/x','licence':'Public domain','credit':''}}
  self.assertIsNotNone(saint_image_rejection(e))
 def test_missing_source_record_rejected(self):
  e={'saintImage':'/media/saints/teresa-avila.jpg'}
  self.assertIsNotNone(saint_image_rejection(e))
 def test_valid_photo_accepted(self):
  e={'saintImage':'/media/saints/teresa-avila.jpg','saintImageSource':{'url':'https://commons.wikimedia.org/wiki/File:Teresa_of_Avila.jpg','licence':'Public domain','credit':'Wikimedia Commons'}}
  self.assertIsNone(saint_image_rejection(e))

if __name__=='__main__': unittest.main()
