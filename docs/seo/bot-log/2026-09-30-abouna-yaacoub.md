# /abouna-yaacoub - pillar 3/4 (Lebanese saints)
2026-09-30 - content pipeline lane

## What shipped
New page /abouna-yaacoub (Blessed Abouna Yaacoub Haddad, 1875-1954, Capuchin, "Apostle of Lebanon") + saints hub card ("Beatified 2008") + sitemap entry. Single hand-authored page (not a mirror); structured data added by apply_seo_tags.py (WebPage + Article + FAQPage + BreadcrumbList). Not added to SAINT_STEMS single-Person list pending review (he is a single subject - candidate for future addition).

## Claim/source matrix (evidence gate)
- Born Feb 1 1875 Ghazir, third of five children; College de la Sagesse; Alexandria 1892; Capuchin convent Khashbau 1893; ordained Nov 1 1901 - Holy See official beatification biography (vatican.va news_services/liturgy/saints/2008/ns_lit_doc_20080622_haddad_en.html)
- Preacher 1903-1914 "Apostle of Lebanon"; Syria/Palestine/Iraq/Turkey; 24 volumes of sermons; French Capuchins left 1914, mission entrusted to him - Vatican bio; capuchin.org memorial page corroborates
- 1919 land at Jal el Dib, chapel Our Lady of the Sea + great Cross; 1920 founded Franciscan Sisters of the Holy Cross of Lebanon; Deir el-Kamar 1933; Hospital of Our Lady 1948; St Joseph's 1949; 1950 psychiatric hospital + St Anthony's House + Providence House - Vatican bio
- "230 schools for 7,500 students by 1910"; feast kept June 26 - capuchin.org (order's own page)
- 3.6M soup-kitchen meals Nov 1918-Jul 1919; "Vincent de Paul of Lebanon" - Wikipedia (en) article; framed without weight-bearing reliance
- Nearly blind + leukemia, lucid to end, died June 26 1954 - Vatican bio
- Cause 1979; miracle process 2005-2007; approved Benedict XVI; beatified June 22 2008 Beirut, Cardinal Jose Saraiva Martins - Vatican bio + Apostolic Letter (vatican.va rc_seg-st_20080621_beato-ghazir_lt.html)
- Tomb at Jal el Dib beside the Cross; beatification painting (Natalia Tsarkova) hangs above the tomb - Wikipedia; consistent with spec; asserted.

## Source conflicts resolved
- Sisters of the Holy Cross founding year: Vatican bio says 1920; Wikipedia says 1930. Page asserts 1920 (Holy See is the stronger, primary source). Noted here.
- "crowds at his funeral": NOT asserted (no primary source fetched).

## Media-rights ledger
- media/saints/abouna-yaacoub.webp: "Syrie. De Ghazir, vue vers le couvent des Capucins" by Andre Salles (1860-1929), 1893, Bibliotheque nationale de France - PUBLIC DOMAIN. Verified via Wikimedia Commons API (pageid 154631950). Converted locally (1200px, q82). Used on page hero + saints hub card.
- REJECTED: File:Jacob_of_Ghazir.webp on Commons - provenance traces to a fan wiki, missing US PD tag (media-rights discipline).

## Deferred cross-links (check_seo stage rule)
- /massabki-brothers link removed from Keep Reading (page not yet on stage) - relink after Massabki deploys.
- /st-estephan-nehme link omitted (page 404 until its bundle deploys) - relink after deploy.

## Verification
- QA: build-home-css, check_i18n_policy, i18n:test, check_seo, git diff --check, test_seo, test_prayer_mirror, test_i18n, nav-sync, dead-code, testimony-security, site-smoke - all PASS.
- Rendered review: desktop 1280 + phone 390 full-page captures of /abouna-yaacoub and saints hub - hero, sections, FAQ, Sources, footer, hub card all render correctly (captures in ship report).
- i18n baseline updated (per-file max-merge) after page commit.
