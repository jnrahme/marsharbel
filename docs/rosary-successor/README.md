# Rosary story successor: unpublished checkpoint

Base: `5c4a38d2643e962a540700b5d1db9b9bc2b7cc69`.

This directory preserves the frozen English text candidate and proposed page mapping. The candidate's embedded review labels are historical producer metadata, not permission or review evidence. The independent text review covers the exact manuscript SHA256 `2ad25dd88b617e6fa374d36d56784caac44b5d73b6ac39617fa9eab9f7737421`. It does not approve layout, metadata, translations, art, audio or release.

## Current implementation

- `scripts/i18n/rosary_successor_adapter.py` checks the frozen manuscript bytes, all20 books, exact narrative/reflection/prayer preservation, unique semantic IDs, page order, and unchanged painting bytes. It stages168 pages in60 canonical/notes files outside the checkout. It refuses runtime output or overwriting a prior staging directory.
- Prayer semantic roles map to the existing `story` kind with `scene=prayer`. Reflection maps to `reflection`. No reader enum or controls are added.
- Staged books are drafts. Staged catalog review status explicitly remains pending metadata/layout review. Evidence claims are not carried from the old four-page books.
- `scripts/i18n/rosary_successor_review.py` validates a separate editorial integrity receipt for20x8 editions. Every receipt pins its exact catalog, canonical text, shared structure and English source. The old pairing file remains unchanged and is hash-bound as history. The validator cannot activate a release or certify native review. Hashes bind bytes but do not authenticate the reviewer or establish authority.
- Both mechanisms are offline. Neither is imported by the live manifest or a runtime generator. No successor review receipt has been manufactured.
- Tests extend the already-wired `test_rosary_books_pairing.py`, so no QA step/shard inventory changes are needed.

Run the staged adapter:

```sh
PYTHONPATH=scripts python3 scripts/i18n/rosary_successor_adapter.py \
  --spec docs/rosary-successor/integration-spec-v1.json \
  --master docs/rosary-successor/twenty-en-candidates-v3.json \
  --output /tmp/rosary-successor-staged
```

## Release work still open

1. Independent page mapping and metadata review, with exact reviewed bytes.
2. Seven real translated successors, including titles, paragraphs, alt text, metadata, prayer instructions, recognized Catholic prayer wording, adult notes and evidence claims. No automatic native-certification claim.
3. Canonical structure and actual locale packets integrated together; stale master hashes updated only after their translations are updated and reviewed.
4. English/locale reader, API, static page and same-page projections generated from canonical inputs. New technical pairing must validate exact final output without borrowing the old reviewer label or modifying historical evidence.
5. Negative controls for stale locale/master bytes, prayer drift, missing movement and wrong switcher; full repository CI, independent rendered review and all160 switcher families/editions checked before a single release.
6. Live reader/API/switcher and phone/desktop/RTL/long-text/200% verification after deploy, followed by cache overwrite checks.

No EN-first live release. RU/HI/TH/ZH scope holds remain. No new recorded audio, illustration or spending. Existing paintings are retained, not advertised as a new illustrated edition; rights and actual scene placement still need the release review.
