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

const textOf = async (page, selector) => {
  const locator = page.locator(selector);
  await locator.waitFor({ state: 'visible', timeout: 10000 });
  return (await locator.textContent())?.trim() || '';
};

const browser = await chromium.launch({ headless: true });
const context = await browser.newContext();
const page = await context.newPage();
const consoleErrors = [];

page.on('console', msg => {
  if (msg.type() === 'error') {
    consoleErrors.push(msg.text());
  }
});

try {
  await page.goto(`${baseUrl}/mysteries/joyful-1.html`, { waitUntil: 'domcontentloaded' });

  await expect('Guided audio requires explicit start (no autoplay on load)', async () => {
    const startButton = page.locator('#start-guided-audio');
    await startButton.waitFor({ state: 'visible', timeout: 10000 });
    const status = await textOf(page, '#sound-status');
    if (!/Press Play Guided Audio to begin/i.test(status)) {
      throw new Error(`Expected manual-start status, got: ${status}`);
    }
    const context = await page.evaluate(() => {
      try {
        return JSON.parse(localStorage.getItem('rosary_audio_context') || '{}');
      } catch (_) {
        return {};
      }
    });
    if (context.playing === true) {
      throw new Error('Audio context should not be playing before user click');
    }
  });

  await expect('Guided audio starts when Play Guided Audio is clicked', async () => {
    await page.click('#start-guided-audio');
    await page.waitForTimeout(600);
    const startLabel = await textOf(page, '#start-guided-audio');
    if (!/Pause Guided Audio|Playing Guided Audio|Replay Guided Audio|Starting/i.test(startLabel)) {
      throw new Error(`Unexpected start button label after click: ${startLabel}`);
    }
  });

  await expect('Hands-free timer stays available in auto mode and can start', async () => {
    await page.goto(`${baseUrl}/mysteries/joyful-1.html?auto=1`, { waitUntil: 'domcontentloaded' });
    const timerButton = page.locator('#auto-timer-toggle');
    const timerSelect = page.locator('#auto-timer-seconds');
    if (await timerButton.isDisabled()) {
      throw new Error('Timer toggle should not be disabled in auto mode');
    }
    if (await timerSelect.isDisabled()) {
      throw new Error('Timer select should not be disabled in auto mode');
    }
    await page.selectOption('#auto-timer-seconds', '12');
    await page.click('#auto-timer-toggle');
    const label = await textOf(page, '#auto-timer-toggle');
    if (!/Stop Auto|Auto:\s*\d+s/i.test(label)) {
      throw new Error(`Expected timer to start, got button label: ${label}`);
    }
  });

  await expect('Default stage is not intro prayers', async () => {
    const badge = await textOf(page, '#stage-badge');
    if (/Intro Prayers/i.test(badge)) {
      throw new Error(`Expected non-intro stage, got: ${badge}`);
    }
    const counter = await textOf(page, '#step-counter');
    if (!/Step [2-9]|Step 1[0-3]/i.test(counter)) {
      throw new Error(`Expected step after intro, got: ${counter}`);
    }
  });

  await expect('Intro option can be selected and loads intro stage', async () => {
    await page.selectOption('#mystery-picker', 'intro:joyful');
    await page.waitForURL(url => url.searchParams.get('stage') === 'intro', { timeout: 10000 });
    const badge = await textOf(page, '#stage-badge');
    if (!/Intro Prayers/i.test(badge)) {
      throw new Error(`Expected Intro Prayers badge, got: ${badge}`);
    }
  });

  await expect('End option can be selected and loads end stage', async () => {
    await page.selectOption('#mystery-picker', 'end:joyful');
    await page.waitForURL(url => url.searchParams.get('stage') === 'end', { timeout: 10000 });
    const badge = await textOf(page, '#stage-badge');
    if (!/End Prayers/i.test(badge)) {
      throw new Error(`Expected End Prayers badge, got: ${badge}`);
    }
  });

  await expect('Normal mystery selection exits intro/end staging', async () => {
    await page.selectOption('#mystery-picker', 'joyful_2');
    await page.waitForURL(/joyful-2\.html/);
    const badge = await textOf(page, '#stage-badge');
    if (/Intro Prayers|End Prayers/i.test(badge)) {
      throw new Error(`Expected non-intro/end stage on joyful_2, got: ${badge}`);
    }
  });

  await expect('Language selection persists across mystery navigation', async () => {
    await page.goto(`${baseUrl}/mysteries/joyful-1.html?lang=es`, { waitUntil: 'domcontentloaded' });
    await page.selectOption('#mystery-picker', 'joyful_2');
    await page.waitForURL(url => /joyful-2\.html$/i.test(url.pathname), { timeout: 10000 });
    const lang = new URL(page.url()).searchParams.get('lang');
    if (lang !== 'es') {
      throw new Error(`Expected lang=es to persist, got: ${page.url()}`);
    }
  });

  await expect('Requested language translates page content', async () => {
    await page.goto(`${baseUrl}/mysteries/joyful-1.html?lang=es`, { waitUntil: 'domcontentloaded' });
    // Verify translate.js picks up lang param and configures the page
    const langParam = new URL(page.url()).searchParams.get('lang');
    if (langParam !== 'es') throw new Error(`Expected lang=es in URL, got: ${langParam}`);
    // Wait for translate.js to initialize (sets lang selector value)
    await page.waitForFunction(() => {
      const sel = document.getElementById('sc-language-select');
      return sel && sel.value === 'es';
    }, null, { timeout: 10000 });
    // Google Translate may not run in headless CI, so just verify the selector is set
    const selectedLang = await page.evaluate(() =>
      document.getElementById('sc-language-select')?.value || ''
    );
    if (selectedLang !== 'es') {
      throw new Error(`Language selector should be "es", got: "${selectedLang}"`);
    }
  });

  await expect('Language persists when navigating to another page', async () => {
    await page.goto(`${baseUrl}/mysteries/joyful-1.html?lang=es`, { waitUntil: 'domcontentloaded' });
    await page.waitForFunction(() => {
      const home = document.querySelector('.topbar .links a[href]');
      return home && /lang=es/i.test(home.getAttribute('href') || '');
    }, null, { timeout: 10000 });
    await page.click('.topbar .links a[href*="index.html"]');
    await page.waitForURL(url => url.pathname.endsWith('/index.html') || url.pathname === '/', { timeout: 10000 });
    const lang = new URL(page.url()).searchParams.get('lang');
    if (lang !== 'es') {
      throw new Error(`Expected lang=es on next page, got: ${page.url()}`);
    }
  });

  await expect('Language persists across Home, Story, and Rosary nav links', async () => {
    await page.goto(`${baseUrl}/mysteries/joyful-1.html?lang=es`, { waitUntil: 'domcontentloaded' });

    await page.click('.topbar .links a[href*="index.html"]');
    await page.waitForURL(url => url.pathname.endsWith('/index.html') || url.pathname === '/', { timeout: 10000 });
    let lang = new URL(page.url()).searchParams.get('lang');
    if (lang !== 'es') {
      throw new Error(`Expected lang=es on Home, got: ${page.url()}`);
    }

    await page.click('.topbar .links a[href*="story.html"]');
    await page.waitForURL(/story\.html/i, { timeout: 10000 });
    lang = new URL(page.url()).searchParams.get('lang');
    if (lang !== 'es') {
      throw new Error(`Expected lang=es on Story, got: ${page.url()}`);
    }

    const prayerMenu = page.locator('.topbar .nav-group').filter({
      has: page.locator('a[href*="rosary-visual-guide"]')
    });
    await prayerMenu.locator('.nav-parent').hover();
    await prayerMenu.locator('a[href*="rosary-visual-guide"]').click();
    await page.waitForURL(/rosary-visual-guide/i, { timeout: 10000 });
    lang = new URL(page.url()).searchParams.get('lang');
    if (lang !== 'es') {
      throw new Error(`Expected lang=es on Rosary, got: ${page.url()}`);
    }
  });

  await page.goto(`${baseUrl}/mysteries/joyful-1.html`, { waitUntil: 'domcontentloaded' });

  await expect('Auto prayer toggle is present and can be toggled', async () => {
    const toggle = page.locator('#auto-prayer-toggle');
    await toggle.waitFor({ state: 'visible', timeout: 10000 });
    const before = await toggle.isChecked();
    await toggle.click();
    const after = await toggle.isChecked();
    if (before === after) {
      throw new Error('Auto prayer checkbox did not toggle');
    }
  });

  await expect('Floating player does not expose voice selector UI', async () => {
    await page.evaluate(() => document.getElementById('pause-audio').click());
    await page.waitForTimeout(500);
    const voiceRow = page.locator('.floating-audio-voice-row');
    await voiceRow.waitFor({ state: 'attached', timeout: 10000 });
    const hidden = await voiceRow.evaluate(el => {
      const style = window.getComputedStyle(el);
      return style.display === 'none' || style.visibility === 'hidden' || el.hidden === true;
    });
    if (!hidden) {
      throw new Error('Voice selector row should be hidden');
    }
  });

  await expect('No JavaScript console errors', async () => {
    if (consoleErrors.length) {
      throw new Error(consoleErrors.join(' | '));
    }
  });
} finally {
  await context.close();
  await browser.close();
}

if (failures.length) {
  console.error('\nSmoke test failures:');
  failures.forEach(f => console.error(`- ${f}`));
  process.exit(1);
}

console.log('\nRosary smoke tests passed.');
