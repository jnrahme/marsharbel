# G3 RTL render test - book reader with Arabic body (Oct 23, 2026 ~7:00 ET)

Method: test-only local render, NOT committed to any production path. Worktree /tmp/longinus-wt @ 37553e5f: storybook.js map locally patched (longinus entry gains `ar: window.LONGINUS_STORY_AR || []`), plus two uncommitted local files (longinus-ar-test-data.js carrying the Longinus AR draft v1 37553e5f, rtl-test.html copy of the built book page). Served locally, Playwright 1.58.2 Chromium, 390x844 DPR2 and 1280x800, ?story=longinus&lang=ar. Screenshots: ar-p1-phone, ar-p2-phone, ar-last-phone, ar-p1-desktop, en-p1-phone (baseline).

VERDICT: the reader's RTL support WORKS. frame dir=rtl + is-rtl class applied; Arabic text shaped and right-aligned correctly; pagination next/prev reversed correctly (next on the right, page advanced 1->2); page dots fill right-to-left; per-page plates swap correctly; no console/page JS errors. The "template is LTR English-only" assumption in G3 is stale for the reader frame itself.

DEFECTS FOUND (real, small):
D1 Resume chip mixes languages: storybook.js line 1669 hardcodes `Continue from ${UI.pagePrefix} ${lastPage+1}?` - "Continue from" and "?" stay English inside an Arabic UI (visible on desktop shot). Affects ar and fr. Fix: move the whole template into COPY.
D2 (design adjudication needed): desktop two-page spread keeps text-left/image-right geometry in RTL; for an RTL book the start page arguably belongs on the right. Phone stacking is unaffected.
D3 Page indicator uses Latin numerals inside the AR sentence ("الصفحة 1 من 10"). Readable and common, but a localization choice to record, not an error.

ASSEMBLY REQUIREMENTS surfaced (not reader defects):
A1 Book page H1/subtitle/meta come from the page template in EN; an AR assembled book needs localized title/subtitle/meta (translate.js only covers chrome).
A2 Evidence panel copy localizes via COPY, but the per-page evidence CLAIM text is author content - every AR book needs translated evidence claims (test used EN evidence text by design).
A3 All-books link "/stories" 404s on a bare static server without the live rewrite rules; verify on stage before any AR release.
A4 Read-aloud audio absent for AR - BLOCKED on Joey's audio decision (unchanged); the UI button renders fine with no AR pack.
A5 Test data carried no tashkeel; the Isaiah AR body HAS full tashkeel - spot-check one Isaiah page in the same harness before its assembly (font rendering of diacritics).

Quota/spend: none. No generation, no audio, no publish.
