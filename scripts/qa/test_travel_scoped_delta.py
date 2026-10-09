"""Synthetic acceptance and strict refusals, actual classifier path."""
import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from i18n.travel_scoped_delta import classified_delta
class ScopedDeltaTests(unittest.TestCase):
 def source(self):
  return '<html><head><title>Same</title></head><body><header><div><nav>'+('<div>x</div>'*5)+'<div><a href="/media">Media</a><a href="/music">Music</a><a href="/video">Video<span class="launch-english-qualifier"> (English)</span></a><a href="/gallery">Gallery</a></div></nav></div></header><main>Body</main></body></html>'
 def target(self):
  return self.source().replace('</head>','<link href="https://marsharbel.com/ru/travel" hreflang="ru" rel="alternate" /></head>').replace('>Gallery<','>Galerie<')
 def pairs(self):return [('Media','Media'),('Music','Music'),('Video','Video'),('Gallery','Galerie')]
 def test_single_line_head_parsed_accept_and_idempotence(self):
  classified_delta(self.source(),self.target(),'travel',self.pairs())
  classified_delta(self.target(),self.target(),'travel',self.pairs())
 def test_off_table_href_body_missing_ru_and_qualifier_refuse(self):
  for bad in [self.target().replace('Galerie','Other'),self.target().replace('/gallery','/other'),self.target().replace('Body','More'),self.source().replace('Gallery','Galerie'),self.target().replace('(English)','(Other)'),self.target().replace('hreflang="ru"','hreflang="ru" data-extra="x"')]:
   with self.subTest(bad=bad),self.assertRaises(ValueError):classified_delta(self.source(),bad,'travel',self.pairs())
if __name__=='__main__':unittest.main()
