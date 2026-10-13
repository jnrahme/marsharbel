"""Safety tests; successful remux is exercised against V6 in proof registry."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('glue', Path(__file__).parents[1]/'tools/glue.py')
glue = importlib.util.module_from_spec(spec)
spec.loader.exec_module(glue)


class GlueSafetyTests(unittest.TestCase):
    def test_existing_output_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/'existing.mp4'
            p.write_bytes(b'untouched')
            with self.assertRaisesRegex(ValueError, 'Output exists'):
                glue.glue('absent', 'absent', p, 1, '', '')
            self.assertEqual(p.read_bytes(), b'untouched')

    def test_hash_mismatch_fails_before_media_access(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/'input.mp4'
            out = Path(d)/'out.mp4'
            p.write_bytes(b'not-media')
            with self.assertRaisesRegex(ValueError, 'Source hash mismatch'):
                glue.glue(p, p, out, 1, 'wrong', 'wrong')
            self.assertFalse(out.exists())


if __name__ == '__main__':
    unittest.main()
