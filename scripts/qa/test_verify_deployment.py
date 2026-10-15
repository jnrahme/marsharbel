"""Exercise deployment verification against a real local HTTP server."""

from functools import partial
from http.server import BaseHTTPRequestHandler, SimpleHTTPRequestHandler, ThreadingHTTPServer
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

    def test_pages_that_htaccess_301s_are_not_expected_to_serve_themselves(self):
        import tempfile
        from verify_deployment import redirected_pages
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".htaccess").write_text(
                "RewriteRule ^saint-charbel-prayers(?:\\.html)?/?$ /en/prayers [R=301,L]\n"
                "RewriteRule ^mysteries/rosary-visual-guide(?:\\.html)?/?$ /rosary-visual-guide [R=301,L]\n"
                "RewriteRule ^plain(?:\\.html)?/?$ /plain.html [L]\n")
            self.assertEqual(redirected_pages(root), {root / "saint-charbel-prayers.html"})




# ---------------------------------------------------------------------------
# Bounded-execution controls for the retry/budget machinery (run 38685876119):
# stalled/slow-body workers, mid-attempt budget, queued cancellation, majority
# timeouts, and the unchanged healthy full-file success receipt.

import contextlib
import io
import json
import time
import unittest.mock

import verify_deployment as vd

HITS = {"count": 0}


def make_root(tmp, pages=1):
    root = Path(tmp)
    (root / "index.html").write_text("<html>home</html>")
    for i in range(pages):
        (root / f"page{i}.html").write_text(f"<html>page{i}</html>")
    (root / "robots.txt").write_text("User-agent: *")
    (root / "locales").mkdir()
    (root / "locales/registry.json").write_text(json.dumps({"locales": {}}))
    return root


def bounded_handler(root, mode, delay=2.0):
    def file_bytes(url_path):
        path = url_path.split("?")[0]
        if path in ("", "/"):
            path = "/index.html"
        elif path.endswith(".txt"):
            pass
        else:
            path = path + ".html"
        target = root / path.lstrip("/")
        return target.read_bytes() if target.is_file() else None

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_GET(self):
            HITS["count"] += 1
            if mode == "stalled":
                time.sleep(30)
                return
            if mode == "slow-headers":
                # Status line, then one unfinished header byte stream every 50ms:
                # headers never complete, yet every socket read beats the timeout.
                try:
                    self.wfile.write(b"HTTP/1.1 200 OK\r\n")
                    self.wfile.flush()
                    for _ in range(100000):
                        self.wfile.write(b"X-Drip: x")
                        self.wfile.flush()
                        time.sleep(0.05)
                except (BrokenPipeError, ConnectionResetError):
                    pass
                return
            if mode == "slow":
                time.sleep(delay)
            body = file_bytes(self.path)
            if mode == "drip":
                self.send_response(200)
                self.send_header("Content-Length", "1000000")
                self.end_headers()
                try:
                    for _ in range(1000000):
                        self.wfile.write(b"x")
                        self.wfile.flush()
                        time.sleep(0.05)
                except (BrokenPipeError, ConnectionResetError):
                    pass
                return
            if body is None:
                self.send_response(404)
                self.end_headers()
                return
            if mode == "wrong":
                body = body + b"tampered"
            self.send_response(200)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    return Handler


class BoundedServer:
    def __init__(self, root, mode, delay=2.0):
        self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), bounded_handler(root, mode, delay))
        self.httpd.daemon_threads = True
        Thread(target=self.httpd.serve_forever, daemon=True).start()
        self.port = self.httpd.server_address[1]

    def stop(self):
        self.httpd.shutdown()
        self.httpd.server_close()


def run_main(root, port, *extra):
    argv = ["verify_deployment.py", "--base-url", f"http://127.0.0.1:{port}",
            "--root", str(root), *extra]
    out = io.StringIO()
    start = time.monotonic()
    with unittest.mock.patch.object(sys, "argv", argv), contextlib.redirect_stdout(out):
        rc = vd.main()
    return rc, out.getvalue(), time.monotonic() - start


class BoundedHealthyPath(unittest.TestCase):
    def test_full_success_receipt_unchanged(self):
        with TemporaryDirectory() as tmp:
            root = make_root(tmp)
            server = BoundedServer(root, "healthy")
            try:
                rc, out, elapsed = run_main(root, server.port, "--attempts", "1", "--interval", "0")
            finally:
                server.stop()
        self.assertEqual(rc, 0, out)
        self.assertIn("Verified 3 live frontend files match the checkout.", out)
        self.assertIn("Attempt 1/1: checking 3 files", out)


