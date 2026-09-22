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
  await expect(page.locator('#submit-testimony-btn')).toBeDisabled();
  await expect(page.locator('#submit-status')).toContainText(/safely paused/i);
});
test('account creation is paused and intake is text-only', async ({ page }) => {
  await page.goto('/account.html');
  await expect(page.getByRole('button', { name: 'Continue securely' })).toBeDisabled();
  await page.goto('/submit-testimony.html');
  await expect(page.locator('input[type=file]')).toHaveCount(0);
  await expect(page.locator('main')).toContainText(/Text only/i);
});
test('submit page states account-required and adults-only launch policy', async ({ page }) => {
  await page.goto('/submit-testimony.html');
  await expect(page.locator('input[name=age_confirmed]')).toBeVisible();
  await expect(page.locator('main')).toContainText(/account is required/i);
  await expect(page.locator('main')).toContainText(/18 or older/i);
});
test('account page records the decided launch policy', async ({ page }) => {
  await page.goto('/account.html');
  await expect(page.locator('main')).toContainText(/required to submit/i);
  await expect(page.locator('main')).toContainText(/18 or older/i);
  await expect(page.locator('main')).toContainText(/30 days/i);
  await expect(page.locator('main')).toContainText(/MFA/i);
});

test('moderation page shows only a sign-in form until a moderator with MFA signs in', async ({ page }) => {
  await page.goto('/testimony-review.html');
  await expect(page.locator('#admin-panel')).toBeHidden();
  await expect(page.getByRole('button', { name: 'Approve' })).toHaveCount(0);
  await expect(page.getByRole('button', { name: 'Reject' })).toHaveCount(0);
  await expect(page.locator('main')).toContainText(/moderator/i);
  await expect(page.locator('main')).toContainText(/multi-factor authentication/i);
  await expect(page.locator('main')).toContainText(/loads no submission data/i);
});
test('public navigation never links to the moderation page', async ({ page }) => {
  for (const path of ['/', '/submit-testimony.html', '/testimonies.html', '/account.html']) {
    await page.goto(path);
    await expect(page.locator('a[href*="testimony-review"]')).toHaveCount(0);
  }
});
test('admin client script gates the panel on the moderator role and MFA', async ({ request }) => {
  const js = await (await request.get('/testimony-admin.js')).text();
  expect(js).toContain("'moderator'");
  expect(js).toContain('aal2');
  expect(js).toContain('getAuthenticatorAssuranceLevel');
  expect(js).toContain('client.auth.getUser()');
});
