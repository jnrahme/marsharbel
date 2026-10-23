# Veronica Giuliani - source-tier register (2026-10-23, post design review)

Standing provenance record for the evidence register carried in
content/books/veronica-giuliani-story/book.json. Written after independent
design review of the private paired EN+AR assembly (visual PASS on tree
956811e0). Document-only advance: no EN/AR content, art, or parser pins
change in this commit.

## Tiers (honest, per Main 08:01 / 08:15)

| Source | Tier | Status |
| --- | --- | --- |
| Benedict XVI, General Audience 2010-12-15 (vatican.va) | Church-primary | VERIFIED quote source for the last-words line («أخبروا الجميع بهذا» continuation attested in the same peregabriel.net/saintamaria/45077 article; audience is the actual quote source) |
| USCCB New American Bible, Romans 8:38-39 | Primary (liturgical text) | VERIFIED live link; p10 reflection page-specific |
| Catholic Encyclopedia 1912, "St. Veronica Giuliani" (newadvent.org/cathen/15363a.htm) | Secondary | URL PRESENTATION ONLY - accuracy NOT established. The CE article consulted during locale review was the WRONG article; no CE-based verification was obtained. |
| Enciclopedia Treccani, "Veronica Giuliani, santa" | Secondary | URL PRESENTATION ONLY - the Treccani/DBI fetch FAILED; no DBI-based verification was obtained. |
| Wikipedia (P6 details: novice-mistress 34 years, mystical-books rule, 1839 declaration) | Tertiary/secondary | SECONDARY-only verification (corroborated as secondary by peregabriel.net/saintamaria/45077: canonization 26 May 1839 Gregory XVI, beatification 17 June 1804 Pius VII). NO Church-primary claim. |

## Hard rule for any production graduation

The Catholic Encyclopedia and Treccani links are presented as URLs only.
They MUST NOT be cited, labeled, or promoted as verified sources in any
production integration, reseal, or publication until the content lane
repairs them: fetch and check the actual CE article and the actual
Treccani/DBI entry against the facts the pages assert, then record the
result here. Owner: content lane (source-verification gap, explicit).
A link existing in book.json is not evidence of accuracy.
