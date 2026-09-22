#!/usr/bin/env node
// Start scripts/dev-server.mjs first, then run npm run test:layout.
import { chromium } from 'playwright';
import { readdir } from 'node:fs/promises';

const baseArg = process.argv.find(arg => arg.startsWith('--base-url='));
const baseUrl = baseArg ? baseArg.slice('--base-url='.length) : 'http://127.0.0.1:4173';
const paths = [
  ...(await readdir('.')).filter(path => path.endsWith('.html') && !path.startsWith('google')),
  ...(await readdir('mysteries')).filter(path => path.endsWith('.html')).map(path => `mysteries/${path}`)
];
const widths = [375, 768, 1024, 1366, 1920];
const failures = [];
const browser = await chromium.launch();

try {
  for (const width of widths) {
    const page = await browser.newPage({
      serviceWorkers: 'block',
      reducedMotion: 'reduce',
      viewport: { width, height: 900 }
    });
    for (const path of paths) {
      await page.goto(new URL(path, `${baseUrl}/`).href, { waitUntil: 'load' });
      // Allow legacy redirect pages to reach their destination.
      await page.waitForTimeout(250);
      await page.evaluate(async () => {
        await document.fonts.ready;
        document.querySelectorAll('.reveal').forEach(element => element.classList.add('on'));
      });
      const issues = await page.evaluate(() => {
        const issues = [];
        const viewportWidth = document.documentElement.clientWidth;
        if (document.documentElement.scrollWidth > viewportWidth + 1) {
          issues.push(`Document overflows viewport: ${document.documentElement.scrollWidth}/${viewportWidth}`);
        }
        const selector = 'main p, main h1, main h2, main h3, main a, main button, main input, main select, main article, main .grid-2';
        for (const element of document.querySelectorAll(selector)) {
          const rect = element.getBoundingClientRect();
          const style = getComputedStyle(element);
          // Honeypot fields are deliberately positioned outside the viewport.
          if (!rect.width || !rect.height || style.visibility === 'hidden' || element.closest('[hidden], .hp-field')) continue;
          const label = `${element.tagName}.${element.className}: ${element.textContent.trim().slice(0, 60)}`;
          if (rect.right > viewportWidth + 2 || rect.left < -2) issues.push(`Outside viewport: ${label}`);
          if (element.scrollWidth > element.clientWidth + 3 && style.overflowX === 'visible') {
            issues.push(`Content exceeds its container: ${label}`);
          }
          // Document overflow alone misses touching paragraphs in adjacent columns.
          if (element.matches('.grid-2') && style.gridTemplateColumns.split(' ').length > 1 && parseFloat(style.columnGap) < 16) {
            issues.push('Multi-column text grid has less than 16px of separation');
          }
        }
        return [...new Set(issues)];
      });
      if (issues.length) failures.push({ path, width, issues });
    }
    await page.close();
    console.log(`Checked ${paths.length} pages at ${width}px`);
  }
} finally {
  await browser.close();
}
for (const failure of failures) console.error(JSON.stringify(failure));
console.log(`${paths.length * widths.length} page/viewport combinations checked; ${failures.length} failures.`);
process.exitCode = failures.length ? 1 : 0;
