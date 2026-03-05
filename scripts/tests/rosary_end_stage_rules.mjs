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

const getCounter = async () => ((await page.textContent('#step-counter')) || '').trim();
const totalStepsFromCounter = counter => {
  const match = counter.match(/of\s+(\d+)/i);
  return match ? Number(match[1]) : NaN;
};

try {
  let defaultTotal = 0;

  await expect('Normal mystery page does not include end-prayers stage by default', async () => {
    await page.goto(`${baseUrl}/mysteries/joyful-1.html`, { waitUntil: 'domcontentloaded' });
    const counter = await getCounter();
    defaultTotal = totalStepsFromCounter(counter);
    if (!Number.isFinite(defaultTotal) || defaultTotal < 2) {
      throw new Error(`Could not parse default step total from: ${counter}`);
    }
  });

  await expect('Explicit end-stage URL includes end-prayers stage', async () => {
    await page.goto(`${baseUrl}/mysteries/joyful-1.html?stage=end`, { waitUntil: 'domcontentloaded' });
    // End-stage initial render shows badge text, so read total from JS instead of counter
    const endTotal = await page.evaluate(() => {
      const dots = document.querySelectorAll('#bead-progress .bead-dot');
      return dots.length;
    });
    if (endTotal !== defaultTotal + 1) {
      throw new Error(`Expected end-stage total to be default+1 (${defaultTotal + 1}), got: ${endTotal}`);
    }
    const badge = ((await page.textContent('#stage-badge')) || '').trim();
    if (!/End Prayers/i.test(badge)) {
      throw new Error(`Expected End Prayers badge, got: ${badge}`);
    }
  });

  await expect('Active set session: non-final mystery stays 12-step', async () => {
    await page.goto(`${baseUrl}/mysteries/joyful-1.html`, { waitUntil: 'domcontentloaded' });
    await page.evaluate(() => {
      localStorage.setItem('rosary_full_session', JSON.stringify({
        active: true,
        set: 'joyful',
        sequence: ['joyful_1', 'joyful_2', 'joyful_3', 'joyful_4', 'joyful_5'],
        currentKey: 'joyful_1',
        autoPrayer: true,
        startedAt: Date.now()
      }));
    });
    await page.reload({ waitUntil: 'domcontentloaded' });
    const counter = await getCounter();
    const total = totalStepsFromCounter(counter);
    if (total !== defaultTotal) {
      throw new Error(`Expected non-final session total ${defaultTotal}, got: ${total}`);
    }
  });

  await expect('Active set session: final mystery includes end-prayers stage', async () => {
    await page.goto(`${baseUrl}/mysteries/joyful-5.html`, { waitUntil: 'domcontentloaded' });
    await page.evaluate(() => {
      localStorage.setItem('rosary_full_session', JSON.stringify({
        active: true,
        set: 'joyful',
        sequence: ['joyful_1', 'joyful_2', 'joyful_3', 'joyful_4', 'joyful_5'],
        currentKey: 'joyful_5',
        autoPrayer: true,
        startedAt: Date.now()
      }));
    });
    await page.reload({ waitUntil: 'domcontentloaded' });
    const counter = await getCounter();
    const total = totalStepsFromCounter(counter);
    if (total !== defaultTotal + 1) {
      throw new Error(`Expected final-session total ${defaultTotal + 1}, got: ${total}`);
    }
  });
} finally {
  await context.close();
  await browser.close();
}

if (failures.length) {
  console.error('\nEnd-stage rule test failures:');
  failures.forEach(f => console.error(`- ${f}`));
  process.exit(1);
}

console.log('\nRosary end-stage rule tests passed.');
