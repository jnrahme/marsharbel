# 2026-09-30 - Massabki Brothers page (pillar 2/4)

Feature: /massabki-brothers - Lebanon's first Maronite lay saints (canonized Oct 20, 2024). Answer-first block, six sections, FAQ, saints hub card, sitemap entry. Spec: parent 9-27 3:21 PM (four-saint series, build order 2).

## Evidence gate
- Claim/source matrix (every load-bearing fact triangulated):
  - Names/roles/family: Francis (silk merchant, 8 children), Abdel Moati (teacher, 5 children), Raphael (unmarried) - Santi e Beati (Borrelli/Flocchini, upd. 2024-10-16) + Bishop Tarabay (Catholic Weekly 2024-10-25).
  - Martyrdom night July 9-10, 1860, Franciscan convent of St Paul, refusal quotes ("I am a Maronite Christian and in the faith of Christ I will die" / "I am a Christian, kill me, I am ready") - Tarabay + Santi e Beati.
  - Beatification Oct 10, 1926 by Pius XI (with 8 Franciscans; Patriarch Hoyek petition; unique process) - Santi e Beati + Commons image date corroboration.
  - Canonization Oct 20, 2024, St Peter's Square, Pope Francis, as 11 Martyrs of Damascus (with Manuel Ruiz Lopez + 7 companions) - Vatican homily (vatican.va 20241020) + Vatican News + Tarabay.
  - First Maronite laymen canonized - Tarabay (Maronite Bishop of Australia).
  - Feast July 10 (Roman Martyrology; Damascus solemn Sunday after July 12; Franciscan calendar July 13) - Santi e Beati.
  - Relics: church of the Conversion of St Paul, Bab Touma, Damascus, one tomb with the friars - Santi e Beati. NOTE: Catholic Weekly says "beneath the altar of the Damascus Cathedral" - used the more precise Santi e Beati location; conflict noted, not both asserted.
  - No Person schema: three subjects, SAINT_STEMS not extended (single-Person schema would mis-model).
- Media-rights ledger: media/saints/massabki-brothers.webp = Commons "Martyrs of Damascus.jpg", official 1926 beatification image, public domain (published 1926), source Custody of the Holy Land (custodia.org). Provenance recorded in caption + Sources.
- Translation parity: en-first; locales after per queue.

## QA
check_seo 240 pages; nav-sync 112 pages 0 out of sync; test_seo+prayer_mirror+i18n; i18n:check/test; dead-code; diff --check; testimony-security; rosary suites (smoke, end-rules, intro-cta, menu, prayer-behavior, ui-regression, story-floating-player, site-smoke, rosary-all); rendered review desktop+phone + hub card (pixel-inspected).

## Integrator corrections (September 30)
- Independent live-source check corrected hero: only Francis is identified as a silk merchant; Abdel Moati is a teacher, Raphael a helper.
- Removed the optional Commons image: its PD-US notice explicitly warns that non-US rights may differ. Text-led treatment until suitable reuse rights are established.
- Frozen legacy baseline restored; new wording counted in locales/en/saint-pillars-copy.json and enforced by policy.
- Removed unsupported literal blood-mingling phrasing and decorative Tuesday reference.
