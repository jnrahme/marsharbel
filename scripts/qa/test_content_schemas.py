#!/usr/bin/env python3
"""Behavior tests for the PR 1A content-layer schema gate.

Positive: every committed content/ instance in the owned directories validates,
and every schema is wired. Negative: the validator must reject missing required
keys, wrong types, unexpected keys, bad enum/pattern values, nested violations,
bad array items and malformed registry wrappers - a gate that cannot fail is
not a gate.
"""
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_content_schemas as gate  # noqa: E402

SCHEMAS = {
    name[: -len(".schema.json")]: gate.load_schema(name[: -len(".schema.json")])
    for name in os.listdir(gate.SCHEMA_DIR)
    if name.endswith(".schema.json")
}


def problems(instance, schema_name):
    errors = []
    gate.validate(instance, SCHEMAS[schema_name], "fixture", errors)
    return errors


class CommittedContentTests(unittest.TestCase):
    def test_all_committed_content_is_valid_and_covered(self):
        self.assertEqual(gate.run(), [])

    def test_every_schema_file_is_wired_into_a_mapping(self):
        mapped = {name for _, name, _ in gate.MAPPINGS}
        self.assertEqual(set(SCHEMAS), mapped)


class DailyVideoTests(unittest.TestCase):
    def valid(self):
        return {
            "date": "2026-11-18",
            "mystery": "glorious",
            "language": "en",
            "youtubeId": "KBLRatggtPo",
            "title": "Today's Rosary | Wednesday, November 18, 2026 | Glorious Mysteries",
        }

    def test_valid_episode_passes(self):
        self.assertEqual(problems(self.valid(), "daily-video"), [])

    def test_missing_required_key_fails(self):
        bad = self.valid()
        del bad["youtubeId"]
        self.assertTrue(any("youtubeId" in e for e in problems(bad, "daily-video")))

    def test_unknown_mystery_fails(self):
        bad = self.valid() | {"mystery": "ordinary"}
        self.assertTrue(problems(bad, "daily-video"))

    def test_bad_date_shape_fails(self):
        bad = self.valid() | {"date": "November 18, 2026"}
        self.assertTrue(problems(bad, "daily-video"))

    def test_bad_youtube_id_fails(self):
        bad = self.valid() | {"youtubeId": "too-short"}
        self.assertTrue(problems(bad, "daily-video"))

    def test_unexpected_key_fails(self):
        bad = self.valid() | {"views": 12}
        self.assertTrue(any("unexpected key" in e for e in problems(bad, "daily-video")))

    def test_registry_wrapper_must_hold_an_episodes_array(self):
        import tempfile

        with tempfile.NamedTemporaryFile(
            "w", suffix=".json", dir=os.path.join(gate.ROOT, "content", "rosary"), delete=False
        ) as fh:
            json.dump({"schema": 1, "episodes": "not-a-list"}, fh)
            tmp_path = fh.name
        try:
            errors = gate.check_file(tmp_path, SCHEMAS["daily-video"], "episodes")
        finally:
            os.unlink(tmp_path)
        self.assertTrue(any("episodes" in e for e in errors))


class PrayerPageTests(unittest.TestCase):
    def valid(self):
        return {
            "slug": "saint-charbel-prayer-for-healing",
            "title": "Saint Charbel Prayer for Healing",
            "path": "/saint-charbel-prayer-for-healing",
            "purpose": "Asking Saint Charbel's intercession for healing.",
            "source": "Original composition of marsharbel.com.",
            "promiseStatus": "none",
        }

    def test_valid_prayer_passes(self):
        self.assertEqual(problems(self.valid(), "prayer-page"), [])

    def test_promise_status_must_be_honest_vocabulary(self):
        bad = self.valid() | {"promiseStatus": "guaranteed-miracle"}
        self.assertTrue(problems(bad, "prayer-page"))

    def test_purpose_is_required(self):
        bad = self.valid()
        del bad["purpose"]
        self.assertTrue(problems(bad, "prayer-page"))

    def test_null_promise_allowed(self):
        good = self.valid() | {"promise": None}
        self.assertEqual(problems(good, "prayer-page"), [])

    def test_numeric_promise_rejected(self):
        bad = self.valid() | {"promise": 5}
        self.assertTrue(problems(bad, "prayer-page"))


