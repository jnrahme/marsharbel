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

    def approved(self,code):
        refs=json.loads((ROOT/'locales/travel-c0016-review-refs.json').read_text())
        record=refs[code+'/travel.html']
        stage=self.raw()
        labels=('Media','Music','Video','Galerie') if code=='de' else ('मीडिया','संगीत','वीडियो','चित्र संग्रह') if code=='hi' else ('Медиа','Музыка','Видео','Галерея (на английском)')
        raw=self.raw(labels)
        ev={**record,'stageRevision':m.STAGE,'preparedRevision':'a'*40}
        ev['candidateFileSha256']=m.sha(raw)
        v={'file':code+'/travel.html','path':'/'+code+'/travel','bodySha256':m.digest(raw),'candidateFileSha256':m.sha(raw),'reviewEvidence':ev}
        altered=copy.deepcopy(refs);altered[code+'/travel.html']['candidateFileSha256']=m.sha(raw)
        encoded=json.dumps(altered).encode()
        return stage,raw,v,encoded

    def test_positive_de_hi_ru_approved_mocked_blobs(self):
        for code in ('de','hi','ru'):
            stage,raw,v,encoded=self.approved(code)
            with self.subTest(code=code),patch.object(m,'blob',side_effect=lambda root,ref,file:stage if ref==m.STAGE else raw),patch.object(Path,'read_bytes',return_value=encoded),patch.object(m,'REVIEW_REFS_SHA256',m.hashlib.sha256(encoded).hexdigest()):
                self.assertEqual(m.validate_variant(ROOT,'travel-travel-master',code,v,raw)['state'],'approved')

    def test_table_tamper_and_approved_reference_drift(self):
        for code in ('de','hi','ru'):
            stage,raw,v,encoded=self.approved(code)
            for field,value in [('scope','invented'),('renderedReview','invented'),('catalogReview','invented'),('candidateFileSha256','f'*64)]:
                bad=copy.deepcopy(v);bad['reviewEvidence'][field]=value
                with self.subTest(code=code,field=field),patch.object(m,'blob',return_value=raw),patch.object(Path,'read_bytes',return_value=encoded),patch.object(m,'REVIEW_REFS_SHA256',m.hashlib.sha256(encoded).hexdigest()),self.assertRaises(ValueError):
                    m.validate_variant(ROOT,'travel-travel-master',code,bad,raw)
            with patch.object(m,'blob',return_value=raw),patch.object(Path,'read_bytes',return_value=encoded+b' '),patch.object(m,'REVIEW_REFS_SHA256',m.hashlib.sha256(encoded).hexdigest()),self.assertRaises(ValueError):
                m.validate_variant(ROOT,'travel-travel-master',code,v,raw)

    def test_missing_or_nonancestor_prepared_revision(self):
        import subprocess
        for ref in ('missing','a'*40):
            with patch.object(m.subprocess,'run',side_effect=subprocess.CalledProcessError(1,['git'])),self.assertRaises(ValueError):m.blob(ROOT,ref,'travel.html')

    def test_indented_en_line_and_nonisolated_or_double_refuse(self):
        raw,v=self.evidence();tag='<link rel="alternate" hreflang="ru" href="https://marsharbel.com/ru/travel"/>'
        old=raw.replace('</head>','\n</head>');new=old.replace('</head>','  '+tag+'\n</head>')
        v['candidateFileSha256']=m.sha(new);v['reviewEvidence']['candidateFileSha256']=m.sha(new)
        with patch.object(m,'blob',side_effect=lambda root,ref,file:old if ref==m.STAGE else new):
            m.validate_variant(ROOT,'travel-travel-master','en',v,new)
        for bad in [raw.replace('</head>',tag+'</head>'),new.replace(tag,tag+'\n'+tag)]:
            with self.assertRaises(ValueError):m.isolated_en_ru(bad,'travel')

    def test_group_laundering_schema_and_membership_refused(self):
        group={'evidenceSchema':'scoped-variants-v1','variants':{k:{} for k in ('en','de','ru','hi')}}
        m.validate_group('travel-travel-master',group)
        for key in ('renderedReviewStatus','catalogReview','renderedReview'):
            bad=copy.deepcopy(group);bad[key]='approved'
            with self.assertRaises(ValueError):m.validate_group('travel-travel-master',bad)
        for bad in [{'variants':group['variants']},{**group,'variants':{**group['variants'],'ar':{}}}]:
            with self.assertRaises(ValueError):m.validate_group('travel-travel-master',bad)
        with self.assertRaises(ValueError):m.validate_group('annaya-tour-travel-master',group)

    def test_both_reader_and_guard_call_shared_group_validation(self):
        for file in ('scripts/i18n/reviewed_travel.py','scripts/i18n/repin_ru_travel_release.py'):
            self.assertIn('validate_group(family,', (ROOT/file).read_text())

    def test_manifest_sets_source_revision_and_no_fabricated_checks(self):
        source=(ROOT/'scripts/i18n/reviewed_travel.py').read_text()
        self.assertIn("'sourceRevision': review['sourceRevision']",source)
        self.assertIn("page['variants'][code]['proof']=validate_variant",source)


if __name__=='__main__':unittest.main()
