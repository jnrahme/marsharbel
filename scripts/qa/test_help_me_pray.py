"""Help Me Pray release-gate tests (faith-desk reconciliation + quality verdicts).

Runtime catalogs are the PUBLIC-REPO projection: private fields (reviewNotice,
originalReview, privateProvenance*, prayer words) are stripped at projection time.
These tests guard the publicationContract: missing locale/key fails the build,
no English fallback, nothing private reaches browser data, Begin stays off.
"""
import hashlib
import json

NEED_KEY_MAP = {
    'beginning/restarting prayer': 'restart',
    'family': 'family',
    'illness': 'illness',
    'gratitude': 'gratitude',
    'discouragement in prayer': 'discouragement',
    'understanding Maronite practice': 'maronite',
}

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LOCALES = ['en', 'ar', 'fr', 'es', 'pt', 'it', 'de', 'pl', 'ru', 'hi', 'th', 'zh-Hans']
NEEDS = ['restart', 'family', 'illness', 'gratitude', 'discouragement', 'maronite']
CARD_IDS = ['restart-01', 'restart-02', 'family-01', 'family-02', 'illness-01', 'illness-02',
            'gratitude-01', 'gratitude-02', 'discouragement-01', 'discouragement-02',
            'maronite-01', 'maronite-02']
PAGE_KEYS = {'title', 'intro', 'needsHeading', 'pendingNotice', 'boundaryHeading', 'boundaryCopy', 'privacyCopy'}
UI_KEYS = {'inReview', 'practicalAnswer', 'why', 'source', 'practiceType', 'boundary',
           'backToNeeds', 'noResults', 'notReady', 'begin', 'close', 'readMore'}
COPY_KEYS = {'question', 'practicalAnswer', 'why', 'source.publisher', 'source.section', 'source.label',
             'practiceType', 'boundaryNote', 'prayerTarget.heading', 'prayerTarget.type'}
CARD_META = {'need', 'copy', 'sourceURL', 'prayerTargetURL', 'additionalSourceURLs', 'beginEnabled'}
PRIVATE_TOKENS = ['reviewNotice', 'originalReview', 'privateProvenance', 'private-review',
                  'This guide is a private draft']
BEGGIANI = 'Chorbishop Seely Beggiani'


def load_catalog(lang):
    return json.loads((ROOT / 'locales' / lang / 'help-me-pray-catalog.json').read_text())


class TestCatalogCompleteness(unittest.TestCase):
    """publicationContract: missingLocaleOrKey=fail-build, englishFallback=false."""

    def test_all_12_locale_catalogs_exist(self):
        missing = [l for l in LOCALES if not (ROOT / 'locales' / l / 'help-me-pray-catalog.json').exists()]
        self.assertEqual(missing, [])

    def test_exact_structure_per_locale(self):
        for lang in LOCALES:
            cat = load_catalog(lang)
            extra = set(cat['page']) - PAGE_KEYS
            if lang == 'ru':
                self.assertEqual(extra, {'languageReviewNotice'}, 'ru page keys: only the deliberate RU-only allowlist key may be extra')
            else:
                self.assertEqual(extra, set(), f'{lang} page keys')
            self.assertEqual(set(cat['needs']), set(NEEDS), f'{lang} needs')
            self.assertEqual(set(cat['ui']), UI_KEYS, f'{lang} ui keys')
            self.assertEqual(set(cat['cards']), set(CARD_IDS), f'{lang} card ids')
            for cid in CARD_IDS:
                card = cat['cards'][cid]
                expected_meta = CARD_META | ({'sourceAuthor'} if cid == 'maronite-02' else set())
                self.assertEqual(set(card), expected_meta, f'{lang}/{cid} card keys')
                self.assertEqual(set(card['copy']), COPY_KEYS, f'{lang}/{cid} copy keys')
                self.assertIs(card['beginEnabled'], False, f'{lang}/{cid} Begin must stay OFF')
                self.assertIn(card['need'], NEED_KEY_MAP, f'{lang}/{cid} need unmapped: {card["need"]!r}')

    def test_no_silent_english_fallback(self):
        en_page = json.dumps(load_catalog('en')['page'], ensure_ascii=False, sort_keys=True)
        for lang in LOCALES[1:]:
            cat = load_catalog(lang)
            self.assertNotEqual(json.dumps(cat['page'], ensure_ascii=False, sort_keys=True), en_page,
                                f'{lang}: page identical to English')

    def test_no_results_is_real_copy(self):
        for lang in LOCALES:
            nr = load_catalog(lang)['ui']['noResults']
            self.assertGreater(len(nr.strip()), 10, f'{lang}: noResults must be real keyed copy')


