# Controlled analytics runner inventory

Bootstrap mode: retain identifiable QA tagging during validation. No GA property/filter settings are changed. Testing does not exclude the All Users total. A clean-audience report requires an explicit QA-excluding subset and verified coverage. Remaining audience is not guaranteed human.

## Repo-owned Playwright checks

Each named runner installs the explicit marker before first navigation and on every new context/page. Shared helper also intercepts GA transport for ordinary repo tests so local tests do not pollute production. The dedicated real-gtag proof test intercepts outgoing collect requests and never sends them to GA. Offline transport proof is a separate substitute, not a Google receipt.

| Runner | Source marker hook |
| --- | --- |
| `scripts/qa/hardini_full_review.cjs` | explicit helper |
| `scripts/qa/hardini_interaction.cjs` | explicit helper |
| `scripts/qa/mother_teresa_full_review.cjs` | explicit helper |
| `scripts/qa/mother_teresa_review.cjs` | explicit helper |
| `scripts/qa/peter_full_review.cjs` | explicit helper |
| `scripts/qa/peter_interaction.cjs` | explicit helper |
| `scripts/qa/rafqa_full_review.cjs` | explicit helper |
| `scripts/qa/rafqa_interaction.cjs` | explicit helper |
| `scripts/qa/storybook_joy_interaction.cjs` | explicit helper |
| `scripts/qa/storybook_joy_review.cjs` | explicit helper |
| `scripts/qa/storybook_reading_review.cjs` | explicit helper |
| `scripts/tests/analytics_qa.mjs` | explicit helper |
| `scripts/tests/analytics_qa_network.mjs` | explicit helper |
| `scripts/tests/checklist_improvements.mjs` | explicit helper |
| `scripts/tests/e2e_full_clickthrough.cjs` | explicit helper |
| `scripts/tests/eucharistic_collection.mjs` | explicit helper |
| `scripts/tests/eucharistic_locales.mjs` | explicit helper |
| `scripts/tests/home_letter_flow.mjs` | explicit helper |
| `scripts/tests/layout_audit.mjs` | explicit helper |
| `scripts/tests/navigation_gallery.mjs` | explicit helper |
| `scripts/tests/news_card_layout.mjs` | explicit helper |
| `scripts/tests/rosary_end_stage_rules.mjs` | explicit helper |
| `scripts/tests/rosary_intro_cta_behavior.mjs` | explicit helper |
| `scripts/tests/rosary_menu_behaviors.mjs` | explicit helper |
| `scripts/tests/rosary_prayer_behavior.mjs` | explicit helper |
| `scripts/tests/rosary_smoke.mjs` | explicit helper |
| `scripts/tests/rosary_ui_regression.mjs` | explicit helper |
| `scripts/tests/seo_runtime.mjs` | explicit helper |
| `scripts/tests/site_smoke.mjs` | explicit helper |
| `scripts/tests/story_floating_player.mjs` | explicit helper |
| `scripts/tests/testimony_ui.mjs` | explicit helper |

All `tests/*.spec.js` use `tests/qa-test.cjs`, whose automatic fixture marks the context; its browser fixture wraps manually created contexts/pages. `playwright.config.cjs` defines five viewport projects. CI Browser quality/QA workflows run those same sources. Plain HTTP SEO/deployment/IndexNow checks do not execute JavaScript and cannot send gtag events.

## Off-repo coverage

This integration lane: ad hoc rendered production checks use `integrator-live-proof` via pre-navigation init script, including all current Peter live-review/playthrough/shelf/AutoContinue scripts. Production byte watchers are HTTP-only. Historical visits are not retroactively excluded. Other lanes and third-party services remain an explicit coverage dependency owned by main; their declarations must be attached before claiming all controlled traffic excluded. Their adoption statements are not network proof.

## Required proof

- Normal unmarked control: auto pageviews/custom events across English homepage, Arabic homepage, story reader; no traffic_type.
- Monitoring: same navigation/events, `tt=qa_monitoring`, runner and kind.
- Analytics debug: same, traffic_type and distinct kind/debug flag.
- SessionStorage fallback/invalid marker cases and ordering checked separately.
- Live deployed bytes/render checks and final network captures required before closeout.

No broad IP/data-center rule. No exact excluded-user count inferred from page-check counts. No claim that past spike was our traffic.
