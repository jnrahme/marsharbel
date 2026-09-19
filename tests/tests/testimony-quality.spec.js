const { test, expect } = require('@playwright/test');
const AxeBuilder = require('@axe-core/playwright').default;

const pages = ['/submit-testimony.html', '/testimony-review.html', '/account.html'];
for (const path of pages) {
  test(`${path} is fail-closed, responsive, and accessible`, async ({ page }) => {
    const errors = [];
    page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
    const response = await page.goto(path, { waitUntil: 'networkidle' });
    expect(response?.ok()).toBeTruthy();
    const layout = await page.evaluate(() => ({viewport: document.documentElement.clientWidth, width: document.documentElement.scrollWidth, broken: [...document.images].filter(i => i.complete && !i.naturalWidth).length}));
    expect(layout.width).toBeLessThanOrEqual(layout.viewport + 1);
    expect(layout.broken).toBe(0);
    const serious = (await new AxeBuilder({ page }).withTags(['wcag2a','wcag2aa','wcag21a','wcag21aa']).analyze()).violations.filter(v => ['serious','critical'].includes(v.impact));
    expect(serious).toEqual([]);
    expect(errors).toEqual([]);
  });
}
test('public intake cannot submit in QA', async ({ page }) => {
  await page.goto('/submit-testimony.html');
  await expect(page.getByRole('button', { name: 'Submit For Review' })).toBeDisabled();
  await expect(page.getByText(/safely paused/i)).toBeVisible();
});
test('account creation and image uploads are disabled in QA', async ({ page }) => {
  await page.goto('/account.html');
  await expect(page.getByRole('button', { name: 'Continue securely' })).toBeDisabled();
  await page.goto('/submit-testimony.html');
  await expect(page.locator('input[type=file]')).toBeDisabled();
});
