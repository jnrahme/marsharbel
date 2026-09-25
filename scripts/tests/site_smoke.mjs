#!/usr/bin/env node
import { chromium } from 'playwright';

function parseBaseUrl(argv) {
  const baseArg = argv.find(arg => arg.startsWith('--base-url='));
  return baseArg ? baseArg.slice('--base-url='.length) : 'http://127.0.0.1:4173';
}

const baseUrl = parseBaseUrl(process.argv.slice(2));

const paths = [
  '/',
  '/history.html',
  '/miracles/',
  '/testimonies.html',
  '/rosary-intro.html',
  '/rosary-prayer-coach.html',
  '/gallery.html',
  '/story.html',
  '/submit-testimony.html',
  '/saint-charbel-prayers.html'
];

const failures = [];
const browser = await chromium.launch({ headless: true });

try {
  for (const path of paths) {
    const page = await browser.newPage();
    const pageErrors = [];

    page.on('pageerror', err => {
      pageErrors.push(err?.message || String(err));
    });

    const url = new URL(path, baseUrl).toString();

    try {
      const response = await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
      const status = response?.status() ?? 0;
      if (status < 200 || status >= 400) {
        failures.push(`${path}: unexpected HTTP status ${status}`);
      }

      const title = (await page.title()).trim();
      if (!title) {
        failures.push(`${path}: empty document title`);
      }

      await page.waitForTimeout(400);

      if (pageErrors.length > 0) {
        failures.push(`${path}: runtime errors -> ${pageErrors.join(' | ')}`);
      }
    } catch (err) {
      failures.push(`${path}: navigation failure -> ${err?.message || String(err)}`);
    } finally {
      await page.close();
    }
  }
} finally {
  await browser.close();
}

if (failures.length > 0) {
  console.error('\nSite smoke test failures:');
  failures.forEach(f => console.error(`- ${f}`));
  process.exit(1);
}

console.log('\nSite smoke tests passed.');
