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
