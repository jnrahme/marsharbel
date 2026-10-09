"""Synthetic scoped-evidence refusal tests; runner supplies real git/build proof."""
import copy
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from i18n import travel_variant_evidence as m


class TravelVariantEvidenceTests(unittest.TestCase):
    def raw(self, labels=('Media','Music','Video','Gallery')):
        return '<html><head></head><body><header><div><nav>'+ '<div></div>'*5 + '<div><a href="/music">'+labels[0]+'</a><div>'+''.join('<a href="/'+href+'">'+label+'</a>' for href,label in zip(['music','videos','gallery'],labels[1:]))+'</div></div></nav></div></header><main><p>Original</p></main></body></html>'

    def test_exact_labels_and_hreflang_only(self):
        old=self.raw();new=self.raw(('Media','Music','Video','Galerie'))
        new=new.replace('</head>','<link href="https://marsharbel.com/ru/travel" hreflang="ru" rel="alternate"/></head>')
        m.label_delta(old,new,'de','travel')

    def test_body_other_attributes_label_and_metadata_refused(self):
        old=self.raw();new=self.raw(('Media','Music','Video','Galerie'))
        for bad in [new.replace('Original','Changed'),new.replace('/music','/other'),new.replace('Galerie','Other'),new.replace('</head>','<meta name="extra"/></head>')]:
            with self.assertRaises(ValueError):m.label_delta(old,bad,'de','travel')

    def test_wrong_and_duplicate_ru_hreflang_refused(self):
        tag='<link href="https://marsharbel.com/ru/travel" hreflang="ru" rel="alternate"/>'
        for tagvalue in [tag+tag,tag.replace('/ru/travel','/ru/other')]:
            with self.assertRaises(ValueError):m.without_ru(self.raw().replace('</head>',tagvalue+'</head>'),'travel')

    def evidence(self):
        raw=self.raw();ev={'stageRevision':m.STAGE,'preparedRevision':'a'*40,'candidateFileSha256':m.sha(raw),'state':'carried','scope':'stage bytes carried; no new review','nativeReviewStatus':'not-certified'}
        return raw,{'file':'travel.html','path':'/travel','candidateFileSha256':m.sha(raw),'bodySha256':'b'*64,'reviewEvidence':ev}

    def test_carried_actual_blob_equality_not_recorded_claim(self):
        raw,v=self.evidence()
        with patch.object(m,'blob',return_value=raw):
            self.assertEqual(m.validate_variant(ROOT,'travel-travel-master','en',v,raw)['state'],'carried')
        with patch.object(m,'blob',side_effect=[raw,raw.replace('Original','Changed')]):
            with self.assertRaises(ValueError):m.validate_variant(ROOT,'travel-travel-master','en',v,raw)

    def test_pending_native_hash_scope_and_extra_locale_refuse(self):
        raw,v=self.evidence()
        for key,value in [('state','pending'),('nativeReviewStatus','approved'),('candidateFileSha256','c'*64),('scope','new full review')]:
            bad=copy.deepcopy(v);bad['reviewEvidence'][key]=value
            with patch.object(m,'blob',return_value=raw),self.assertRaises(ValueError):m.validate_variant(ROOT,'travel-travel-master','en',bad,raw)
        with self.assertRaises(ValueError):m.validate_variant(ROOT,'travel-travel-master','ar',v,raw)

    def test_after_review_non_hreflang_bytes_refused(self):
        raw,v=self.evidence()
        with patch.object(m,'blob',return_value=raw),self.assertRaises(ValueError):m.validate_variant(ROOT,'travel-travel-master','en',v,raw.replace('Original','Changed'))

    def test_pinned_stage_and_carried_fake_review_refuse(self):
        raw,v=self.evidence()
        for key,value in [('stageRevision','d'*40),('renderedReview','fake')]:
            bad=copy.deepcopy(v);bad['reviewEvidence'][key]=value
            with patch.object(m,'blob',return_value=raw),self.assertRaises(ValueError):m.validate_variant(ROOT,'travel-travel-master','en',bad,raw)


if __name__=='__main__':unittest.main()
