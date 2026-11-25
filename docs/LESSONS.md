# Marsharbel lessons, corrections and rules

Universal log for anyone working on [marsharbel.com](https://marsharbel.com): agents, Instinct, designers, marketers, and people. Read this before merch, site, rosary, or growth work. Follow the rules here. Joey's newer direct instruction wins if something here is older.

This file does not replace the site repo's `AGENTS.md`, which remains the engineering rulebook and should be updated when a new hard engineering rule lands. Instinct briefing technique stays in [instinct-playbook/lessons-log.md](instinct-playbook/lessons-log.md). Merch print-file application detail is in [merch-print-files-v5/APPLY.md](merch-print-files-v5/APPLY.md).

**No secrets.** Never add passwords, codes, tokens, keys, recovery phrases, or sign-in links to this file, the vault, chat, or the public repo.

Dates and times are America/New_York (ET) unless a source says otherwise.

Sources used to compile this file (24 Nov 2026): Joey's standing rules in durable memory (`/bot/rules`, `/bot/workstream/marsharbel-task-board`, `/bot/organization/marsharbel`); the Marsharbel.com CEO conversation and WhatsApp Messenger relays of Joey's and Instinct's corrections; this vault (`Projects/Marsharbel.md`, `task-board/board.md`, `growth-log.md`, `instinct-playbook/lessons-log.md`, merch audits and APPLY.md, `Decisions/2026-09-21 Marsharbel site.md`); and the site repo `AGENTS.md`. Nothing here was invented. Where a later instruction supersedes an earlier one, the later one is marked.

## How to append

1. Run `git pull --rebase` in `jnrahme/joey-projects-vault` first.
2. **New or changed rule:** add or edit a bullet in the matching section (Hard, Process, Store and merch, or Content). Note the date and who decided it (usually Joey). If it supersedes an older bullet, say so in that bullet and leave a short pointer rather than deleting history.
3. **New mistake or correction:** append one row to the table in section 5, at the bottom. Columns: Date | What went wrong | Correction | Rule that prevents it repeating. Keep it factual and short. Point at the rule in sections 1–4 when one exists.
4. Do not invent numbers, outcomes, or rules. If something is still an open question for Joey, say so. Do not record secrets.
5. Commit and push to the vault `main` branch. Also copy the updated file to `/workspace/marsharbel-lessons/LESSONS.md` so it can be added to the `jnrahme/marsharbel` repo (for example under `docs/`). If the engineering rule is new, update the site repo `AGENTS.md` in the same change set when you are working in that repo.

---

## 1. Hard rules

What never to do, and what stays Joey's call.

1. **Joey decides:** money, payments, cards, spending, agreements, sharing or using credentials, security settings, making the Shopify store public, product or file deletions he has not already approved, and other irreversible steps. Standing since he named a Marsharbel CEO on 10 Nov 2026, restated 11 Nov and 14 Nov (standing permission to brief Instinct as Joey does not cover these).
2. **Never** enable real payments, remove the store password, publish a store theme, spend money, or enter card information. The merch store (`marsharbel-test`) stays password-protected, Draft/test only, with no real payments until Joey approves release (standing, 10–12 Nov 2026). Leave product status and prices unchanged unless he says otherwise.
3. **Do not** let Instinct, or anyone else, reset the Shopify store password.
4. **Never** put passwords, codes, keys, or tokens in chat, in this vault, or in the public `jnrahme/marsharbel` repo. The repo has been public since 24 Sep 2026. Vault notes may name a credential's purpose, not its value.
5. **Never** complete Google "Verify it's you" / sign-in prompts, and never send "ready" or otherwise approve those prompts for Joey. If YouTube Studio or another Google surface asks him to confirm on his phone, wait for him.
6. **Do not** open WhatsApp Web to talk to Instinct. Instinct briefs go through the WhatsApp Messenger teammate, as Joey, and those sends need his approval on the exact message. An expired approval card is final: do not retry or reword it.
7. **Do not invent numbers.** Name the metric exactly (for example GA4 users vs sessions vs "daily users"), the date range, and the time zone, and say who measured it. Instinct "est." impact figures are judgment, not measured results (growth log, 20 Nov 2026). If you do not have a fresh export, say so.
8. **Verify, then announce** (Joey, after the 12 Oct 2026 Arabic-pages incident). Never say "live", "done", or "public", and never send a link, until the exact thing being shared has been checked and works. Applies to site pages, merch, rosary videos, and status reports.
9. **Do not claim** an external or native-speaker review took place if it did not (site repo `AGENTS.md`, editorial review).
10. **Stop all coding and new code briefs** (your own and Instinct's) once Joey's weekly usage reaches 90%. Check usage before heavy work (Joey, 16 Nov 2026).
11. **Paperclip board auth recovery is declined.** Do not run it. Track work on Instinct's side and in this vault until Joey says otherwise (Joey, 23 Nov 2026).
12. **Never pause the daily rosary** in English and Arabic, even when other lanes are blocked (standing, recorded on the project page).
13. **Language integrity** (hard rule, Joey, 12 Oct 2026, after the Arabic switcher incident): every new page ships in every language in the same release; localized pages must stay linked and structurally mirrored; any locale change gets a language-switcher and hreflang check before it is announced.
14. **Do not delete published URLs.** Deploys are throttled and must never wholesale overwrite or delete existing site files (Joey, 21 Sep 2026, after a manual upload took core files offline). Product deletions in the store also stay with Joey until he approves a specific delete.
15. **Do not add frameworks, new subdomains, or a second language control** unless Joey explicitly asks (site repo `AGENTS.md`). Keep the site simple. The existing top language selector is the one control on app pages.

---

## 2. Process rules

1. **North Star** (Joey, 19 Nov 2026, 11:19 PM): 1,000+ real human visitors a day (GA4) and Google page 1 for Saint Charbel searches. Instinct runs a daily growth check; the CEO does a live-site check; at least 10 growth tasks stay in progress; stuck work gets unblocked; work is logged on the [task board](task-board/board.md) and in [growth-log.md](growth-log.md).
2. **PRs go into `stage`.** Never push directly to `stage` or `main`. Cut a branch from the latest `stage`, open a PR, run the full QA gate, merge only when CI is green (standing since 24 Sep 2026; auto-merge on green CI is allowed without a further check with Joey, 11 Nov 2026, 11:45 AM). `stage` is production: a merge to `stage` deploys marsharbel.com. `main` is updated only by stage-to-main promote PRs.
3. **No-breakage rule** (Joey; wording used in briefs and restated in this work): before pushing anything live, run the full test suite and a quick smoke check of the main pages (home, saint pages, and any prayer or devotion pages, in the languages that exist, switcher included) to confirm nothing broke. If any test fails or a page errors, do not push — report what failed instead. Only push when everything passes. Merge only on green CI.
4. **Rendered review before done** (Joey, 27 Sep 2026; site repo `AGENTS.md`). CI green is a precondition, not the gate. Open the affected pages in a browser on desktop and phone. HTTP 200 and tests alone have shipped unstyled pages. If no browser is available, the work waits. Verify live after every merge. If something broke, roll back and report; do not hot-patch live files outside the merge flow.
5. **One merge at a time** (after the 10 Oct 2026 Hostinger webhook race): confirm live, then merge the next. Pause on red rather than stacking speculative changes.
6. **Spec-driven site work:** each change has a written spec with success criteria and ships as a PR into `stage` that must pass CI before merge (11 Nov 2026).
7. **Every brief gets a board row** (Joey, 19 Nov 2026) in `Projects/Marsharbel/task-board/board.md`: date sent, owner, task, priority, status (`sent` / `in progress` / `completed` / `dropped`), date completed, notes and links. Grouped by week starting Monday, ET. Update the row as replies come in. The same rule covers Instinct, Designer, Marketing, and CEO research.
8. **Make sure assets actually reach Instinct** (Joey, 20 Nov 2026). Send the files, upload them where they need to go, or share them through Joey's email that Instinct can read. Do not stop at describing them.
9. **Finished work only when showing Joey.** No Shopify "Example product" tiles, stock photos, empty spots, or other placeholders (Joey, 20 Nov 2026). Proof before done: PR links, live URLs, desktop and phone screenshots, per-item status.
10. **Take charge of steps that do not need Joey** (Joey, 11 Nov 2026), including confirmations, admin setup that is already authorized, and chasing Instinct. Message him only for things that require him or that he truly needs to understand (Joey, 20 Nov 2026). Standing permission (14 Nov 2026, 1:55 PM): speak to Instinct as Joey and get the work done; money, credentials, and going public still need him.
11. **When work stalls for a few days** (Joey, 24 Nov 2026 voice call): Instinct is the main driver, but use your own development power to unblock languages, SEO, and the Shopify store. Still follow the no-breakage, green-CI, and Joey-only rules. Keep this log where any agent or person working on the app can read it (the vault and the repo).
12. **Instinct briefs** follow the current rules in [instinct-playbook/lessons-log.md](instinct-playbook/lessons-log.md) (v2, 19 Nov 2026): priority label and one job per item; exact metric definitions; a list of what not to touch; pre-approve routine steps so work does not stall; say which brief supersedes which; measurable specs (inches, colors, URLs), not adjectives; product-type layout rules; ask for the exact blocker in words; one end-of-day report per daily job; every review gate names who clears it and how (no ownerless "Scrum" or native-speaker gates); reuse pipelines and assets instead of rebuilding by hand each day.
13. **PR-specific holds (as of 23–24 Nov 2026):** do not merge #947 until its review caveats are resolved, CI is green on the exact head that was reviewed, and the full suite plus smoke check pass. Do not merge #939; once the Scope B PR exists, close #939 with a pointer to that PR.
14. **Checkpoint work to an origin branch** at every milestone. Work must not exist only in scratch (a full storybook WIP was lost to a workspace wipe on 27 Sep 2026).
15. **Keep the Marsharbel dashboard "Work in progress" section current** whenever a brief is sent or status changes, and on every routine run (Joey, 19 Nov 2026, 11:20 PM).
16. **Growth is judged on GA4 and Search Console outcomes**, not on how many items shipped (Joey, 17 Oct 2026). Instinct's standing shipping target is at least 20 small PRs a day into marsharbel.com (Joey, 16 Nov 2026); that target does not override the no-breakage or green-CI rules.

---

## 3. Store and merch design rules

The test store stays password-on and unpublished. Apply these before any product is shown to Joey or left in the catalog. Every product must pass a measured check (true-scale mockups, readable text, matching CREAM and INK files) before he sees it (Joey, 20 Nov 2026: "pay attention to all the details and get this done right on all the merchandise").

### Placement

- **NOVHEM back** (Joey, 16 Nov 2026, tightened 20 Nov after the merch audit): back art is at most 12×12 in (12 in wide, centered, top about 4 in below the back collar seam), inside Printful's 12×16 back area. Do not use the "large 15×18" placement, which shrinks sizes M and below. No bottom captions, no MARSHARBEL.COM footers, rest of the back clean. This applies to current and future shirts.
- **Drop tees, measured Printful setting** (Joey, 22 Nov 2026, after checking the 4:16 PM sheets): keep the placement that already matched By His Wounds and He Is Risen, **3.3 in from the top of the print area**, 12 in wide. Instinct had offered to move it to a literal 4 in; Joey kept 3.3 in so the drop line matches those tees.
- **Front A:** 4 in wide left-chest mark (cross + MARSHARBEL). Top 3 in below the front collar seam; center 4 in toward the wearer's left of the center line (Joey, 20 Nov 2026, 12:08 PM).
- **Front B:** 9 in wide centered lockup with the verse reference, top 3 in below the front collar seam. Both fronts stay offered; the lockup does not replace the chest mark (Joey, 20 Nov 2026, restated when live products were discussed).
- **Zip hoodie and crew left-chest mark:** 3.6 in wide, fully on the left chest panel, clear of the zipper (passed 22 Nov 2026; 3.6 in matches the hoodie and crew, rather than a literal 4 in on the zip).
- **Zips stay Black only** for now; no new zip colors (Joey, 22 Nov 2026).
- Tee sleeve: centered in Printful's 4×3.5 in sleeve area. Hoodie sleeve: long vertical MARSHARBEL stack in the 3×12 in sleeve area. Inside label (tee): logo only, centered in the 3×3 in area.
- Check mockups at XS, M, and 5XL for each color.

### Ink and color

- **Black / INK art** on White, Ash, Natural, and Sand.
- **Cream ink only** on dark garments (black, navy, charcoal, forest, and other darks).
- Do not apply the optional two-colour Sand (`SAND-FIX-A`) files unless Joey approves them. His rule is black ink on Sand (APPLY.md).
- Print files should be 300 DPI, true alpha, no edge halos, and no semi-transparent fades (partial alpha prints as haze on DTG). Isolated dots below the print-floor should be grown before a file is applied (merch DTG audit, 22 Nov 2026).

### Galleries

- Show **back, then front**, for each color.
- **Group by color** (all of color A's images, then all of color B's), and link each variant to its own color's photos (Joey, 20 Nov 2026).
- Open with the printed side, never a blank side (Joey, 20 Nov 2026).
- **No side views.** Instinct began removing them from every color and every later build on 22 Nov 2026; keep galleries to one back and one front per color unless Joey asks for more. Drop only exact duplicates.

### Art and copy

- **Joey rejects AI-looking merch art** ("AI slop") on tees, mugs, and totes (14–17 Nov 2026 and the 20 Nov audit). New work may use a tattoo / pencil-sketch / crosshatched ink look as a style guide only, not a copy of someone else's drawing.
- **Keep the original Jesus Saves face** exactly as it is. Do not swap faces. Do not use Dürer, "peaceful" face options, or other face-option files (APPLY.md; Joey, 20–22 Nov 2026). An earlier 20 Nov note that he preferred a peaceful public-domain Christ after rejecting a tortured-looking face is superseded for Jesus Saves by this keep-the-original rule.
- **No captions or footers on the art.**
- Scripture must be a standard translation, checked word for word: cite **1 Peter 1:18-19** (not 1:19 alone); Iron Sharpens Iron uses a standard rendering (for example NIV/NASB/NABRE "one person sharpens another"), not The Message's "one friend sharpens another"; **WITH HIS STRIPES** for the KJV Isaiah 53:5 design (20 Nov 2026 audit and Joey's "fix all of them").
- Liked references: black streetwear designs A Pray For Us and B Saint Charbel Back (halftone face). Design C Heart of Annaya was rejected (14–17 Nov 2026).
- Saint Benedict Medal: apply **v2** (12×12 back), not v1. The Iron Sharpens Iron alternate "as one friend" files are reference only; do not apply unless asked (APPLY.md).
- Live backs A, B, J1, and J2 are dark-garment (CREAM) only in the v5 set; there is no light-garment INK file for those four. Live D has both.
- Homepage and catalog: keep the layout, fill every section with real Marsharbel products, art, and Saint Charbel copy. No empty spots or stock photos, still on the draft/password theme (Joey, 20 Nov 2026, ~12:46–12:50 PM).
- Show apparel, mugs, totes, and tumblers in ways that fit the product type (do not hang a mug on a shirt rail).

---

## 4. Content rules

Rosary, prayers, saints, accuracy, and AI.

### Accuracy and sources

- Re-derive factual claims from primary sources before shipping (Holy See, UNESCO, and other cited sources). Do not ship claims from memory or from competitor sites (site repo `AGENTS.md`).
- Original content only: nothing copied from competitors, no thin or AI-looking pages.
- Use "Letters", never "testimonials".
- Journalist-quality pages: images, videos, links, references. Pictures on every page.
- Keep the site's independent status clear, and distinguish original devotions from traditional or official texts.
- Do not invent traffic, ranking, or inventory numbers. Quote the export and its dates.

### AI and images

- **Content pages:** real photos from referenced sources, with rights recorded. Never generated or animated images on content pages. Storybook art is the one exception: painterly illustration (Joey, standing, site repo `AGENTS.md`).
- **No thin or AI-looking pages.** Merch follows the same bar (section 3).
- Licensed images and type-led motion only when a social post is briefed; no AI faces or AI art of the saint (brief to Instinct, 20 Nov 2026).
- Outreach follows Joey's godly-outreach voice (research the recipient, warm, humble, scripture-true, humanized, signed "In Christ, Joey Rahme"). **The gallery/AI line stays out** of those drafts (project page operating conventions, 4 Oct 2026).
- This log does not record a standing requirement to add a public "AI disclosure" label on pages. The standing rule is not to ship generated images or AI-looking merch and pages in the first place. If Joey later requires a disclosure line, add it here and in `AGENTS.md`.

### Languages, prayers, and saints

- Translations mirror the English page exactly; only the text changes. Every new or changed user-facing string lives under `locales/<language>/` with a stable message ID. Published pages must not silently fall back to English or machine translation to hide missing catalog text. Do not replace real translations with English copied into every locale. Validate meaning, not only structure (site repo `AGENTS.md`).
- Language-switcher and hreflang checks before announcing any locale change (section 1).
- Delete no URLs. The `/prayers` 301 and similar redirects ship as their own PRs, with the no-breakage gate.
- Saint of the Day cards need the language checks for every published locale before merge (for example the 24 Nov 2026 Saint Catherine card: all 11 language checks passed, then the full suite before the PR).
- Storybooks: scripts from primary sources; no miracle promises; reported experiences framed as reported; composite scenes flagged as composite. Each book needs English narration and must pass the source and Bible-reference gates before it is treated as finished (Joey correction, 22 Nov 2026). Every storybook ends with a "Points of reflection" outro (3–5 points). Checkpoint to origin as the book is built.

### Daily rosary (YouTube, Marsharbel channel)

- Never pause the English and Arabic daily rosary habit.
- Upload **Private** first, wait for copyright checks to come back clean, then set **Public**. Do not upload a packet that has failed its check.
- Do not trash a Drive packet until that date's video is confirmed Public.
- Do not re-upload a video that is already Public.
- Do not claim a day's rosary is missing, red, or unpublished without opening the live channel. Status must be verified (see the 23 Nov 2026 entry in section 5).
- Hold or replace packets with known defects, including a smeared closing card (original Nov 24, Nov 27, and Dec 1 English packets; use the corrected 23 Nov 6:47 PM packets) and the "we meditating" line in the concluding prayer (Dec 13, 14, and 15). If a defective version was already scheduled, set it to Private until the fixed version replaces it.
- Other recorded defects that blocked publish: the Nov 22 English master briefly showed the Nov 18 Saint Odo card; the Nov 23 English closing Versicle and Response was doubled; Arabic had a Creed text error and, at one point, a missing saint opening. Each had to pass its repair check before going public.
- Arabic packets may be uploaded to the same Marsharbel channel (Joey, 24 Nov 2026). Leave later Arabic packets in Drive for the morning upload if Instinct's YouTube picker fails; do not require Joey to upload them himself unless he chooses to.

---

## 5. Dated mistakes log

Append new rows at the bottom. Dates are ET.

| Date | What went wrong | Correction | Rule that prevents it repeating |
|---|---|---|---|
| 2026-09-21 | A manual Hostinger upload took core site files offline. Files from earlier commits had never reached the server, and a stale "all fine" report made it worse. | Joey set deploy rules: a deploy is not done until a full-site crawl against the repo passes; run the full QA gate before reporting done; never wholesale overwrite or delete existing files; a reported visual problem gets a top-to-bottom pass; verify a fresh `stage` pull and the live server before asserting the site is fine. `stage` later became the working branch, with PR + green-QA merges. | Hard rule 14; process rules 2–5; verify-then-announce (hard rule 8). See `Decisions/2026-09-21 Marsharbel site.md`. |
| 2026-09-22 | Extra language menus were added when the app already had a language selector at the top. Joey did not want the additional menus. | Keep a single language control (`#sc-language-select`) on existing app pages. Reuse existing UI; do not add a second control for the same purpose. Add a regression check when fixing a duplicate control. | Hard rule 15; site repo `AGENTS.md` "reuse existing controls". |
| 2026-09-27 | A hub shipped unstyled while returning HTTP 200. Test-only verification was treated as enough. | Nothing merges, deploys, or is reported done without a rendered review on desktop and phone. CI green is a precondition, not the gate. | Process rule 4 (golden rule). |
| 2026-09-27 | A full storybook's work-in-progress existed only in scratch and was lost to a workspace wipe. | Checkpoint production work to an origin branch at every milestone. | Process rule 14. |
| 2026-10-10 | Hostinger git-integration and a manual deploy raced, after merges were stacked. | One merge at a time: confirm live, then the next. After every merge, wait for the git-integration sync before a TUS deploy. Pause on red. | Process rule 5. |
| 2026-10-12 | Arabic pages were reachable by direct URL but not from the language switcher. An announcement went out with a wrong link. | Language-integrity hard rule: ship every language together, keep switcher and hreflang working, and never announce until the exact link and switcher path are verified. | Hard rules 8 and 13. |
| 2026-11-10 | An unbounded `pip install beautifulsoup4` pulled SoupSieve 4.0, which changed selectors and broke QA parsers that need the reviewed 2.10 behavior. | Install QA dependencies with `pip install -r scripts/qa/requirements.txt`. Dependency upgrades need explicit compatibility tests. | Site repo `AGENTS.md`, "QA parser reproducibility". |
| 2026-11-14 to 16 | Instinct's back-print tees came back too tall, with bottom captions, not Joey's placement. | Give exact measurements in every brief: top about 4 in below the collar, 12 in wide, centered, no captions. Later tightened to a 12×12 in maximum because Printful's back area starts near the collar. | Store placement (NOVHEM); Instinct brief rule 6 (measurable specs). |
| 2026-11-16 | The 20 PRs-a-day shipping target stayed at about 1–3 PRs a day. | Break work into many small named PRs, track counts daily, and do not wait on ownerless review gates. The target still does not override no-breakage or green CI. | Process rules 12 and 16; Instinct brief rule 1. |
| 2026-11-11 to 19 | Daily news and other handoffs stalled for days without a clear blocker. | Ask for the exact blocker (check, gate, reviewer, approval) before asking for a fix. | Instinct brief rule 9. |
| 2026-11-18 to 19 | The daily English rosary sat unpublished waiting on Joey's yes for a YouTube re-verify. | Pre-approve routine steps. Only money, agreements, credentials, and going public stay with Joey. Do not complete Google sign-in prompts for him. | Instinct brief rule 4; hard rule 5. |
| 2026-11-19 | A hanger-rail showroom went up fast, but the rail was choppy, a mug hung on a hanger, and products were not prominent. | Spell out how each product type is shown (apparel on the rail; mugs, totes, and tumblers in their own sections). | Store rules, product-type display; Instinct brief rule 7. |
| 2026-11-19 | An older hanger-rail brief and a newer redesign were both in flight. | When a brief replaces an older one, say "this replaces X". | Instinct brief rule 5. |
| 2026-11-19 | A 28-day GSC/GA4 export labeled total users as "daily users", and a script was added to Joey's private analytics repo without asking. Instinct flagged both itself. | Define metrics exactly, and say where files may and may not go. Do not invent or relabel numbers. | Hard rule 7; Instinct brief rules 2 and 3. |
| 2026-11-19 | Language reviews were stuck for weeks on a "Scrum" or native sign-off that nobody gives, which contradicts `AGENTS.md`. | Never create a review gate with no owner. Every gate names who clears it and how. Joey's rule is: research sources and use best judgment; external reviewers are not a required gate. | Process rule 12; Instinct brief rule 19. |
| 2026-11-20 | Front art sizing and placement on merch were wrong. Live backs sat about 1.4 in below the collar, chest logos were 2.4–3.0 in from center, several backs still had caption bars and MARSHARBEL.COM footers, and some files were taller than the 12×16 area with a 4 in drop. Joey said "fix all of them." | Recompose backs to at most 12×12 in at the NOVHEM drop; move chest marks to Front A (4 in) or Front B (9 in); strip captions and footers; measure before showing Joey. | Store placement rules; process rule 9. |
| 2026-11-20 | Merch used an AI-generated, upscaled Christ face, and a tortured-looking face was shown. Joey rejects AI-looking art. Ink was also mismatched: cream on Ash and White (art disappears) and dark ink on a Black tote. | Do not put an AI face on any product. Match INK to light garments and cream to dark only. For Jesus Saves, keep the original face; do not swap it for a replacement. | Store art and ink rules. |
| 2026-11-20 | Scripture on merch was wrong or loosely paraphrased: Covered By His Blood cited 1 Peter 1:19 only; Iron Sharpens Iron used The Message wording "as one friend sharpens another" while calling it the full verse. | Cite 1 Peter 1:18-19. Use a standard translation for Iron Sharpens Iron. Check verses word for word before a file is applied. | Store art and copy (scripture). |
| 2026-11-20 | Semi-transparent pixels in new back files (about 4–22%) risked DTG haze. | Re-export CREAM and INK backs with a hard threshold or dither (target at or near 0% partial alpha). Confirm with the print-file verifier before applying. | Store ink and file-quality rules. |
| 2026-11-21 | Light-garment INK backs dropped out the cross fill, leaving a broken outline (It Is Finished and others). | Rebuild the ink cross as a solid shape and audit every INK back against its cream twin before relinking. | Store ink rules; measured check before Joey sees a product. |
| 2026-11-22 | Product galleries included side views, and some opened on a blank side (for example Peace in Prayer Classic Light Tee). | Galleries are back then front, grouped by color, printed side first, no side views. | Store gallery rules. |
| 2026-11-22 | With His Stripes backs were not on the same drop as the other drop tees. Ave Maria zip fronts were blank. The Jesus Saves zip chest mark was clipped by the zipper so only part of MARSHARBEL showed. | Joey kept the 3.3 in-from-top placement that matches By His Wounds and He Is Risen. Zip fronts got a 3.6 in left-chest mark, clear of the zipper. Zips stay Black only. Deletes of damaged drafts wait for Joey. | Store placement, zip, and Joey-only deletion rules. |
| 2026-11-22 | The Nov 22 English rosary master showed the Nov 18 Saint Odo card after the intro. The Arabic master had a Creed text error (and later a missing saint opening). The Nov 21 Facebook rosary promo was missed. | Hold the films until an independent check passes, then publish. Confirm the wrong card is gone and the Creed is fixed before sending public links. Do not announce a publish that has not been verified. | Content, rosary checks; hard rule 8. |
| 2026-11-23 | The Nov 23 English rosary had a doubled closing Versicle and Response. Earlier English packets for Nov 24, Nov 27, and Dec 1 had a smeared closing card. Dec 13 (then 14 and 15) used the line "we meditating" in the concluding prayer. | Repair from existing audio, rerun the speech-to-text check, and post a corrected packet marked as fixed. Skip smeared originals; use the corrected 6:47 PM packets for those three dates. Do not upload Dec 13–15 until the "meditating" line is fixed; if a bad version was scheduled, set it to Private until it is replaced. | Content, rosary defect holds. |
| 2026-11-23 | A four-job status check marked the rosary lane red, but the Nov 23 English video was already Public on the Marsharbel channel. | Verify the live video (or channel) before reporting rosary status. Do not invent or pass through an unchecked red/yellow/green. | Hard rules 7 and 8. |
| 2026-11-22 to 24 | Messages to Instinct that needed Joey's approval expired unanswered (including a 23 Nov 8:16 PM daily check and later held replies). Retrying would have broken the approval rule. | Hold the exact draft. Do not resend or reword it unless Joey approves that send. An expired card is final. | Hard rule 6. |
| 2026-11-24 | Assumed main was the live site. | marsharbel.com serves stage via the Hostinger sync, so every stage merge is a live push and must pass the full suite and smoke check first. | Process rules 2–4. |
