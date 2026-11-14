# Search review fix round

Base: reviewed search head 4accd15561c94db0ec44949dee3d8d0efb8d6001 plus stage d3111c5d2f57f50cd19ade22f8c20fcb70cc66e6. Stage merge preserves annaya_tier3_check and CI timeout changes.

- Focus trap derives visible enabled tabbable controls in DOM order on each Tab. Result options remain arrow-key driven and tabindex=-1.
- Description extraction matches attribute quote delimiters, handles opposite quotes/entities and reordered attributes. --check compares all excerpt fields, not just URL coverage.
- Unexpected sitemap skips fail by default; explicit allowed-skip set is empty. Tests cover missing source/title and noindex attribute order.
- Token dedup uses a null-prototype object; reserved Object.prototype words remain searchable.
- Four English short guides bootstrap existing search assets through their owning international template/generator. No translate.js addition or duplicate language selector. Other template consumer receives an empty slot; no film output change.
- Independent HTMLParser contract checks all 410 sitemap pages against descriptions and bootstrap coverage. Browser keyboard tests cover popular links, recent buttons, clear, close/focus return, result arrow navigation, and all four short guides on phone/laptop.

Focused results before full gate: 21 Node tests and 20 browser tests pass; source contract passes for 410 pages. Full QA is required separately on the final commit; this note is not acceptance.

Design scope: focus-handler behavior only in search.js; no CSS, header positioning, scroll padding, overlay markup, or motion changes. Visual inspection: EN/AR phone and EN desktop overlays plus English short-guide phone/desktop screenshots preserve the existing layout. Emulated Chromium only, not physical-device proof.

IndexNow: no new URLs; existing short guides gain search bootstrap only. Post-deploy verification remains required after approval.
