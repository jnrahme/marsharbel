"""Help Me Pray release-gate tests (faith-desk reconciliation 2026-10-11).

These tests encode the desk's four engineering requirements. Until the
reconciled 12-locale catalogs land, they FAIL CLOSED by design: a draft PR
carrying this family cannot merge without real, complete catalogs.
"""
import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FAMILY = 'help-me-pray-master'
LOCALES = ['en', 'ar', 'fr', 'es', 'pt', 'it', 'de', 'pl', 'ru', 'hi', 'th', 'zh-Hans']
NEEDS = ['restart', 'family', 'illness', 'gratitude', 'discouragement', 'maronite']

PAGE_KEYS = {'title', 'intro', 'needsHeading', 'reviewNotice', 'pendingNotice', 'boundaryHeading', 'boundaryCopy', 'privacyCopy'}
CARD_KEYS = {'question', 'practicalAnswer', 'why', 'source.publisher', 'source.section', 'source.label',
             'practiceType', 'boundaryNote', 'prayerTarget.heading', 'prayerTarget.type', 'sourceAuthor'}
BEGGIANI = 'Chorbishop Seely Beggiani, A Guide to the Maronite Divine Liturgy, Eparchy of Saint Maron of Brooklyn'


def catalog_path(lang):
    return ROOT / 'locales' / lang / 'help-me-pray-catalog.json'


def load_catalog(lang):
    p = catalog_path(lang)
    if not p.exists():
        raise FileNotFoundError(f'missing catalog {p}')
    return json.loads(p.read_text())


class TestCatalogCompleteness(unittest.TestCase):
    """Requirement 2: a missing translation/catalog key must FAIL THE BUILD."""

    def test_all_12_locale_catalogs_exist(self):
        missing = [lang for lang in LOCALES if not catalog_path(lang).exists()]
        self.assertEqual(missing, [], f'catalogs missing for: {missing} (fail-closed until reconciled catalogs land)')

    def test_exact_key_set_no_holes_no_extras(self):
        for lang in LOCALES:
            try:
                cat = load_catalog(lang)
            except FileNotFoundError:
                self.skipTest(f'{lang} catalog not landed yet (covered by existence test)')
            page = cat.get('page', {})
            self.assertEqual(set(page), PAGE_KEYS, f'{lang}: page keys mismatch')
            self.assertEqual(set(cat.get('needs', {})), set(NEEDS), f'{lang}: needs mismatch')
            self.assertIn('cards', cat, f'{lang}: cards section missing (fail-closed until reconciled)')
            self.assertIn('ui', cat, f'{lang}: ui section missing')
            for need in NEEDS:
                for i, card in enumerate(cat.get('cards', {}).get(need, [])):
                    self.assertEqual(set(card), CARD_KEYS, f'{lang}/{need}[{i}]: card keys mismatch')

    def test_no_silent_english_fallback(self):
        en = load_catalog('en') if catalog_path('en').exists() else None
        if en is None:
            self.skipTest('en catalog not landed yet')
        en_text = json.dumps(en, ensure_ascii=False)
        for lang in LOCALES[1:]:
            try:
                cat = load_catalog(lang)
            except FileNotFoundError:
                continue
            self.assertNotEqual(json.dumps(cat, ensure_ascii=False), en_text,
                                f'{lang}: catalog identical to English (silent fallback)')

    def test_no_results_is_never_an_ordinary_empty_state(self):
        """noResults must be an explicit keyed string, never a bare empty render."""
        for lang in LOCALES:
            try:
                cat = load_catalog(lang)
            except FileNotFoundError:
                continue
            nr = cat.get('ui', {}).get('noResults')
            self.assertIsInstance(nr, str, f'{lang}: ui.noResults key required')
            self.assertGreater(len(nr.strip()), 20, f'{lang}: noResults must be real copy, not an empty-state stub')