class ProductTests(unittest.TestCase):
    def valid(self):
        return {
            "id": "tee-classic",
            "kind": "apparel",
            "title": "Hermitage Tee",
            "blurb": "Heavy cotton unisex tee.",
            "art": "/media/storybook-charbel-v2/images/page-01.webp",
            "alt": "Hermitage Tee - storybook artwork",
            "priceCents": None,
            "checkoutUrl": None,
        }

    def test_valid_product_passes(self):
        self.assertEqual(problems(self.valid(), "product"), [])

    def test_negative_price_fails(self):
        bad = self.valid() | {"priceCents": -1}
        self.assertTrue(problems(bad, "product"))

    def test_boolean_price_is_not_an_integer(self):
        bad = self.valid() | {"priceCents": True}
        self.assertTrue(problems(bad, "product"))

    def test_unknown_kind_fails(self):
        bad = self.valid() | {"kind": "subscription"}
        self.assertTrue(problems(bad, "product"))

    def test_printify_subschema_enforced(self):
        bad = self.valid() | {"printify": {"blueprintHint": "Tee", "verify": "yes"}}
        self.assertTrue(problems(bad, "product"))

    def test_art_must_be_a_site_path(self):
        bad = self.valid() | {"art": "https://example.com/x.webp"}
        self.assertTrue(problems(bad, "product"))


class LanguagePageTests(unittest.TestCase):
    def valid(self):
        return {
            "locale": "en",
            "nativeName": "English",
            "direction": "ltr",
            "home": "/",
            "ogLocale": "en_US",
            "slugs": {"biography": "biography"},
        }

    def test_valid_language_page_passes(self):
        self.assertEqual(problems(self.valid(), "language-page"), [])

    def test_direction_enum(self):
        bad = self.valid() | {"direction": "sideways"}
        self.assertTrue(problems(bad, "language-page"))

    def test_slugs_are_kebab_case(self):
        bad = self.valid() | {"slugs": {"biography": "Biography Page"}}
        self.assertTrue(problems(bad, "language-page"))

    def test_empty_slugs_fail(self):
        bad = self.valid() | {"slugs": {}}
        self.assertTrue(problems(bad, "language-page"))

    def test_topic_guides_items_checked(self):
        bad = self.valid() | {"topicGuides": ["ok-slug", "Not A Slug"]}
        self.assertTrue(problems(bad, "language-page"))

    def test_locale_shape(self):
        good = self.valid() | {"locale": "zh-Hans"}
        self.assertEqual(problems(good, "language-page"), [])
        bad = self.valid() | {"locale": "EN"}
        self.assertTrue(problems(bad, "language-page"))


class SchemaDocumentTests(unittest.TestCase):
    def test_schemas_are_objects_with_titles(self):
        for name, schema in SCHEMAS.items():
            self.assertEqual(schema.get("type"), "object", name)
            self.assertTrue(schema.get("title"), name)
            self.assertIn("$schema", schema, name)

    def test_episodes_registry_shape_on_committed_file(self):
        path = os.path.join(gate.ROOT, "content", "rosary", "episodes.json")
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        self.assertIsInstance(data.get("episodes"), list)
        self.assertGreaterEqual(len(data["episodes"]), 1)

    def test_anchored_pattern_rejects_trailing_newline(self):
        # Python's "$" matches before a trailing newline; JS (JSON Schema)
        # semantics must not let a newline-suffixed value through.
        self.assertTrue(gate.pattern_matches("^[A-Za-z0-9_-]{11}$", "KBLRatggtPo"))
        self.assertFalse(gate.pattern_matches("^[A-Za-z0-9_-]{11}$", "KBLRatggtPo\n"))
        self.assertFalse(gate.pattern_matches("^[a-z]{2}$", "en\n"))
        self.assertTrue(gate.pattern_matches("Charbel", "Saint Charbel"))


if __name__ == "__main__":
    unittest.main()