class BoundedExecution(unittest.TestCase):
    def test_scrum_negative_control_nonreturning_worker(self):
        # Scrum's control shape at 92c196a: worker that never yields inside the
        # window with --budget 0.1 returned only after the worker finished
        # (1.3046s = 13x). The budget must now be enforced mid-flight.
        with TemporaryDirectory() as tmp:
            root = make_root(tmp)
            original = vd.verify_file
            vd.verify_file = lambda *a, **k: (time.sleep(1.3), None)[1]
            try:
                rc, out, elapsed = run_main(root, "9", "--attempts", "1", "--interval", "0",
                                            "--budget", "0.1")
            finally:
                vd.verify_file = original
        self.assertEqual(rc, 1)
        self.assertIn("budget-exhausted", out)
        self.assertLess(elapsed, 1.0, f"budget not enforced: {elapsed:.3f}s")

    def test_slow_body_aborted_inside_request_budget(self):
        with TemporaryDirectory() as tmp:
            root = make_root(tmp)
            server = BoundedServer(root, "drip")
            try:
                rc, out, elapsed = run_main(root, server.port, "--attempts", "1", "--interval", "0",
                                            "--request-budget", "0.5", "--budget", "30")
            finally:
                server.stop()
        self.assertEqual(rc, 1)
        self.assertIn("aborted slow read", out)
        self.assertLess(elapsed, 8.0, f"slow-drip not bounded: {elapsed:.3f}s")

    def test_mid_attempt_budget_with_slow_workers(self):
        with TemporaryDirectory() as tmp:
            root = make_root(tmp)
            server = BoundedServer(root, "slow", delay=2.0)
            try:
                rc, out, elapsed = run_main(root, server.port, "--attempts", "3", "--interval", "0",
                                            "--budget", "0.3", "--request-budget", "10")
            finally:
                server.stop()
        self.assertEqual(rc, 1)
        self.assertIn("budget-exhausted", out)
        self.assertLess(elapsed, 1.5, f"mid-attempt budget overshoot: {elapsed:.3f}s")

    def test_queued_work_cancelled_not_drained(self):
        with TemporaryDirectory() as tmp:
            root = make_root(tmp, pages=20)
            server = BoundedServer(root, "slow", delay=1.0)
            HITS["count"] = 0
            try:
                rc, out, elapsed = run_main(root, server.port, "--attempts", "1", "--interval", "0",
                                            "--budget", "0.3", "--request-budget", "10")
            finally:
                server.stop()
        self.assertEqual(rc, 1)
        self.assertIn("budget-exhausted", out)
        self.assertLessEqual(HITS["count"], 6, f"queued work was drained: {HITS['count']} hits")
        self.assertLess(elapsed, 1.5, f"cancellation not prompt: {elapsed:.3f}s")
        # scrum's control: abandoned workers must not drain the queue afterwards.
        time.sleep(1.5)
        self.assertLessEqual(HITS["count"], 6,
                             f"queue drained after abandon: {HITS['count']} hits")

    def test_majority_timeouts_fail_fast(self):
        with TemporaryDirectory() as tmp:
            root = make_root(tmp, pages=20)
            server = BoundedServer(root, "stalled")
            try:
                rc, out, elapsed = run_main(root, server.port, "--attempts", "5", "--interval", "0",
                                            "--socket-timeout", "0.4", "--request-budget", "5",
                                            "--budget", "120")
            finally:
                server.stop()
        self.assertEqual(rc, 1)
        self.assertIn("mass-timeout", out)
        self.assertLess(elapsed, 6.0, f"mass-timeout detected too late: {elapsed:.3f}s")


class BetweenAttemptsBudget(unittest.TestCase):
    def test_budget_expiring_between_attempts_skips_retry(self):
        # Attempt 1 fails fast with content mismatches; the retry sleep must be
        # clamped to the remaining budget and the loop must stop there.
        with TemporaryDirectory() as tmp:
            root = make_root(tmp)
            server = BoundedServer(root, "wrong")
            try:
                rc, out, elapsed = run_main(root, server.port, "--attempts", "5",
                                            "--interval", "30", "--budget", "0.5",
                                            "--request-budget", "5")
            finally:
                server.stop()
        self.assertEqual(rc, 1)
        self.assertIn("budget-exhausted", out)
        self.assertNotIn("Attempt 2/", out)
        self.assertLess(elapsed, 3.0, f"retry sleep not clamped: {elapsed:.3f}s")


class CliProcessExit(unittest.TestCase):
    """Whole-process controls: the budget must bound CLI EXIT, not just main()'s
    return, with workers stuck in the header phase or the body phase."""

    def run_cli(self, root, port, *extra, timeout=15):
        cmd = [sys.executable, str(Path(__file__).resolve().parent / "verify_deployment.py"),
               "--base-url", f"http://127.0.0.1:{port}", "--root", str(root), *extra]
        start = time.monotonic()
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return proc.returncode, proc.stdout, time.monotonic() - start

    def test_cli_process_exit_under_slow_headers(self):
        with TemporaryDirectory() as tmp:
            root = make_root(tmp)
            server = BoundedServer(root, "slow-headers")
            try:
                rc, out, elapsed = self.run_cli(root, server.port, "--attempts", "1",
                                                "--interval", "0", "--budget", "0.5",
                                                "--request-budget", "0.2",
                                                "--socket-timeout", "5")
            finally:
                server.stop()
        self.assertEqual(rc, 1, out)
        self.assertIn("budget-exhausted", out)
        self.assertLess(elapsed, 4.0, f"CLI process outlived the budget: {elapsed:.3f}s")

    def test_cli_process_exit_under_slow_body(self):
        with TemporaryDirectory() as tmp:
            root = make_root(tmp)
            server = BoundedServer(root, "drip")
            try:
                rc, out, elapsed = self.run_cli(root, server.port, "--attempts", "1",
                                                "--interval", "0", "--budget", "5",
                                                "--request-budget", "0.2",
                                                "--socket-timeout", "5")
            finally:
                server.stop()
        self.assertEqual(rc, 1, out)
        self.assertTrue("mass-timeout" in out or "budget-exhausted" in out, out)
        self.assertLess(elapsed, 4.0, f"CLI process outlived the bound: {elapsed:.3f}s")


if __name__ == "__main__":
    unittest.main()