class TestReviewNoticeSplit(unittest.TestCase):
    """Requirement 1: private reviewNotice and public pending-card notice are separate."""

    def test_private_notice_key_is_separate_and_never_in_public_render(self):
        try:
            en = load_catalog('en')
        except FileNotFoundError:
            self.skipTest('en catalog not landed yet')
        page = en['page']
        self.assertIn('reviewNotice', page)
        self.assertIn('pendingNotice', page, 'public pending-card notice must be its OWN key')
        self.assertNotEqual(page['reviewNotice'].strip(), page['pendingNotice'].strip(),
                            'private and public notices must not share copy')
        master = (ROOT / 'templates/masters/help-me-pray.html').read_text()
        built_public = master  # public render must never bind reviewNotice into a visible node
        self.assertNotIn(page['reviewNotice'].strip(), built_public,
                         'private reviewNotice wording leaked into the public master')


class TestPendingPrayerNotSerialized(unittest.TestCase):
    """Requirement 3: pending-card prayer text stays OUT of serialized browser data."""

    def test_no_prayer_text_in_serialized_payload(self):
        try:
            en = load_catalog('en')
        except FileNotFoundError:
            self.skipTest('en catalog not landed yet')
        data_file = ROOT / 'assets/help-me-pray-data.json'
        if not data_file.exists():
            return  # no serialized payload yet; when it exists it must be clean
        payload = data_file.read_text()
        for need in NEEDS:
            for card in en.get('cards', {}).get(need, []):
                if card.get('review', {}).get('status') != 'approved':
                    prayer = card.get('prayerTarget', {}).get('text')
                    if prayer:
                        self.assertNotIn(prayer, payload,
                                         f'pending card {card.get("id", need)} prayer text serialized to browser data')


class TestPublicExport(unittest.TestCase):
    """Independent-verdict copy gate: the public export must be deliberately clean."""

    EXPORT = ROOT / 'assets/help-me-pray-data.json'

    def test_public_export_exists_and_is_clean(self):
        self.assertTrue(self.EXPORT.exists(), 'public export not built yet (fail-closed until renderer lands)')
        raw = self.EXPORT.read_text()
        data = json.loads(raw)
        # pendingNotice survives the public export
        try:
            en = load_catalog('en')
            self.assertIn(en['page']['pendingNotice'], raw, 'pendingNotice dropped from public export')
        except FileNotFoundError:
            self.fail('en catalog missing')
        # nothing private reaches browser data
        for forbidden in ('reviewNotice', 'originalReview', 'privateProvenance', 'prayerText', 'quote'):
            self.assertNotIn(forbidden, raw, f'private field {forbidden} reached browser data')
        self.assertNotIn(en['page']['reviewNotice'], raw, 'reviewNotice wording reached browser data')
        # Begin is deliberately off in exported data
        self.assertIn('"beginEnabled": false', raw.replace(': false', ':false').replace('"beginEnabled":false', '"beginEnabled": false') if False else raw,
                      'beginEnabled=false must be present in exported data')
        # maronite-02 carries the deliberate localized public author citation
        cards = json.dumps(data, ensure_ascii=False)
        self.assertIn('maronite-02', cards, 'maronite-02 missing from export')
        self.assertIn('Beggiani', cards,
                      'maronite-02 public author citation dropped - must carry localized: ' + BEGGIANI)


class TestLocaleMasterDigest(unittest.TestCase):
    """Requirement 4: locale master carries a fresh digest + review records."""

    def test_master_digest_and_review_records(self):
        master_file = ROOT / 'locales/help-me-pray-locale-master.json'
        self.assertTrue(master_file.exists(), 'locale master not landed yet (fail-closed)')
        master = json.loads(master_file.read_text())
        self.assertIn('digest', master)
        self.assertIn('reviews', master)
        self.assertIn('internal-faith', master['reviews'])
        self.assertIn('locale', master['reviews'])
        body = json.dumps(master.get('catalogs', {}), ensure_ascii=False, sort_keys=True)
        self.assertEqual(master['digest'], hashlib.sha256(body.encode()).hexdigest(),
                         'locale master digest is stale - recompute after any catalog change')


if __name__ == '__main__':
    unittest.main()
