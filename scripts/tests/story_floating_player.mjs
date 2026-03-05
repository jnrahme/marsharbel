#!/usr/bin/env node

/**
 * Comprehensive tests for the Story page floating audio player.
 *
 * Covers:
 * - Floating player appears with correct UI profile on Story page
 * - Story-specific buttons hidden (Auto Prayer, Open Mystery, Next, Voice select)
 * - Storybook controls (Read Aloud, Previous/Next Page, Auto Continue, speed)
 * - Floating player shows correct mode/title/subtitle for storybook audio
 * - Floating player Close/Pause/Back/Skip work
 * - Navigation between story pages updates floating player context
 * - Rosary auto-prayer state is NOT affected by story page audio
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
  // STORY PAGE: Storybook controls
  // ============================================================

  await page.goto(`${baseUrl}/story.html`, { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(500);

  await expect('Story page loads with correct page indicator', async () => {
    const step = await page.locator('#story-step').textContent();
    if (!/Page\s+1\s+of\s+\d+/i.test(step)) {
      throw new Error(`Expected "Page 1 of N", got: ${step}`);
    }
  });

  await expect('Story page has Read Aloud button', async () => {
    const readBtn = page.locator('#story-read');
    const visible = await readBtn.isVisible();
    if (!visible) throw new Error('Read Aloud button not visible');
    const text = await readBtn.textContent();
    if (!/Read Aloud/i.test(text)) {
      throw new Error(`Expected "Read Aloud", got: ${text}`);
    }
  });

  await expect('Story page has Previous/Next Page buttons', async () => {
    const prev = page.locator('#story-prev');
    const next = page.locator('#story-next');
    if (!await prev.isVisible()) throw new Error('Previous Page not visible');
    if (!await next.isVisible()) throw new Error('Next Page not visible');
    if (!await prev.isDisabled()) throw new Error('Previous Page should be disabled on first page');
  });

  await expect('Auto Continue checkbox exists and is toggleable', async () => {
    const checkbox = page.locator('#story-auto-continue');
    if (!await checkbox.isVisible()) throw new Error('Auto Continue checkbox not visible');
    const before = await checkbox.isChecked();
    await checkbox.click();
    const after = await checkbox.isChecked();
    if (before === after) throw new Error('Auto Continue did not toggle');
    await checkbox.click(); // restore
  });

  await expect('Speed buttons exist (Slow, Normal, Fast)', async () => {
    const btns = page.locator('.story-rate-btn');
    const count = await btns.count();
    if (count !== 3) throw new Error(`Expected 3 rate buttons, got: ${count}`);
    const labels = [];
    for (let i = 0; i < count; i++) {
      labels.push(await btns.nth(i).textContent());
    }
    if (!labels.includes('Slow') || !labels.includes('Normal') || !labels.includes('Fast')) {
      throw new Error(`Expected Slow/Normal/Fast, got: ${labels.join(', ')}`);
    }
  });

  await expect('Normal speed is active by default', async () => {
    const active = page.locator('.story-rate-btn.is-active');
    const text = await active.textContent();
    if (text !== 'Normal') throw new Error(`Expected "Normal" active, got: ${text}`);
  });

  // ============================================================
  // STORY PAGE: Floating player UI profile
  // ============================================================

  await expect('Floating player is hidden before reading starts', async () => {
    const hasOnClass = await page.evaluate(() => {
      return document.querySelector('.floating-audio')?.classList.contains('on') || false;
    });
    if (hasOnClass) throw new Error('Floating player should be hidden initially');
  });

  // Trigger reading to activate the floating player
  await page.click('#story-read');
  await page.waitForTimeout(800);

  await expect('Floating player appears after Read Aloud is clicked', async () => {
    const visible = await page.evaluate(() => {
      return document.querySelector('.floating-audio')?.classList.contains('on') || false;
    });
    if (!visible) throw new Error('Floating player should be visible after reading starts');
  });

  await expect('Floating player shows storybook mode label', async () => {
    const mode = await page.locator('#floating-audio-mode').textContent();
    if (!/Story Audio|Guided Audio/i.test(mode)) {
      throw new Error(`Expected storybook mode, got: ${mode}`);
    }
  });

  await expect('Floating player shows story page title', async () => {
    const title = await page.locator('#floating-audio-title').textContent();
    if (!title || title === 'Rosary narration') {
      throw new Error(`Expected story page title, got: ${title}`);
    }
  });

  await expect('Floating player shows Storybook subtitle', async () => {
    const subtitle = await page.locator('#floating-audio-subtitle').textContent();
    if (!subtitle || /Active step/i.test(subtitle)) {
      throw new Error(`Expected storybook subtitle (page indicator), got: ${subtitle}`);
    }
  });

  // Story-specific: certain rosary buttons should be hidden
  await expect('Auto Prayer button is hidden on Story page', async () => {
    const hidden = await page.evaluate(() => {
      const el = document.getElementById('floating-audio-auto-prayer');
      return !el || el.hidden || el.style.display === 'none';
    });
    if (!hidden) throw new Error('Auto Prayer button should be hidden on Story page');
  });

  await expect('Open Mystery link is hidden on Story page', async () => {
    const hidden = await page.evaluate(() => {
      const el = document.getElementById('floating-audio-open');
      return !el || el.hidden || el.style.display === 'none';
    });
    if (!hidden) throw new Error('Open Mystery link should be hidden on Story page');
  });

  await expect('Next (rosary) button is hidden on Story page', async () => {
    const hidden = await page.evaluate(() => {
      const el = document.getElementById('floating-audio-next');
      return !el || el.hidden || el.style.display === 'none';
    });
    if (!hidden) throw new Error('Next button should be hidden on Story page');
  });

  await expect('Voice selector row is hidden on Story page', async () => {
    const hidden = await page.evaluate(() => {
      const el = document.querySelector('.floating-audio-voice-row');
      return !el || el.hidden || el.style.display === 'none';
    });
    if (!hidden) throw new Error('Voice selector row should be hidden on Story page');
  });

  // Floating player action buttons that SHOULD be visible
  await expect('Floating player Pause button is visible', async () => {
    const toggle = page.locator('#floating-audio-toggle');
    const hidden = await toggle.isHidden();
    if (hidden) throw new Error('Pause/Play toggle should be visible');
  });

  await expect('Floating player back/skip buttons are visible', async () => {
    const back = page.locator('#floating-audio-back');
    const skip = page.locator('#floating-audio-skip');
    if (await back.isHidden()) throw new Error('Back button should be visible');
    if (await skip.isHidden()) throw new Error('Skip button should be visible');
  });

  await expect('Floating player Close and Minimize buttons are visible', async () => {
    const close = page.locator('#floating-audio-close');
    const minimize = page.locator('#floating-audio-minimize');
    if (await close.isHidden()) throw new Error('Close button should be visible');
    if (await minimize.isHidden()) throw new Error('Minimize button should be visible');
  });

  await expect('Floating player progress bar is visible', async () => {
    const hidden = await page.evaluate(() => {
      const el = document.querySelector('.floating-audio-progress');
      return el?.hidden || false;
    });
    if (hidden) throw new Error('Progress bar should be visible on Story page');
  });

  // ============================================================
  // FLOATING PLAYER: Close stops reading
  // ============================================================

  await expect('Close button hides floating player and stops reading', async () => {
    await page.click('#floating-audio-close');
    await page.waitForTimeout(300);
    const playerVisible = await page.evaluate(() => {
      return document.querySelector('.floating-audio')?.classList.contains('on') || false;
    });
    if (playerVisible) throw new Error('Floating player should be hidden after close');
    const readLabel = await page.locator('#story-read').textContent();
    if (!/Read Aloud/i.test(readLabel)) {
      throw new Error(`Expected "Read Aloud" after close, got: ${readLabel}`);
    }
  });

  // ============================================================
  // NAVIGATION: Next Page updates floating player context
  // ============================================================

  await page.click('#story-next');
  await page.waitForTimeout(300);

  await expect('Next Page advances to page 2', async () => {
    const step = await page.locator('#story-step').textContent();
    if (!/Page\s+2\s+of/i.test(step)) {
      throw new Error(`Expected "Page 2 of N", got: ${step}`);
    }
  });

  await expect('Previous Page is enabled on page 2', async () => {
    if (await page.locator('#story-prev').isDisabled()) {
      throw new Error('Previous Page should be enabled on page 2');
    }
  });

  // Read page 2 and verify floating player updates
  await page.click('#story-read');
  await page.waitForTimeout(800);

  await expect('Floating player title updates for page 2', async () => {
    const title = await page.locator('#floating-audio-title').textContent();
    const pageTitle = await page.locator('#story-title').textContent();
    if (title !== pageTitle) {
      throw new Error(`Floating title "${title}" doesn't match page title "${pageTitle}"`);
    }
  });

  // Stop reading for next tests
  await page.click('#floating-audio-close');
  await page.waitForTimeout(300);

  // ============================================================
  // ISOLATION: Story audio does NOT set rosary auto-prayer state
  // ============================================================

  await expect('Story audio context uses storybook source', async () => {
    // Read aloud to populate context
    await page.click('#story-read');
    await page.waitForTimeout(500);
    const ctx = await page.evaluate(() => {
      try {
        return JSON.parse(localStorage.getItem('rosary_audio_context') || '{}');
      } catch (_) {
        return {};
      }
    });
    if (ctx.source !== 'storybook') {
      throw new Error(`Expected source "storybook", got: ${ctx.source}`);
    }
    if (ctx.mode !== 'prerendered' && ctx.mode !== 'speech' && ctx.mode !== 'storybook') {
      throw new Error(`Unexpected mode: ${ctx.mode}`);
    }
    await page.click('#floating-audio-close');
    await page.waitForTimeout(200);
  });

  await expect('Story audio does not enable rosary auto-prayer', async () => {
    const ctx = await page.evaluate(() => {
      try {
        return JSON.parse(localStorage.getItem('rosary_audio_context') || '{}');
      } catch (_) {
        return {};
      }
    });
    if (ctx.autoPrayerVoiceEnabled === true) {
      throw new Error('Story should never enable autoPrayerVoiceEnabled');
    }
  });

  await expect('Story audio does not set rosary step/mystery metadata', async () => {
    // Start reading on story page
    await page.click('#story-read');
    await page.waitForTimeout(500);
    const ctx = await page.evaluate(() => {
      try {
        return JSON.parse(localStorage.getItem('rosary_audio_context') || '{}');
      } catch (_) {
        return {};
      }
    });
    // Should not have rosary-specific keys
    if (ctx.mysteryKey || ctx.mysteryIndex || ctx.stageIndex !== undefined) {
      throw new Error(`Story context should not have rosary keys: ${JSON.stringify({ mysteryKey: ctx.mysteryKey, mysteryIndex: ctx.mysteryIndex, stageIndex: ctx.stageIndex })}`);
    }
    if (ctx.stage !== 'Storybook') {
      throw new Error(`Expected stage "Storybook", got: ${ctx.stage}`);
    }
    await page.click('#floating-audio-close');
    await page.waitForTimeout(200);
  });

  // ============================================================
  // CROSS-PAGE: Rosary page auto-player unaffected by story state
  // ============================================================

  // Set up a fake rosary session state, then navigate to story and back
  await expect('Rosary auto-prayer state survives story page visit', async () => {
    // Navigate to rosary page
    await page.goto(`${baseUrl}/mysteries/joyful-1.html`, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(300);

    // Enable auto-prayer toggle if it exists
    const hasToggle = await page.evaluate(() => !!document.getElementById('auto-prayer-toggle'));
    if (hasToggle) {
      const wasBefore = await page.locator('#auto-prayer-toggle').isChecked();
      if (!wasBefore) {
        await page.locator('#auto-prayer-toggle').click();
      }
    }

    // Read the auto-prayer state
    const rosaryStateBefore = await page.evaluate(() => {
      const el = document.getElementById('auto-prayer-toggle');
      return el ? el.checked : null;
    });

    // Navigate to story
    await page.goto(`${baseUrl}/story.html`, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(300);

    // Read aloud on story page
    await page.click('#story-read');
    await page.waitForTimeout(500);
    await page.click('#floating-audio-close');
    await page.waitForTimeout(200);

    // Navigate back to rosary
    await page.goto(`${baseUrl}/mysteries/joyful-1.html`, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(300);

    const rosaryStateAfter = await page.evaluate(() => {
      const el = document.getElementById('auto-prayer-toggle');
      return el ? el.checked : null;
    });

    if (rosaryStateBefore !== null && rosaryStateAfter !== rosaryStateBefore) {
      throw new Error(`Auto-prayer toggle changed from ${rosaryStateBefore} to ${rosaryStateAfter} after story visit`);
    }
  });

  await expect('Rosary floating player still shows rosary UI after story visit', async () => {
    // Start guided audio on rosary page
    await page.click('#start-guided-audio');
    await page.waitForTimeout(1000);

    // Verify floating player shows rosary mode (not storybook)
    const ctx = await page.evaluate(() => {
      try {
        return JSON.parse(localStorage.getItem('rosary_audio_context') || '{}');
      } catch (_) {
        return {};
      }
    });

    if (ctx.source === 'storybook') {
      throw new Error('Rosary audio context should not have storybook source');
    }

    // Auto Prayer button should be visible on rosary page
    const autoPrayerVisible = await page.evaluate(() => {
      const el = document.getElementById('floating-audio-auto-prayer');
      return el && !el.hidden && el.style.display !== 'none';
    });
    if (!autoPrayerVisible) {
      throw new Error('Auto Prayer button should be visible on rosary page');
    }

    // Open Mystery link should be visible on rosary page
    const openVisible = await page.evaluate(() => {
      const el = document.getElementById('floating-audio-open');
      return el && !el.hidden && el.style.display !== 'none';
    });
    if (!openVisible) {
      throw new Error('Open Mystery link should be visible on rosary page');
    }
  });

  // ============================================================
  // STORY PAGE: Minimize and reading indicator
  // ============================================================

  await page.goto(`${baseUrl}/story.html`, { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(300);

  await expect('Reading indicator shows Reading state when audio starts', async () => {
    await page.click('#story-read');
    await page.waitForTimeout(500);
    const label = await page.locator('#story-reading-label').textContent();
    if (!/Reading/i.test(label)) {
      throw new Error(`Expected reading indicator, got: ${label}`);
    }
    await page.click('#floating-audio-close');
    await page.waitForTimeout(200);
  });

  await expect('Minimize button toggles floating player minimized state', async () => {
    await page.click('#story-read');
    await page.waitForTimeout(500);
    const beforeMinimized = await page.evaluate(() => {
      return document.querySelector('.floating-audio')?.classList.contains('is-minimized') || false;
    });
    await page.click('#floating-audio-minimize');
    await page.waitForTimeout(200);
    const afterMinimized = await page.evaluate(() => {
      return document.querySelector('.floating-audio')?.classList.contains('is-minimized') || false;
    });
    if (beforeMinimized === afterMinimized) {
      throw new Error('Minimize did not toggle is-minimized class');
    }
    // Restore
    await page.click('#floating-audio-minimize');
    await page.click('#floating-audio-close');
    await page.waitForTimeout(200);
  });

  // ============================================================
  // STORY PAGE: Evidence section
  // ============================================================

  await expect('Evidence section is present with content', async () => {
    const title = await page.locator('#story-evidence-title').textContent();
    if (!/Evidence/i.test(title)) {
      throw new Error(`Expected evidence title, got: ${title}`);
    }
    const items = await page.locator('#story-evidence-list li').count();
    if (items === 0) {
      throw new Error('Evidence list should have at least one item');
    }
  });

} finally {
  await context.close();
  await browser.close();
}

if (failures.length) {
  console.error('\nStory floating player test failures:');
  failures.forEach(f => console.error(`- ${f}`));
  process.exit(1);
}

console.log('\nStory floating player tests passed.');
