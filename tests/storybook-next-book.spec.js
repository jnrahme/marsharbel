const { test, expect } = require('@playwright/test');
const AxeBuilder = require('@axe-core/playwright').default;
// The end-of-book card follows the library shelf order in stories.html: next card in the shelf, wrapping at the end.
test('last page suggests the next shelf book, and is hidden before that', async ({ page }, info) => {
  test.skip(info.project.name !== 'laptop');
  test.setTimeout(60000);
  await page.addInitScript(() => { window.__MARSHARBEL_QA__ = { kind: 'monitoring', runner: 'storybook-next-book' }; });
  await page.route(/google-analytics\.com/, r => r.fulfill({ status: 204 }));
  await page.emulateMedia({ reducedMotion: 'reduce' });
  await page.goto('/maroun-story');
  await expect(page.locator('#story-step')).toContainText('Page 1 of');
  await expect(page.locator('.st-next')).toHaveCount(0);
  const count = Number((await page.locator('#story-step').textContent()).match(/of (\d+)/)[1]);
  for (let n = 2; n <= count; n++) await page.locator('#story-next').click();
  const card = page.locator('.st-next');
  await expect(card).toBeVisible();
  await expect(card).toHaveAttribute('href', /massabki-story$/);
  await expect(card.locator('.st-next-title')).not.toBeEmpty();
  await expect(card.locator('img')).toHaveJSProperty('complete', true);
  expect(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth)).toBe(false);
  const axe = await new AxeBuilder({ page }).include('.st-next').analyze();
  expect(axe.violations).toEqual([]);
  await page.locator('#story-prev').click();
  await expect(card).toBeHidden();
});
