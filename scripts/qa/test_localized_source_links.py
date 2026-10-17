"""Negative controls for the localized-source-links swap and its policy inverse."""
import sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from bs4 import BeautifulSoup
from i18n.localized_source_links import (apply_localized_source_links, resolve_family,
                                         scoped_mapping, strip_localized_source_links)
from i18n.mirror_structure import signature

USCCB = 'https://www.usccb.org/catechism/pt2sect2chpt4'
DE = 'https://www.vatican.va/archive/catechism_ge/p2s2c4a1_ge.htm'
FR = 'https://www.vatican.va/archive/catechism_fr/p2s2c4a1_fr.htm'
AR = 'https://www.vatican.va/archive/catechism_ar.pdf'


def page(*hrefs):
    links = ' '.join(f'<a href="{h}">Catechism</a>' for h in hrefs)
    return f'<html><body><main><p>Sources: {links}</p></main></body></html>'


def registry(de=True, fr=True, ar=False, other_family=False):
    links = {}
    if de: links['de'] = {USCCB: DE}
    if fr: links['fr'] = {USCCB: FR}
    if ar: links['ar'] = {USCCB: AR}
    fams = {'medal-family': {'master': 'medal.html',
                             'routes': {code: f'/{code}/medal' for code in links},
                             'sourceLinks': links}}
    if other_family:
        fams['other-family'] = {'master': 'other.html', 'routes': {'de': '/de/other'},
                                'sourceLinks': {'de': {'https://master2': 'https://locale2'}}}
    return {'pageMirrors': fams}


class ApplySide(unittest.TestCase):
    def test_swaps_exactly_one_anchor(self):
        out = apply_localized_source_links(page(USCCB), {USCCB: DE})
        self.assertIn(f'href="{DE}"', out)
        self.assertNotIn(USCCB, out)

    def test_missing_anchor_rejected(self):
        with self.assertRaises(ValueError):
            apply_localized_source_links(page('https://example.com'), {USCCB: DE})

    def test_duplicate_anchor_rejected(self):
        with self.assertRaises(ValueError):
            apply_localized_source_links(page(USCCB, USCCB), {USCCB: DE})

    def test_shared_locale_target_rejected(self):
        with self.assertRaises(ValueError):
            apply_localized_source_links(page(USCCB), {USCCB: DE, 'https://m2': DE})


class InverseSide(unittest.TestCase):
    def strip(self, html, lang, reg):
        return strip_localized_source_links(BeautifulSoup(html, 'html.parser'), reg, 'medal-family', lang)

    def test_reverts_registered_pair(self):
        out = self.strip(page(DE), 'de', registry())
        self.assertEqual(out.select_one('a')['href'], USCCB)

    def test_unregistered_anchors_untouched(self):
        out = self.strip(page(DE, 'https://example.com/x'), 'de', registry())
        hrefs = [a['href'] for a in out.select('a')]
        self.assertEqual(hrefs, [USCCB, 'https://example.com/x'])

    def test_missing_anchor_rejected(self):
        with self.assertRaises(ValueError):
            self.strip(page('https://example.com'), 'de', registry())

    def test_duplicate_locale_anchor_rejected(self):
        with self.assertRaises(ValueError):
            self.strip(page(DE, DE), 'de', registry())

    def test_wrong_locale_anchor_rejected(self):
        # de twin carrying the French edition's target: fail, never silently revert.
        with self.assertRaises(ValueError):
            self.strip(page(DE, FR), 'de', registry())

    def test_unregistered_family_target_rejected(self):
        with self.assertRaises(ValueError):
            self.strip(page(DE, 'https://locale2'), 'de', registry(other_family=True))

    def test_no_registry_wide_reversal(self):
        # Scrum's case: an ar page containing two German anchors. The old global
        # inverse silently reversed both; the scoped inverse must fail loudly.
        with self.assertRaises(ValueError):
            self.strip(page(AR, DE, DE), 'ar', registry(ar=True))

    def test_unmapped_locale_rejected(self):
        with self.assertRaises(ValueError):
            self.strip(page(USCCB), 'hi', registry())

    def test_signature_requires_context(self):
        with self.assertRaises(ValueError):
            signature(page(DE), '/de/medal', ('localized-source-links',))

    def test_signature_with_context_reverts(self):
        import json
        from unittest.mock import patch
        real = json.loads((ROOT / 'locales/registry.json').read_text())
        cfg = real['pageMirrors']['saint-charbel-medal-master']
        lang, mapping = next(iter(cfg['sourceLinks'].items()))
        locale_href = next(iter(mapping.values()))
        out = signature(page(locale_href), f'/{lang}/medal', ('localized-source-links',),
                        {'family': 'saint-charbel-medal-master', 'lang': lang})
        self.assertIsInstance(out, dict)


class PolicyIdentity(unittest.TestCase):
    def test_resolve_family_requires_exactly_one(self):
        reg = registry()
        self.assertEqual(resolve_family(reg, 'medal.html', '/de/medal', 'de'), 'medal-family')
        with self.assertRaises(ValueError):
            resolve_family(reg, 'medal.html', '/zz/medal', 'de')

    def test_scoped_mapping_requires_registration(self):
        with self.assertRaises(ValueError):
            scoped_mapping(registry(), 'medal-family', 'hi')
        with self.assertRaises(ValueError):
            scoped_mapping(registry(), 'ghost-family', 'de')


if __name__ == '__main__':
    unittest.main()
