"""Exercise deployment verification against a real local HTTP server."""

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
from threading import Thread
import unittest
import struct
import zlib

from verify_deployment import contents_match


def icon_png(indices=(1, 0), filter_type=0, metadata=False):
    def chunk(kind, payload):
        return struct.pack('>I', len(payload)) + kind + payload + struct.pack('>I', zlib.crc32(kind + payload))
    row = bytes(indices) if filter_type == 0 else bytes((indices[0], (indices[1] - indices[0]) % 256))
    return (b'\x89PNG\r\n\x1a\n'
            + chunk(b'IHDR', struct.pack('>IIBBBBB', 2, 1, 8, 3, 0, 0, 0))
            + chunk(b'PLTE', b'\x00\x00\x00\xff\xff\xff')
            + (chunk(b'tEXt', b'Comment\x00CDN metadata') if metadata else b'')
            + chunk(b'IDAT', zlib.compress(bytes((filter_type,)) + row, 1 if metadata else 9))
            + chunk(b'IEND', b''))


class QuietHandler(SimpleHTTPRequestHandler):
    """Serve like the production .htaccess: clean URLs map to .html files."""

    redirects = {}

    def log_message(self, *args):
        pass

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path in self.redirects:
            self.send_response(301)
            self.send_header("Location", self.redirects[path])
            self.end_headers()
            return
        if path.endswith(".html"):
            self.send_response(301)
            self.send_header("Location", path[:-len(".html")])
            self.end_headers()
            return
        super().do_GET()

    def translate_path(self, path):
        local = super().translate_path(path)
        if not Path(local).exists() and Path(local + ".html").is_file():
            return local + ".html"
        return local


class DeploymentVerificationTest(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "checkout"
        self.live = Path(self.temp.name) / "live"
        for folder in (self.root, self.live):
            folder.mkdir()
            (folder / "index.html").write_text("<h1>Current</h1>")
            (folder / "app.js").write_text("// current app")
            (folder / "locales").mkdir()
            (folder / "locales/registry.json").write_text('{"locales":{"pt":{}}}')
            (folder / "pt").mkdir()
            (folder / "pt/oracoes.html").write_text("<h1>Orações</h1>")
            (folder / "mysteries").mkdir()
            (folder / "mysteries/joyful-1.html").write_text("<h1>Joyful</h1>")
        self.server = ThreadingHTTPServer(
            ("127.0.0.1", 0), partial(QuietHandler, directory=str(self.live)))
        self.thread = Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.stop_server)

        QuietHandler.redirects = {}

    def stop_server(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()

    def run_check(self):
        return subprocess.run(
            [sys.executable, str(Path(__file__).with_name("verify_deployment.py")),
             "--root", str(self.root), "--base-url",
             f"http://127.0.0.1:{self.server.server_port}", "--attempts", "1"],
            capture_output=True, text=True, timeout=10)

    def test_matching_frontend(self):
        result = self.run_check()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Verified 4 live frontend files", result.stdout)

    def test_stale_asset_is_failure_even_with_http_200(self):
        (self.live / "app.js").write_text("// stale app")
        result = self.run_check()
        self.assertEqual(result.returncode, 1)
        self.assertIn("app.js: deployed contents differ", result.stdout)

    def test_missing_mystery_page_is_failure(self):
        (self.live / "mysteries/joyful-1.html").unlink()
        result = self.run_check()
        self.assertEqual(result.returncode, 1)
        self.assertIn("joyful-1.html: HTTP Error 404", result.stdout)

    def test_missing_localized_page_is_failure(self):
        (self.live / "pt/oracoes.html").unlink()
        result = self.run_check()
        self.assertEqual(result.returncode, 1)
        self.assertIn("pt/oracoes.html: HTTP Error 404", result.stdout)

    def test_missing_registry_is_actionable_failure(self):
        (self.root / "locales/registry.json").unlink()
        result = self.run_check()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("valid locales/registry.json", result.stderr)

    def test_empty_checkout_cannot_pass(self):
        (self.root / "index.html").unlink()
        result = self.run_check()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("root must contain the website", result.stderr)

    def test_lossless_png_reencoding_matches(self):
        self.assertTrue(contents_match(Path('icon.png'), icon_png(), icon_png(filter_type=1, metadata=True)))

    def test_changed_or_corrupt_png_cannot_match(self):
        self.assertFalse(contents_match(Path('icon.png'), icon_png(), icon_png(indices=(1, 1))))
        self.assertFalse(contents_match(Path('icon.png'), icon_png(), b'not a PNG'))

    def test_redirected_page_is_failure_naming_the_target(self):
        QuietHandler.redirects = {"/mysteries/joyful-1": "/old-preview/joyful-1"}
        result = self.run_check()
        self.assertEqual(result.returncode, 1)
        self.assertIn("mysteries/joyful-1.html: mysteries/joyful-1 redirects (301) to /old-preview/joyful-1", result.stdout)

    def test_pages_are_checked_at_their_clean_urls(self):
        from verify_deployment import public_path
        self.assertEqual(public_path("index.html"), "")
        self.assertEqual(public_path("pt/index.html"), "pt/")
        self.assertEqual(public_path("testimonies.html"), "testimonies")
        self.assertEqual(public_path("app.js"), "app.js")


if __name__ == "__main__":
    unittest.main()
