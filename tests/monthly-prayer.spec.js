const { test, expect } = require('@playwright/test');
const AxeBuilder = require('@axe-core/playwright').default;

for (const [date, active, next] of [
  ['2026-09-20T12:00:00', false, 'September'],
  ['2026-09-21T12:00:00', true, null],
  ['2026-09-22T12:00:00', true, null],
  ['2026-09-23T12:00:00', false, 'October'],
  ['2026-12-31T12:00:00', false, 'January'],
  ['2028-02-29T12:00:00', false, 'March']
]) {
  test(`monthly invitation on ${date}`, async ({ page }) => {
    await page.clock.install({ time: new Date(date) });
    await page.goto('/');
    const section = page.locator('#monthly-prayer');
    await expect(section.locator('details')).toHaveJSProperty('open', active);
    if (next) await expect(section.locator('[data-prayer-timing]')).toContainText(next);
    await section.locator('summary').click();
    await expect(section.locator('details')).toHaveJSProperty('open', !active);
    await page.clock.fastForward(60_000);
    await expect(section.locator('details')).toHaveJSProperty('open', !active);
  });
}

test('updates when the local day changes', async ({ page }) => {
  await page.clock.install({ time: new Date('2026-09-20T23:59:30') });
  await page.goto('/');
  await expect(page.locator('#monthly-prayer details')).toHaveJSProperty('open', false);
  await page.clock.fastForward(60_000);
  await expect(page.locator('#monthly-prayer details')).toHaveJSProperty('open', true);
  await expect(page.locator('[data-prayer-status]')).toHaveText('We are united in prayer today');
});

test('prayer is accessible, responsive, and links to existing resources', async ({ page }) => {
  await page.clock.install({ time: new Date('2026-09-22T12:00:00') });
  await page.goto('/');
  const section = page.locator('#monthly-prayer');
  await section.scrollIntoViewIfNeeded();
  const violations = (await new AxeBuilder({ page }).include('#monthly-prayer').withTags(['wcag2a', 'wcag2aa', 'wcag21aa']).analyze()).violations;
  expect(violations).toEqual([]);
  expect(await section.evaluate(el => el.scrollWidth <= el.clientWidth + 1)).toBe(true);
  for (const href of await section.locator('a[href^="./"]').evaluateAll(links => links.map(a => a.getAttribute('href')))) {
    expect((await page.request.get(href)).ok()).toBe(true);
  }
  await section.locator('summary').focus();
  await page.keyboard.press('Enter');
  await expect(section.locator('details')).toHaveJSProperty('open', false);
});

test('prayer stays available without JavaScript', async ({ browser, baseURL }) => {
  const context = await browser.newContext({ javaScriptEnabled: false });
  const page = await context.newPage();
  await page.goto(baseURL);
  await page.locator('#monthly-prayer summary').click();
  await expect(page.locator('#monthly-prayer-heading')).toBeVisible();
  await context.close();
});
