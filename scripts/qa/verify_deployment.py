#!/usr/bin/env python3
"""Verify public frontend files against this checkout, not just HTTP success."""

import re
import argparse
import json
import struct
import zlib
import queue
import threading
from pathlib import Path
import time
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import HTTPRedirectHandler, Request, build_opener


def palette_png_pixels(data):
    """Decode our 8-bit palette icons, allowing lossless CDN recompression."""
    if not data.startswith(b'\x89PNG\r\n\x1a\n'):
        return None
    try:
        chunks = {}
        offset = 8
        while offset < len(data):
            length = struct.unpack('>I', data[offset:offset + 4])[0]
            kind = data[offset + 4:offset + 8]
            payload = data[offset + 8:offset + 8 + length]
            crc = struct.unpack('>I', data[offset + 8 + length:offset + 12 + length])[0]
            if zlib.crc32(kind + payload) != crc:
                return None
            chunks.setdefault(kind, bytearray()).extend(payload)
            offset += length + 12
        width, height, depth, color, compression, filtering, interlace = struct.unpack('>IIBBBBB', chunks[b'IHDR'])
        if (depth, color, compression, filtering, interlace) != (8, 3, 0, 0, 0):
            return None
        raw = zlib.decompress(chunks[b'IDAT'])
        if len(raw) != height * (width + 1) or b'IEND' not in chunks:
            return None
        palette = chunks[b'PLTE']
        alpha = chunks.get(b'tRNS', b'')
        pixels = bytearray()
        previous = bytearray(width)
        for y in range(height):
            start = y * (width + 1)
            filter_type = raw[start]
            if filter_type > 4:
                return None
            row = bytearray(raw[start + 1:start + width + 1])
            for x in range(width):
                left = row[x - 1] if x else 0
                above = previous[x]
                corner = previous[x - 1] if x else 0
                predictor = left + above - corner
                paeth = min((left, above, corner), key=lambda value: abs(predictor - value))
                row[x] = (row[x] + (0, left, above, (left + above) // 2, paeth)[filter_type]) % 256
                index = row[x]
                rgb = palette[index * 3:index * 3 + 3]
                if len(rgb) != 3:
                    return None
                pixels.extend(rgb)
                pixels.append(alpha[index] if index < len(alpha) else 255)
            previous = row
        # Preserve color-management semantics as well as dimensions and pixels.
        color_metadata = tuple(bytes(chunks.get(key, b'')) for key in (b'gAMA', b'cHRM', b'sRGB', b'iCCP'))
        return width, height, bytes(pixels), color_metadata
    except (KeyError, ValueError, struct.error, zlib.error):
        return None


def contents_match(path, expected, actual):
    if expected == actual:
        return True
    if path.suffix.lower() == '.png':
        decoded = palette_png_pixels(expected)
        return decoded is not None and decoded == palette_png_pixels(actual)
    return False


def redirected_pages(root):
    """Checkout pages that .htaccess deliberately 301s elsewhere (no longer served as themselves)."""
    htaccess = root / ".htaccess"
    if not htaccess.is_file():
        return set()
    names = set()
    for line in htaccess.read_text().splitlines():
        match = re.match(r"\s*RewriteRule\s+\^([a-z0-9-]+)\(\?:\\\.html\)\?/\?\$\s+\S+\s+\[[^\]]*R=301", line)
        if match:
            names.add(root / f"{match.group(1)}.html")
    return names


def frontend_files(root):
    files = {path for pattern in ("*.html", "*.js", "*.css", "*.webmanifest")
             for path in root.glob(pattern)}
    files.update((root / "mysteries").glob("*.html"))
    for language in json.loads((root / "locales/registry.json").read_text())["locales"]:
        files.update((root / language).glob("*.html"))
    files.update(root / name for name in ("robots.txt", "sitemap.xml", "sitemap-images.xml", "sitemap-video.xml", "indexnow-key.txt"))
    files.update((root / "media/promo/optimized").glob("*.webp"))
    files.update((root / "media/fonts").glob("*.woff2"))
    files.update((root / "media/optimized").glob("*.webp"))
    files.update((root / "media/optimized").glob("*.avif"))
    files.update((root / "media/promo/optimized").glob("*.avif"))
    files.update((root / "pwa").glob("*-v2.png"))
    files -= redirected_pages(root)
    return sorted(path for path in files if path.is_file())


class NoRedirect(HTTPRedirectHandler):
    """Surface redirects so a moved or misrouted page cannot pass silently."""

    def redirect_request(self, *args):
        return None


OPENER = build_opener(NoRedirect)


def public_path(relative):
    """URL path visitors load for a checkout file (Apache serves pages without .html)."""
    if relative == "index.html" or relative.endswith("/index.html"):
        return relative[: -len("index.html")]
    if relative.endswith(".html"):
        return relative[: -len(".html")]
    return relative


def verify_file(root, path, base_url, nonce, request_budget=45, socket_timeout=15):
    """Verify one file with a TOTAL wall-time bound, not just socket-operation timeouts.

    urlopen's timeout governs each blocking socket call; a slow-drip response can
    otherwise extend one request indefinitely. Reading in chunks and checking a
    wall-clock deadline between chunks bounds one request to about
    request_budget + one socket timeout, whatever the server does.
    """
    relative = path.relative_to(root).as_posix()
    url = f"{base_url.rstrip('/')}/{quote(public_path(relative))}?deployment-check={nonce}"
    request = Request(url, headers={"Cache-Control": "no-cache",
                                   "User-Agent": "Marsharbel-Deployment-Check/1.0"})
    deadline = time.monotonic() + request_budget
    try:
        with OPENER.open(request, timeout=socket_timeout) as response:
            # read1 returns after a single socket read, so the wall-clock deadline is
            # re-checked between socket operations even on a slow-drip body.
            read_chunk = getattr(response, "read1", response.read)
            chunks = []
            while True:
                if time.monotonic() >= deadline:
                    return (f"{relative}: timed out - response not complete after "
                            f"{request_budget:.0f}s total (aborted slow read)")
                chunk = read_chunk(65536)
                if not chunk:
                    break
                chunks.append(chunk)
            actual = b"".join(chunks)
        if not contents_match(path, path.read_bytes(), actual):
            return f"{relative}: deployed contents differ from checkout"
    except HTTPError as error:
        if 300 <= error.code < 400:
            return f"{relative}: {public_path(relative) or '/'} redirects ({error.code}) to {error.headers.get('Location')}"
        return f"{relative}: {error}"
    except (URLError, TimeoutError, OSError) as error:
        return f"{relative}: {error}"
    return None


def categorize(error):
    """Bucket a failure line for the self-diagnosis summary."""
    text = error.lower()
    if "timed out" in text or "timeout" in text:
        return "timeout"
    if "redirects" in text:
        return "redirect"
    if "contents differ" in text:
        return "mismatch"
    return "http-error"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="https://marsharbel.com")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--attempts", type=int, default=10)
    parser.add_argument("--interval", type=float, default=20)
    parser.add_argument("--socket-timeout", type=float, default=15,
                        help="per-socket-operation timeout in seconds (default 15); the worst "
                             "request tail is request-budget + one socket timeout")
    parser.add_argument("--request-budget", type=float, default=45,
                        help="total wall-time bound per file request in seconds (default 45); "
                             "with the 15s socket timeout the worst request tail is about 60s, "
                             "keeping the whole job under budget + 60s")
    parser.add_argument("--budget", type=float, default=660,
                        help="internal time budget in seconds (default 660, deliberately below "
                             "the workflow's 15-minute job timeout so the script names its own "
                             "failure signature instead of dying silently on cancellation)")
    args = parser.parse_args()
    if args.attempts < 1 or args.interval < 0 or args.budget <= 0 or args.request_budget <= 0 or args.socket_timeout <= 0:
        parser.error("attempts must be positive and interval/budget/request-budget/socket-timeout must be nonnegative/positive")
    root = args.root.resolve()
    if not (root / "index.html").is_file():
        parser.error("root must contain the website, including index.html")
    try:
        files = frontend_files(root)
    except (OSError, ValueError, KeyError) as error:
        parser.error(f"root must contain a valid locales/registry.json: {error}")
    started = time.monotonic()
    deadline = started + args.budget
    last_errors = []
    attempts_run = 0
    stopped = None
    for attempt in range(1, args.attempts + 1):
        if attempt > 1 and time.monotonic() >= deadline:
            stopped = "budget-exhausted"
            break
        attempts_run = attempt
        nonce = time.time_ns()
        print(f"Attempt {attempt}/{args.attempts}: checking {len(files)} files "
              f"({time.monotonic() - started:.0f}s of {args.budget:.0f}s budget used)", flush=True)
        errors = []
        done = 0
        consecutive_timeouts = 0
        # Daemon workers: abandoning an attempt never blocks interpreter exit, so the
        # budget is a real process-exit bound even when a worker is stuck in connect,
        # DNS, or a slow-drip HEADER phase that no in-thread wall check can interrupt.
        # (ThreadPoolExecutor's non-daemon threads are joined at exit - that is what
        # let a stuck worker outlive the job after shutdown(wait=False).)
        tasks = queue.Queue()
        results = queue.Queue()
        stop = threading.Event()

        def worker():
            while True:
                path = tasks.get()
                # Stop-event checked BEFORE each task: an abandoned attempt never
                # drains queued requests, and sentinels retire workers cleanly after
                # normal completion (no idle daemons left behind).
                if path is None or stop.is_set():
                    return
                try:
                    results.put(verify_file(root, path, args.base_url, nonce,
                                            args.request_budget, args.socket_timeout))
                except Exception as error:  # a worker bug must not hang the attempt
                    results.put(f"{path.relative_to(root).as_posix()}: {error}")

        for _ in range(6):
            threading.Thread(target=worker, daemon=True).start()
        for path in files:
            tasks.put(path)
        pending = len(files)
        while pending:
            poll = min(2.0, max(0.05, deadline - time.monotonic()))
            try:
                error = results.get(timeout=poll)
            except queue.Empty:
                error = None
                if time.monotonic() < deadline:
                    continue
            else:
                pending -= 1
                done += 1
                if error:
                    errors.append(error)
                    consecutive_timeouts = consecutive_timeouts + 1 if categorize(error) == "timeout" else 0
                else:
                    consecutive_timeouts = 0
                if done % 50 == 0 or done == len(files):
                    print(f"Attempt {attempt}: {done}/{len(files)} checked, {len(errors)} failing, "
                          f"{time.monotonic() - started:.0f}s elapsed", flush=True)
            timeouts = sum(1 for item in errors if categorize(item) == "timeout")
            if timeouts > len(files) // 2 or consecutive_timeouts >= 12:
                print(f"MASS TIMEOUT mid-attempt: {timeouts} timeout failures of {done} checked "
                      f"({consecutive_timeouts} consecutive); the site is mid-deploy or stalling. "
                      f"Failing fast with {pending} checks abandoned.", flush=True)
                stopped = "mass-timeout"
                break
            if time.monotonic() >= deadline:
                print(f"Internal budget exhausted mid-attempt: abandoning the remaining "
                      f"{pending} checks of attempt {attempt}.", flush=True)
                stopped = "budget-exhausted"
                break
        stop.set()
        for _ in range(6):
            tasks.put(None)
        last_errors = errors
        if not errors and stopped is None:
            print(f"Verified {len(files)} live frontend files match the checkout.", flush=True)
            return 0
        print(f"Attempt {attempt}/{args.attempts}: {len(errors)} files not verified", flush=True)
        for error in errors:
            print(f"  {error}", flush=True)
        if stopped is not None:
            break
        if attempt < args.attempts:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                stopped = "budget-exhausted"
                break
            time.sleep(min(args.interval, remaining))
    if stopped is None:
        stopped = "persistent-mismatch"
    categories = {}
    for error in last_errors:
        kind = categorize(error)
        categories[kind] = categories.get(kind, 0) + 1
    print(f"SELF-DIAGNOSIS: {stopped} - {attempts_run} attempt(s) in "
          f"{time.monotonic() - started:.0f}s against {len(files)} files; "
          f"last attempt failures by category: "
          f"{json.dumps(categories, sort_keys=True) if categories else '{}'}.", flush=True)
    print("Deployment verification failed. Check Hostinger Git build output and cache.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
