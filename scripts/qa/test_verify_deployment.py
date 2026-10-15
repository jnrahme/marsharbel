#!/usr/bin/env python3
"""Bounded-execution controls for verify_deployment: stalled/slow-body workers,
mid-attempt budget, queued cancellation, majority timeouts, healthy full success."""
import contextlib
import importlib.util
import io
import json
import sys
import tempfile
import threading
import time
import unittest
import unittest.mock
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("verify_deployment", ROOT / "scripts/qa/verify_deployment.py")
vd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vd)

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


def file_bytes(root, url_path):
    path = url_path.split("?")[0]
    if path in ("", "/"):
        path = "/index.html"
    elif path.endswith(".txt"):
        pass
    else:
        path = path + ".html"
    target = root / path.lstrip("/")
    return target.read_bytes() if target.is_file() else None


def handler_for(root, mode, delay=2.0):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_GET(self):
            HITS["count"] += 1
            if mode == "stalled":
                time.sleep(30)
                return
            if mode == "slow":
                time.sleep(delay)
            body = file_bytes(root, self.path)
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
            self.send_response(200)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    return Handler


class Server:
    def __init__(self, root, mode, delay=2.0):
        self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), handler_for(root, mode, delay))
        self.httpd.daemon_threads = True
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()
        self.port = self.httpd.server_address[1]

    def stop(self):
        self.httpd.shutdown()
        self.httpd.server_close()


def run(root, port, *extra):
    argv = ["verify_deployment.py", "--base-url", f"http://127.0.0.1:{port}",
            "--root", str(root), *extra]
    out = io.StringIO()
    start = time.monotonic()
    with unittest.mock.patch.object(sys, "argv", argv), contextlib.redirect_stdout(out):
        rc = vd.main()
    return rc, out.getvalue(), time.monotonic() - start


class HealthyPath(unittest.TestCase):
    def test_full_success_receipt_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_root(tmp)
            server = Server(root, "healthy")
            try:
                rc, out, elapsed = run(root, server.port, "--attempts", "1", "--interval", "0")
            finally:
                server.stop()
        self.assertEqual(rc, 0, out)
        self.assertIn("Verified 3 live frontend files match the checkout.", out)
        self.assertIn("Attempt 1/1: checking 3 files", out)


class BoundedExecution(unittest.TestCase):
    def test_scrum_negative_control_nonreturning_worker(self):
        # Scrum's control shape: worker that never yields inside the window, --budget 0.1.
        # Before the repair the script returned only after the worker finished (1.3046s, 13x).
        with tempfile.TemporaryDirectory() as tmp:
            root = make_root(tmp)
            original = vd.verify_file
            vd.verify_file = lambda *a, **k: (time.sleep(1.3), None)[1]
            try:
                rc, out, elapsed = run(root, "9", "--attempts", "1", "--interval", "0",
                                       "--budget", "0.1")
            finally:
                vd.verify_file = original
        self.assertEqual(rc, 1)
        self.assertIn("budget-exhausted", out)
        self.assertLess(elapsed, 1.0, f"budget not enforced: {elapsed:.3f}s")

    def test_slow_body_aborted_inside_request_budget(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_root(tmp)
            server = Server(root, "drip")
            try:
                rc, out, elapsed = run(root, server.port, "--attempts", "1", "--interval", "0",
                                       "--request-budget", "0.5", "--budget", "30")
            finally:
                server.stop()
        self.assertEqual(rc, 1)
        self.assertIn("aborted slow read", out)
        self.assertLess(elapsed, 8.0, f"slow-drip not bounded: {elapsed:.3f}s")

    def test_mid_attempt_budget_with_slow_workers(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_root(tmp)
            server = Server(root, "slow", delay=2.0)
            try:
                rc, out, elapsed = run(root, server.port, "--attempts", "3", "--interval", "0",
                                       "--budget", "0.3", "--request-budget", "10")
            finally:
                server.stop()
        self.assertEqual(rc, 1)
        self.assertIn("budget-exhausted", out)
        self.assertLess(elapsed, 1.5, f"mid-attempt budget overshoot: {elapsed:.3f}s")

    def test_queued_work_cancelled_not_drained(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_root(tmp, pages=20)
            server = Server(root, "slow", delay=1.0)
            HITS["count"] = 0
            try:
                rc, out, elapsed = run(root, server.port, "--attempts", "1", "--interval", "0",
                                       "--budget", "0.3", "--request-budget", "10")
            finally:
                server.stop()
        self.assertEqual(rc, 1)
        self.assertIn("budget-exhausted", out)
        self.assertLessEqual(HITS["count"], 6, f"queued work was drained: {HITS['count']} hits")
        self.assertLess(elapsed, 1.5, f"cancellation not prompt: {elapsed:.3f}s")

    def test_majority_timeouts_fail_fast(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = make_root(tmp, pages=20)
            server = Server(root, "stalled")
            try:
                rc, out, elapsed = run(root, server.port, "--attempts", "5", "--interval", "0",
                                       "--socket-timeout", "0.4", "--request-budget", "5",
                                       "--budget", "120")
            finally:
                server.stop()
        self.assertEqual(rc, 1)
        self.assertIn("mass-timeout", out)
        self.assertLess(elapsed, 6.0, f"mass-timeout detected too late: {elapsed:.3f}s")


if __name__ == "__main__":
    unittest.main(verbosity=2)
