#!/usr/bin/env node

/**
 * UI Regression Tests for the 6 bugs fixed in PR #10.
 * Covers: audio coupling, studio track visibility, mystery numbering,
 * language picker duplicates, and data-testid / notranslate on all pages.
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

const mysteryPages = [
  'joyful-1', 'joyful-2', 'joyful-3', 'joyful-4', 'joyful-5',
  'luminous-1', 'luminous-2', 'luminous-3', 'luminous-4', 'luminous-5',
  'sorrowful-1', 'sorrowful-2', 'sorrowful-3', 'sorrowful-4', 'sorrowful-5',
  'glorious-1', 'glorious-2', 'glorious-3', 'glorious-4', 'glorious-5'
];

const setNames = {
  joyful: 'Joyful Mysteries',
  luminous: 'Luminous Mysteries',
  sorrowful: 'Sorrowful Mysteries',
  glorious: 'Glorious Mysteries'
};

const requiredTestIds = [
  'prev-step', 'next-step', 'pause-audio', 'toggle-sound',
  'play-studio', 'auto-timer-toggle', 'start-guided-audio'
];

const browser = await chromium.launch({ headless: true });
const context = await browser.newContext();
const page = await context.newPage();

try {
  // --- Bug 1: Audio state coupling ---
  await page.goto(`${baseUrl}/mysteries/joyful-1.html`, { waitUntil: 'domcontentloaded' });

  await expect('Play Voice stays independent after clicking Play Guided Audio', async () => {
    const voiceBefore = await page.locator('[data-testid="pause-audio"]').textContent();
    if (voiceBefore !== 'Play Voice') {
      throw new Error(`Expected initial label "Play Voice", got: ${voiceBefore}`);
    }
    await page.click('#start-guided-audio');
    await page.waitForTimeout(1500);
    const voiceAfter = await page.locator('[data-testid="pause-audio"]').textContent();
    if (voiceAfter !== 'Play Voice') {
      throw new Error(`Voice button changed to "${voiceAfter}" after guided audio start`);
    }
    const guidedLabel = (await page.locator('#start-guided-audio').textContent())?.trim();
    if (!/Pause Guided Audio|Playing Guided Audio|Replay Guided Audio/i.test(guidedLabel)) {
      throw new Error(`Guided audio button should show playing state, got: ${guidedLabel}`);
    }
  });

  // --- Bug 3: Studio track button hidden until audio loads ---
  await expect('Studio track button is hidden before audio metadata loads', async () => {
    await page.goto(`${baseUrl}/mysteries/joyful-1.html`, { waitUntil: 'domcontentloaded' });
    const hidden = await page.evaluate(() => {
      const el = document.getElementById('play-studio');
      if (!el) return 'missing';
      return el.hidden || el.style.display === 'none';
    });
    if (hidden === 'missing') {
      throw new Error('Studio track button element not found');
    }
    if (!hidden) {
      throw new Error('Studio track button should be hidden initially');
    }
  });

  // --- Bug 4: Mystery numbering across all sets ---
  for (const mystery of ['joyful-1', 'luminous-1', 'sorrowful-1', 'glorious-1']) {
    const [set, num] = mystery.split('-');
    const expectedSet = setNames[set];

    await expect(`Mystery numbering correct on ${mystery}`, async () => {
      await page.goto(`${baseUrl}/mysteries/${mystery}.html`, { waitUntil: 'domcontentloaded' });
      const progress = await page.evaluate(() => {
        const el = document.getElementById('mystery-hero-progress');
        return el ? el.textContent.trim() : null;
      });
      if (!progress) {
        throw new Error('Mystery hero progress element not found');
      }
      const expected = `Mystery ${num} of 5`;
      if (!progress.includes(expected)) {
        throw new Error(`Expected "${expected}", got: ${progress}`);
      }
      if (!progress.includes(expectedSet)) {
        throw new Error(`Expected set name "${expectedSet}" in progress, got: ${progress}`);
      }
    });
  }

  // Also test non-first mystery to verify index
  await expect('Mystery 3 of 5 shows correct numbering', async () => {
    await page.goto(`${baseUrl}/mysteries/joyful-3.html`, { waitUntil: 'domcontentloaded' });
    const progress = await page.evaluate(() => {
      const el = document.getElementById('mystery-hero-progress');
      return el ? el.textContent.trim() : null;
    });
    if (!/Mystery 3 of 5/.test(progress)) {
      throw new Error(`Expected "Mystery 3 of 5", got: ${progress}`);
    }
  });

  // --- Bug 5: Language picker has no duplicates ---
  await expect('Language picker has no duplicate entries', async () => {
    await page.goto(`${baseUrl}/mysteries/joyful-1.html`, { waitUntil: 'domcontentloaded' });
    const result = await page.evaluate(() => {
      const select = document.querySelector('.lang-switcher select');
      if (!select) return { error: 'no language select found' };
      const labels = Array.from(select.options).map(o => o.textContent.trim());
      const values = Array.from(select.options).map(o => o.value);
      const dupLabels = labels.filter((l, i) => labels.indexOf(l) !== i);
      const dupValues = values.filter((v, i) => values.indexOf(v) !== i);
      return { totalOptions: labels.length, dupLabels, dupValues };
    });
    if (result.error) throw new Error(result.error);
    if (result.dupLabels.length > 0) {
      throw new Error(`Duplicate language labels: ${result.dupLabels.join(', ')}`);
    }
    if (result.dupValues.length > 0) {
      throw new Error(`Duplicate language values: ${result.dupValues.join(', ')}`);
    }
  });

  // --- Bug 6: data-testid and notranslate across all mystery pages ---
  // Test a sample from each set (first and last) plus the standalone template
  const sampled = ['joyful-1', 'joyful-5', 'luminous-1', 'sorrowful-3', 'glorious-5'];

  for (const mystery of sampled) {
    await expect(`All interactive buttons have data-testid on ${mystery}`, async () => {
      await page.goto(`${baseUrl}/mysteries/${mystery}.html`, { waitUntil: 'domcontentloaded' });
      const missing = await page.evaluate((required) => {
        const found = [];
        for (const tid of required) {
          const el = document.querySelector(`[data-testid="${tid}"]`);
          if (!el) found.push(tid);
        }
        return found;
      }, requiredTestIds);
      if (missing.length > 0) {
        throw new Error(`Missing data-testid: ${missing.join(', ')}`);
      }
    });

    await expect(`Action containers have notranslate on ${mystery}`, async () => {
      const result = await page.evaluate(() => {
        const containers = [
          document.querySelector('.meditation-top-controls'),
          document.querySelector('.meditation-actions')
        ];
        const missing = [];
        containers.forEach((el, i) => {
          if (!el) { missing.push(`container[${i}] not found`); return; }
          if (!el.classList.contains('notranslate')) {
            missing.push(el.className);
          }
        });
        return missing;
      });
      if (result.length > 0) {
        throw new Error(`Containers missing notranslate: ${result.join(', ')}`);
      }
    });
  }

  // Also test the standalone mystery-meditation.html template
  await expect('Standalone mystery-meditation.html has notranslate on containers', async () => {
    await page.goto(`${baseUrl}/mystery-meditation.html`, { waitUntil: 'domcontentloaded' });
    const result = await page.evaluate(() => {
      const containers = [
        document.querySelector('.meditation-top-controls'),
        document.querySelector('.meditation-actions')
      ];
      return containers
        .filter(el => el && !el.classList.contains('notranslate'))
        .map(el => el.className);
    });
    if (result.length > 0) {
      throw new Error(`Containers missing notranslate: ${result.join(', ')}`);
    }
  });

  // --- Bug 7: Auto Prayer toggle must not hide floating player ---
  await page.goto(`${baseUrl}/mysteries/joyful-1.html`, { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(500);

  await expect('Auto Prayer toggle from floating player does not hide player', async () => {
    await page.evaluate(() => document.getElementById('start-guided-audio').click());
    await page.waitForTimeout(1500);

    const playerBefore = await page.evaluate(() =>
      document.querySelector('.floating-audio')?.classList.contains('on') || false
    );
    if (!playerBefore) throw new Error('Floating player should be visible after starting guided audio');

    const ctxBefore = await page.evaluate(() => JSON.parse(localStorage.getItem('rosary_audio_context') || '{}'));
    if (!ctxBefore.playing && !ctxBefore.paused) throw new Error('Audio should be active before toggle test');

    await page.evaluate(() => document.getElementById('floating-audio-auto-prayer').click());
    await page.waitForTimeout(500);

    const playerAfter = await page.evaluate(() =>
      document.querySelector('.floating-audio')?.classList.contains('on') || false
    );
    if (!playerAfter) throw new Error('Floating player disappeared after toggling Auto Prayer');

    const ctxAfter = await page.evaluate(() => JSON.parse(localStorage.getItem('rosary_audio_context') || '{}'));
    if (!ctxAfter.playing && !ctxAfter.paused) {
      throw new Error(`Audio state lost after Auto Prayer toggle: playing=${ctxAfter.playing}, paused=${ctxAfter.paused}`);
    }
  });

  await expect('Auto Prayer toggle from floating player updates button label', async () => {
    const label = await page.evaluate(() =>
      document.getElementById('floating-audio-auto-prayer')?.textContent || ''
    );
    if (!/Auto Prayer: (Enabled|Disabled)/i.test(label)) {
      throw new Error(`Expected "Auto Prayer: Enabled" or "Auto Prayer: Disabled", got: "${label}"`);
    }
  });

  await expect('Auto Prayer toggle from floating player syncs with page checkbox', async () => {
    const floatingEnabled = await page.evaluate(() =>
      document.getElementById('floating-audio-auto-prayer')?.classList.contains('is-enabled') || false
    );
    const pageChecked = await page.evaluate(() =>
      document.getElementById('auto-prayer-toggle')?.checked || false
    );
    if (floatingEnabled !== pageChecked) {
      throw new Error(`Floating button enabled=${floatingEnabled} but page checkbox checked=${pageChecked}`);
    }
  });

  await expect('Toggling Auto Prayer twice keeps floating player visible', async () => {
    // Toggle on
    await page.evaluate(() => document.getElementById('floating-audio-auto-prayer').click());
    await page.waitForTimeout(300);
    // Toggle off
    await page.evaluate(() => document.getElementById('floating-audio-auto-prayer').click());
    await page.waitForTimeout(300);

    const visible = await page.evaluate(() =>
      document.querySelector('.floating-audio')?.classList.contains('on') || false
    );
    if (!visible) throw new Error('Floating player disappeared after double-toggling Auto Prayer');

    const ctx = await page.evaluate(() => JSON.parse(localStorage.getItem('rosary_audio_context') || '{}'));
    if (!ctx.playing && !ctx.paused) {
      throw new Error(`Audio state lost after double toggle: playing=${ctx.playing}, paused=${ctx.paused}`);
    }
  });

} finally {
  await context.close();
  await browser.close();
}

if (failures.length) {
  console.error('\nUI regression test failures:');
  failures.forEach(f => console.error(`- ${f}`));
  process.exit(1);
}

console.log('\nUI regression tests passed.');
