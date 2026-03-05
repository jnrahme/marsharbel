#!/usr/bin/env node

import { chromium } from 'playwright';

const baseUrlArg = process.argv.find(arg => arg.startsWith('--base-url='));
const baseUrl = (baseUrlArg ? baseUrlArg.split('=')[1] : 'http://127.0.0.1:4173').replace(/\/$/, '');

const browser = await chromium.launch({ headless: true });
const context = await browser.newContext();
const page = await context.newPage();

try {
  await page.goto(`${baseUrl}/mysteries/joyful-1.html`, { waitUntil: 'domcontentloaded' });

  const cueText = async () => ((await page.textContent('#prayer-live-text')) || '').trim();
  const badgeText = async () => ((await page.textContent('#stage-badge')) || '').trim();

  await page.click('#next-step');
  await page.click('#next-step');
  await page.waitForTimeout(200);

  const meditationBadge = await badgeText();
  if (!/Meditation 1/i.test(meditationBadge)) {
    throw new Error(`Expected Meditation 1 stage, got: ${meditationBadge}`);
  }
  const meditationCue = await cueText();
  if (!/Pray:\s*Hail Mary/i.test(meditationCue)) {
    throw new Error(`Expected Hail Mary cue on meditation stage, got: ${meditationCue}`);
  }
  if (/Fatima/i.test(meditationCue)) {
    throw new Error(`Fatima should not be in meditation cue, got: ${meditationCue}`);
  }

  for (let i = 0; i < 10; i += 1) {
    await page.click('#next-step');
  }
  await page.waitForTimeout(200);

  const closingBadge = await badgeText();
  if (!/Decade Closing/i.test(closingBadge)) {
    throw new Error(`Expected Decade Closing stage, got: ${closingBadge}`);
  }
  const closingCue = await cueText();
  if (!/Glory Be/i.test(closingCue) || !/Fatima Prayer/i.test(closingCue)) {
    throw new Error(`Expected Glory Be + Fatima cue at decade close, got: ${closingCue}`);
  }

  console.log('PASS: Rosary prayer behavior cues are correct (Meditations: Hail Mary, Decade close: Glory Be + Fatima).');
} finally {
  await context.close();
  await browser.close();
}
