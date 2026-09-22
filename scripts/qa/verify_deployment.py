#!/usr/bin/env python3
"""Verify public frontend files against this checkout, not just HTTP success."""

import argparse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import time
from urllib.error import URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


def frontend_files(root):
    files = {path for pattern in ("*.html", "*.js", "*.css", "*.webmanifest")
             for path in root.glob(pattern)}
    files.update((root / "mysteries").glob("*.html"))
    files.update(root / name for name in ("robots.txt", "sitemap.xml"))
    files.update((root / "media/promo/optimized").glob("*.webp"))
    return sorted(path for path in files if path.is_file())


def verify_file(root, path, base_url, nonce):
    relative = path.relative_to(root).as_posix()
    url = f"{base_url.rstrip('/')}/{quote(relative)}?deployment-check={nonce}"
    request = Request(url, headers={"Cache-Control": "no-cache",
                                   "User-Agent": "Marsharbel-Deployment-Check/1.0"})
    try:
        with urlopen(request, timeout=15) as response:
            actual = response.read()
        if actual != path.read_bytes():
            return f"{relative}: deployed contents differ from checkout"
    except (URLError, TimeoutError, OSError) as error:
        return f"{relative}: {error}"
    return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="https://marsharbel.com")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--attempts", type=int, default=10)
    parser.add_argument("--interval", type=float, default=20)
    args = parser.parse_args()
    if args.attempts < 1 or args.interval < 0:
        parser.error("attempts must be positive and interval must be nonnegative")
    root = args.root.resolve()
    files = frontend_files(root)
    if not files or not (root / "index.html").is_file():
        parser.error("root must contain the website, including index.html")
    for attempt in range(1, args.attempts + 1):
        nonce = time.time_ns()
        with ThreadPoolExecutor(max_workers=6) as pool:
            errors = list(filter(None, pool.map(
                lambda path: verify_file(root, path, args.base_url, nonce), files)))
        if not errors:
            print(f"Verified {len(files)} live frontend files match the checkout.", flush=True)
            return 0
        print(f"Attempt {attempt}/{args.attempts}: {len(errors)} files not verified", flush=True)
        for error in errors:
            print(f"  {error}", flush=True)
        if attempt < args.attempts:
            time.sleep(args.interval)
    print("Deployment verification failed. Check Hostinger Git build output and cache.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
