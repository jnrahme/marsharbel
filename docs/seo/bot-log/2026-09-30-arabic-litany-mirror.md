# Arabic Litany mirror, 30 September 2026

Reader promise: pray all twenty-nine Saint Charbel invocations in Arabic, with the same guide, FAQ and source links as the English master.

Based on stage ba29d9a and its English `litany-of-saint-charbel.html`. The Arabic copy is explicitly a translation of that English traditional text, not a claimed monastery Arabic edition. All eight sections, six prayer paragraphs, 29 invocation/response pairs, closing collect, portrait, CTA set and five FAQs are preserved. The generator fails when any English visible slot changes without translation review. Original source URLs remain unchanged:

- https://www.charbelfriends.com/lang3/litany_and_prayer.html
- https://mothersforpriests.org/wp-content/uploads/2020/07/jumbo-litany-of-saint-charbel-1.pdf

Authored route: `/ar/litany-of-saint-charbel`, self-canonical, reciprocal English/Arabic/x-default links, localized FAQ schema and registry/sitemap routing. Chaplet links stay English until the separate queued Chaplet registry entry exists; the generator then maps them to Arabic. No new media or rights claim is introduced.

Verification: reproducible build, localization policy and SEO coverage (240 pages) passed; 82 Python tests passed, including DOM parity, 29-response count, FAQ/schema equality and deliberate master-drift rejection. 74 small-phone international browser tests passed. Local HTTP renders at actual 390px and 1440px loaded the portrait, used RTL, had no horizontal overflow or JS errors, and the full-litany CTA reached #the-litany. Full-page phone/desktop captures and enlarged prayer/hero crops were visually inspected. Full QA was attempted but its 95-second time limit ended during site smoke; no full-suite pass is claimed.

Preview font prerequisite: stage CSS requests v3 Arabic fonts absent from the repository. Both are live production-only assets returning 200 with font/woff2; temporary copies from production were used only for local preview, excluded from this change. Main confirmed the integrator owns reconciling these assets into stage. Not a live regression or a Litany handoff blocker.

Live locale hub checkpoint: English and seven locale homes returned 200 with their own canonical and the same reciprocal nine-entry hreflang map. No material change. This is byte/markup verification, not a new rendered production review.

Done definition: integrated on current stage, complete full QA and independent final-artifact review, then production byte checks plus rendered desktop/phone proof and reciprocal language-selector/navigation verification. Next ship target: next integrator train after QA; no publication time confirmed. Merge/deploy/live verification remain with integrator and Main. This entry records a review handoff, not a live completion.
