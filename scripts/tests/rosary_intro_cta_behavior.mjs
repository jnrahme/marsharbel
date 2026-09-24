#!/usr/bin/env node

import { chromium } from 'playwright';

const baseUrlArg = process.argv.find(arg => arg.startsWith('--base-url='));
const baseUrl = (baseUrlArg ? baseUrlArg.split('=')[1] : 'http://127.0.0.1:4173').replace(/\/$/, '');

const setForToday = () => {
  const day = new Date().getDay();
  if (day === 1 || day === 6) return 'joyful';
  if (day === 2 || day === 5) return 'sorrowful';
  if (day === 4) return 'luminous';
  return 'glorious';
};

const firstForSet = {
  joyful: 'joyful-1',
  sorrowful: 'sorrowful-1',
  luminous: 'luminous-1',
  glorious: 'glorious-1'
};

const browser = await chromium.launch({ headless: true });
const context = await browser.newContext();
const page = await context.newPage();

try {
  await page.goto(`${baseUrl}/rosary-intro.html`, { waitUntil: 'domcontentloaded' });
  await page.click('[data-action="today"]');

  const expectedSet = setForToday();
  const expectedPath = `/mysteries/${firstForSet[expectedSet]}`;

  await page.waitForURL(url =>
    url.pathname.replace(/\.html$/, "") === expectedPath
    && url.searchParams.get('auto') === '1'
    && url.searchParams.get('stage') === 'intro'
  );

  const session = await page.evaluate(() => {
    try {
      return JSON.parse(localStorage.getItem('rosary_full_session') || 'null');
    } catch (_) {
      return null;
    }
  });

  if (!session || session.set !== expectedSet || !Array.isArray(session.sequence) || session.sequence.length !== 5) {
    throw new Error(`Unexpected rosary session payload: ${JSON.stringify(session)}`);
  }

  console.log('PASS: Start Today CTA routes to today set intro and stores active 5-mystery session.');
} finally {
  await context.close();
  await browser.close();
}