class TestNothingPrivateInRepoRuntime(unittest.TestCase):
    """Quality's allowlist: private fields are stripped before the public repo."""

    def test_runtime_catalogs_carry_no_private_tokens(self):
        for lang in LOCALES:
            raw = (ROOT / 'locales' / lang / 'help-me-pray-catalog.json').read_text()
            for token in PRIVATE_TOKENS:
                self.assertNotIn(token, raw, f'{lang}: private token {token!r} in runtime catalog')

    def test_master_never_binds_private_wording(self):
        master = (ROOT / 'help-me-pray.html').read_text()
        for token in PRIVATE_TOKENS:
            self.assertNotIn(token, master, f'private token {token!r} in public master')

    def test_maronite02_public_author_citation(self):
        for lang in LOCALES:
            card = load_catalog(lang)['cards']['maronite-02']
            self.assertEqual(card.get('sourceAuthor'), BEGGIANI, f'{lang}: maronite-02 citation')
            self.assertTrue(card['copy']['source.label'].strip(), f'{lang}: PARAPHRASE label localized')


class TestPublicExport(unittest.TestCase):
    """The browser payload must be a clean positive-allowlist projection."""

    EXPORT = ROOT / 'assets/help-me-pray-data.json'

    def test_public_export_exists_and_is_clean(self):
        self.assertTrue(self.EXPORT.exists(), 'public export not built (run scripts/i18n/help_me_pray_export.py)')
        raw = self.EXPORT.read_text()
        data = json.loads(raw)
        en = load_catalog('en')
        parsed = json.loads(raw)
        for lang in LOCALES:
            self.assertEqual(parsed[lang]['page']['pendingNotice'],
                             json.loads((ROOT / f'locales/{lang}/help-me-pray-catalog.json').read_text())['page']['pendingNotice'],
                             f'{lang}: pendingNotice dropped or altered in public export')
            for cid, card in parsed[lang]['cards'].items():
                self.assertIn(card['needKey'], NEEDS, f'{lang}/{cid} needKey')
                self.assertFalse(card['beginEnabled'], f'{lang}/{cid} beginEnabled')
        for token in PRIVATE_TOKENS + ['prayerText', '"quote"']:
            self.assertNotIn(token, raw, f'{token!r} reached browser data')
        self.assertIn('"beginEnabled": false', raw, 'beginEnabled=false must be present per card')
        self.assertNotIn('"beginEnabled": true', raw, 'a card has Begin ON - forbidden before release gates')
        self.assertIn(BEGGIANI, raw, 'maronite-02 Beggiani citation dropped from export')

    def test_no_prayer_body_text_in_export(self):
        if not self.EXPORT.exists():
            self.skipTest('export not built yet')
        raw = self.EXPORT.read_text()
        for pf in (ROOT / 'locales').glob('*/help-me-pray-prayers.json'):
            for row in json.loads(pf.read_text())['rows']:
                self.assertNotIn(row['text'], raw,
                                 f'{pf.parent.name}:{row["prayer"]} body text reached browser data (pendingPrayerTextInBrowserData=false)')


