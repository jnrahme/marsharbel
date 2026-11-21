#!/usr/bin/env python3
"""Fail when a Playwright spec writes to or reads from an absolute machine path.

CI runners do not have /downloads, /tmp/<name> or a home directory laid out like a
workstation, so a spec that screenshots to /downloads passes locally and fails in CI
(this cost a 25 minute browser-quality cycle on #509). Use testInfo.outputPath() or a
repo-relative path instead.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ABSOLUTE = re.compile(r"""['"`](/downloads|/tmp|/home|/Users|/mnt)/""")


def check(root=ROOT):
    errors = []
    for path in sorted((root / "tests").glob("*.js")):
        for number, line in enumerate(path.read_text().splitlines(), 1):
            if ABSOLUTE.search(line):
                errors.append(f"{path.relative_to(root)}:{number}: absolute path in a spec; use testInfo.outputPath() or a repo-relative path")
    return errors


if __name__ == "__main__":
    problems = check()
    if problems:
        raise SystemExit("\n".join(problems))
    print("Spec path check passed: no absolute machine paths in tests/*.js.")
