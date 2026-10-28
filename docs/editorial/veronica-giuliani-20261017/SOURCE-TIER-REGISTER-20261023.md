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

## Dated correction 2026-10-24 (content lane; document-only)

Authorized by Main Oct 24 ~06:58 EDT as a narrow document-only register
correction. No EN/AR content, art, parser, pin, integration or publication
change. The 2026-10-23 table above is preserved unchanged as the record of
what was known that day.

- Catholic Encyclopedia (newadvent.org/cathen/15363a.htm): VERIFIED
  2026-10-24. Distinction restored: the URL recorded in book.json was always
  the correct "St. Veronica Giuliani" article. The 2026-10-23 gap was that
  the locale reviewer consulted a wrong article during review - a
  review-process lookup failure, not a source defect. Fetched 2026-10-24 and
  checked against the facts the pages assert: born Mercatello 1660; died
  Citta di Castello 9 July 1727; Capuchin Poor Clare reception 1677, taking
  the name Veronica; 34 years novice-mistress; refused novices mystical
  books; elected abbess 1716; canonized by Gregory XVI in 1839. All
  confirmed.
- Treccani/DBI: VERIFIED 2026-10-24. The 2026-10-23 fetch failure was a
  malformed-URL lookup failure (missing "santa-" prefix), not a source
  absence. Correct entry:
  https://www.treccani.it/enciclopedia/santa-veronica-giuliani_(Dizionario-Biografico)/
  (Dizionario Biografico degli Italiani, Vol. 98, 2020, Simona Negruzzo),
  fetched 2026-10-24. Confirms: born 27 December 1660 at Mercatello sul
  Metauro (supports the book's age 66 at death); habit 28 Oct 1677; solemn
  vows 1 Nov 1678; novice-mistress from 1693; stigmata 5 Apr 1697; Holy
  Office sanctions revoked 7 Mar 1716; elected abbess 5 Apr 1716; died
  9 July 1727; canonized 26 May 1839 by Gregory XVI; liturgical memorial
  9 July.
- UNRESOLVED CONFLICT (explicitly not settled here): DBI gives beatification
  by Pius VII on 31 August 1802; the earlier secondary corroboration
  (peregabriel.net/saintamaria/45077) gave 17 June 1804. The book text
  asserts no beatification date (verified by content search 2026-10-24: no
  180x reference in en.json or book.json), so the conflict touches only this
  register's corroboration note. No date chosen; any future production
  citation of a beatification date requires Main's tiebreak ruling first.
- The 2026-10-23 graduation rule stands with both secondary sources now
  actually verified; the beatification-date conflict is the only open
  source-accuracy item.
