# Integration notes: peter storybook

- Reader page: `peter-story.html` (clone rafqa-story.html, `is-story-page` body, storybook-joy.css).
- Data file: root `peter-story-data.js` produced by `python3 story-production/peter/build_story_data.py` (writes `window.PETER_STORY_EN`).
- Media: `media/storybook-peter/images/page-01..10.webp` (1280x720) and `media/storybook-peter/en/page-01..10.mp3`.
- Voice pack registration in storybook.js: id `kokoro-peter`, base `./media/storybook-peter/en`; recommended voice id mapping for storyId `peter`.
- Shelf: add one promo card on stories.html.
- EVIDENCE_SOURCES entries to add in storybook.js:
    peterBenedict2006a: { label: 'Holy See (Benedict XVI audience, 17 May 2006)', url: 'https://www.vatican.va/content/benedict-xvi/en/audiences/2006/documents/hf_ben-xvi_aud_20060517.html' },
    peterBenedict2006b: { label: 'Holy See (Benedict XVI audience, 24 May 2006)', url: 'https://www.vatican.va/content/benedict-xvi/en/audiences/2006/documents/hf_ben-xvi_aud_20060524.html' },
    bibleActs2: { label: 'NABRE, Acts 2 (USCCB)', url: 'https://bible.usccb.org/bible/acts/2' },
    bibleActs12: { label: 'NABRE, Acts 12 (USCCB)', url: 'https://bible.usccb.org/bible/acts/12' },
    eusebiusHE3: { label: 'Eusebius, Church History 3 (via New Advent)', url: 'https://www.newadvent.org/fathers/250103.htm' },
    stPeterNecropolis: { label: 'Fabbrica di San Pietro (Holy See), The Necropolis', url: 'https://www.basilicasanpietro.va/en/san-pietro/the-necropolis' },
- QA: adapt scripts/qa/rafqa_full_review.cjs and rafqa_interaction.cjs for this book (10 pages, first-page title, voice-pack id); run rendered desktop+phone review before merge (AGENTS.md golden rule).
- Audio spec: Kokoro am_michael, speed 0.94, 24kHz, 0.11s intra-sentence and 0.47s sentence-end rests; total narration duration must exceed 5 minutes (measure with ffprobe after assembly).
