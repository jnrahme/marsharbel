#!/usr/bin/env python3
"""Map changed files to the QA steps that cover them (Q-006).

Reads the real suite inventory from `run_full_qa.sh --list-steps` (same code
path CI shards use), applies ordered path rules, and prints the selected step
commands, deduplicated, in suite order. Fail-safe: anything ambiguous,
unmapped, or suite-wiring selects the FULL suite - a wrong answer is always
"run more", never "run less".

Usage:
  python3 scripts/qa/affected_tests.py BASE [HEAD]   # diff base...head
  python3 scripts/qa/affected_tests.py --files f1 f2 ...
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

LOCALES = ("ar", "de", "es", "fr", "hi", "it", "pt", "ru", "th", "zh-Hans")

# Suite wiring and generators: any change can alter every step's behavior.
FULL_SUITE = (
    re.compile(r"^\.github/workflows/"),
    re.compile(r"^scripts/qa/run_full_qa\.sh$"),
    re.compile(r"^scripts/qa/shard-manifest\.tsv$"),
    re.compile(r"^scripts/qa/requirements\.txt$"),
    re.compile(r"^scripts/qa/(lib|fixtures)/"),
    re.compile(r"^scripts/qa/affected_tests\.py$"),
    re.compile(r"^scripts/(build|i18n)/"),
    re.compile(r"^package(-lock)?\.json$"),
)

TEST_FILE = re.compile(r"^(scripts/qa|scripts/tests)/([^/]+\.(py|cjs|mjs|mts|sh))$")
LOCALE_DIR = re.compile(r"^(" + "|".join(LOCALES) + r")/|locales/(" + "|".join(LOCALES) + r")/")
SITEMAP_FEED = re.compile(r"^(sitemap(-images|-video)?\.xml|feed\.xml)$")


def suite_steps(root=ROOT):
    """(index, command) for every step the unsharded suite would run."""
    out = subprocess.run(
        ["bash", "scripts/qa/run_full_qa.sh", "--list-steps"],
        cwd=root, check=True, capture_output=True, text=True).stdout
    steps = []
    for line in out.splitlines():
        index, _, command = line.partition("\t")
        if command:
            steps.append((int(index), command.strip()))
    if not steps:
        raise SystemExit("run_full_qa.sh --list-steps returned no steps")
    return steps


def select(paths, steps):
    """Return (selected commands, reasons). Unknown coverage selects everything."""
    selected, reasons = {}, []
    def mark(matching, why):
        hits = [(i, c) for i, c in steps if matching(c)]
        return hits, why

    for path in sorted(set(paths)):
        if any(rule.search(path) for rule in FULL_SUITE):
            reasons.append(f"{path}: suite wiring or generator; full suite")
            return [c for _, c in steps], reasons
        test = TEST_FILE.match(path)
        if test:
            name = test.group(2)
            hits, why = mark(lambda c, n=name: n in c, f"{path}: steps running {name}")
            if not hits:
                reasons.append(f"{path}: no step references it; full suite")
                return [c for _, c in steps], reasons
            reasons.append(why + f" ({len(hits)})")
            for i, c in hits:
                selected[i] = c
            continue
        locale = LOCALE_DIR.match(path)
        if locale:
            code = next(g for g in locale.groups() if g)
            # Delimited by non-alphanumerics so _ru_ in test names matches but
            # "run"/"shard" do not; i18n/locale/language checkers cover every locale.
            pattern = re.compile(
                r"(?<![a-zA-Z0-9])" + re.escape(code) + r"(?![a-zA-Z0-9])"
                r"|i18n|locale|language")
            hits, why = mark(lambda c, p=pattern: p.search(c), f"{path}: steps covering locale {code}")
            if not hits:
                reasons.append(f"{path}: no locale-specific step; full suite")
                return [c for _, c in steps], reasons
            reasons.append(why + f" ({len(hits)})")
            for i, c in hits:
                selected[i] = c
            continue
        if SITEMAP_FEED.match(path):
            hits, why = mark(lambda c: "sitemap" in c or "feed" in c, f"{path}: sitemap/feed steps")
            if hits:
                reasons.append(why + f" ({len(hits)})")
                for i, c in hits:
                    selected[i] = c
                continue
        reasons.append(f"{path}: no coverage rule; full suite")
        return [c for _, c in steps], reasons
    if not paths:
        reasons.append("no changed files; nothing selected")
    return [c for _, c in sorted(selected.items())], reasons


def changed_paths(base, head):
    out = subprocess.run(
        ["git", "diff", "--name-only", f"{base}...{head}"],
        cwd=ROOT, check=True, capture_output=True, text=True).stdout
    return [line.strip() for line in out.splitlines() if line.strip()]


def main(argv):
    if argv[:1] == ["--files"]:
        paths = argv[1:]
    elif len(argv) in (1, 2):
        paths = changed_paths(argv[0], argv[1] if len(argv) == 2 else "HEAD")
    else:
        sys.exit(__doc__)
    commands, reasons = select(paths, suite_steps())
    for reason in reasons:
        print("# " + reason, file=sys.stderr)
    print("\n".join(commands))


if __name__ == "__main__":
    main(sys.argv[1:])