class TestLocaleMasterDigest(unittest.TestCase):
    """Locale master carries a fresh digest + review records over landed content."""

    def test_master_digest_and_review_records(self):
        master = json.loads((ROOT / 'locales/help-me-pray-locale-master.json').read_text())
        self.assertIn('internal-faith', master['reviews'])
        self.assertIn('locale', master['reviews'])
        body = json.dumps(master.get('catalogs', {}), ensure_ascii=False, sort_keys=True)
        self.assertEqual(master['digest'], hashlib.sha256(body.encode()).hexdigest(),
                         'locale master digest stale - rerun the digest step after content changes')

    def test_no_english_need_label_in_non_en_renders(self):
        """Rendered locale pages show localized need labels, never the English ones."""
        en_needs = json.loads((ROOT / 'locales/en/help-me-pray-catalog.json').read_text())['needs']
        registry = json.loads((ROOT / 'locales/registry.json').read_text())
        fam = registry['pageMirrors']['help-me-pray-master']
        for lang in fam['renderLocales']:
            if lang == 'en':
                continue
            page = (ROOT / lang / 'help-me-pray.html').read_text()
            cat = json.loads((ROOT / f'locales/{lang}/help-me-pray-catalog.json').read_text())
            for key, label in cat['needs'].items():
                self.assertIn(label, page, f'{lang}: localized need label {key} missing from render')
            for key, en_label in en_needs.items():
                if en_label not in cat['needs'].values():
                    self.assertNotIn(en_label, page, f'{lang}: English need label {key} leaked into render')

    def test_export_needkey_resolves_in_needs(self):
        """Every exported card needKey resolves to a non-empty localized label; fail-closed contract."""
        payload = json.loads((ROOT / 'assets/help-me-pray-data.json').read_text())
        for lang in LOCALES:
            needs = payload[lang]['needs']
            self.assertEqual(set(needs), set(NEEDS), f'{lang}: needs keys')
            for key, label in needs.items():
                self.assertIsInstance(label, str) ; self.assertTrue(label.strip(), f'{lang}/{key} empty label')
            for cid, card in payload[lang]['cards'].items():
                self.assertIn(card['needKey'], needs, f'{lang}/{cid}: needKey has no label')

    def test_card_need_mapping_stable(self):
        """Card-to-needKey mapping is identical across all 12 locales (desk contract)."""
        mapping = None
        for lang in LOCALES:
            cat = json.loads((ROOT / f'locales/{lang}/help-me-pray-catalog.json').read_text())
            current = {cid: NEED_KEY_MAP[c['need']] for cid, c in cat['cards'].items()}
            if mapping is None:
                mapping = current
            else:
                self.assertEqual(mapping, current, f'{lang}: card->needKey mapping drift')

    def test_language_review_notice_ru_only(self):
        """languageReviewNotice: deliberate RU-only allowlist; no global key, no English gloss."""
        NOTICE = 'Русский текст пока не проверен носителем русского языка.'
        GLOSS = 'The Russian wording has not yet been reviewed'
        payload = json.loads((ROOT / 'assets/help-me-pray-data.json').read_text())
        for lang in LOCALES:
            cat = json.loads((ROOT / f'locales/{lang}/help-me-pray-catalog.json').read_text())
            if lang == 'ru':
                self.assertEqual(cat['page'].get('languageReviewNotice'), NOTICE)
                self.assertEqual(payload['ru']['page'].get('languageReviewNotice'), NOTICE,
                                 'notice must survive the public export')
            else:
                self.assertNotIn('languageReviewNotice', cat['page'], f'{lang}: global key expansion')
                self.assertNotIn('languageReviewNotice', payload[lang]['page'], f'{lang}: notice leaked into export')
            self.assertNotIn(GLOSS, json.dumps(payload[lang], ensure_ascii=False), f'{lang}: English gloss in browser data')
        for render in ROOT.glob('*/help-me-pray.html'):
            self.assertNotIn(GLOSS, render.read_text(), f'{render}: English gloss in render')
            if render.parts[0] != 'ru':
                self.assertNotIn(NOTICE, render.read_text(), f'{render}: RU notice in non-RU static render')


if __name__ == '__main__':
    unittest.main()
