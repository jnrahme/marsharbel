"""Synthetic C-0016 repair refusals; no repository repin execution."""
import importlib.util
from pathlib import Path
import unittest
ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('ru_repin', ROOT/'scripts/i18n/repin_ru_travel_release.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)


class RuTravelRepinTests(unittest.TestCase):
    def test_scope_is_twelve_plus_seven(self):
        self.assertEqual(len(m.FAMILIES), 12)
        self.assertEqual(len(m.TARGET_FILES), 19)
        self.assertFalse(any('zh-' in x or 'th-' in x for x in m.FAMILIES))

    def source(self):
        return b'<html><head>\n<title>Same</title>\n</head><body><main>Body</main></body></html>'

    def target(self):
        return self.source().replace(b'</head>', b'<link rel="alternate" hreflang="ru" href="https://example.test/ru/travel">\n</head>')

    def test_hreflang_only_and_rerun(self):
        m.hreflang_delta(self.source(), self.target(), 'https://example.test/ru/travel')
        m.hreflang_delta(self.target(), self.target(), 'https://example.test/ru/travel')

    def test_body_metadata_and_wrong_route_refused(self):
        for raw in [self.target().replace(b'Body', b'Other'), self.target().replace(b'Same', b'Other'),
                    self.target().replace(b'/ru/travel', b'/ru/other'),
                    self.target().replace(b'hreflang="ru"', b'hreflang="th"')]:
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                m.hreflang_delta(self.source(), raw, 'https://example.test/ru/travel')

    def test_duplicate_hreflang_refused(self):
        raw = self.target().replace(b'</head>', b'<link rel="alternate" hreflang="ru" href="https://example.test/ru/travel">\n</head>')
        with self.assertRaises(ValueError):
            m.hreflang_delta(self.source(), raw, 'https://example.test/ru/travel')

    def test_nineteen_scope_only_preserves_other_assertions(self):
        before = 'prefix\n' + m.OLD_LIST + '\npending-five unchanged'
        after = m.bounded_test(before)
        self.assertEqual(after, before.replace(m.OLD_LIST, m.NEW_LIST))
        self.assertEqual(m.bounded_test(after), after)
        with self.assertRaises(ValueError):
            m.bounded_test(before + m.OLD_LIST)

    def test_path_scoped_pin_and_unknown_provenance(self):
        text = '{"variants":{"ru":{"catalogSha256":"'+'a'*64+'"}},"frozen":{"catalogSha256":"'+'a'*64+'"}}'
        updated = m.pin_text(text, ('variants','ru','catalogSha256'), 'a'*64, 'b'*64)
        self.assertEqual(updated, text.replace('a'*64, 'b'*64, 1))
        with self.assertRaises(ValueError):
            m.pin_text(text, ('variants','ru','catalogSha256'), 'c'*64, 'b'*64)
        with self.assertRaises(ValueError):
            m.pin_text(text, ('variants','de','catalogSha256'), 'a'*64, 'b'*64)


if __name__ == '__main__':
    unittest.main()
