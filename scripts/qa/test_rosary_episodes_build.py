#!/usr/bin/env python3
"""Behavior tests for scripts/build_rosary_episodes.py (content layer PR 1B)."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
import build_rosary_episodes as builder  # noqa: E402

REAL = json.loads((ROOT / 'content' / 'rosary' / 'episodes.json').read_text())


def registry(episodes):
    return {'schema': 1, 'episodes': episodes}


def episode(**over):
    base = {
        'date': '2026-11-18',
        'mystery': 'glorious',
        'language': 'en',
        'youtubeId': 'KBLRatggtPo',
        'title': 'A real episode title',
    }
    base.update(over)
    return base


class RegistryValidationTests(unittest.TestCase):
    def load(self, data):
        with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False) as f:
            json.dump(data, f)
            path = Path(f.name)
        return builder.load_episodes(path)

    def test_real_registry_validates(self):
        episodes = self.load(REAL)
        self.assertEqual(len(episodes), 3)

    def test_missing_required_field_rejected(self):
        ep = episode()
        del ep['title']
        with self.assertRaises(ValueError):
            self.load(registry([ep]))

    def test_unknown_field_rejected(self):
        with self.assertRaises(ValueError):
            self.load(registry([episode(channelUrl='https://x.example')]))

    def test_bad_youtube_id_rejected(self):
        for bad in ('short', 'KBLRatggtPo?', 'KBLRatggtPo\n', 'x' * 12):
            with self.assertRaises(ValueError, msg=bad):
                self.load(registry([episode(youtubeId=bad)]))

    def test_bad_date_rejected(self):
        for bad in ('18-11-2026', '2026-13-01', '2026-02-30', 'yesterday'):
            with self.assertRaises(ValueError, msg=bad):
                self.load(registry([episode(date=bad)]))

    def test_bad_mystery_rejected(self):
        with self.assertRaises(ValueError):
            self.load(registry([episode(mystery='joyful2')]))

    def test_bad_language_rejected(self):
        for bad in ('EN', 'english', 'e1'):
            with self.assertRaises(ValueError, msg=bad):
                self.load(registry([episode(language=bad)]))

    def test_wrong_schema_version_rejected(self):
        with self.assertRaises(ValueError):
            self.load({'schema': 2, 'episodes': []})


class RenderTests(unittest.TestCase):
    def test_newest_first_deterministic(self):
        eps = [
            episode(date='2026-10-18', youtubeId='AAAAAAAAAAA'),
            episode(date='2026-11-18', youtubeId='BBBBBBBBBBB'),
            episode(date='2026-11-16', language='ar', youtubeId='CCCCCCCCCCC'),
        ]
        out = builder.render(eps)
        self.assertLess(out.index('BBBBBBBBBBB'), out.index('CCCCCCCCCCC'))
        self.assertLess(out.index('CCCCCCCCCCC'), out.index('AAAAAAAAAAA'))
        self.assertEqual(out, builder.render(eps))

    def test_html_injection_escaped(self):
        out = builder.render([episode(title='<script>alert(1)</script>&"x"')])
        self.assertNotIn('<script>alert', out)
        self.assertIn('&lt;script&gt;', out)
        self.assertIn('&quot;x&quot;', out)

    def test_nocookie_embed_and_watch_link(self):
        out = builder.render([episode()])
        self.assertIn('https://www.youtube-nocookie.com/embed/KBLRatggtPo', out)
        self.assertIn('https://www.youtube.com/watch?v=KBLRatggtPo', out)
        self.assertIn('rel="noopener"', out)

    def test_metadata_line_and_saint(self):
        out = builder.render([episode(saint='Saint Luke the Evangelist')])
        self.assertIn('Glorious Mysteries · English · November 18, 2026', out)
        self.assertIn('Feast focus: Saint Luke the Evangelist.', out)

    def test_arabic_language_label(self):
        out = builder.render([episode(language='ar')])
        self.assertIn('Arabic', out)

    def test_empty_state_has_no_iframe(self):
        out = builder.render([])
        self.assertNotIn('<iframe', out)
        self.assertIn('No episodes are registered yet', out)

    def test_private_preview_contract(self):
        out = builder.render([episode()])
        self.assertIn('<meta name="robots" content="noindex, nofollow"', out)
        self.assertIn('{{> primary-nav}}', out)


class CheckModeTests(unittest.TestCase):
    def run_builder(self, *args):
        return subprocess.run(
            [sys.executable, str(ROOT / 'scripts' / 'build_rosary_episodes.py'), *args],
            capture_output=True, text=True, cwd=ROOT)

    def test_check_passes_on_committed_output(self):
        result = self.run_builder('--check')
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_check_detects_drift(self):
        out = ROOT / 'src' / 'pages' / 'rosary-episodes.html'
        original = out.read_text()
        try:
            out.write_text(original + '\n<!-- drift -->\n')
            result = self.run_builder('--check')
            self.assertEqual(result.returncode, 1)
            self.assertIn('stale', result.stderr)
        finally:
            out.write_text(original)
        self.assertEqual(self.run_builder('--check').returncode, 0)

    def test_write_is_idempotent(self):
        before = (ROOT / 'src' / 'pages' / 'rosary-episodes.html').read_text()
        self.assertEqual(self.run_builder().returncode, 0)
        self.assertEqual((ROOT / 'src' / 'pages' / 'rosary-episodes.html').read_text(), before)


if __name__ == '__main__':
    unittest.main()
