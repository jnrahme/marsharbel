# Bot log - 2026-09-26 - Padre Pio storybook page (/pio-story)

## Request
Joey (WhatsApp, 2026-09-26): "now add his story to our story book section and
make sure it follows the player and read loud stuff we have for saint charbel."

## What shipped
/pio-story - a 16-page read-aloud storybook for Padre Pio using the SAME player
(storybook.js/storybook.css) as the Charbel storybook, parameterized by story id
(body data-story="pio" or ?story=pio; charbel remains the default and is
unchanged - regression-verified). No new CSS, no new player code path.

- Pages: the approved 980-word script (16 pages), exact narrated bodies from the
  technical lane's pages.json.
- Narration: Kokoro am_michael speed .94 page clips (.36s sentence rests),
  media/storybook-pio/en/page-01..16.mp3, voice pack "Story Voice (Recommended)"
  + Browser Voice fallback. Pack/resume localStorage keys scoped per story so
  Charbel prefs/progress are untouched.
- Illustrations: 16 WebP composites at media/storybook-pio/images/, with the
  visible disclosure "original composite scenes, not historical footage" in the
  hero. Voice-model disclosure alongside.
- Prayer/heart cards: authored by the content lane (16 pairs, child-friendly,
  same pattern as Charbel's cards).
- Evidence panel: per-page documented/pastoral claims linked to the Vatican
  biography (2002) and the John Paul II canonization homily.
- Shell extras: What Young Hearts Can Learn (4 cards), True Dates (1887-2002),
  honest fine-print note (stigmata rests on his letters + witness testimony;
  decades-long Church investigation), Research Basis (Vatican x2 + National
  Centre for Padre Pio).
- Sitemap entry added (weekly, 0.9, lastmod 2026-09-26).

## NOT in this bundle (merge-gated follow-ups, owned by this lane)
- Story dropdown entry for /pio-story and cross-link from /st-padre-pio: nav is
  being reworked by the pending prayer-hub bundle; these ride the owned nav
  re-sync. pio-story.html carries the current stage nav, unmodified.
- Translations (English only until translated + reviewed, per asset handoff).

## Verification
node --check storybook.js OK. Playwright d+m: 16 page turns, kokoro pack
selected by default, evidence links render, Charbel story.html regression clean
(original packs/images/pages), mobile p1/p2 render. Audio playback confirmed by
network: page-01 probe 200 (pack resolution), page-02 playback fetch 200,
reading indicator + elapsed timer live. Zero console errors. check_i18n_policy
PASS (pio-story.html 82 + storybook.js strings registered in baseline).
check_seo PASS for this page (135 indexable); 4 stale lastmods listed are
pre-existing on stage post-#202/#203 (integrator's sitemap_lastmod deploy step).
git diff --check clean.

## Sources
Vatican biography: https://www.vatican.va/news_services/liturgy/saints/ns_lit_doc_20020616_padre-pio_en.html
Canonization homily: https://www.vatican.va/content/john-paul-ii/en/homilies/2002/documents/hf_jp-ii_hom_20020616_padre-pio.html
Kokoro model/license: https://huggingface.co/hexgrad/Kokoro-82M (Apache)
