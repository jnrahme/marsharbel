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

class RosarySuccessorReview(unittest.TestCase):
    """Synthetic receipts exercise integrity only, never assert real review."""
    def setUp(self):
        from i18n.rosary_successor_review import sha256, SCHEMA, SCOPE
        self.record = {'schema': SCHEMA, 'scope': SCOPE,
            'nativeReviewStatus': 'not-certified', 'activationStatus': 'unpublished',
            'previousPairingSha256': sha256(ROOT / 'locales/rosary-books-pairing.json'),
            'reviews': {}}
        for loc in LOCALES:
            self.record['reviews'][loc] = {'status': 'agent-reviewed',
                'producer': 'fixture-producer', 'reviewer': 'fixture-reviewer',
                'evidenceRef': 'fixture-only-not-a-real-review', 'books': {}}
            for slug in SLUGS:
                paths = [f'content/books/{slug}/{loc}.json',
                         f'locales/{loc}/{slug}-master-copy.json',
                         f'content/books/{slug}/book.json']
                self.record['reviews'][loc]['books'][slug] = {
                    'englishSourceSha256': sha256(ROOT / f'content/books/{slug}/en.json'),
                    'artifacts': {p: sha256(ROOT / p) for p in paths}}

    def check(self):
        from i18n.rosary_successor_review import validate_successor_review
        return validate_successor_review(ROOT, self.record)

    def test_complete_integrity_is_still_unpublished(self):
        self.assertEqual(self.check()['reviewedEditions'], 160)
        self.assertEqual(self.check()['activationStatus'], 'unpublished')

    def test_missing_locale_rejected(self):
        del self.record['reviews']['ar']
        with self.assertRaisesRegex(ValueError, 'locale membership'):
            self.check()

    def test_held_locale_rejected(self):
        self.record['reviews']['ru'] = self.record['reviews']['ar']
        with self.assertRaisesRegex(ValueError, 'locale membership'):
            self.check()

    def test_missing_book_rejected(self):
        del self.record['reviews']['ar']['books'][SLUGS[0]]
        with self.assertRaisesRegex(ValueError, 'book membership'):
            self.check()

    def test_changed_text_or_prayer_invalidates_receipt(self):
        row = self.record['reviews']['ar']['books'][SLUGS[0]]
        row['artifacts'][f'content/books/{SLUGS[0]}/ar.json'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'artifact drift'):
            self.check()

    def test_changed_english_source_invalidates_locale_review(self):
        self.record['reviews']['ar']['books'][SLUGS[0]]['englishSourceSha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'English review source drift'):
            self.check()

    def test_prior_history_cannot_be_resealed(self):
        self.record['previousPairingSha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'history drift'):
            self.check()

    def test_self_review_rejected(self):
        self.record['reviews']['ar']['reviewer'] = 'fixture-producer'
        with self.assertRaisesRegex(ValueError, 'Independent review incomplete'):
            self.check()

    def test_activation_or_native_claim_rejected(self):
        self.record['activationStatus'] = 'activated'
        with self.assertRaisesRegex(ValueError, 'cannot activate'):
            self.check()
        self.record['activationStatus'] = 'unpublished'
        self.record['nativeReviewStatus'] = 'certified'
        with self.assertRaisesRegex(ValueError, 'Native certification'):
            self.check()

    def test_unrelated_artifact_rejected(self):
        self.record['reviews']['ar']['books'][SLUGS[0]]['artifacts']['../private'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'artifact coverage'):
            self.check()

class RosarySuccessorAdapter(unittest.TestCase):
    def setUp(self):
        import tempfile
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.output = Path(self.tmp.name) / 'staged'
        self.master = (ROOT / 'docs/rosary-successor/twenty-en-candidates-v3.json').read_bytes()
        self.spec = json.loads((ROOT / 'docs/rosary-successor/integration-spec-v1.json').read_text())

    def build(self):
        from i18n.rosary_successor_adapter import build_successor
        return build_successor(ROOT, self.spec, self.master, self.output)

    def test_exact_all_books_stage_168_pages_without_runtime_change(self):
        before = (ROOT / 'content/books/joyful-annunciation/en.json').read_bytes()
        self.assertEqual(self.build()['pages'], 168)
        self.assertEqual(before, (ROOT / 'content/books/joyful-annunciation/en.json').read_bytes())
        book = json.loads((self.output / 'content/books/joyful-annunciation/book.json').read_text())
        self.assertEqual(book['status'], 'draft')
        self.assertTrue(all(p['kind'] in ('story', 'reflection') for p in book['pages']))
        self.assertTrue(all(not p['audio'] for p in book['pages']))

    def test_changed_manuscript_fails(self):
        self.master += b' '
        with self.assertRaisesRegex(ValueError, 'manuscript bytes'):
            self.build()
        self.assertFalse(self.output.exists())

    def test_changed_prayer_fails_before_any_write(self):
        self.spec['books'][0]['reader_pages'][-1]['paragraphs'][0] += ' changed'
        with self.assertRaisesRegex(ValueError, 'Prayer text'):
            self.build()
        self.assertFalse(self.output.exists())

    def test_missing_movement_fails_before_any_write(self):
        self.spec['books'][0]['reader_pages'][0]['paragraphs'].pop()
        with self.assertRaisesRegex(ValueError, 'Missing, duplicated'):
            self.build()
        self.assertFalse(self.output.exists())

    def test_duplicate_id_fails(self):
        pages = self.spec['books'][0]['reader_pages']
        pages[1]['id'] = pages[0]['id']
        with self.assertRaisesRegex(ValueError, 'Semantic page ID'):
            self.build()

    def test_runtime_output_rejected(self):
        self.output = ROOT / 'content'
        with self.assertRaisesRegex(ValueError, 'outside the runtime'):
            self.build()

    def test_existing_staging_is_not_overwritten(self):
        self.build()
        with self.assertRaisesRegex(ValueError, 'Refusing to overwrite'):
            self.build()

if __name__ == '__main__':
    unittest.main()
