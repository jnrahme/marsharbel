"""Rosary pairings are scoped to reviewed bytes, locales and routes."""
import copy
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from i18n.reviewed_rosary_books import rosary_books_manifest, SLUGS, LOCALES

class RosaryBooksPairing(unittest.TestCase):
    def setUp(self):
        self.record = json.loads((ROOT / 'locales/rosary-books-pairing.json').read_text())
        # Fixture approval only; never written to repo evidence.
        self.record['activationStatus'] = 'activated-pending-live-click'
        self.record['review']['evidenceRef'] = 'fixture-only'
        self.loads = json.loads

    def build(self, manifest=None, texts=None):
        def load(text, *a, **kw):
            if '"books"' in text and '"gateStatus"' in text:
                return copy.deepcopy(self.record)
            return self.loads(text, *a, **kw)
        with patch('i18n.reviewed_rosary_books.json.loads', side_effect=load):
            return rosary_books_manifest(ROOT, texts or {}, manifest or {'pages': {}})

    def test_pending_noop(self):
        self.record['activationStatus'] = 'pending-authorization'
        self.assertEqual(self.build(), {'pages': {}})

    def test_exact_membership(self):
        m = self.build()
        self.assertEqual(len(m['pages']), 20)
        for page in m['pages'].values():
            self.assertEqual(set(page['variants']), set(LOCALES))
            for variant in page['variants'].values():
                self.assertNotIn('nativeSampleReview', variant['proof'])
                self.assertEqual(variant['proof']['nativeReviewStatus'], 'not-certified')

    def test_body_drift_closed(self):
        file = ROOT / 'glorious-ascension.html'
        with self.assertRaisesRegex(ValueError, 'body drift'):
            self.build(texts={file: file.read_text().replace('<main', '<main data-drift="yes"', 1)})

    def test_catalog_drift_closed(self):
        self.record['books']['glorious-ascension']['variants']['ar']['catalogSha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'catalog drift'):
            self.build()

    def test_missing_artifact_closed(self):
        self.record['books']['glorious-ascension']['artifacts'].pop('content/books/glorious-ascension/book.json')
        with self.assertRaisesRegex(ValueError, 'artifacts incomplete'):
            self.build()

    def test_extra_locale_and_missing_family_closed(self):
        self.record['books']['glorious-ascension']['variants']['ru'] = {}
        with self.assertRaisesRegex(ValueError, 'locale membership drift'):
            self.build()
        del self.record['books']['glorious-ascension']
        with self.assertRaisesRegex(ValueError, 'review incomplete'):
            self.build()

    def test_no_reviewed_family_overwrite(self):
        seed = {'pages': {'existing': {'variants': {'en': {'path': '/joyful-annunciation', 'status': 'verified'}}}}}
        with self.assertRaisesRegex(ValueError, 'would replace reviewed'):
            self.build(seed)

    def test_false_completed_review_closed(self):
        self.record['review']['technicalReviewStatus'] = 'approved'
        with self.assertRaisesRegex(ValueError, 'review incomplete'):
            self.build()

    def test_wrong_authorization_identity_closed(self):
        self.record['review']['reviewer'] = 'Instinct main (model review)'
        with self.assertRaisesRegex(ValueError, 'review incomplete'):
            self.build()

    def test_missing_review_closed(self):
        self.record['review']['evidenceRef'] = ''
        with self.assertRaisesRegex(ValueError, 'review incomplete'):
            self.build()

class RosaryProvenancePolicy(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.expected = rosary_books_manifest(ROOT, {}, {'pages': {}})

    def test_exact_reviewer_occurrences_only(self):
        from i18n.manifest_policy import rosary_books_provenance
        count = rosary_books_provenance(ROOT, self.expected)
        reviewer = next(iter(self.expected['pages'].values()))['variants']['en']['proof']['reviewer']
        self.assertEqual(count, {reviewer: 160})

    def test_changed_proof_fails(self):
        from i18n.manifest_policy import rosary_books_provenance
        changed = copy.deepcopy(self.expected)
        key = next(iter(changed['pages']))
        changed['pages'][key]['variants']['ar']['proof']['reviewer'] += ' changed'
        with self.assertRaisesRegex(ValueError, 'differs from validated'):
            rosary_books_provenance(ROOT, changed)

    def test_missing_family_fails(self):
        from i18n.manifest_policy import rosary_books_provenance
        changed = copy.deepcopy(self.expected)
        changed['pages'].pop(next(iter(changed['pages'])))
        with self.assertRaisesRegex(ValueError, 'family membership'):
            rosary_books_provenance(ROOT, changed)

    def test_foreign_family_fails(self):
        from i18n.manifest_policy import rosary_books_provenance
        changed = copy.deepcopy(self.expected)
        changed['pages']['foreign-family'] = copy.deepcopy(next(iter(changed['pages'].values())))
        with self.assertRaisesRegex(ValueError, 'family membership'):
            rosary_books_provenance(ROOT, changed)

if __name__ == '__main__':
    unittest.main()
