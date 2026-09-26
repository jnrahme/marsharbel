# Bot log - 2026-09-26 - st-padre-pio: full prayer collection

## Request
Joey (WhatsApp, 2026-09-26): Pio has "a lot more prayers like the Guardian Angel
prayer" - wants his full prayer collection on the site.

## What shipped
Expanded #his-prayer into "His Prayers" - seven prayer cards using the existing
prayer-grid/prayer-card components (no new CSS), each with an honest provenance
label. No new standalone pages (the prayer-hub bundle is pending; hub/finder
integration rides the owned nav re-sync follow-up). One cross-link added to
prayer-library.

## The collection and its provenance
1. The Rosary - his documented counsel ("the weapon").
2. The Guardian Angel Prayer - traditional; the prayer he told spiritual children
   to repeat (letter to Raffaelina Cerase, Letters vol. II; EWTN article from the
   friary of Our Lady of Grace). "Send me your guardian angel."
3. "Stay with Me, Lord" after Communion - FULL text; labeled attributed,
   devotional tradition, not a signed manuscript.
4. Efficacious Novena to the Sacred Heart - traditional text from St. Margaret
   Mary Alacoque; Padre Pio prayed it daily for all who asked (National Centre
   for Padre Pio, Barto PA). No outcome guarantee; devotional "efficacious" name
   attributed to tradition.
5. Prayer to St. Michael the Archangel - traditional (Leo XIII); he instructed
   penitents to pray it (National Centre); Monte Sant'Angelo / Gargano note.
6. Prayer to Saint Pio of Pietrelcina - official intercession prayer, National
   Centre for Padre Pio, post-canonization.
7. The Church's Prayer on His Feast (Sept 23) - Roman Missal collect (ICEL,
   via liturgies.net).

## Sources added to the page's Sources list
EWTN guardian angels article; padrepiodevotions.org (Stay with me, Lord);
padrepio.org/pray/efficacious-novena + /prayer-to-saint-pio (National Centre);
liturgies.net (Roman Missal collect).

## Verification
check_i18n_policy PASS (54 new strings max-merge registered in baseline, Pio entry
only). apply_seo_tags: 0 changes to this page's structured data. check_seo PASS
except three PRE-EXISTING stale sitemap lastmods on jpii/teresa/saints - present
on pristine stage 860c973 too (post-#203), integrator's sitemap_lastmod.py deploy
step owns those; reverted apply_seo_tags's datePublished bumps on those two files
so this bundle touches only st-padre-pio.html + baseline. Pixel pass: desktop
1280px (3 segments) + mobile 390px (7 segments) of the full section, all cards
legible, no overflow, zero console errors.
