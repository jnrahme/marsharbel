#!/usr/bin/env python3
"""Structural contract of .github/workflows/post-merge-regen.yml.

Q-007: after a squash merge lands on stage, committed generated files can be
stale relative to the rewritten history. The regen workflow must stay
deterministic, drift-gated and self-terminating; these tests pin the parts of
that contract a refactor could silently break (no PyYAML on CI runners, so
assertions run against the workflow text itself).
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WF = (ROOT / ".github/workflows/post-merge-regen.yml").read_text(encoding="utf-8")

GENERATED = ["sitemap.xml", "feed.xml", "sitemap-images.xml", "sitemap-video.xml"]
GENERATORS = [
    "scripts/sitemap_lastmod.py",
    "scripts/build_feeds.py",
    "scripts/build-media-sitemaps.py",
]


class TriggerAndSafety(unittest.TestCase):
    def test_runs_on_stage_push_only(self):
        on_block = WF.split("on:", 1)[1].split("permissions:", 1)[0]
        self.assertIn("push:", on_block)
        self.assertIn("- stage", on_block)
        self.assertNotIn("pull_request", on_block)

    def test_serialized_not_cancelled(self):
        self.assertIn("group: post-merge-regen", WF)
        self.assertIn("cancel-in-progress: false", WF)

    def test_scoped_permissions(self):
        perms = WF.split("permissions:", 1)[1].split("concurrency:", 1)[0]
        self.assertIn("contents: write", perms)
        self.assertIn("pull-requests: write", perms)
        self.assertNotIn("actions:", perms)

    def test_full_history_checkout(self):
        # sitemap_lastmod.py refuses shallow clones; regen needs real dates.
        self.assertIn("fetch-depth: 0", WF)


class Regeneration(unittest.TestCase):
    def test_every_generated_file_has_a_generator_step(self):
        regen = WF.split("Regenerate derived files", 1)[1]
        for generator in GENERATORS:
            self.assertIn(f"python3 {generator}", regen)

    def test_drift_gate_covers_exactly_the_generated_files(self):
        gate = re.search(r"git diff --quiet -- ([^\n;]+)", WF)
        self.assertIsNotNone(gate, "drift gate missing")
        self.assertEqual(sorted(gate.group(1).split()), sorted(GENERATED))

    def test_commit_adds_only_generated_files(self):
        add = re.search(r"git add ([^\n;]+)", WF)
        self.assertIsNotNone(add)
        self.assertEqual(sorted(add.group(1).split()), sorted(GENERATED))

    def test_no_pr_without_drift(self):
        # The diff gate must exit before any branch/push/PR command runs.
        gate_at = WF.index("git diff --quiet")
        for mutating in ("git push", "gh pr create", "gh pr merge"):
            self.assertGreater(WF.index(mutating), gate_at, mutating)


class PullRequestShape(unittest.TestCase):
    def test_single_reusable_branch_into_stage(self):
        self.assertIn('BRANCH="bot/post-merge-regen"', WF)
        self.assertIn("--base stage", WF)
        self.assertIn('git push --force origin "$BRANCH"', WF)

    def test_existing_pr_is_reused(self):
        self.assertIn("gh pr list --base stage", WF)

    def test_auto_merge_squash(self):
        self.assertIn("gh pr merge --auto --squash", WF)


if __name__ == "__main__":
    unittest.main()
