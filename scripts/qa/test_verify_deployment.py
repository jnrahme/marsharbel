"""Exercise deployment verification against a real local HTTP server."""

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
from threading import Thread
import unittest


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


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
            (folder / "mysteries").mkdir()
            (folder / "mysteries/joyful-1.html").write_text("<h1>Joyful</h1>")
        self.server = ThreadingHTTPServer(
            ("127.0.0.1", 0), partial(QuietHandler, directory=str(self.live)))
        self.thread = Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.stop_server)

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
        self.assertIn("Verified 3 live frontend files", result.stdout)

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

    def test_empty_checkout_cannot_pass(self):
        (self.root / "index.html").unlink()
        result = self.run_check()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("root must contain the website", result.stderr)


if __name__ == "__main__":
    unittest.main()
