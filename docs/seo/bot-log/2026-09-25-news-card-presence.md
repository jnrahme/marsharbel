# Latest News homepage feature sizing, September 25, 2026

## Checked and changed

At the September 25 stage tip, the homepage's Latest News card was 340 x 178px on desktop and 350 x 178px on a 390px mobile viewport. The thumbnail was 64 x 64px. The card is still a single feature containing a rotating headline; no news item, destination, or underlying editorial claim changed.

The card now has more padding, a 100 x 100px desktop or 88 x 88px mobile thumbnail, a more readable headline, and a slightly larger link and label. The desktop feature column grows to 410px. It renders about 410 x 240px on desktop and 350 x 222px on mobile, with no horizontal overflow at 390, 768, or 1440px. The card remains inside the existing hero composition.

## Why and expected impact

The larger card makes the latest article easier to notice and read while respecting the one-card request. This is a presentation improvement, not a change to the news feed or a claim of search-ranking impact.

## Checks

The generated home stylesheet is current. QA components passed in bounded runs: localization, SEO/sitemap, feeds, static testimony baseline, testimony security, full site smoke, and the rosary regression suite including its separately executed long checklist. New browser layout checks assert one visible card, one active headline, larger image/card dimensions, valid links and image alternatives, and no horizontal overflow at 390/768/1440px. Desktop and mobile screenshots were visually inspected. The full sequential `qa:ci` command exceeded the shell's 120-second cap during the long checklist, but its components completed in separate runs. One speechSynthesis-dependent checklist case was skipped because no voices are exposed in the test environment.
