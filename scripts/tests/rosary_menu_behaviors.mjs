#!/usr/bin/env node

import { chromium } from 'playwright';

const baseUrlArg = process.argv.find(arg => arg.startsWith('--base-url='));
const baseUrl = (baseUrlArg ? baseUrlArg.split('=')[1] : 'http://127.0.0.1:4173').replace(/\/$/, '');

const failures = [];
const pass = name => console.log(`PASS: ${name}`);
const fail = (name, err) => {
  failures.push(`${name}: ${err instanceof Error ? err.message : String(err)}`);
  console.log(`FAIL: ${name}`);
};

const expect = async (name, fn) => {
  try {
    await fn();
    pass(name);
  } catch (err) {
    fail(name, err);
  }
};

const browser = await chromium.launch({ headless: true });
const context = await browser.newContext();
const page = await context.newPage();

const optionValue = async () => page.$eval('#mystery-picker', el => el.value);
const optionCount = async () => page.$$eval('#mystery-picker option', opts => opts.length);
const optGroupLabels = async () => page.$$eval('#mystery-picker optgroup', groups => groups.map(g => g.label.trim()));
const optionsInGroup = async groupLabel =>
  page.$$eval('#mystery-picker optgroup', (groups, label) => {
    const group = groups.find(g => g.label.trim() === label);
    if (!group) return [];
    return Array.from(group.querySelectorAll('option')).map(o => ({ value: o.value, text: o.textContent?.trim() || '' }));
  }, groupLabel);

try {
  await page.goto(`${baseUrl}/mysteries/joyful-1.html`, { waitUntil: 'domcontentloaded' });

  await expect('Menu has four mystery groups', async () => {
    const labels = await optGroupLabels();
    const expected = ['Joyful Mysteries', 'Luminous Mysteries', 'Sorrowful Mysteries', 'Glorious Mysteries'];
    if (JSON.stringify(labels) !== JSON.stringify(expected)) {
      throw new Error(`Unexpected group labels: ${labels.join(', ')}`);
    }
  });

  await expect('Menu has 28 options total (intro + 5 mysteries + end per set)', async () => {
    const count = await optionCount();
    if (count !== 28) {
      throw new Error(`Expected 28 options, got ${count}`);
    }
  });

  await expect('Each group has intro first and end last', async () => {
    const groups = ['Joyful Mysteries', 'Luminous Mysteries', 'Sorrowful Mysteries', 'Glorious Mysteries'];
    for (const label of groups) {
      const opts = await optionsInGroup(label);
      if (opts.length !== 7) {
        throw new Error(`${label} expected 7 options, got ${opts.length}`);
      }
      if (!opts[0].value.startsWith('intro:')) {
        throw new Error(`${label} first option should be intro`);
      }
      if (!opts[6].value.startsWith('end:')) {
        throw new Error(`${label} last option should be end`);
      }
    }
  });

  await expect('Default page selection is the current mystery key', async () => {
    const value = await optionValue();
    if (value !== 'joyful_1') {
      throw new Error(`Expected selected value joyful_1, got ${value}`);
    }
  });

  await expect('Selecting a mystery navigates to that mystery page', async () => {
    await page.selectOption('#mystery-picker', 'joyful_4');
    await page.waitForURL(/\/mysteries\/joyful-4\.html(?:\?.*)?$/);
    const url = new URL(page.url());
    if (url.searchParams.get('stage')) {
      throw new Error(`Expected no stage param on normal mystery select, got ${url.search}`);
    }
    const value = await optionValue();
    if (value !== 'joyful_4') {
      throw new Error(`Expected selected joyful_4, got ${value}`);
    }
  });

  await expect('Selecting Intro (Joyful) opens first Joyful with stage=intro', async () => {
    await page.selectOption('#mystery-picker', 'intro:joyful');
    await page.waitForURL(url =>
      /\/mysteries\/joyful-1\.html$/.test(url.pathname) && url.searchParams.get('stage') === 'intro'
    );
    const value = await optionValue();
    if (value !== 'intro:joyful') {
      throw new Error(`Expected selected intro:joyful, got ${value}`);
    }
  });

  await expect('Selecting End (Joyful) opens fifth Joyful with stage=end', async () => {
    await page.selectOption('#mystery-picker', 'end:joyful');
    await page.waitForURL(url =>
      /\/mysteries\/joyful-5\.html$/.test(url.pathname) && url.searchParams.get('stage') === 'end'
    );
    const value = await optionValue();
    if (value !== 'end:joyful') {
      throw new Error(`Expected selected end:joyful, got ${value}`);
    }
  });

  await expect('Cross-set mystery selection works from end-stage page', async () => {
    await page.selectOption('#mystery-picker', 'sorrowful_3');
    await page.waitForURL(/\/mysteries\/sorrowful-3\.html(?:\?.*)?$/);
    const url = new URL(page.url());
    if (url.searchParams.get('stage')) {
      throw new Error(`Expected stage param cleared on normal mystery select, got ${url.search}`);
    }
    const value = await optionValue();
    if (value !== 'sorrowful_3') {
      throw new Error(`Expected selected sorrowful_3, got ${value}`);
    }
  });

  await expect('Selecting Intro (Luminous) opens first Luminous with stage=intro', async () => {
    await page.selectOption('#mystery-picker', 'intro:luminous');
    await page.waitForURL(url =>
      /\/mysteries\/luminous-1\.html$/.test(url.pathname) && url.searchParams.get('stage') === 'intro'
    );
    const value = await optionValue();
    if (value !== 'intro:luminous') {
      throw new Error(`Expected selected intro:luminous, got ${value}`);
    }
  });

  await expect('Selecting End (Glorious) opens fifth Glorious with stage=end', async () => {
    await page.selectOption('#mystery-picker', 'end:glorious');
    await page.waitForURL(url =>
      /\/mysteries\/glorious-5\.html$/.test(url.pathname) && url.searchParams.get('stage') === 'end'
    );
    const value = await optionValue();
    if (value !== 'end:glorious') {
      throw new Error(`Expected selected end:glorious, got ${value}`);
    }
  });
} finally {
  await context.close();
  await browser.close();
}

if (failures.length) {
  console.error('\nMenu behavior test failures:');
  failures.forEach(f => console.error(`- ${f}`));
  process.exit(1);
}

console.log('\nRosary menu behavior tests passed.');
