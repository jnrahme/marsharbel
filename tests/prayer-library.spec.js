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

test('prayer library covers every promised category and cites sources', async ({ page }) => {
  await page.goto('/prayer-library.html');
  const main = page.locator('main');
  await expect(main).toContainText(/Maronite & Syriac Tradition/i);
  await expect(main).toContainText(/Core Catholic Prayers/i);
  await expect(main).toContainText(/Prayers by Need/i);
  await expect(main).toContainText(/By Season & Feast/i);
  await expect(main).toContainText(/By Sacrament/i);
  await expect(main).toContainText(/Scripture for Prayer/i);
  // every prayer card carries a source/usage note
  const cards = await page.locator('.prayer-card').count();
  const notes = await page.locator('.prayer-card .section-sub').count();
  expect(notes).toBeGreaterThanOrEqual(cards);
  expect(cards).toBeGreaterThanOrEqual(20);
});

test('prayer library links into the rest of the site', async ({ page }) => {
  await page.goto('/prayer-library.html');
  for (const href of ['./saint-charbel-prayers.html', './rosary-visual-guide.html', './mystery-meditation.html', './become-like-charbel.html']) {
    await expect(page.locator(`main a[href="${href}"]`).first()).toBeVisible();
  }
});

test('scripture quotes name their public-domain translation', async ({ page }) => {
  await page.goto('/prayer-library.html');
  await expect(page.locator('main')).toContainText(/Douay-Rheims/);
});
