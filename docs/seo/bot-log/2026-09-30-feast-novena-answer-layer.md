# 2026-09-30 - Feast day + novena answer layer (AEO scoreboard retrofit)

Pages: /saint-charbel-feast-day, /saint-charbel-novena. Lane: content-pipeline. Request: parent, 9-30 9:27 PM.

Added to each page: a "Short answer" paragraph at the top of the hero, and a visible FAQ section (5 Q&A). FAQPage JSON-LD is generated from the visible FAQ by scripts/apply_seo_tags.py (not hand-authored). New English strings registered in locales/legacy-text-baseline.json.

## Claim / source matrix (every answer restates the page's own existing body copy; no new facts)
- Feast July 24 universal, third Sunday of July Maronite: page "Two Dates, One Feast".
- 2027 = July 18, 2028 = July 16 (Sundays, weekday-checked by calendar computation): page's own upcoming-feasts list.
- Died Dec 24 1898; ordained July 23 1859; Rome's reason for July 24 not published: page "Why July".
- Annaya vigil / outdoor Liturgy / holy oil: page "The Feast at Annaya".
- Novena nine days, July 15-23, miss-a-day rule, no guarantee: page "How to Pray This Novena" / "When to Pray It", traditional text by the Monastery of Saint Maron, Annaya.

## Flag for review
Parent brief said "Feast day is July 24". Both dates are correct and the page says so; the answer blocks state both, July 24 first.
The page's statement that Rome assigned July 24 "when the feast was added after the 1977 canonization" is the page's existing claim, restated, not independently re-verified here.
No media added. No locale pages changed (en masters only).

## Integration corrections
New copy uses the scoped English catalog `locales/en/feast-novena-answer-copy.json`; frozen legacy baseline restored. Fresh source checks on September 30 verified Roman July24/Maronite third-Sunday dates and monastery nine-day prayer text. Removed unsupported1977 assignment-history explanation from English body/FAQ, replaced rigid missed-day requirement with qualified pastoral advice, corrected "same prayer" to day-by-day prayers and avoided unattended-candle advice. Source checks: EWTN News/ACI MENA feast reporting, Catholic Culture July24 calendar, Deir Annaya's novena, and Divine Mercy general missed-day guidance.2027July18/2028July16 Sundays calculated. Locale masters unchanged by this English-only release; localization follow-up remains.
