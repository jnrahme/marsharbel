const { test, expect } = require('@playwright/test');
const AxeBuilder = require('@axe-core/playwright').default;

test('/prayer-library.html loads cleanly, is responsive, and accessible', async ({ page }) => {
  const errors = [];
  page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
  const response = await page.goto('/prayer-library.html', { waitUntil: 'networkidle' });
  expect(response?.ok()).toBeTruthy();
  const layout = await page.evaluate(() => ({viewport: document.documentElement.clientWidth, width: document.documentElement.scrollWidth, broken: [...document.images].filter(i => i.complete && !i.naturalWidth).length}));
  expect(layout.width).toBeLessThanOrEqual(layout.viewport + 1);
  expect(layout.broken).toBe(0);
  const serious = (await new AxeBuilder({ page }).withTags(['wcag2a','wcag2aa','wcag21a','wcag21aa']).analyze()).violations.filter(v => ['serious','critical'].includes(v.impact));
  expect(serious).toEqual([]);
  expect(errors).toEqual([]);
});

test('every prayer card carries the five required fact fields', async ({ page }) => {
  await page.goto('/prayer-library.html');
  const cards = page.locator('.prayer-card');
  const count = await cards.count();
  expect(count).toBeGreaterThanOrEqual(25);
  const required = ['Purpose', 'How to pray', 'When & how long', 'Source & tradition', 'Spiritual fruit'];
  for (let i = 0; i < count; i++) {
    const facts = cards.nth(i).locator('.prayer-facts');
    await expect(facts).toHaveCount(1);
    const labels = await facts.locator('dt').allTextContents();
    for (const field of required) {
      expect(labels.map(l => l.trim()), `card ${i} missing "${field}"`).toContain(field);
    }
  }
});

test('every "Prayers for Certain Things" finder link resolves to a prayer card', async ({ page }) => {
  await page.goto('/prayer-library.html');
  const hrefs = await page.locator('.cta-row.finder a[href^="#"]').evaluateAll(links => links.map(a => a.getAttribute('href')));
  expect(hrefs.length).toBeGreaterThanOrEqual(10);
  for (const href of hrefs) {
    const target = page.locator(`.prayer-card${href}`);
    await expect(target, `finder link ${href} has no matching card`).toHaveCount(1);
  }
});

test('promises carry Church-status labels and no guaranteed-outcome language', async ({ page }) => {
  await page.goto('/prayer-library.html');
  const main = page.locator('main');
  await expect(main).toContainText(/Enchiridion Indulgentiarum/);
  await expect(main).toContainText(/CCC 1508/);
  await expect(main).toContainText(/mechanically guarantees/);
  const promiseLabels = await page.locator('.prayer-card .prayer-facts dt', { hasText: 'Promises & status' }).count();
  expect(promiseLabels).toBeGreaterThanOrEqual(8);
});

test('prayer library links into the rest of the site', async ({ page }) => {
  await page.goto('/prayer-library.html');
  for (const slug of ['saint-charbel-prayers', 'rosary-visual-guide', 'mystery-meditation', 'become-like-charbel']) {
    await expect(page.locator(`main a[href*="${slug}"]`).first()).toBeVisible();
  }
});

test('scripture quotes name their public-domain translation', async ({ page }) => {
  await page.goto('/prayer-library.html');
  await expect(page.locator('main')).toContainText(/Douay-Rheims/);
});
