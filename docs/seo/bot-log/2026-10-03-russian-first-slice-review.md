# Russian first slice - review candidate, not release approval

Reader promise: learn who Saint Charbel was, including his Maronite Catholic identity, from a complete biography with dated events and a clear distinction between records and reported tradition.

## Source and scope

- `/ru/` is a small Russian section homepage built through the locale-home template. Only biography is published; no placeholder prayer, rosary or travel pages.
- `/ru/biography` mirrors the full `history.html` English master, not the short `/en/biography` guide. All 212 visible MAIN slots, all eight narrative sections, nine FAQ answers, five photographs, IDs, links and source references are preserved. No exact-twin resolver approval is created.
- English catalog summary is used only for the homepage teaser and the catalog's required six-section guide record. The served biography is the full guarded-master render, not this short record.
- Source master: `src/pages/history.html` -> `history.html`, base stage `282e55193f26b416f8eafcb6b43d0d7dbc99b1d3`.
- Existing German biography receives reciprocal Russian hreflang and digest refresh only. German novena/feast/miracles digests refresh because adding native Russian footer navigation changes master bytes, not MAIN text.
- Section-home navigation gains Русский. Prayer/Eucharistic publication sets remain unchanged. All 284 identity variants remain pending with empty proofs. Registration is not certification of an exact article twin.

## Glossary for independent native/faith review

| English | Russian draft | Note |
|---|---|---|
| Saint Charbel Makhlouf | святой Шарбель Маклуф | Vatican News uses Шарбель Махлуф; review surname choice and consistency |
| Maronite Church | Маронитская церковь | Eastern Catholic Church in communion with Rome, not Orthodox |
| Lebanese Maronite Order | Ливанский маронитский орден | Review official Russian usage |
| monastery / hermitage / hermit | монастырь / скит / отшельник | Do not imply Orthodox jurisdiction |
| Eucharist / adoration | Евхаристия / поклонение Святым Дарам | Catholic terminology |
| beatification / canonization | беатификация, причисление к лику блаженных / канонизация | Distinct dates and processes |
| optional memorial | факультативная память | Review liturgical-calendar terminology |
| Roman Martyrology | Римский мартиролог | Historical record attribution preserved |
| vows | обеты бедности, целомудрия и послушания | Monastic vows, not generalized household demands |
| incorrupt body / reported light | нетленное тело / сообщения о свете | Always attributed; conflicting examinations retained |
| Annaya / Bkaakafra / Mayfouq | Аннайя / Бекаа-Кафра / Майфук | Check inflection and accepted place names |
| novena / rosary | новенна / Розарий | Navigation labels only; no Russian prayer texts generated |

## Quote and faith restrictions

- No Russian Scripture or prayer machine translation. The liturgical fragment at stroke/death remains in the English source wording and is explicitly identified as not a Russian prayer translation.
- Papal prose and death-record quotations are labeled own translations, not official Russian editions.
- 8 May birth date is traditional; no authenticated birth certificate. Ordination is 1859, not an unqualified exact day. Death age discrepancy 68/70 retained.
- Official beatification/canonization miracles are distinguished from private healing testimony, light at the tomb, body/moisture reports, and monthly 22nd devotion.
- Russian Catholic/Orthodox answer is added in standfirst and first FAQ without deleting any source section or adding unsupported ecclesial recognition.
- English destinations in the reading list and key prose links carry `(на английском)`; source-note language caveat is explicit.

## Consulted source URLs

- https://www.vatican.va/content/paul-vi/fr/homilies/1977/documents/hf_p-vi_hom_19771009.html (primary: formation, vocation, community/hermit years, death and theological framing; read current text)
- http://www.maronite-institute.org/MARI/JMS/april98/Saint_Sharbel.htm (secondary/archival synthesis: death record, rules, letters and testimony; read current text)
- https://www.santiebeati.it/dettaglio/35850 (secondary: dates and conflicting account; read current text)
- https://www.vaticannews.va/ru/church/news/2020-07/istoriya-odnoj-kanonizacii-sharbel-mahluf.html (Russian terminology and communion with Rome; read current text. Stronger miracle assertions and exact dates here were NOT adopted over the qualified English master.)

The remaining English master source links are retained verbatim. Their underlying facts inherit the English source's editorial review; the Russian producer has not independently re-investigated every English claim. Native/faith reviewer must check the complete Russian translation against the source, including proper names, quotes, medical language and Church distinctions.

## Producer proof

- Builder output and source page composition checks passed.
- `check_i18n_policy.py` passed (strict keyed text and exact render freshness).
- SEO checker passed: 284 canonical pages and sitemap entries.
- `test_russian_slice.py`: 4 passed. Complete tags/IDs/media, reciprocal home/full biography clusters, bounded publication sets, no placeholder internal destinations, zero invented twin proof.
- Existing `test_exact*.py`: 8 passed.
- `russian-first-slice.spec.js`: 4 passed at phone/laptop. Loaded local images, no console errors/HTTP asset failures/sideways scroll; actual home link, refusal feedback, footer route exercised.
- Rendered at 390 and 1440 px; inspected Cyrillic hero/chrome, homepage, tables, photos, prose, FAQ, sources and footer screenshots. Cyrillic is legible with existing fonts. Desktop hero keeps the source's narrow large heading.
- Full QA did not pass: the first attempt hit an occupied default port; a separate-port attempt repeatedly timed out decoding unrelated Travel photos and was stopped. Full i18n suite is still being collected separately. These are open gates, not waived.
- No production validation yet. No native Russian or independent faith sign-off yet. No merge or deployment yet.

## Integration/release gates

1. Fresh independent native Russian + faith review of the entire candidate and source, with concrete corrections or pass.
2. Rebase on settled stage; recheck master digests and pending manifest hashes, without inventing review proofs.
3. Full CI/QA and page/source freshness green, including new focused Russian test in CI.
4. Live `/ru` -> `/ru/`, `/ru/` 200 and `/ru/biography` 200; canonical and reciprocal cluster checks. Re-test native footer/home route, exact-page selector refusal and desktop/phone pixels after deploy.
5. Do not certify article twins or expand prayers/scripture until separately authorized and reviewed.
