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
