# Locale expansion foundation: review handoff

Owner request: six-market language/country SEO and answer coverage; tracking item todo-01M3VMSG4V53G5QFMNZR70844F. Existing registry is en/ar/fr/es/pt/it/de/pl. Portuguese/Polish need depth, not registration. Four proposed additions remain ru/hi/th/zh-Hans. No new locale is enabled in this patch.

Base: stage e774657. Published URLs and existing generated HTML remain unchanged. Generated locale-routes.js adds alias identities only. No region-specific URLs, country claims or fonts are introduced.

## What changed

- Registry owns OG locale metadata and stable ordering, selector aliases, explicit per-topic publication and prayer/Eucharistic publication sets.
- English and localized Eucharistic builders, sitemap/routes and tests honor the publication set rather than forcing ten stories for a new language.
- Selector canonicalizes aliases using generated registry metadata. A synthetic future zh-Hans publication test verifies old zh-cn preference and mixed-case query handling without enabling Chinese today.
- Transaction-safe DOM slot translation validates the entire source and plain-text catalog before touching a parsed DOM. Tags and edge whitespace remain intact; changed English master fails closed.
- Feast renderer reads language/route/catalog from the registry and chrome, breadcrumbs, accessible primary label, footer and selected internal links from the localized catalog. Arabic output is byte-identical to stage. Future locale feast routes must also exist in their topic publication set.
- Dynamic test language lists derive from the registry. Browser locale tests isolate external transports and mark monitoring sessions.

## Verification

100 Python tests passed before the final extra FAQ/breadcrumb ambiguity guards; targeted foundation (9) and feast (2) tests re-passed after those guards. Build freshness and i18n policy passed. SEO checks found 265 indexable pages matching sitemap and metadata rules. Existing generated HTML byte-identical, including Arabic feast. Diff/JavaScript syntax clean.

Selector tests at 390/1440: en/de/it authored route round-trip, single selector, synthetic zh-Hans canonical option, zh-cn saved preference and mixed-case query route passed. Synthetic locale never enters production registry.

Eucharistic collection test passed (eleven English routes). Published locale browser checks passed at both 390 and 1440 across 77 routes, filters, images, sources and overflow checks. Rosary smoke/menu/end/prayer-behavior/intro CTA/UI and story floating-player/checklist scripts passed separately. Checklist speech-voice test skips where browser has no speechSynthesis voices.

Actual German prayer page rendered locally at 390 and 1440; full-page scroll, readable layout, single selector and no overflow inspected in captures. Screenshots accompany handoff. This is not deployed/live proof.

Full npm qa command exceeded the execution window during its site runtime portion, so there is no full-command success claim. Remaining integrator gate: complete site runtime/SEO browser subchecks and independent code/visual review, then final full QA and production proof after authorized merge/deploy.

## Next content batch

Preserve /de/gebete and /it/preghiere. Rebuild German biography/novena at existing URLs as exact-master renders, add German feast/miracle hub after full catalogs, then Italian novena/oil against the final English oil master. Country hreflang design requires separate review; no fake cloned country URLs. hi/th light launch means fewer complete master pages, never shortened translations. Autocomplete harvests are phrasing evidence, not measured volume or proof of no demand.

Sources for language/region design:
- https://developers.google.com/search/docs/specialty/international/localized-versions
- https://developers.google.com/search/docs/specialty/international/managing-multi-regional-sites
