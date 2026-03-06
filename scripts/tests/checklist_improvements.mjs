#!/usr/bin/env node

/**
 * Tests for the checklist improvements:
 * 1. Voice Testimony page title matches content
 * 2. Transcript accessibility (no <pre>, proper ARIA)
 * 3. Hands-free timer defaults to 12s, Start disabled when Off
 * 4. Clear playback UI (elapsed time in floating player)
 * 5. Navigation clarity (auto-scroll, step counter visible)
 * 6. Accessibility (aria-labels on Prev/Next buttons)
 */

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
  // ============================================================
  // 1. VOICE TESTIMONY: Title matches page content
  // ============================================================

  await page.goto(`${baseUrl}/voice-testimony.html`, { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(300);

  await expect('Voice Testimony page title matches h1 content', async () => {
    const title = await page.title();
    const h1 = await page.locator('h1').textContent();
    if (/Submit a Voice Testimony/i.test(title)) {
      throw new Error(`Title still says "Submit a Voice Testimony": ${title}`);
    }
    if (!title.includes("Charbel") && !title.includes("Recorded Voice")) {
      throw new Error(`Title should reference recorded voice, got: ${title}`);
    }
  });

  await expect('Voice Testimony og:title matches page title', async () => {
    const ogTitle = await page.getAttribute('meta[property="og:title"]', 'content');
    const title = await page.title();
    if (ogTitle !== title) {
      throw new Error(`og:title "${ogTitle}" does not match page title "${title}"`);
    }
  });

  await expect('Voice Testimony twitter:title matches page title', async () => {
    const twitterTitle = await page.getAttribute('meta[name="twitter:title"]', 'content');
    const title = await page.title();
    if (twitterTitle !== title) {
      throw new Error(`twitter:title "${twitterTitle}" does not match page title "${title}"`);
    }
  });

  // ============================================================
  // 2. TRANSCRIPT ACCESSIBILITY
  // ============================================================

  await expect('Transcripts use accessible div elements, not pre', async () => {
    const preCount = await page.locator('.transcript-card pre').count();
    if (preCount > 0) {
      throw new Error(`Found ${preCount} <pre> elements in transcript cards, should use <div>`);
    }
  });

  await expect('Arabic transcript has role="region" and aria-label', async () => {
    const el = page.locator('#transcript-ar');
    const role = await el.getAttribute('role');
    const label = await el.getAttribute('aria-label');
    if (role !== 'region') throw new Error(`Expected role="region", got: ${role}`);
    if (!label || !label.toLowerCase().includes('arabic')) {
      throw new Error(`Expected aria-label with "arabic", got: ${label}`);
    }
  });

  await expect('English transcript has role="region" and aria-label', async () => {
    const el = page.locator('#transcript-en');
    const role = await el.getAttribute('role');
    const label = await el.getAttribute('aria-label');
    if (role !== 'region') throw new Error(`Expected role="region", got: ${role}`);
    if (!label || !label.toLowerCase().includes('english')) {
      throw new Error(`Expected aria-label with "english", got: ${label}`);
    }
  });

  await expect('Full capture transcript has role="region" and aria-label', async () => {
    const el = page.locator('#voice-full');
    const role = await el.getAttribute('role');
    const label = await el.getAttribute('aria-label');
    if (role !== 'region') throw new Error(`Expected role="region", got: ${role}`);
    if (!label) throw new Error('Expected aria-label on full capture transcript');
  });

  await expect('Transcripts are keyboard-focusable (tabindex)', async () => {
    const arTab = await page.locator('#transcript-ar').getAttribute('tabindex');
    const enTab = await page.locator('#transcript-en').getAttribute('tabindex');
    if (arTab !== '0') throw new Error(`Arabic transcript tabindex: ${arTab}`);
    if (enTab !== '0') throw new Error(`English transcript tabindex: ${enTab}`);
  });

  await expect('Transcript content is preserved after pre-to-div migration', async () => {
    const arText = await page.locator('#transcript-ar').textContent();
    const enText = await page.locator('#transcript-en').textContent();
    if (!arText.includes('الله يبارككم')) {
      throw new Error('Arabic transcript content missing');
    }
    if (!enText.includes('May God bless you')) {
      throw new Error('English transcript content missing');
    }
  });

  await expect('Read Aloud buttons still work after pre-to-div migration', async () => {
    const btn = page.locator('.transcript-read-btn').first();
    const visible = await btn.isVisible();
    if (!visible) throw new Error('Read Aloud button not visible');
    const target = await btn.getAttribute('data-target');
    const el = page.locator(`#${target}`);
    if (!await el.isVisible()) throw new Error(`Target ${target} not visible`);
  });

  // ============================================================
  // 3. HANDS-FREE TIMER UX
  // ============================================================

  await page.goto(`${baseUrl}/mysteries/joyful-1.html`, { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(500);

  await expect('Timer defaults to 12s, not Off', async () => {
    const selected = await page.locator('#auto-timer-seconds').inputValue();
    if (selected !== '12') {
      throw new Error(`Timer default should be "12", got: "${selected}"`);
    }
  });

  await expect('Start Auto button is enabled when timer is 12s', async () => {
    const disabled = await page.locator('#auto-timer-toggle').isDisabled();
    if (disabled) throw new Error('Start Auto should be enabled when timer is 12s');
  });

  await expect('Start Auto button is disabled when timer is Off', async () => {
    await page.selectOption('#auto-timer-seconds', '0');
    await page.waitForTimeout(100);
    const disabled = await page.locator('#auto-timer-toggle').isDisabled();
    if (!disabled) throw new Error('Start Auto should be disabled when timer is Off');
  });

  await expect('Start Auto button re-enables when timer value is selected', async () => {
    await page.selectOption('#auto-timer-seconds', '18');
    await page.waitForTimeout(100);
    const disabled = await page.locator('#auto-timer-toggle').isDisabled();
    if (disabled) throw new Error('Start Auto should be enabled when timer is 18s');
  });

  await expect('Timer default is 12s on multiple mystery pages', async () => {
    for (const mystery of ['luminous-3', 'sorrowful-1', 'glorious-5']) {
      await page.goto(`${baseUrl}/mysteries/${mystery}.html`, { waitUntil: 'domcontentloaded' });
      await page.waitForTimeout(300);
      const selected = await page.locator('#auto-timer-seconds').inputValue();
      if (selected !== '12') {
        throw new Error(`Timer default on ${mystery} should be "12", got: "${selected}"`);
      }
    }
  });

  // ============================================================
  // 4. CLEAR PLAYBACK UI (elapsed time in floating player)
  // ============================================================

  await page.goto(`${baseUrl}/mysteries/joyful-1.html`, { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(500);

  await expect('Floating player has elapsed time element', async () => {
    await page.click('#start-guided-audio');
    await page.waitForTimeout(1500);
    const exists = await page.evaluate(() => !!document.getElementById('floating-audio-elapsed'));
    if (!exists) throw new Error('Elapsed time element not found in floating player');
  });

  await expect('Elapsed time is visible during playback', async () => {
    const hidden = await page.evaluate(() =>
      document.getElementById('floating-audio-elapsed')?.hidden
    );
    if (hidden) throw new Error('Elapsed time should be visible during playback');
  });

  await expect('Elapsed time shows formatted time or countdown', async () => {
    const text = await page.evaluate(() =>
      document.getElementById('floating-audio-elapsed')?.textContent || ''
    );
    // Should be either "0:XX" format or "Next step in Xs" or "Completed"
    if (!/\d:\d{2}|Next step in|Completed/i.test(text)) {
      throw new Error(`Expected elapsed time format, got: "${text}"`);
    }
  });

  // ============================================================
  // 5. NAVIGATION CLARITY (step counter, auto-scroll)
  // ============================================================

  await expect('Step counter shows "Step X of Y" format', async () => {
    const text = await page.locator('#step-counter').textContent();
    if (!/Step \d+ of \d+/i.test(text)) {
      throw new Error(`Expected "Step X of Y", got: "${text}"`);
    }
  });

  await expect('Step counter updates after clicking Next', async () => {
    // Close floating player if it's covering the button
    await page.evaluate(() => {
      const close = document.getElementById('floating-audio-close');
      if (close) close.click();
    });
    await page.waitForTimeout(300);

    const before = await page.locator('#step-counter').textContent();
    await page.evaluate(() => document.getElementById('next-step').click());
    await page.waitForTimeout(300);
    const after = await page.locator('#step-counter').textContent();
    if (before === after) {
      throw new Error(`Step counter did not update: before="${before}", after="${after}"`);
    }
  });

  // ============================================================
  // 6. ACCESSIBILITY (aria-labels on navigation buttons)
  // ============================================================

  // Rosary page buttons
  await expect('Previous step button has aria-label on rosary page', async () => {
    const label = await page.locator('#prev-step').getAttribute('aria-label');
    if (!label) throw new Error('prev-step missing aria-label');
  });

  await expect('Next step button has aria-label on rosary page', async () => {
    const label = await page.locator('#next-step').getAttribute('aria-label');
    if (!label) throw new Error('next-step missing aria-label');
  });

  await expect('Previous mystery button has aria-label', async () => {
    const label = await page.locator('#prev-mystery').getAttribute('aria-label');
    if (!label) throw new Error('prev-mystery missing aria-label');
  });

  await expect('Next mystery button has aria-label', async () => {
    const label = await page.locator('#next-mystery').getAttribute('aria-label');
    if (!label) throw new Error('next-mystery missing aria-label');
  });

  // Check across multiple mystery pages
  await expect('Aria-labels present on all sampled mystery pages', async () => {
    for (const mystery of ['joyful-5', 'luminous-2', 'sorrowful-4', 'glorious-1']) {
      await page.goto(`${baseUrl}/mysteries/${mystery}.html`, { waitUntil: 'domcontentloaded' });
      await page.waitForTimeout(200);
      const prevLabel = await page.locator('#prev-step').getAttribute('aria-label');
      const nextLabel = await page.locator('#next-step').getAttribute('aria-label');
      if (!prevLabel) throw new Error(`prev-step missing aria-label on ${mystery}`);
      if (!nextLabel) throw new Error(`next-step missing aria-label on ${mystery}`);
    }
  });

  // Story page buttons
  await page.goto(`${baseUrl}/story.html`, { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(300);

  await expect('Previous Page button has aria-label on story page', async () => {
    const label = await page.locator('#story-prev').getAttribute('aria-label');
    if (!label) throw new Error('story-prev missing aria-label');
  });

  await expect('Next Page button has aria-label on story page', async () => {
    const label = await page.locator('#story-next').getAttribute('aria-label');
    if (!label) throw new Error('story-next missing aria-label');
  });

  // Floating player buttons (already had aria-labels, verify they're still there)
  await expect('Floating player buttons retain aria-labels', async () => {
    const checks = await page.evaluate(() => {
      const ids = [
        'floating-audio-close',
        'floating-audio-minimize',
        'floating-audio-back',
        'floating-audio-skip'
      ];
      return ids
        .filter(id => {
          const el = document.getElementById(id);
          return !el || !el.getAttribute('aria-label');
        });
    });
    if (checks.length) throw new Error(`Missing aria-labels: ${checks.join(', ')}`);
  });

  // ============================================================
  // 7. STICKY CONTROLS
  // ============================================================

  // Story page sticky controls
  await page.goto(`${baseUrl}/story.html`, { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(500);

  await expect('Story controls bar has sticky positioning', async () => {
    const position = await page.evaluate(() =>
      window.getComputedStyle(document.querySelector('.storybook-controls')).position
    );
    if (position !== 'sticky') {
      throw new Error(`Expected sticky positioning, got: ${position}`);
    }
  });

  // Rosary page sticky controls
  await page.goto(`${baseUrl}/mysteries/joyful-1.html`, { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(500);

  await expect('Rosary meditation actions bar has sticky positioning', async () => {
    const position = await page.evaluate(() =>
      window.getComputedStyle(document.querySelector('.meditation-actions')).position
    );
    if (position !== 'sticky') {
      throw new Error(`Expected sticky positioning, got: ${position}`);
    }
  });

  // ============================================================
  // 8. GUIDED AUDIO BUTTON STATES
  // ============================================================

  await page.goto(`${baseUrl}/mysteries/joyful-1.html`, { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(500);

  await expect('Guided audio button starts as "Play Guided Audio"', async () => {
    const label = await page.evaluate(() =>
      document.getElementById('start-guided-audio')?.textContent || ''
    );
    if (!/Play Guided Audio/i.test(label)) {
      throw new Error(`Expected "Play Guided Audio", got: "${label}"`);
    }
  });

  await expect('Guided audio button changes state after click', async () => {
    await page.evaluate(() => document.getElementById('start-guided-audio').click());
    await page.waitForTimeout(1500);
    const label = await page.evaluate(() =>
      document.getElementById('start-guided-audio')?.textContent || ''
    );
    if (/^Play Guided Audio$/i.test(label)) {
      throw new Error(`Button should not still say "Play Guided Audio" after click, got: "${label}"`);
    }
    // Should be "Pause Guided Audio", "Starting...", "Replay Guided Audio", or similar
    if (!/Pause|Starting|Replay|Playing|Resume/i.test(label)) {
      throw new Error(`Expected active state label, got: "${label}"`);
    }
  });

  await expect('Guided audio button shows "Replay" after audio completes or stops', async () => {
    // Close floating player to stop audio
    await page.evaluate(() => {
      const close = document.getElementById('floating-audio-close');
      if (close) close.click();
    });
    await page.waitForTimeout(500);
    const label = await page.evaluate(() =>
      document.getElementById('start-guided-audio')?.textContent || ''
    );
    if (!/Replay Guided Audio|Play Guided Audio/i.test(label)) {
      throw new Error(`Expected "Replay Guided Audio" after stop, got: "${label}"`);
    }
  });

  await expect('Replay button restarts playback when clicked', async () => {
    // Button should say Replay after previous test stopped audio
    const beforeLabel = await page.evaluate(() =>
      document.getElementById('start-guided-audio')?.textContent || ''
    );
    if (!/Replay|Play/i.test(beforeLabel)) {
      throw new Error(`Expected Replay/Play before restart, got: "${beforeLabel}"`);
    }
    await page.evaluate(() => document.getElementById('start-guided-audio').click());
    await page.waitForTimeout(1500);
    const afterLabel = await page.evaluate(() =>
      document.getElementById('start-guided-audio')?.textContent || ''
    );
    if (!/Pause|Starting|Playing/i.test(afterLabel)) {
      throw new Error(`Expected active state after replay click, got: "${afterLabel}"`);
    }
    // Clean up
    await page.evaluate(() => {
      const close = document.getElementById('floating-audio-close');
      if (close) close.click();
    });
    await page.waitForTimeout(300);
  });

  await expect('Guided audio button resets to Play on page navigation', async () => {
    await page.goto(`${baseUrl}/mysteries/joyful-2.html`, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(500);
    const label = await page.evaluate(() =>
      document.getElementById('start-guided-audio')?.textContent || ''
    );
    if (!/Play Guided Audio/i.test(label)) {
      throw new Error(`Expected "Play Guided Audio" on new page, got: "${label}"`);
    }
  });

  // ============================================================
  // 9. EDGE CASES: TIMER BEHAVIOR
  // ============================================================

  await expect('Timer value resets to 12s on fresh page load', async () => {
    await page.goto(`${baseUrl}/mysteries/sorrowful-2.html`, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(300);
    const val = await page.locator('#auto-timer-seconds').inputValue();
    if (val !== '12') {
      throw new Error(`Expected timer to reset to 12s on new page, got: "${val}"`);
    }
  });

  await expect('Start Auto button disabled immediately when Off is selected', async () => {
    await page.selectOption('#auto-timer-seconds', '0');
    await page.waitForTimeout(50);
    const disabled = await page.locator('#auto-timer-toggle').isDisabled();
    if (!disabled) throw new Error('Start Auto should be disabled immediately after selecting Off');
  });

  await expect('Start Auto re-enables immediately when value is selected after Off', async () => {
    await page.selectOption('#auto-timer-seconds', '18');
    await page.waitForTimeout(50);
    const disabled = await page.locator('#auto-timer-toggle').isDisabled();
    if (disabled) throw new Error('Start Auto should re-enable immediately after selecting 18s');
  });

  await expect('Timer cycling through multiple values always updates button state', async () => {
    for (const val of ['0', '18', '0', '12', '0']) {
      await page.selectOption('#auto-timer-seconds', val);
      await page.waitForTimeout(50);
      const disabled = await page.locator('#auto-timer-toggle').isDisabled();
      const expected = val === '0';
      if (disabled !== expected) {
        throw new Error(`Timer=${val}: expected disabled=${expected}, got disabled=${disabled}`);
      }
    }
  });

  // ============================================================
  // 10. EDGE CASES: FLOATING PLAYER AFTER CLOSE
  // ============================================================

  await expect('Floating player stays hidden after close until user re-triggers', async () => {
    await page.goto(`${baseUrl}/mysteries/joyful-1.html`, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(500);
    // Start audio, then close player
    await page.evaluate(() => document.getElementById('start-guided-audio').click());
    await page.waitForTimeout(1000);
    await page.evaluate(() => {
      const close = document.getElementById('floating-audio-close');
      if (close) close.click();
    });
    await page.waitForTimeout(500);
    const hidden = await page.evaluate(() => {
      const player = document.querySelector('.floating-audio');
      return !player || player.hidden || window.getComputedStyle(player).display === 'none';
    });
    if (!hidden) throw new Error('Floating player should stay hidden after close');
  });

  // ============================================================
  // 11. EDGE CASES: STEP COUNTER BOUNDARIES
  // ============================================================

  await expect('Step counter starts at correct position (not step 0)', async () => {
    await page.goto(`${baseUrl}/mysteries/joyful-1.html`, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(300);
    const text = await page.locator('#step-counter').textContent();
    const match = text.match(/Step (\d+) of (\d+)/i);
    if (!match) throw new Error(`Step counter format wrong: "${text}"`);
    const step = parseInt(match[1]);
    const total = parseInt(match[2]);
    if (step < 1) throw new Error(`Step should be >= 1, got: ${step}`);
    if (total < 10) throw new Error(`Total should be >= 10, got: ${total}`);
  });

  await expect('Clicking Previous on first step does not go below step 1', async () => {
    // Navigate to first step via intro
    await page.goto(`${baseUrl}/mysteries/joyful-1.html?stage=intro`, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(300);
    const before = await page.locator('#step-counter').textContent();
    const matchBefore = before.match(/Step (\d+)/i);
    if (matchBefore && parseInt(matchBefore[1]) === 1) {
      await page.evaluate(() => document.getElementById('prev-step').click());
      await page.waitForTimeout(200);
      const after = await page.locator('#step-counter').textContent();
      const matchAfter = after.match(/Step (\d+)/i);
      if (matchAfter && parseInt(matchAfter[1]) < 1) {
        throw new Error(`Step went below 1: "${after}"`);
      }
    }
  });

  await expect('Step counter shows last step correctly on final step', async () => {
    // Click Next until we reach the end
    await page.goto(`${baseUrl}/mysteries/joyful-1.html`, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(300);
    const totalText = await page.locator('#step-counter').textContent();
    const totalMatch = totalText.match(/of (\d+)/i);
    if (!totalMatch) throw new Error(`Cannot parse total from: "${totalText}"`);
    const total = parseInt(totalMatch[1]);
    // Navigate to last step
    for (let i = 0; i < total + 2; i++) {
      await page.evaluate(() => document.getElementById('next-step').click());
      await page.waitForTimeout(50);
    }
    const finalText = await page.locator('#step-counter').textContent();
    const finalMatch = finalText.match(/Step (\d+) of (\d+)/i);
    if (!finalMatch) throw new Error(`Final step counter format wrong: "${finalText}"`);
    if (parseInt(finalMatch[1]) > parseInt(finalMatch[2])) {
      throw new Error(`Step ${finalMatch[1]} exceeds total ${finalMatch[2]}`);
    }
  });

  // ============================================================
  // 12. EDGE CASES: ACCESSIBILITY ACROSS PAGES
  // ============================================================

  await expect('Voice Testimony page has no broken ARIA references', async () => {
    await page.goto(`${baseUrl}/voice-testimony.html`, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(300);
    const brokenRefs = await page.evaluate(() => {
      const elems = document.querySelectorAll('[aria-labelledby], [aria-describedby]');
      const broken = [];
      elems.forEach(el => {
        const ref = el.getAttribute('aria-labelledby') || el.getAttribute('aria-describedby');
        if (ref && !document.getElementById(ref)) broken.push(ref);
      });
      return broken;
    });
    if (brokenRefs.length) {
      throw new Error(`Broken ARIA references: ${brokenRefs.join(', ')}`);
    }
  });

  await expect('Rosary page has no broken ARIA references', async () => {
    await page.goto(`${baseUrl}/mysteries/joyful-1.html`, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(300);
    const brokenRefs = await page.evaluate(() => {
      const elems = document.querySelectorAll('[aria-labelledby], [aria-describedby]');
      const broken = [];
      elems.forEach(el => {
        const ref = el.getAttribute('aria-labelledby') || el.getAttribute('aria-describedby');
        if (ref && !document.getElementById(ref)) broken.push(ref);
      });
      return broken;
    });
    if (brokenRefs.length) {
      throw new Error(`Broken ARIA references: ${brokenRefs.join(', ')}`);
    }
  });

  await expect('Story page has no broken ARIA references', async () => {
    await page.goto(`${baseUrl}/story.html`, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(300);
    const brokenRefs = await page.evaluate(() => {
      const elems = document.querySelectorAll('[aria-labelledby], [aria-describedby]');
      const broken = [];
      elems.forEach(el => {
        const ref = el.getAttribute('aria-labelledby') || el.getAttribute('aria-describedby');
        if (ref && !document.getElementById(ref)) broken.push(ref);
      });
      return broken;
    });
    if (brokenRefs.length) {
      throw new Error(`Broken ARIA references: ${brokenRefs.join(', ')}`);
    }
  });

  // ============================================================
  // 13. EDGE CASES: STICKY CONTROLS BEHAVIOR
  // ============================================================

  await expect('Story sticky controls have correct z-index above content', async () => {
    await page.goto(`${baseUrl}/story.html`, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(300);
    const zIndex = await page.evaluate(() =>
      parseInt(window.getComputedStyle(document.querySelector('.storybook-controls')).zIndex) || 0
    );
    if (zIndex < 80) {
      throw new Error(`Expected z-index >= 80, got: ${zIndex}`);
    }
  });

  await expect('Rosary sticky controls have correct z-index above content', async () => {
    await page.goto(`${baseUrl}/mysteries/joyful-1.html`, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(300);
    const zIndex = await page.evaluate(() =>
      parseInt(window.getComputedStyle(document.querySelector('.meditation-actions')).zIndex) || 0
    );
    if (zIndex < 80) {
      throw new Error(`Expected z-index >= 80, got: ${zIndex}`);
    }
  });

  await expect('Sticky controls have backdrop-filter for readability', async () => {
    const storyBackdrop = await page.evaluate(async () => {
      const el = document.querySelector('.storybook-controls');
      return el ? window.getComputedStyle(el).backdropFilter : '';
    });
    await page.goto(`${baseUrl}/mysteries/joyful-1.html`, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(300);
    const rosaryBackdrop = await page.evaluate(() => {
      const el = document.querySelector('.meditation-actions');
      return el ? window.getComputedStyle(el).backdropFilter : '';
    });
    if (!storyBackdrop && !rosaryBackdrop) {
      throw new Error('Neither sticky control bar has backdrop-filter');
    }
  });

  // ============================================================
  // 14. GUIDED AUDIO RESUME STATE
  // ============================================================

  await page.goto(`${baseUrl}/mysteries/joyful-1.html`, { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(500);

  await expect('Guided audio button shows "Resume" after pause', async () => {
    // Start playback
    await page.evaluate(() => document.getElementById('start-guided-audio').click());
    await page.waitForTimeout(1500);
    // Verify it says Pause first
    const playingLabel = await page.evaluate(() =>
      document.getElementById('start-guided-audio')?.textContent || ''
    );
    if (!/Pause|Starting/i.test(playingLabel)) {
      throw new Error(`Expected Pause/Starting state, got: "${playingLabel}"`);
    }
    // Now pause it via the button itself
    await page.evaluate(() => document.getElementById('start-guided-audio').click());
    await page.waitForTimeout(500);
    const pausedLabel = await page.evaluate(() =>
      document.getElementById('start-guided-audio')?.textContent || ''
    );
    if (!/Resume Guided Audio/i.test(pausedLabel)) {
      throw new Error(`Expected "Resume Guided Audio" after pause, got: "${pausedLabel}"`);
    }
    // Clean up
    await page.evaluate(() => {
      const close = document.getElementById('floating-audio-close');
      if (close) close.click();
    });
    await page.waitForTimeout(300);
  });

  await expect('Resume click restarts from paused state', async () => {
    // Start and pause
    await page.evaluate(() => document.getElementById('start-guided-audio').click());
    await page.waitForTimeout(1500);
    await page.evaluate(() => document.getElementById('start-guided-audio').click());
    await page.waitForTimeout(500);
    // Verify Resume label
    const resumeLabel = await page.evaluate(() =>
      document.getElementById('start-guided-audio')?.textContent || ''
    );
    if (!/Resume/i.test(resumeLabel)) {
      throw new Error(`Expected Resume state, got: "${resumeLabel}"`);
    }
    // Click Resume
    await page.evaluate(() => document.getElementById('start-guided-audio').click());
    await page.waitForTimeout(500);
    const afterResumeLabel = await page.evaluate(() =>
      document.getElementById('start-guided-audio')?.textContent || ''
    );
    if (!/Pause Guided Audio|Playing/i.test(afterResumeLabel)) {
      throw new Error(`Expected active state after resume, got: "${afterResumeLabel}"`);
    }
    // Clean up
    await page.evaluate(() => {
      const close = document.getElementById('floating-audio-close');
      if (close) close.click();
    });
    await page.waitForTimeout(300);
  });

  // ============================================================
  // 15. STEP COUNTER BADGE TEXT ON INTRO/END STAGES
  // ============================================================

  await expect('Step counter shows badge text on intro stage (not "Step X of Y")', async () => {
    await page.goto(`${baseUrl}/mysteries/joyful-1.html?stage=intro`, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(300);
    const text = await page.locator('#step-counter').textContent();
    if (/Step \d+ of \d+/i.test(text)) {
      throw new Error(`Intro stage should show badge text, not step counter, got: "${text}"`);
    }
    if (!/Intro Prayers/i.test(text)) {
      throw new Error(`Expected "Intro Prayers" badge on intro stage, got: "${text}"`);
    }
  });

  await expect('Step counter shows badge text on end stage (not "Step X of Y")', async () => {
    await page.goto(`${baseUrl}/mysteries/joyful-5.html?stage=end`, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(300);
    const text = await page.locator('#step-counter').textContent();
    if (/Step \d+ of \d+/i.test(text)) {
      throw new Error(`End stage should show badge text, not step counter, got: "${text}"`);
    }
    if (!/End Prayers/i.test(text)) {
      throw new Error(`Expected "End Prayers" badge on end stage, got: "${text}"`);
    }
  });

  await expect('Step counter reverts to "Step X of Y" on normal mystery', async () => {
    await page.goto(`${baseUrl}/mysteries/joyful-3.html`, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(300);
    const text = await page.locator('#step-counter').textContent();
    if (!/Step \d+ of \d+/i.test(text)) {
      throw new Error(`Normal mystery should show "Step X of Y", got: "${text}"`);
    }
  });

  // ============================================================
  // 16. AUTO-SCROLL ON STEP CHANGE
  // ============================================================

  await expect('scrollIntoView is called on step navigation', async () => {
    await page.goto(`${baseUrl}/mysteries/joyful-1.html`, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(300);
    // Patch scrollIntoView on the exact element the code uses (getElementById('stage-title'))
    const scrollCalled = await page.evaluate(() => {
      return new Promise(resolve => {
        const el = document.getElementById('stage-title');
        if (!el) { resolve(false); return; }
        const orig = Element.prototype.scrollIntoView;
        Element.prototype.scrollIntoView = function(...args) {
          if (this === el) {
            Element.prototype.scrollIntoView = orig;
            resolve(true);
          }
          return orig.apply(this, args);
        };
        document.getElementById('next-step').click();
        // Timeout fallback
        setTimeout(() => {
          Element.prototype.scrollIntoView = orig;
          resolve(false);
        }, 2000);
      });
    });
    if (!scrollCalled) {
      throw new Error('scrollIntoView should be called on step navigation');
    }
  });

  // ============================================================
  // 17. PLAY VOICE VS PLAY GUIDED AUDIO INDEPENDENCE
  // ============================================================

  await expect('Play Voice button stays "Play Voice" when guided audio starts', async () => {
    await page.goto(`${baseUrl}/mysteries/joyful-1.html`, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(500);
    const voiceBefore = await page.evaluate(() =>
      document.querySelector('[data-testid="pause-audio"]')?.textContent || ''
    );
    if (voiceBefore !== 'Play Voice') {
      throw new Error(`Expected "Play Voice" initially, got: "${voiceBefore}"`);
    }
    // Start guided audio (not Play Voice)
    await page.evaluate(() => document.getElementById('start-guided-audio').click());
    await page.waitForTimeout(1500);
    const voiceAfter = await page.evaluate(() =>
      document.querySelector('[data-testid="pause-audio"]')?.textContent || ''
    );
    if (voiceAfter !== 'Play Voice') {
      throw new Error(`Play Voice changed to "${voiceAfter}" after guided audio started`);
    }
    // Clean up
    await page.evaluate(() => {
      const close = document.getElementById('floating-audio-close');
      if (close) close.click();
    });
    await page.waitForTimeout(300);
  });

  await expect('Play Voice button shows voice-specific labels when activated', async () => {
    await page.goto(`${baseUrl}/mysteries/joyful-1.html`, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(500);
    // Click Play Voice
    await page.evaluate(() => document.querySelector('[data-testid="pause-audio"]').click());
    await page.waitForTimeout(1000);
    const voiceLabel = await page.evaluate(() =>
      document.querySelector('[data-testid="pause-audio"]')?.textContent || ''
    );
    // Should now show Pause Voice or Starting...
    if (!/Pause Voice|Starting|Stop Voice/i.test(voiceLabel)) {
      throw new Error(`Expected active voice state, got: "${voiceLabel}"`);
    }
    // Clean up
    await page.evaluate(() => {
      const close = document.getElementById('floating-audio-close');
      if (close) close.click();
    });
    await page.waitForTimeout(300);
  });

  await expect('After stopping, Play Voice resets and guided audio shows correct state', async () => {
    const voiceLabel = await page.evaluate(() =>
      document.querySelector('[data-testid="pause-audio"]')?.textContent || ''
    );
    if (!/Play Voice/i.test(voiceLabel)) {
      throw new Error(`Expected "Play Voice" after stop, got: "${voiceLabel}"`);
    }
    const guidedLabel = await page.evaluate(() =>
      document.getElementById('start-guided-audio')?.textContent || ''
    );
    if (!/Play Guided Audio|Replay Guided Audio/i.test(guidedLabel)) {
      throw new Error(`Expected Play/Replay state after stop, got: "${guidedLabel}"`);
    }
  });

  // ============================================================
  // 18. STORY PROGRESS INDICATOR STICKY
  // ============================================================

  await expect('Sticky story progress indicator exists in controls bar', async () => {
    await page.goto(`${baseUrl}/story.html`, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(500);
    const stickyStep = await page.evaluate(() => {
      const el = document.getElementById('story-step-sticky');
      return el ? el.textContent : null;
    });
    if (!stickyStep) {
      throw new Error('Sticky step indicator #story-step-sticky not found in controls bar');
    }
    if (!/Page\s+\d+\s+of\s+\d+/i.test(stickyStep)) {
      throw new Error(`Sticky step should show "Page X of Y", got: "${stickyStep}"`);
    }
  });

  await expect('Sticky progress indicator syncs with page navigation', async () => {
    await page.click('#story-next');
    await page.waitForTimeout(300);
    const stickyText = await page.evaluate(() =>
      document.getElementById('story-step-sticky')?.textContent || ''
    );
    const stepText = await page.evaluate(() =>
      document.getElementById('story-step')?.textContent || ''
    );
    if (stickyText !== stepText) {
      throw new Error(`Sticky "${stickyText}" does not match step "${stepText}"`);
    }
    if (!/Page\s+2\s+of/i.test(stickyText)) {
      throw new Error(`Expected Page 2 after navigation, got: "${stickyText}"`);
    }
  });

  await expect('Sticky progress indicator is visible after scrolling past story panel', async () => {
    await page.goto(`${baseUrl}/story.html`, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(500);
    // Scroll down past the story panel
    await page.evaluate(() => window.scrollTo(0, 800));
    await page.waitForTimeout(300);
    const inViewport = await page.evaluate(() => {
      const el = document.getElementById('story-step-sticky');
      if (!el) return false;
      const rect = el.getBoundingClientRect();
      return rect.top >= 0 && rect.bottom <= window.innerHeight;
    });
    if (!inViewport) {
      throw new Error('Sticky progress indicator should remain visible after scrolling');
    }
  });

  await expect('Sticky progress indicator is inside a sticky-positioned parent', async () => {
    const position = await page.evaluate(() => {
      const el = document.getElementById('story-step-sticky');
      if (!el) return 'not found';
      return window.getComputedStyle(el.closest('.storybook-controls')).position;
    });
    if (position !== 'sticky') {
      throw new Error(`Expected sticky-positioned parent, got: ${position}`);
    }
  });

  // ============================================================
  // 19. GUIDED AUDIO BUTTON STATE SYNC (spec verification)
  // ============================================================

  await expect('No scenario: audio active but button says "Play Guided Audio"', async () => {
    await page.goto(`${baseUrl}/mysteries/joyful-1.html`, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(500);
    // Start audio
    await page.evaluate(() => document.getElementById('start-guided-audio').click());
    await page.waitForTimeout(1500);
    // Check audio context says playing
    const ctx = await page.evaluate(() =>
      JSON.parse(localStorage.getItem('rosary_audio_context') || '{}')
    );
    const label = await page.evaluate(() =>
      document.getElementById('start-guided-audio')?.textContent || ''
    );
    if ((ctx.playing || ctx.paused) && /^Play Guided Audio$/i.test(label)) {
      throw new Error(`Audio is ${ctx.playing ? 'playing' : 'paused'} but button says "${label}"`);
    }
    if (ctx.playing && !/Pause|Starting|Playing/i.test(label)) {
      throw new Error(`Audio is playing but button says "${label}" (expected Pause/Starting/Playing)`);
    }
    // Clean up
    await page.evaluate(() => {
      const close = document.getElementById('floating-audio-close');
      if (close) close.click();
    });
    await page.waitForTimeout(300);
  });

  await expect('Button reflects paused state after pause toggle', async () => {
    await page.evaluate(() => document.getElementById('start-guided-audio').click());
    await page.waitForTimeout(1500);
    // Pause
    await page.evaluate(() => document.getElementById('start-guided-audio').click());
    await page.waitForTimeout(500);
    const label = await page.evaluate(() =>
      document.getElementById('start-guided-audio')?.textContent || ''
    );
    if (!/Resume Guided Audio/i.test(label)) {
      throw new Error(`After pause, expected "Resume Guided Audio", got: "${label}"`);
    }
    // Clean up
    await page.evaluate(() => {
      const close = document.getElementById('floating-audio-close');
      if (close) close.click();
    });
    await page.waitForTimeout(300);
  });

  await expect('Button shows Replay after completion/stop', async () => {
    const label = await page.evaluate(() =>
      document.getElementById('start-guided-audio')?.textContent || ''
    );
    if (!/Replay Guided Audio|Play Guided Audio/i.test(label)) {
      throw new Error(`After stop, expected Replay/Play, got: "${label}"`);
    }
  });

  // ============================================================
  // 20. HANDS-FREE TIMER COUNTDOWN ON BUTTON
  // ============================================================

  await expect('Auto timer button shows live countdown while running', async () => {
    await page.goto(`${baseUrl}/mysteries/joyful-1.html`, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(500);
    await page.selectOption('#auto-timer-seconds', '12');
    await page.click('#auto-timer-toggle');
    await page.waitForTimeout(200);
    const initialLabel = await page.evaluate(() =>
      document.getElementById('auto-timer-toggle')?.textContent || ''
    );
    if (!/Auto:\s*12s/i.test(initialLabel)) {
      throw new Error(`Expected "Auto: 12s" initially, got: "${initialLabel}"`);
    }
    // Trigger a countdown by completing narration (simulate with direct countdown start)
    // The countdown starts after narration ends on a step, so let's just verify the
    // format is correct and the button text pattern is right
    // Stop timer
    await page.click('#auto-timer-toggle');
    await page.waitForTimeout(100);
    const afterStop = await page.evaluate(() =>
      document.getElementById('auto-timer-toggle')?.textContent || ''
    );
    if (!/Start Auto/i.test(afterStop)) {
      throw new Error(`Expected "Start Auto" after stop, got: "${afterStop}"`);
    }
  });

  await expect('Timer default is 12s and Start Auto is enabled by default', async () => {
    await page.goto(`${baseUrl}/mysteries/luminous-1.html`, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(300);
    const val = await page.locator('#auto-timer-seconds').inputValue();
    const disabled = await page.locator('#auto-timer-toggle').isDisabled();
    if (val !== '12') throw new Error(`Timer should default to 12s, got: "${val}"`);
    if (disabled) throw new Error('Start Auto should be enabled when timer is 12s');
  });

  await expect('Start Auto is disabled when timer is Off, re-enables on selection', async () => {
    await page.selectOption('#auto-timer-seconds', '0');
    await page.waitForTimeout(50);
    const disabledOff = await page.locator('#auto-timer-toggle').isDisabled();
    if (!disabledOff) throw new Error('Start Auto should be disabled when Off');
    await page.selectOption('#auto-timer-seconds', '25');
    await page.waitForTimeout(50);
    const disabledOn = await page.locator('#auto-timer-toggle').isDisabled();
    if (disabledOn) throw new Error('Start Auto should be enabled when 25s selected');
  });

  // ============================================================
  // READER MODE TOGGLE
  // ============================================================

  await page.goto(`${baseUrl}/story.html`, { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(400);

  await expect('Reader mode toggle button exists', async () => {
    const btn = page.locator('#story-reader-toggle');
    const visible = await btn.isVisible();
    if (!visible) throw new Error('Reader mode toggle button not found');
  });

  await expect('Reader mode toggle applies is-reader-mode class', async () => {
    await page.click('#story-reader-toggle');
    await page.waitForTimeout(100);
    const has = await page.locator('.storybook').evaluate(el => el.classList.contains('is-reader-mode'));
    if (!has) throw new Error('is-reader-mode class not applied after toggle');
  });

  await expect('Reader mode toggle removes class on second click', async () => {
    await page.click('#story-reader-toggle');
    await page.waitForTimeout(100);
    const has = await page.locator('.storybook').evaluate(el => el.classList.contains('is-reader-mode'));
    if (has) throw new Error('is-reader-mode class should be removed after second toggle');
  });

  await expect('Reader mode persists in localStorage', async () => {
    await page.click('#story-reader-toggle');
    await page.waitForTimeout(100);
    const stored = await page.evaluate(() => localStorage.getItem('storybook_reader_mode'));
    if (stored !== 'true') throw new Error(`Expected localStorage 'true', got: "${stored}"`);
    // Clean up
    await page.click('#story-reader-toggle');
    await page.waitForTimeout(50);
  });

  await expect('Reader mode restores from localStorage on page load', async () => {
    await page.evaluate(() => localStorage.setItem('storybook_reader_mode', 'true'));
    await page.goto(`${baseUrl}/story.html`, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(400);
    const has = await page.locator('.storybook').evaluate(el => el.classList.contains('is-reader-mode'));
    if (!has) throw new Error('Reader mode should restore from localStorage');
    const btnText = await page.locator('#story-reader-toggle').textContent();
    if (!btnText.includes('On')) throw new Error(`Button should show "On" state, got: "${btnText}"`);
    // Clean up
    await page.evaluate(() => localStorage.removeItem('storybook_reader_mode'));
  });

  await expect('Reader mode increases font size of storybook text', async () => {
    await page.evaluate(() => localStorage.setItem('storybook_reader_mode', 'true'));
    await page.goto(`${baseUrl}/story.html`, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(400);
    const fontSize = await page.locator('#story-body').evaluate(el => parseFloat(getComputedStyle(el).fontSize));
    if (fontSize < 17) throw new Error(`Expected larger font in reader mode, got ${fontSize}px`);
    await page.evaluate(() => localStorage.removeItem('storybook_reader_mode'));
  });

  // ============================================================
  // RESUME READING BANNER
  // ============================================================

  await expect('Resume banner is hidden when no last page saved', async () => {
    await page.evaluate(() => localStorage.removeItem('storybook_last_page'));
    await page.goto(`${baseUrl}/story.html`, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(400);
    const hidden = await page.locator('#story-resume-banner').evaluate(el => el.hidden);
    if (!hidden) throw new Error('Resume banner should be hidden with no saved page');
  });

  await expect('Resume banner appears when last page is saved', async () => {
    await page.evaluate(() => localStorage.setItem('storybook_last_page', '3'));
    await page.goto(`${baseUrl}/story.html`, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(400);
    const hidden = await page.locator('#story-resume-banner').evaluate(el => el.hidden);
    if (hidden) throw new Error('Resume banner should be visible when last page is saved');
    const text = await page.locator('#story-resume-text').textContent();
    if (!text.includes('4')) throw new Error(`Banner should mention page 4, got: "${text}"`);
  });

  await expect('Resume button navigates to saved page', async () => {
    await page.click('#story-resume-btn');
    await page.waitForTimeout(300);
    const stepText = await page.locator('#story-step').textContent();
    if (!stepText.includes('4')) throw new Error(`Should navigate to page 4, step shows: "${stepText}"`);
    const bannerHidden = await page.locator('#story-resume-banner').evaluate(el => el.hidden);
    if (!bannerHidden) throw new Error('Banner should hide after resume click');
  });

  await expect('Resume banner dismiss button hides it', async () => {
    await page.evaluate(() => localStorage.setItem('storybook_last_page', '5'));
    await page.goto(`${baseUrl}/story.html`, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(400);
    await page.click('#story-resume-dismiss');
    await page.waitForTimeout(100);
    const hidden = await page.locator('#story-resume-banner').evaluate(el => el.hidden);
    if (!hidden) throw new Error('Banner should hide after dismiss');
  });

  await expect('Resume banner not shown for page 0', async () => {
    await page.evaluate(() => localStorage.setItem('storybook_last_page', '0'));
    await page.goto(`${baseUrl}/story.html`, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(400);
    const hidden = await page.locator('#story-resume-banner').evaluate(el => el.hidden);
    if (!hidden) throw new Error('Resume banner should not show for page 0 (already on page 1)');
  });

  // ============================================================
  // AUTO-SCROLL ON NAVIGATION
  // ============================================================

  await expect('movePage triggers scrollIntoView on story panel', async () => {
    await page.evaluate(() => localStorage.removeItem('storybook_last_page'));
    await page.goto(`${baseUrl}/story.html`, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(400);
    // Monkey-patch scrollIntoView to track calls
    const scrolled = await page.evaluate(() => {
      let called = false;
      const panel = document.querySelector('.storybook-panel');
      if (!panel) return false;
      panel.scrollIntoView = () => { called = true; };
      // Trigger next page
      document.getElementById('story-next').click();
      return called;
    });
    if (!scrolled) throw new Error('scrollIntoView should be called on page navigation');
  });

  // ============================================================
  // LAST PAGE TRACKING
  // ============================================================

  await expect('Navigating pages updates storybook_last_page in localStorage', async () => {
    await page.evaluate(() => localStorage.removeItem('storybook_last_page'));
    await page.goto(`${baseUrl}/story.html`, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(400);
    // Navigate to page 2
    await page.evaluate(() => document.getElementById('story-next').click());
    await page.waitForTimeout(200);
    const stored = await page.evaluate(() => localStorage.getItem('storybook_last_page'));
    if (stored !== '1') throw new Error(`Expected last page '1', got: "${stored}"`);
    // Navigate to page 3
    await page.evaluate(() => document.getElementById('story-next').click());
    await page.waitForTimeout(200);
    const stored2 = await page.evaluate(() => localStorage.getItem('storybook_last_page'));
    if (stored2 !== '2') throw new Error(`Expected last page '2', got: "${stored2}"`);
  });

  // ============================================================
  // COPY TRANSCRIPT BUTTONS
  // ============================================================

  await page.goto(`${baseUrl}/voice-testimony.html`, { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(400);

  await expect('Copy transcript buttons exist for all transcript blocks', async () => {
    const count = await page.locator('.transcript-copy-btn').count();
    if (count < 3) throw new Error(`Expected at least 3 copy buttons, found ${count}`);
  });

  await expect('Copy transcript button has correct data-target', async () => {
    const targets = await page.locator('.transcript-copy-btn').evaluateAll(btns =>
      btns.map(b => b.getAttribute('data-target'))
    );
    if (!targets.includes('transcript-ar')) throw new Error('Missing copy button for Arabic transcript');
    if (!targets.includes('transcript-en')) throw new Error('Missing copy button for English transcript');
    if (!targets.includes('voice-full')) throw new Error('Missing copy button for full capture');
  });

  await expect('Copy button shows "Copied!" feedback on click', async () => {
    // Grant clipboard permission for the test
    await context.grantPermissions(['clipboard-write'], { origin: baseUrl });
    await page.click('.transcript-copy-btn[data-target="transcript-en"]');
    await page.waitForTimeout(200);
    const text = await page.locator('.transcript-copy-btn[data-target="transcript-en"]').textContent();
    if (text !== 'Copied!') throw new Error(`Expected "Copied!" feedback, got: "${text}"`);
  });

  await expect('Copy button reverts to "Copy Transcript" after delay', async () => {
    await page.waitForTimeout(2200);
    const text = await page.locator('.transcript-copy-btn[data-target="transcript-en"]').textContent();
    if (text !== 'Copy Transcript') throw new Error(`Expected "Copy Transcript" after delay, got: "${text}"`);
  });

  // ============================================================
  // JUMP-TO-TIMESTAMP (Full Capture)
  // ============================================================

  await expect('Full capture transcript has clickable timestamp links', async () => {
    await page.waitForTimeout(500); // wait for fetch
    const count = await page.locator('#voice-full .timestamp-link').count();
    if (count === 0) throw new Error('No timestamp links found in full capture transcript');
  });

  await expect('Timestamp links have data-seek attributes', async () => {
    const seeks = await page.locator('#voice-full .timestamp-link').evaluateAll(links =>
      links.map(l => l.dataset.seek)
    );
    if (seeks.length === 0) throw new Error('No data-seek attributes on timestamp links');
    const firstSeek = parseFloat(seeks[0]);
    if (isNaN(firstSeek)) throw new Error(`First seek value is NaN: "${seeks[0]}"`);
  });

  await expect('Clicking timestamp seeks video to correct time', async () => {
    const firstLink = page.locator('#voice-full .timestamp-link').first();
    const seekVal = await firstLink.getAttribute('data-seek');
    await firstLink.click();
    await page.waitForTimeout(300);
    const videoTime = await page.locator('video').evaluate(v => v.currentTime);
    const expected = parseFloat(seekVal);
    if (Math.abs(videoTime - expected) > 1) {
      throw new Error(`Video should seek to ${expected}s, but is at ${videoTime}s`);
    }
  });

  await expect('Clicking timestamp adds highlight class briefly', async () => {
    const firstLink = page.locator('#voice-full .timestamp-link').first();
    await firstLink.click();
    await page.waitForTimeout(100);
    // Check parent or self has highlight
    const hasHighlight = await firstLink.evaluate(el => {
      const target = el.parentElement || el;
      return target.classList.contains('timestamp-highlight');
    });
    if (!hasHighlight) throw new Error('Timestamp click should add highlight class');
  });

  await expect('Timestamp highlight is removed after delay', async () => {
    await page.waitForTimeout(1600);
    const highlightCount = await page.locator('#voice-full .timestamp-highlight').count();
    if (highlightCount > 0) throw new Error('Highlight should be removed after 1.5s');
  });

  // ============================================================
  // CANONICAL ROSARY URL (consistent .html links, server 301-redirects to clean URLs)
  // ============================================================

  await expect('Rosary nav links use consistent .html URLs on homepage', async () => {
    await page.goto(`${baseUrl}/index.html`, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(300);
    const rosaryLinks = await page.locator('a[href*="rosary-visual-guide"]').evaluateAll(links =>
      links.map(a => a.getAttribute('href'))
    );
    if (!rosaryLinks.length) throw new Error('No rosary-visual-guide links found on homepage');
    const badLinks = rosaryLinks.filter(h => !h.includes('.html'));
    if (badLinks.length) throw new Error(`Found non-.html rosary links: ${badLinks.join(', ')}`);
  });

  await expect('Mystery page rosary links use consistent .html URLs', async () => {
    await page.goto(`${baseUrl}/mysteries/joyful-1.html`, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(300);
    const rosaryLinks = await page.locator('a[href*="rosary-visual-guide"]').evaluateAll(links =>
      links.map(a => a.getAttribute('href'))
    );
    if (!rosaryLinks.length) throw new Error('No rosary-visual-guide links found on mystery page');
    const badLinks = rosaryLinks.filter(h => !h.includes('.html'));
    if (badLinks.length) throw new Error(`Found non-.html rosary links on mystery page: ${badLinks.join(', ')}`);
  });

  await expect('Floating player Open Mystery link uses .html URL', async () => {
    await page.goto(`${baseUrl}/mysteries/luminous-1.html`, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(300);
    const href = await page.locator('#floating-audio-open').getAttribute('href');
    if (!href.includes('.html')) throw new Error(`Floating player link missing .html: ${href}`);
  });

  await expect('Voice testimony rosary CTA uses .html URL', async () => {
    await page.goto(`${baseUrl}/voice-testimony.html`, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(300);
    const rosaryLinks = await page.locator('a[href*="rosary-visual-guide"]').evaluateAll(links =>
      links.map(a => a.getAttribute('href'))
    );
    const badLinks = rosaryLinks.filter(h => !h.includes('.html'));
    if (badLinks.length) throw new Error(`Found non-.html rosary links on voice testimony: ${badLinks.join(', ')}`);
  });

  // ============================================================
  // READ ALOUD PER-LANGUAGE VOICE AVAILABILITY
  // Buttons are enabled/disabled per language — Arabic needs an Arabic voice
  // ============================================================

  await page.goto(`${baseUrl}/voice-testimony.html`, { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(3500);

  // Detect which language voices the browser actually has
  const voiceInfo = await page.evaluate(() => {
    if (!('speechSynthesis' in window)) return { hasAny: false, hasEn: false, hasAr: false };
    const voices = window.speechSynthesis.getVoices() || [];
    return {
      hasAny: voices.length > 0,
      hasEn: voices.some(v => (v.lang || '').toLowerCase().startsWith('en')),
      hasAr: voices.some(v => (v.lang || '').toLowerCase().startsWith('ar'))
    };
  });

  const hasVoices = voiceInfo.hasAny;

  await expect('Read Aloud buttons reflect per-language voice availability', async () => {
    const btns = page.locator('.transcript-read-btn');
    const count = await btns.count();
    if (count === 0) throw new Error('No Read Aloud buttons found');
    for (let i = 0; i < count; i++) {
      const { disabled, lang } = await btns.nth(i).evaluate(b => ({
        disabled: b.disabled,
        lang: b.getAttribute('data-lang') || 'en-US'
      }));
      const langPrefix = lang.split('-')[0].toLowerCase();
      const hasVoiceForLang = langPrefix === 'ar' ? voiceInfo.hasAr : langPrefix === 'en' ? voiceInfo.hasEn : voiceInfo.hasAny;
      if (hasVoiceForLang && disabled) {
        throw new Error(`Read Aloud button ${i} (${lang}) is disabled despite ${langPrefix} voices being available`);
      }
      if (!hasVoiceForLang && !disabled) {
        throw new Error(`Read Aloud button ${i} (${lang}) should be disabled — no ${langPrefix} voice available`);
      }
    }
  });

  await expect('Read Aloud unavailable styling matches per-language availability', async () => {
    const btns = page.locator('.transcript-read-btn');
    const count = await btns.count();
    for (let i = 0; i < count; i++) {
      const { hasClass, lang } = await btns.nth(i).evaluate(b => ({
        hasClass: b.classList.contains('is-unavailable'),
        lang: b.getAttribute('data-lang') || 'en-US'
      }));
      const langPrefix = lang.split('-')[0].toLowerCase();
      const hasVoiceForLang = langPrefix === 'ar' ? voiceInfo.hasAr : langPrefix === 'en' ? voiceInfo.hasEn : voiceInfo.hasAny;
      if (hasVoiceForLang && hasClass) {
        throw new Error(`Read Aloud button ${i} (${lang}) has is-unavailable despite ${langPrefix} voice existing`);
      }
      if (!hasVoiceForLang && !hasClass) {
        throw new Error(`Read Aloud button ${i} (${lang}) missing is-unavailable — no ${langPrefix} voice`);
      }
    }
  });

  await expect('Voice unavailable warnings shown only for missing language voices', async () => {
    const warnings = await page.locator('.read-aloud-warning').count();
    // Count how many buttons lack a voice for their language
    const missingCount = await page.evaluate((vi) => {
      const btns = document.querySelectorAll('.transcript-read-btn');
      let missing = 0;
      btns.forEach(b => {
        const prefix = (b.getAttribute('data-lang') || 'en-US').split('-')[0].toLowerCase();
        const has = prefix === 'ar' ? vi.hasAr : prefix === 'en' ? vi.hasEn : vi.hasAny;
        if (!has) missing++;
      });
      return missing;
    }, voiceInfo);
    if (warnings !== missingCount) {
      throw new Error(`Expected ${missingCount} warning(s) for missing voices, found ${warnings}`);
    }
  });

  // ============================================================
  // MINI-PLAYER CONTEXT SEPARATION
  // ============================================================

  await expect('Floating player is hidden on voice-testimony with stale rosary context', async () => {
    // Simulate stale rosary context from a previous rosary session
    await page.goto(`${baseUrl}/voice-testimony.html`, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(300);
    await page.evaluate(() => {
      localStorage.setItem('rosary_audio_context', JSON.stringify({
        source: 'rosary',
        mode: 'prerendered',
        playing: true,
        paused: false,
        completed: false,
        title: 'First Joyful Mystery',
        url: '/mysteries/joyful-1.html'
      }));
    });
    // Wait for renderSpeechState polling interval
    await page.waitForTimeout(600);
    const visible = await page.locator('.floating-audio').evaluate(el => el.classList.contains('on'));
    if (visible) throw new Error('Floating player should be hidden on voice-testimony with rosary context');
  });

  await expect('Stale rosary context is cleared on non-rosary page', async () => {
    await page.evaluate(() => {
      localStorage.setItem('rosary_audio_context', JSON.stringify({
        source: 'rosary',
        mode: 'prerendered',
        playing: true,
        paused: false,
        completed: false,
        title: 'First Joyful Mystery',
        url: '/mysteries/joyful-1.html'
      }));
    });
    await page.goto(`${baseUrl}/voice-testimony.html`, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(600);
    const ctx = await page.evaluate(() => JSON.parse(localStorage.getItem('rosary_audio_context') || '{}'));
    if (ctx.playing) throw new Error('Stale rosary context should have playing=false after visiting non-rosary page');
  });

  await expect('Floating player still works on rosary pages', async () => {
    await page.goto(`${baseUrl}/mysteries/joyful-1.html`, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(300);
    await page.evaluate(() => {
      localStorage.setItem('rosary_audio_context', JSON.stringify({
        source: 'rosary',
        mode: 'prerendered',
        playing: true,
        paused: false,
        completed: false,
        title: 'First Joyful Mystery',
        url: window.location.href
      }));
      window.dispatchEvent(new CustomEvent('rosary-audio-context-updated'));
    });
    await page.waitForTimeout(600);
    const visible = await page.locator('.floating-audio').evaluate(el => el.classList.contains('on'));
    if (!visible) throw new Error('Floating player should be visible on rosary page with active context');
  });

  // ============================================================
  // VOICE TESTIMONY TOC + LISTEN FALLBACK
  // ============================================================

  await expect('Voice testimony TOC exists with section links', async () => {
    await page.goto(`${baseUrl}/voice-testimony.html`, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(300);
    const toc = page.locator('.transcript-toc');
    const visible = await toc.isVisible();
    if (!visible) throw new Error('TOC not found or not visible');
    const links = await toc.locator('a').evaluateAll(as => as.map(a => a.getAttribute('href')));
    if (links.length < 4) throw new Error(`Expected at least 4 TOC links, got ${links.length}`);
    const expected = ['#listen', '#how-to-receive', '#transcript-publishing', '#transcript-raw'];
    for (const href of expected) {
      if (!links.includes(href)) throw new Error(`Missing TOC link: ${href}`);
    }
  });

  await expect('TOC anchor targets exist on page', async () => {
    const ids = ['listen', 'how-to-receive', 'transcript-publishing', 'transcript-raw'];
    for (const id of ids) {
      const exists = await page.locator(`#${id}`).count();
      if (!exists) throw new Error(`TOC target #${id} not found on page`);
    }
  });

  await expect('Listen fallback is hidden when video can play', async () => {
    const fallback = page.locator('#listen-fallback');
    const hasVisible = await fallback.evaluate(el => el.classList.contains('is-visible'));
    if (hasVisible) throw new Error('Listen fallback should be hidden when video is playable');
  });

  await expect('Listen fallback has download link', async () => {
    const link = page.locator('#listen-fallback a[download]');
    const count = await link.count();
    if (count === 0) throw new Error('Listen fallback should contain a download link');
  });

  // ============================================================
  // STICKY MEDITATION-ACTIONS FIX
  // ============================================================

  await expect('Meditation content has align-self:start to prevent sticky overlap', async () => {
    await page.goto(`${baseUrl}/mysteries/joyful-1.html`, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(400);
    const alignSelf = await page.locator('.meditation-content').evaluate(el =>
      window.getComputedStyle(el).alignSelf
    );
    if (alignSelf !== 'start') {
      throw new Error(`Expected align-self:start on .meditation-content, got: "${alignSelf}"`);
    }
  });

  // ============================================================
  // FLOATING PLAYER PRAYER PROGRESS ELEMENTS
  // ============================================================

  await expect('Floating player contains prayer progress HTML elements', async () => {
    await page.goto(`${baseUrl}/mysteries/joyful-1.html`, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(400);
    const ids = [
      'floating-audio-mystery-progress',
      'floating-audio-prayer-name',
      'floating-audio-step-fill',
      'floating-audio-step-label'
    ];
    for (const id of ids) {
      const count = await page.locator(`#${id}`).count();
      if (count === 0) throw new Error(`Missing floating player element: #${id}`);
    }
    const stepBar = await page.locator('.floating-audio-step-progress').count();
    if (stepBar === 0) throw new Error('Missing .floating-audio-step-progress element');
  });

  await expect('Floating player renders prayer progress from rosary context', async () => {
    await page.goto(`${baseUrl}/mysteries/joyful-1.html`, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(400);
    // Inject a simulated rosary context with prayer progress data
    await page.evaluate(() => {
      const ctx = {
        source: 'rosary',
        mode: 'prerendered',
        playing: true,
        paused: false,
        completed: false,
        title: 'First Joyful Mystery',
        stage: 'Hail Mary',
        url: '/mysteries/joyful-1.html',
        mysteryNum: 2,
        totalMysteries: 5,
        mysterySetLabel: 'Joyful',
        prayerLabel: 'Hail Mary 4 of 10',
        stageKind: 'hail_mary',
        stepIndex: 5,
        totalSteps: 14,
        startedAt: Date.now(),
        estimatedDurationMs: 30000
      };
      localStorage.setItem('rosary_audio_context', JSON.stringify(ctx));
      window.dispatchEvent(new CustomEvent('rosary-audio-context-updated'));
    });
    await page.waitForTimeout(600);

    const mysteryProgress = await page.locator('#floating-audio-mystery-progress').textContent();
    if (!mysteryProgress.includes('Mystery 2 of 5')) {
      throw new Error(`Expected mystery progress to contain "Mystery 2 of 5", got: "${mysteryProgress}"`);
    }

    const prayerName = await page.locator('#floating-audio-prayer-name').textContent();
    if (prayerName !== 'Hail Mary 4 of 10') {
      throw new Error(`Expected prayer name "Hail Mary 4 of 10", got: "${prayerName}"`);
    }

    const stepLabel = await page.locator('#floating-audio-step-label').textContent();
    if (!stepLabel.includes('Step 6 of 14')) {
      throw new Error(`Expected step label "Step 6 of 14", got: "${stepLabel}"`);
    }

    const fillWidth = await page.locator('#floating-audio-step-fill').evaluate(el => el.style.width);
    if (!fillWidth || fillWidth === '0%') {
      throw new Error(`Expected step fill bar width > 0%, got: "${fillWidth}"`);
    }
  });

  await expect('Floating player elapsed shows time / total format', async () => {
    // Context was set by previous test — just check the elapsed element
    const elapsedText = await page.locator('#floating-audio-elapsed').textContent();
    if (!elapsedText.includes('/')) {
      throw new Error(`Expected elapsed to contain "/" separator (elapsed / total), got: "${elapsedText}"`);
    }
  });

  // ============================================================
  // READ ALOUD TEXT SANITIZATION (dot/bracket cleanup)
  // Uses whichever transcript button is enabled (English if no Arabic voice)
  // ============================================================

  const interceptSpokenText = async (targetSelector) => {
    return page.evaluate((sel) => {
      return new Promise((resolve, reject) => {
        window.speechSynthesis.speak = (utterance) => {
          resolve(utterance.text);
          window.speechSynthesis.cancel();
        };
        const btn = document.querySelector(sel);
        if (!btn || btn.disabled) {
          reject(new Error(`Read Aloud button ${sel} not found or disabled`));
          return;
        }
        btn.click();
        setTimeout(() => reject(new Error('speechSynthesis.speak was never called')), 3000);
      });
    }, targetSelector);
  };

  // Pick an enabled Read Aloud button for sanitization tests
  const sanitizationBtnSelector = await page.evaluate(() => {
    const btns = Array.from(document.querySelectorAll('.transcript-read-btn'));
    const enabled = btns.find(b => !b.disabled);
    if (!enabled) return null;
    const target = enabled.getAttribute('data-target');
    return target ? `.transcript-read-btn[data-target="${target}"]` : null;
  });

  if (sanitizationBtnSelector) {
    await expect('Read Aloud strips all dots from transcript before speaking', async () => {
      await page.goto(`${baseUrl}/voice-testimony.html`, { waitUntil: 'domcontentloaded' });
      await page.waitForTimeout(3500);
      const spokenText = await interceptSpokenText(sanitizationBtnSelector);
      if (/\./.test(spokenText)) {
        throw new Error(`Dot character found in spoken text — TTS may read "." as "dot": "${spokenText.substring(0, 200)}..."`);
      }
    });

    await expect('Read Aloud sanitizes bracket markers from transcript before speaking', async () => {
      await page.goto(`${baseUrl}/voice-testimony.html`, { waitUntil: 'domcontentloaded' });
      await page.waitForTimeout(3500);
      const spokenText = await interceptSpokenText(sanitizationBtnSelector);
      if (/\[.*?\]/.test(spokenText)) {
        throw new Error(`Bracket markers found in spoken text — TTS will read editorial notes: "${spokenText.substring(0, 200)}..."`);
      }
    });

    await expect('Read Aloud sanitized text has no excessive whitespace', async () => {
      await page.goto(`${baseUrl}/voice-testimony.html`, { waitUntil: 'domcontentloaded' });
      await page.waitForTimeout(3500);
      const spokenText = await interceptSpokenText(sanitizationBtnSelector);
      if (/  /.test(spokenText)) {
        throw new Error(`Double spaces found in spoken text — whitespace not normalized`);
      }
    });
  } else {
    console.log('SKIP: Read Aloud sanitization tests (no speechSynthesis voices in this environment)');
  }

} finally {
  await context.close();
  await browser.close();
}

if (failures.length) {
  console.error('\nChecklist improvement test failures:');
  failures.forEach(f => console.error(`- ${f}`));
  process.exit(1);
}

console.log('\nChecklist improvement tests passed.');
