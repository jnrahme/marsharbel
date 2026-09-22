# marsharbel.com — LLM Codebase Reference

> This document is the single source of truth for any LLM (Claude, GPT, Copilot, etc.) working in this repository. Read this first. Every section exists to prevent a specific class of mistake.

## What This Project Is

A static Catholic devotional website for Saint Charbel Makhlouf (marsharbel.com). No build step, no bundler, no framework. Every file in root is served directly. Vanilla HTML + CSS + JS. Hosted on Hostinger (production) with Netlify PR previews.

**Live site**: `https://marsharbel.com`
**Preview pattern**: `https://pr-{NUMBER}--{SITE}.netlify.app`

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Project Structure](#project-structure)
3. [How Pages Work](#how-pages-work)
4. [JavaScript Architecture](#javascript-architecture)
5. [CSS Architecture](#css-architecture)
6. [The Rosary System](#the-rosary-system)
7. [The Storybook System](#the-storybook-system)
8. [The Voice Testimony Page](#the-voice-testimony-page)
9. [The Floating Audio Player](#the-floating-audio-player)
10. [localStorage Keys](#localstorage-keys)
11. [Window Globals](#window-globals)
12. [Custom Events](#custom-events)
13. [Testing Infrastructure](#testing-infrastructure)
14. [How to Write a New Test](#how-to-write-a-new-test)
15. [CI/CD Pipeline](#cicd-pipeline)
16. [Git Workflow](#git-workflow)
17. [Adding a New Feature — Step by Step](#adding-a-new-feature--step-by-step)
18. [Common Pitfalls](#common-pitfalls)
19. [Dead Code Rules](#dead-code-rules)
20. [File Reference Tables](#file-reference-tables)

---

## Quick Start

```bash
# Prerequisites: Node 20+, Python 3 (for local server)
npm ci                       # Install Playwright
npm run qa                   # Run full QA suite (starts server, runs all tests)
npm test                     # Quick smoke test only
```

The pre-push git hook runs `npm run qa` automatically. If tests fail, the push is blocked.

To serve the site locally for manual testing:

```bash
python3 -m http.server 4173  # Then open http://127.0.0.1:4173
```

---

## Project Structure

```
marsharbel/
├── *.html                       # 22 root-level pages (served directly)
├── mysteries/                   # 20 rosary mystery pages (joyful-1..5, luminous-1..5, etc.)
│   └── {set}-{number}.html      # Each page loads mystery-meditation JS
├── media/
│   ├── rosary/                  # ~260 MP3 clips organized by mystery
│   │   ├── joyful_1/step-01.mp3..step-13.mp3
│   │   ├── prayers/             # Shared prayer audio (our_father.mp3, hail_mary.mp3, etc.)
│   │   └── manifest.json        # Clip metadata (paths, durations)
│   ├── storybook/               # Story narration audio by language
│   │   ├── en-elevenlabs/       # ElevenLabs voice pack
│   │   ├── en/                  # Studio British voice pack
│   │   ├── ar/                  # Arabic voice pack
│   │   ├── fr/                  # French voice pack
│   │   └── images/              # Story page illustrations
│   └── voice-lab/               # Voice evaluation tools
├── gallery/                     # Photo gallery images
├── transcripts/                 # Testimony transcripts (ar, en, publishing, whisper, fullcapture)
├── book-pages/                  # Scanned source book pages
├── pwa/                         # PWA icons (192px, 512px, apple-touch-icon)
├── scripts/
│   ├── qa/                      # QA orchestration scripts
│   │   ├── run_full_qa.sh       # Main QA runner
│   │   ├── dead_code_check.sh   # Dead code detection
│   │   └── agentic_smoke.sh     # Accessibility snapshot capture
│   └── tests/                   # Playwright test files
│       ├── *.mjs                # 9 test suites (ESM, headless Chromium)
│       └── run_*.sh             # Shell wrappers (start server + run tests)
├── .github/workflows/           # 6 CI/CD workflows
├── styles.css                   # Global styles (design tokens, layout, components)
├── storybook.css                # Story page styles
├── app.js                       # Reveal animations + Lent countdown
├── global-audio-player.js       # Floating audio dock + RosaryAudioContext
├── translate.js                 # 100+ language translation via Google Translate API
├── mystery-data.js              # All 20 mystery definitions with i18n
├── mystery-library.js           # Scripture readings + reflections per mystery
├── mystery-meditation.v20260304.js  # Rosary meditation engine (1500 lines)
├── storybook.js                 # Story page engine (1100 lines)
├── gallery.js                   # Gallery lightbox
├── testimonies.js               # Supabase testimony fetcher
├── service-worker.js            # PWA offline caching
├── manifest.webmanifest         # PWA manifest
└── package.json                 # Only devDependency: playwright
```

---

## How Pages Work

Every page loads the same 3 shared scripts (in this order at bottom of `<body>`):

```html
<script src="./app.js"></script>           <!-- Reveal animations + Lent countdown -->
<script src="./global-audio-player.js"></script>  <!-- Floating player + RosaryAudioContext -->
<script src="./translate.js"></script>     <!-- Language switcher + i18n -->
```

Mystery pages load additional scripts:

```html
<script src="../mystery-data.js"></script>
<script src="../mystery-library.js"></script>
<script>
  window.MYSTERY_KEY = 'joyful_1';
  window.MYSTERY_BASE = '../';
  window.ROSARY_AUDIO_VERSION = '20260302-intro-audio-fix';
</script>
<script src="../mystery-meditation.v20260304.js"></script>
```

The story page loads:

```html
<link rel="stylesheet" href="./storybook.css" />
<script src="./storybook.js"></script>
```

**Important**: Script load order matters. `global-audio-player.js` must load before page-specific scripts because it creates `window.RosaryAudioContext` which other scripts read.

---

## JavaScript Architecture

### No Build Step

All JS files are vanilla ES5/ES6 IIFEs or top-level scripts. No modules, no imports, no bundler. Scripts communicate via:

1. **Window globals** (e.g., `window.RosaryAudioContext`, `window.ROSARY_MYSTERIES`)
2. **localStorage** (merge-based writes for audio context)
3. **Custom DOM events** (e.g., `rosary-audio-context-updated`)
4. **Direct DOM manipulation** (getElementById, querySelector)

### File Responsibilities

| File | What It Does | Creates Globals |
|------|-------------|----------------|
| `app.js` | IntersectionObserver for `.reveal` animation, counter animation, Lent countdown | None |
| `global-audio-player.js` | Creates floating audio dock, manages playback state | `window.RosaryAudioContext` |
| `translate.js` | Language switcher, Google Translate integration, RTL support | `window.__scTranslateInitialized`, `window.__scApplyTranslation` |
| `mystery-data.js` | All 20 rosary mystery definitions (titles, fruits, steps, i18n) | `window.ROSARY_MYSTERIES` |
| `mystery-library.js` | Scripture readings and reflections for each mystery | `window.ROSARY_MYSTERY_LIBRARY` |
| `mystery-meditation.v20260304.js` | Rosary meditation orchestrator (stages, audio, timer, navigation) | `window.RosaryNarrationController` |
| `storybook.js` | Story page rendering, narration, voice packs, reader mode | Overwrites `window.RosaryNarrationController` |
| `gallery.js` | Lightbox with keyboard navigation | `window.__closeGallery` |
| `testimonies.js` | Fetches/renders approved testimonies from Supabase | None |
| `service-worker.js` | PWA offline cache (cache name: `st-charbel-pwa-v2`) | None |

---

## CSS Architecture

Two CSS files, no preprocessor:

### `styles.css` — Global (1944 lines)

Design tokens as CSS custom properties:

```css
--bg: #0d1418;            /* Dark background */
--panel: #121d23;         /* Card/panel background */
--text: #f4efe6;          /* Light text */
--gold: #d3b26e;          /* Primary accent (gold) */
--gold-soft: #b89658;     /* Softer gold */
--line: rgba(211, 178, 110, 0.28);  /* Borders */
--ok: #a3d39c;            /* Success */
--warn: #f3cf8f;          /* Warning */
```

Fonts: **Cormorant Garamond** (serif, headings) + **Manrope** (sans-serif, body)

Layout: `site-shell` container at `min(1180px, 100% - 2.4rem)` centered.

Key classes:
- `.reveal` — Fade-in on scroll (handled by `app.js` IntersectionObserver)
- `.card` — Content card with border and gradient background
- `.btn.primary` / `.btn.subtle` — Button variants
- `.grid-2` — Two-column responsive grid
- `.hero` / `.kicker` — Page hero sections
- `.topbar` — Sticky navigation header with backdrop blur
- `.floating-audio` — Floating player dock (created by JS, styled here)
- `.meditation-actions` — Sticky rosary controls bar

### `storybook.css` — Story-specific (1237 lines)

Scene illustrations (CSS-drawn: mountains, moon, clouds, figures, candle, cross), page turn animations, evidence panel, reading indicator, rate controls, reader mode styles, resume banner, auto-continue toggle. All storybook-specific UI.

---

## The Rosary System

This is the most complex part of the codebase. Understanding it prevents most bugs.

### Mystery Page Template

Each of the 20 files in `mysteries/` follows the same pattern. They set 3 window globals then load the meditation engine:

```javascript
window.MYSTERY_KEY = 'joyful_1';           // Which mystery this page is
window.MYSTERY_BASE = '../';               // Path prefix to root
window.ROSARY_AUDIO_VERSION = '20260302-intro-audio-fix';  // Cache buster for audio clips
```

### Stage System

Each mystery is broken into ordered **stages** (not individual steps). The stages array:

```
intro_prayers    — [OPTIONAL] Apostles' Creed + Our Father + 3 Hail Marys + Glory Be
lecture          — Receive the Mystery (narration + Scripture intro)
our_father       — Listen to the Word (Scripture reading + Our Father)
hail_mary × 10  — Meditation 1-10 (each mapped to mystery.steps[])
decade_closing   — Glory Be + Fatima Prayer
end_prayers      — [OPTIONAL] Hail Holy Queen + Concluding Prayer
```

**When intro/end appear**: Only when navigated with `?stage=intro` or `?stage=end`, OR when it's the last mystery in an active full-rosary session.

### Audio Playback

Two modes with fallback:

1. **Prerendered clips** (primary): MP3 files from `media/rosary/{mystery_key}/step-{NN}.mp3`
2. **Prayer sequence** (fallback): Individual prayer MP3s chained together

All clip paths get a version parameter: `step-01.mp3?v=20260302-intro-audio-fix`

### Narration Controller

The meditation engine exports `window.RosaryNarrationController`:

```javascript
window.RosaryNarrationController = {
  play: () => playVoice({ userInitiated: true }),
  togglePause: togglePauseVoice,
  stop: () => { stopVoice(); ... },
  next: nextStage,
  previous: () => { ... }
};
```

The floating player calls these methods when the user clicks its buttons.

### Auto Timer

A per-stage countdown (12s, 18s, or 25s). After narration completes, timer counts down, then auto-advances to next stage. The button shows `"Auto: {N}s"` during countdown.

### Active Rosary Session

Stored in `localStorage` as `rosary_full_session`:

```javascript
{
  active: true,
  set: 'joyful',
  sequence: ['joyful_1', 'joyful_2', 'joyful_3', 'joyful_4', 'joyful_5'],
  currentKey: 'joyful_1',
  autoPrayer: true,
  startedAt: Date.now()
}
```

When last mystery in sequence finishes, session clears and user returns to rosary guide.

### Request ID Pattern (Race Condition Prevention)

```javascript
let playbackRequestId = 0;
const nextPlaybackRequest = () => ++playbackRequestId;

// Every audio operation gets an ID. Callbacks check:
if (!isActivePlaybackRequest(requestId)) return;
// This prevents stale callbacks from previous stages interfering
```

---

## The Storybook System

`storybook.js` renders an interactive story with narration.

### Key Concepts

- **Pages**: Array of story page objects with title, body, prayer, heart, scene, evidence, audio
- **Voice Packs**: ElevenLabs (recommended), Studio, or Browser TTS fallback
- **Evidence**: Each page has sourced evidence (Vatican documents, monastic archives)
- **Reader Mode**: Toggle for larger fonts/padding, persisted in localStorage
- **Resume Banner**: Saves last page, shows "Continue from Page N?" on return
- **Auto-Continue**: When enabled, automatically reads next page after current finishes
- **Auto-Scroll**: Navigating pages scrolls to the storybook panel

### How Storybook Integrates with Floating Player

Storybook overrides `window.RosaryNarrationController` with its own controls:

```javascript
window.RosaryNarrationController = {
  togglePause: () => readCurrentPage(),
  stop: () => stopReading(),
  next: () => movePage(isRtl ? -1 : 1),
  previous: () => movePage(isRtl ? 1 : -1)
};
```

It syncs via `RosaryAudioContext.set()` with `source: 'storybook'` and `mode: 'storybook'`.

### Important: render() Writes to localStorage

The `render()` function calls `writeLastPage(index)`. If you read `lastPage` from localStorage after calling `render()`, you'll get the new value (0 on init), not the saved value. The init function reads the saved page BEFORE the first render.

---

## The Voice Testimony Page

`voice-testimony.html` — contains a video player, Arabic + English transcripts, and a full raw capture.

### Features

- **Read Aloud**: Browser `speechSynthesis` for transcript blocks
- **Copy Transcript**: Clipboard copy buttons for each transcript block
- **Jump-to-Timestamp**: Full capture timestamps `[XXXX.XX-YYYY.YY]` are parsed into clickable links that seek the `<video>` element

### Transcript Loading

The full capture transcript is fetched via `fetch('./transcripts/charbel-testimony-ar-fullcapture-v3.txt')` and timestamps are converted to clickable `<span class="timestamp-link">` elements with `data-seek` attributes.

---

## The Floating Audio Player

`global-audio-player.js` creates an `<aside class="floating-audio">` appended to `document.body`.

### How It Becomes Visible

1. Any page calls `RosaryAudioContext.set({ playing: true })` or `{ paused: true }`
2. A 500ms `setInterval(renderSpeechState, 500)` polls localStorage
3. If context shows active state, floating dock gets `.on` class
4. The dock reads `ui` flags from context to show/hide buttons per page type

### Page UI Profiles

Different pages show different floating player buttons:

```javascript
// Rosary page flags:
{ showBack: true, showToggle: true, showSkip: true, showAutoPrayer: true, showNext: true, ... }

// Story page flags:
{ showBack: true, showToggle: true, showSkip: true, showAutoPrayer: false, showNext: false, ... }
```

### The Merge-Based Write Pattern

**Critical**: `RosaryAudioContext.set()` uses object spread to merge, not replace:

```javascript
const writeContext = next => {
  const prev = readJSON(STORAGE_KEY);
  localStorage.setItem(STORAGE_KEY, JSON.stringify({ ...prev, ...next }));
};
```

This means calling `.set({ playing: true })` preserves all other keys. Never use `localStorage.setItem('rosary_audio_context', ...)` directly — always go through `RosaryAudioContext.set()`.

---

## localStorage Keys

| Key | Used By | Type | Purpose |
|-----|---------|------|---------|
| `rosary_audio_context` | global-audio-player.js, mystery-meditation, storybook | JSON (merge) | Current playback state |
| `rosary_audio_dock_state` | global-audio-player.js | JSON | Dock minimized/collapsed state |
| `rosary_audio_dock_position` | global-audio-player.js | JSON | Dock x/y position |
| `rosary_audio_voice_pref` | global-audio-player.js | JSON | Selected voice {name, lang} |
| `rosary_full_session` | mystery-meditation | JSON | Active 5-mystery rosary session |
| `sc_lang_pref` | translate.js | string | Language code preference |
| `storybook_auto_continue` | storybook.js | string | "true" / "false" |
| `storybook_reader_mode` | storybook.js | string | "true" / "false" |
| `storybook_last_page` | storybook.js | string | Page index number |
| `storybook_voice_pack_{lang}` | storybook.js | string | Voice pack ID |
| `testimony_last_submit_at` | submit-testimony.js | string | Rate-limit timestamp |

**Rule**: All localStorage reads/writes are wrapped in try/catch with no-op fallback. Never assume localStorage is available.

---

## Window Globals

| Global | Set By | Read By | Purpose |
|--------|--------|---------|---------|
| `window.RosaryAudioContext` | global-audio-player.js | mystery-meditation, storybook | `.set(data)` to update floating player |
| `window.RosaryNarrationController` | mystery-meditation OR storybook | global-audio-player.js | `.togglePause()`, `.stop()`, `.next()`, `.previous()` |
| `window.ROSARY_MYSTERIES` | mystery-data.js | mystery-meditation | Full mystery definitions |
| `window.ROSARY_MYSTERY_LIBRARY` | mystery-library.js | mystery-meditation | Scripture + reflections |
| `window.MYSTERY_KEY` | mystery HTML inline script | mystery-meditation | Current mystery identifier |
| `window.MYSTERY_BASE` | mystery HTML inline script | mystery-meditation | Path prefix to root |
| `window.ROSARY_AUDIO_VERSION` | mystery HTML inline script | mystery-meditation | Audio clip cache buster |
| `window.__scTranslateInitialized` | translate.js | translate.js | Prevent double-init |
| `window.__scApplyTranslation` | translate.js | (external) | Re-apply translation |

---

## Custom Events

| Event | Dispatched By | Listened By | Purpose |
|-------|--------------|-------------|---------|
| `rosary-audio-context-updated` | RosaryAudioContext.set() | global-audio-player.js | Triggers floating player re-render |
| `rosary-audio-close` | global-audio-player.js (close button) | mystery-meditation, storybook | Stop playback when player closed |
| `sc:content-updated` | mystery-meditation (on render) | translate.js | Re-translate new content |

---

## Testing Infrastructure

### Stack

- **Playwright** (v1.58.2) with headless Chromium
- **Python 3** `http.server` on port 4173 for local serving
- **Bash** shell scripts for orchestration
- **Node ESM** (.mjs) test files

### Test Suites

| Suite | File | Tests | What It Covers |
|-------|------|-------|---------------|
| Site Smoke | `site_smoke.mjs` | 10+ | All main pages load without errors |
| Rosary Smoke | `rosary_smoke.mjs` | 14 | Core meditation features, no autoplay, language persistence |
| Rosary Menu | `rosary_menu_behaviors.mjs` | 10 | Mystery picker dropdown navigation |
| Rosary End Rules | `rosary_end_stage_rules.mjs` | 4 | When end-prayers stage appears |
| Rosary Prayer | `rosary_prayer_behavior.mjs` | 1 | Prayer cue correctness |
| Rosary Intro CTA | `rosary_intro_cta_behavior.mjs` | 1 | Start Today routing + session creation |
| UI Regression | `rosary_ui_regression.mjs` | 30 | Button states, numbering, data-testid, audio independence |
| Story Player | `story_floating_player.mjs` | 39 | Floating player + storybook controls |
| Checklist | `checklist_improvements.mjs` | 80+ | Accessibility, timer, reader mode, resume, copy, timestamps |

### Running Tests

```bash
npm run qa                    # FULL suite (what pre-push hook runs)
npm run test:rosary-smoke     # Just rosary smoke
npm run test:checklist        # Just checklist improvements
npm run qa:dead-code          # Dead code check only
```

### Test Execution Flow

```
npm run qa
  → scripts/qa/run_full_qa.sh
    → npm run test:site-smoke
      → scripts/tests/run_site_smoke.sh
        → Start python3 -m http.server 4173 (if not already running)
        → node scripts/tests/site_smoke.mjs --base-url=http://127.0.0.1:4173
        → Kill server on exit
    → npm run test:rosary-all
      → (8 test suites in sequence, each starts/stops its own server)
```

Each shell script is a symlink-style dispatcher — they all share the same runner template (`run_rosary_smoke.sh`) with a `case` statement routing by filename.

---

## How to Write a New Test

### 1. Add test cases to an existing .mjs file

If your feature is related to an existing suite, add tests there. Example pattern:

```javascript
await expect('My new feature works', async () => {
  await page.goto(`${baseUrl}/story.html`, { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(400);
  const result = await page.locator('#my-element').textContent();
  if (result !== 'expected') {
    throw new Error(`Expected "expected", got: "${result}"`);
  }
});
```

### 2. Create a new test suite

If it's a new area, create `scripts/tests/my_feature.mjs`:

```javascript
#!/usr/bin/env node
import { chromium } from 'playwright';

const baseUrlArg = process.argv.find(arg => arg.startsWith('--base-url='));
const baseUrl = (baseUrlArg ? baseUrlArg.split('=')[1] : 'http://127.0.0.1:4173').replace(/\/$/, '');
const failures = [];

const expect = async (name, fn) => {
  try {
    await fn();
    console.log(`PASS: ${name}`);
  } catch (err) {
    failures.push(`${name}: ${err instanceof Error ? err.message : String(err)}`);
    console.log(`FAIL: ${name}`);
  }
};

const browser = await chromium.launch({ headless: true });
const context = await browser.newContext();
const page = await context.newPage();

try {
  // Your tests here
  await expect('Feature exists', async () => {
    await page.goto(`${baseUrl}/page.html`, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(300);
    // assertions...
  });
} finally {
  await context.close();
  await browser.close();
}

if (failures.length) {
  console.error('\nTest failures:');
  failures.forEach(f => console.error(`- ${f}`));
  process.exit(1);
}
console.log('\nAll tests passed.');
```

### 3. Create a shell runner

Create `scripts/tests/run_my_feature.sh` — you can copy `run_rosary_smoke.sh` and add a case:

```bash
run_my_feature.sh) node scripts/tests/my_feature.mjs "--base-url=${BASE_URL}" ;;
```

Or create a dedicated runner. Make it executable: `chmod +x scripts/tests/run_my_feature.sh`

### 4. Register in package.json

```json
"test:my-feature": "scripts/tests/run_my_feature.sh"
```

Add it to `test:rosary-all` (or create a new aggregate) if it should run in full QA.

### Key Testing Patterns

- **Always `waitForTimeout(300-400)`** after navigation for JS to initialize
- **Use `page.evaluate()`** to bypass floating player overlay blocking clicks
- **Use `page.locator().evaluate()`** for computed style checks
- **Grant clipboard permissions** before testing copy: `await context.grantPermissions(['clipboard-write'], { origin: baseUrl })`
- **Monkey-patch `scrollIntoView`** in `page.evaluate()` to verify scroll calls in headless mode
- **Check localStorage** via `page.evaluate(() => localStorage.getItem(key))`
- **Set localStorage before reload**: navigate to page first, set value, then `page.goto()` again

---

## CI/CD Pipeline

### Workflows

| Workflow | Trigger | What It Does |
|----------|---------|-------------|
| `qa.yml` | Every push + PRs | Full QA suite, upload debug artifacts on failure |
| `dead-code-check.yml` | PRs + push to main/stage | Detect unreferenced files |
| `pr-preview.yml` | PR opened/synced | Deploy Netlify preview, comment PR with URL |
| `cleanup-preview.yml` | PR closed | Delete Netlify preview deploy |
| `deploy-stage.yml` | Push to `stage` | Run QA, then verify live frontend files match the checkout; Hostinger deploys independently via webhook |
| `auto-pr-to-main.yml` | Push to `stage` | Create PR from stage to main |

### Deployment Flow

```
Feature Branch → PR (triggers: QA + dead-code + preview deploy)
                   ↓
              Merge to stage (triggers: QA + Hostinger deploy + auto-PR to main)
                   ↓
              Review promote PR → Merge to main (production)
```

### What Blocks a Merge

Hostinger's webhook receipt is not a deployment result. The deployment workflow
compares live HTML, JavaScript, CSS and web manifest contents with the pushed
checkout and fails if they remain different after retries. It does not verify
every media file or server-side PHP behavior. Run it locally with
`python3 scripts/qa/verify_deployment.py --attempts 1`.

If Hostinger reports `Project directory is not a git repository`, preserve the
hosted files outside `public_html` before recreating the Git checkout. Keep
`.git` intact for future pushes; archive-based replacement of the live folder
can break this integration. Check hPanel's latest Git build output, then verify
the website itself.

- QA test failure (any of 190+ tests)
- Dead code detected (unreferenced JS, images, or orphan HTML)

---

## Git Workflow

### Branch Strategy

- `main` — Production (marsharbel.com)
- `stage` — Staging (auto-deploys to Hostinger)
- Feature branches — Anything else (get PR previews)

### Pre-Push Hook

`.git/hooks/pre-push` runs `npm run qa` before every push. This takes ~2-3 minutes. If tests fail, the push is blocked.

**Bypass** (avoid): `git push --no-verify`

### Commit Convention

No strict convention enforced. Descriptive messages preferred. The auto-PR workflow uses a standard title ("Promote stage -> main").

---

## Adding a New Feature — Step by Step

### 1. Understand What You're Touching

Read the relevant JS file fully before modifying. Key files are 1000-1500 lines — skimming causes bugs.

### 2. Make Your Changes

- **HTML**: Add elements to the relevant `.html` file
- **CSS**: Add styles to `styles.css` (global) or `storybook.css` (story-only)
- **JS**: Modify the relevant JS file (no module imports — everything is inline)

### 3. If You Added a New Element

- Give it an `id` if JS needs to reference it
- Add `aria-label` for interactive elements
- Add `notranslate` class if it shouldn't be translated
- Add `data-testid` if it's an action button on rosary pages

### 4. If You Added a New JS File

- Reference it in every HTML page that needs it (with correct path)
- Make sure it loads AFTER its dependencies (e.g., after `global-audio-player.js`)
- The dead-code checker will flag it if no HTML references it

### 5. If You Used localStorage

- Wrap reads/writes in try/catch
- Use the merge pattern for `rosary_audio_context` (go through `RosaryAudioContext.set()`)
- Document the key in this README

### 6. Write Tests

Add Playwright tests covering your feature. At minimum:
- Element exists and is visible
- Feature works on click/interaction
- State persists if using localStorage
- Edge cases (empty state, boundary values)

### 7. Run QA Locally

```bash
npm run qa
```

This must pass before pushing. The pre-push hook enforces this.

### 8. Push and Verify Preview

```bash
git push origin your-branch
```

CI runs QA + dead-code check. PR gets a Netlify preview URL. Verify manually in the preview.

---

## Common Pitfalls

### 1. Floating Player Overlay Blocks Clicks

The floating player sits on top of page content. In tests, use `page.evaluate()` to click elements behind it:

```javascript
await page.evaluate(() => document.getElementById('my-btn').click());
```

### 2. render() Overwrites localStorage

In `storybook.js`, the `render()` function calls `writeLastPage(index)`. If you call `readLastPage()` after `render()`, you get the new value (0 on first load), not the saved value. Read saved state BEFORE calling render.

### 3. Script Load Order

`global-audio-player.js` must load before `mystery-meditation.v20260304.js` and `storybook.js`. Both of those read `window.RosaryAudioContext`.

### 4. Versioned Files

Files like `mystery-meditation.v20260304.js` and `global-audio-player.v20260304.js` are versioned backups. The dead-code checker flags old versions. If you create a new version, update ALL HTML files that reference the old one.

### 5. The `supportsSpeech = false` Flag

In `global-audio-player.js`, browser TTS is disabled (`const supportsSpeech = false`). The voice selector UI is hidden. Don't re-enable this without understanding the implications across all pages.

### 6. RTL Support

Arabic (`?lang=ar`) triggers RTL mode. Storybook adds `.is-rtl` class and swaps prev/next directions. Navigation arrow keys are also swapped. Test RTL if you modify navigation.

### 7. Mystery Pages Are in a Subdirectory

Files in `mysteries/` use `../` prefix for all resource paths (`../styles.css`, `../media/`, etc.). Don't use root-relative paths in mystery pages.

### 8. Don't Destructively Write to rosary_audio_context

Always use `RosaryAudioContext.set({ key: value })` — never `localStorage.setItem('rosary_audio_context', ...)`. The merge pattern preserves other keys.

### 9. Test Server Port Conflicts

Tests use port 4173. If a previous test run crashed, the server may still be running. The shell scripts check `lsof` and reuse existing servers. To force cleanup: `kill $(lsof -t -i:4173)`.

### 10. headless Playwright Limitations

- `scrollIntoView` doesn't physically scroll — monkey-patch it to verify calls
- `speechSynthesis` is not available in headless Chromium — tests that need it must mock
- Video elements won't auto-play — but you can set `currentTime` programmatically

---

## Dead Code Rules

The `scripts/qa/dead_code_check.sh` CI check will fail your PR if:

1. **Unreferenced JS file**: A `.js` file in root not referenced by any `.html` or `.js` file
2. **Old versioned backup**: A `.v{DATE}.js` file superseded by a newer version and not referenced
3. **Unreferenced image**: A file in `gallery/` or `mockup-products/` not referenced anywhere
4. **Backup image**: Any `.bak.png` in `media/storybook/images/`
5. **Orphan HTML**: A root `.html` page with no inbound links from other pages or JS

**Intentional exclusions** (won't be flagged):
- `index.html`, `google*.html` (entry points)
- `mystery-meditation.html` (alternate rosary entry point)
- `rosary-source-text.html` (SEO redirect)
- `testimony-review.html` (admin page)
- `voice-lab.html` (dev tool)
- `service-worker.js` (registered via manifest, not script tag)

---

## File Reference Tables

### Root HTML Pages (22)

| File | Purpose | Unique Scripts |
|------|---------|---------------|
| `index.html` | Homepage with Lent countdown | — |
| `history.html` | Saint Charbel biography | — |
| `story.html` | Interactive storybook for kids | `storybook.css`, `storybook.js` |
| `miracles.html` | Documented miracles | — |
| `testimonies.html` | User testimonies | `testimonies.js` |
| `gallery.html` | Photo gallery | `gallery.js` |
| `become-like-charbel.html` | Life disciplines | — |
| `rosary-visual-guide.html` | Rosary landing page | — |
| `rosary-intro.html` | Rosary introduction | — |
| `rosary-prayer-coach.html` | Prayer guidance | — |
| `rosary-source-text.html` | Source scriptures (SEO redirect) | — |
| `rosary-minibook.html` | Minibook format | — |
| `saint-charbel-prayers.html` | Prayer collection | — |
| `voice-testimony.html` | Audio testimony + transcripts | — |
| `submit-testimony.html` | Testimony form | `submit-testimony.js` |
| `testimony-review.html` | Admin review (noindex) | `testimony-admin.js` |
| `mystery-meditation.html` | Standalone meditation | All mystery scripts |
| `shop.html` | Product mockup | — |
| `shop-mockup.html` | Shop design | — |
| `voice-lab.html` | Voice testing (dev) | `voice-lab.js` |
| `google*.html` (2) | Search verification | — |

### Mystery Pages (20)

All in `mysteries/` directory. Pattern: `{set}-{N}.html` where set is `joyful|luminous|sorrowful|glorious` and N is `1-5`.

Each loads: `mystery-data.js`, `mystery-library.js`, inline config script, `mystery-meditation.v20260304.js`

### Test Suites (9)

All in `scripts/tests/`. Each `.mjs` file has a corresponding `run_*.sh` wrapper.

| File | Registered As | In Full QA |
|------|--------------|-----------|
| `site_smoke.mjs` | `test:site-smoke` | Yes |
| `rosary_smoke.mjs` | `test:rosary-smoke` | Yes |
| `rosary_menu_behaviors.mjs` | `test:rosary-menu` | Yes |
| `rosary_end_stage_rules.mjs` | `test:rosary-end-rules` | Yes |
| `rosary_prayer_behavior.mjs` | `test:rosary-prayer-behavior` | Yes |
| `rosary_intro_cta_behavior.mjs` | `test:rosary-intro-cta` | Yes |
| `rosary_ui_regression.mjs` | `test:rosary-ui-regression` | Yes |
| `story_floating_player.mjs` | `test:story-floating-player` | Yes |
| `checklist_improvements.mjs` | `test:checklist` | Yes |

### GitHub Workflows (6)

| File | Trigger | Blocks Merge |
|------|---------|-------------|
| `qa.yml` | All pushes + PRs | Yes |
| `dead-code-check.yml` | PRs + main/stage push | Yes |
| `pr-preview.yml` | PR opened/synced | No (deploy only) |
| `cleanup-preview.yml` | PR closed | No (cleanup only) |
| `deploy-stage.yml` | Push to stage | N/A (production gate) |
| `auto-pr-to-main.yml` | Push to stage | No (creates PR) |
