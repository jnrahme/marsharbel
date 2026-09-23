const { test, expect } = require('@playwright/test');
const AxeBuilder = require('@axe-core/playwright').default;

const pages = ['/submit-testimony.html', '/testimony-review.html', '/account.html'];
// These checks exercise the paused setup state regardless of live rollout flags.
test.beforeEach(async ({ page }) => {
  await page.route('**/testimony-config.js*', route => route.fulfill({
    contentType: 'application/javascript',
    body: 'window.TESTIMONY_CONFIG = Object.freeze({accountsEnabled:false, submissionsEnabled:false, moderationEnabled:false});'
  }));
});
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
test('submit page states guest access and adults-only policy', async ({ page }) => {
  await page.goto('/submit-testimony.html');
  await expect(page.locator('input[name=age_confirmed]')).toBeVisible();
  await expect(page.locator('main')).toContainText(/No account is needed/i);
  await expect(page.locator('main')).toContainText(/18 or older/i);
});
test('account page records the decided launch policy', async ({ page }) => {
  await page.goto('/account.html');
  await expect(page.locator('main')).toContainText(/No account is needed/i);
  await expect(page.locator('main')).toContainText(/18 or older/i);
  await expect(page.locator('main')).toContainText(/30-day/i);
  await expect(page.locator('main')).toContainText(/authenticated review and approval/i);
});

test('moderation page shows only a sign-in form until the authorized moderator signs in', async ({ page }) => {
  await page.goto('/testimony-review.html');
  await expect(page.locator('#admin-panel')).toBeHidden();
  await expect(page.getByRole('button', { name: 'Approve' })).toHaveCount(0);
  await expect(page.getByRole('button', { name: 'Reject' })).toHaveCount(0);
  await expect(page.locator('main')).toContainText(/moderator/i);
  await expect(page.locator('main')).toContainText(/email, password, and human verification/i);
  await expect(page.locator('main')).toContainText(/Only the site moderator can review private submissions/i);
});
test('testimony footers provide discreet admin links outside primary navigation', async ({ page }) => {
  for (const path of ['/', '/submit-testimony.html', '/testimonies.html', '/account.html']) {
    await page.goto(path);
    await expect(page.locator('header a[href*="testimony-review"]')).toHaveCount(0);
    await expect(page.locator('footer a[href*="testimony-review"]')).toHaveCount(['/submit-testimony.html', '/testimonies.html'].includes(path) ? 1 : 0);
    if (['/submit-testimony.html', '/testimonies.html'].includes(path)) {
      await page.getByRole('link', { name: 'Admin', exact: true }).click();
      await expect(page).toHaveURL(/testimony-review/);
      await expect(page.locator('#admin-login-form')).toBeVisible();
    }
  }
});
test('admin client script gates the panel on the moderator role and MFA', async ({ request }) => {
  const js = await (await request.get('/testimony-admin.js')).text();
  expect(js).toContain("'moderator'");
  expect(js).toContain('aal2');
  expect(js).toContain('getAuthenticatorAssuranceLevel');
  expect(js).toContain('client.auth.getUser()');
});


test('paused admin fields accept typing but never submit credentials', async ({ page }) => {
  await page.goto('/testimony-review.html');
  const email = page.locator('#admin-login-form [name="email"]');
  const password = page.locator('#admin-login-form [name="password"]');
  await email.fill('typing-check@example.test');
  await password.fill('not-a-real-password');
  await expect(email).toHaveValue('typing-check@example.test');
  await expect(password).toHaveValue('not-a-real-password');
  await expect(page.locator('#admin-login-form button')).toBeDisabled();
  await expect(page.locator('#admin-status')).toContainText('Sign-in is not enabled yet');
  const originalUrl = page.url();
  const allowed = await page.locator('#admin-login-form').evaluate(form => form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true })));
  expect(allowed).toBe(false);
  await password.press('Enter');
  await expect(page).toHaveURL(originalUrl);
  await expect(page.locator('#admin-panel')).toBeHidden();
});

test('paused public forms prevent native GET submission', async ({ page }) => {
  for (const [path, form] of [['/submit-testimony.html','#testimony-form'], ['/account.html','#account-login']]) {
    await page.goto(path);
    expect(await page.locator(form).evaluate(el=>el.dispatchEvent(new Event('submit',{bubbles:true,cancelable:true})))).toBe(false);
  }
});
