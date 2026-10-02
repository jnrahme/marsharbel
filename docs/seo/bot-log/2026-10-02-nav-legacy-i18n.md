# Legacy navigation locale integration candidate

Based on content/nav-legacy c2ef0a3 (scripture v3 base b4c2c2f). Includes only patch 2/2 fced41c for chaplet/feast trails; patch 1/2 was already present.

Reviewed six-locale header/trail strings and qualifiers came from the parent's independent editorial review. Arabic approval inspected in the owner's WhatsApp history: wamid.HBgLMTQwNDQzNzUzNzMVAgASGBQzQjkwNjIzN0M2RjIwNThFNEMwOAA= at 2026-10-02 17:49:09 EDT, replying 'yes also...' after asks at 17:41:52, 17:42:03 and 17:45:24. Those asks cover the four labels, standard trail and English qualifier. Arabic history variant was not included and is deliberately absent; the renderer fails if requested. No native attestation claimed for six other languages.

Retired header.story, header.storyForChildren, header.latestNews. Added legacy, encyclopedia, childrenBooks, news. Gallery and Saints are retained and moved. English-only encyclopedia destinations retain their canonical route, with hreflang=en, translated accessible name plus localized qualifier. The separate qualifier span inherits the page language. Nav child has a layout wrapper around sibling link/span. Legacy parent's accessible name discloses English; visible disclosure sits in its child item to avoid duplicating the menu qualifier.

MAIN against c2ef0a3 changes only EN/AR chaplet+feast trail markup. Feast gains five exact source-guarded slots, not an exemption. Chaplet intro excludes enc-trail. Existing complete history link remains /history, not the shorter Arabic biography guide.

Tour helper reused from the reviewed tour package: EN/AR only, second under Travel. Other locales do not inherit the new English tour item. No MAIN mutation from header postprocessing.

Producer evidence: 18 mirror tests, 3 trail/nav tests, build freshness, policy, 133 English nav-sync, 270-page SEO pass. Browser checks at 390/1440: exact Arabic trail DOM text, English destination disclosure, no page horizontal overflow; real menu click reaches English Encyclopedia. Inspected actual phone and desktop screenshots for trails and open menus. Initial qualifier layout was visually detached; fixed wrapper/CSS and rechecked actual pixels. Final Arabic menus readable, qualifier alongside/under its own child title, no duplicate top-level visible hint.

Not a publication claim. Pending independent rendered copy/visual gate, final current-stage rebase/full QA, German exact-candidate MAIN slot and chrome reconciliation, production proof by merge lane. No translated hub pages added.
