"""Synthetic acceptance and strict refusals, actual classifier path."""
import sys
from pathlib import Path
import unittest
import tempfile
import hashlib
import json
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from i18n.travel_scoped_delta import classified_delta, scoped_delta
from i18n import travel_variant_evidence as evidence
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
 def test_scoped_delta_pinned_refs_and_candidate_refusals(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);path=root/'locales/travel-c0016-review-refs.json';path.parent.mkdir()
   candidate=self.source().replace('>Gallery<','>Galerie<')
   digest=hashlib.sha256(candidate.encode()).hexdigest()
   record={'candidateFileSha256':digest,'scope':evidence.SCOPED}
   raw=json.dumps({'de/travel.html':record}).encode();path.write_bytes(raw)
   variant={'reviewEvidence':{'preparedRevision':'b'*40,'candidateFileSha256':digest}}
   def blob(r,ref,file):return self.source() if ref==evidence.STAGE else candidate
   with patch.object(evidence,'REVIEW_REFS_SHA256',hashlib.sha256(raw).hexdigest()),patch.object(evidence,'blob',side_effect=blob):
    scoped_delta(root,self.source().encode(),self.target().encode(),'de','travel',variant)
    path.write_bytes(raw+b' ')
    with self.assertRaisesRegex(ValueError,'Reviewer table edited'):
     scoped_delta(root,self.source().encode(),self.target().encode(),'de','travel',variant)
    path.write_bytes(raw)
    with patch.object(evidence,'blob',side_effect=lambda r,ref,file:self.source()):
     with self.assertRaisesRegex(ValueError,'Label table source not pinned'):
      scoped_delta(root,self.source().encode(),self.target().encode(),'de','travel',variant)
    with self.assertRaisesRegex(ValueError,'Unreviewed label scope'):
     scoped_delta(root,self.source().encode(),self.target().encode(),'hi','travel',variant)
if __name__=='__main__':unittest.main()
