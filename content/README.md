# Content layer (PR 1A)

Structured content records separated from page code, so dailies, products and
language pages become data edits instead of code edits. Nothing reads these
files at build or runtime yet: this PR adds the schemas, the seed records and
the CI validator only (zero risk to served pages). First build-time reader
lands in PR 1B; the remaining types migrate one per PR (1C).

## Types and homes

| Type | Schema | Records |
|---|---|---|
| Daily video episode | `schemas/daily-video.schema.json` | `rosary/episodes.json` (one entry per episode in `episodes[]`) |
| Prayer page | `schemas/prayer-page.schema.json` | `prayers/<slug>.json` |
| Product | `schemas/product.schema.json` | `products/<id>.json` |
| Language page metadata | `schemas/language-page.schema.json` | `language-pages/<locale>.json` |

`content/books`, `content/ui` and the books-level JSON files predate this layer
and keep their existing contracts (`scripts/books/*`, `npm run books:check`)
until their own migration PRs.

## The gate

`python3 scripts/qa/check_content_schemas.py` validates every record against
its schema and fails on any violation; it also fails when a JSON file in an
owned directory has no schema mapping, or a schema is not wired into the
mapping. Wired into `scripts/qa/run_full_qa.sh` (behavior tests:
`scripts/qa/test_content_schemas.py`). The validator is stdlib-only by design;
`scripts/qa/requirements.txt` stays untouched.

The validator supports exactly the schema subset the four schemas use: `type`
(including unions like `["integer", "null"]`), `required`, `properties`,
`additionalProperties` (false or a subschema), `items`, `enum`, `pattern`,
`minLength`, `minProperties`, `minItems`, `minimum`. Extending a schema beyond
that subset fails closed with "unsupported type" until the validator learns it.

## Seed records

- `rosary/episodes.json`: three real published episodes from the Marsharbel
  YouTube channel (titles verified against YouTube oEmbed, 19 Nov 2026).
- `prayers/saint-charbel-prayer-for-healing.json`: purpose/how/source grounded
  in the live page and Prayer Library card; `promiseStatus: none` is the
  honest-status vocabulary from the Prayer Library.
- `products/tee-classic.json`: byte-mirrors the product's entry in the live
  launch catalog `store/catalog.json`; the schema is that catalog's shape so
  migration is a data move.
- `language-pages/en.json`: mirrors the `en` entry of `locales/registry.json`,
  which stays the source of truth.
