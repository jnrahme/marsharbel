# Extracted-feature mirror gate

This status is distinct from a whole-page strict mirror and from migration debt.
The English source remains `news.html`; the bounded family is one named feature,
not an archive master, a locale self-master or an exception to structure QA.

`film-premiere-v1` is explicitly registered in `scripts/i18n/feature_mirror.py`.
Only its exact source/template/catalog, source article ID, target route and Arabic
catalog are accepted. Expanding scope needs a reviewed gate change.

The independent executor creates `config/feature-mirrors/film-premiere-v1.json`:

- `version`: 1; `family`: `film-premiere-v1`.
- `textKeys`: exactly the placeholder keys used by the selected feature template.
- `templateSha256`: digest of BeautifulSoup's serialization of the selected raw
  template article, including placeholders.
- `englishCatalogSha256`: digest of json.dumps of the selected English values,
  with ensure_ascii=False and sort_keys=True.
- `sourceFeatureSha256`: digest of BeautifulSoup's serialization of the actual
  served English article, which must equal the rendered keyed template.
- `shellSha256`: digest returned by shell_digest on final generated Arabic bytes.
  It excludes only the one article, preserving complete shell bytes including
  labels, metadata, URL queries, controls and runtime dictionaries.

These are provenance/structure pins, not native-language approval or visual
sign-off. Authors do not create or refresh them. After independent source,
translation and final-shell review, the executor registers the target page in
locale-mirror-policy.json with status extracted-feature, family film-premiere-v1,
master news.html, locale ar and the exact standalone route. No normalizers or
exceptions are allowed. Normalization is limited to moving the archive H3/linked
heading into one standalone H1, removing that heading's whole-card link, changing
the sole H4 into H2 and replacing the article wrapper class.

The locale catalog must cover exactly the article keys, not unrelated homepage
copy. Metadata can use common messages outside that catalog. The generated
translated article must byte-serialize identically to the keyed adapted template.
This proves text presence and shared links/video/media/attributes without ignoring
translated prose. Semantic translation quality still needs separate review.

The gate has mutation controls for missing/extra/empty/markup values, duplicate or
foreign source selectors/keys, stale template/catalog/served-feature provenance,
wrong links/queries/video, omitted iframe permissions, changed prose/structure,
extra shell content, modified runtime scripts/control attributes/footer,
language/direction/canonical errors and wildcard/self-master escape attempts.
It runs in run_full_qa.sh alongside unchanged strict mirror checks.

Activation remains separate: add the generator to international outputs before
shared framing/postprocessing, emit sitemap/routing/inbound links, regenerate,
check final repeatability, pin the final shell independently, inspect desktop/phone
and 200% Arabic pixels. Never mark a standalone feature as a verified whole
English archive equivalent or claim reciprocal archive hreflang equivalence.
