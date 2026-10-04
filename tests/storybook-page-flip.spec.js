const { test, expect } = require('@playwright/test');
// The reader turns a real leaf (front and back) on tablets and desktops, lifts the page on phones, and stays still with reduced motion.
const sizes = [['desktop', 1280, 800, 'spread'], ['tablet portrait', 820, 1180, 'spread'], ['tablet landscape', 1180, 820, 'spread'], ['phone', 390, 844, 'phone']];
for (const [name, width, height, kind] of sizes) {
  test(`page flip runs on ${name}`, async ({ page }, info) => {
    test.skip(info.project.name !== 'laptop');
    test.setTimeout(60000);
    await page.setViewportSize({ width, height });
    await page.addInitScript(() => { window.__MARSHARBEL_QA__ = { kind: 'monitoring', runner: 'storybook-page-flip' }; });
    await page.route(/google-analytics\.com/, r => r.fulfill({ status: 204 }));
    await page.goto('/maroun-story');
    await expect(page.locator('#story-step')).toContainText('Page 1 of');
    await page.locator('#story-next').click();
    await expect(page.locator('.st-flip')).toHaveCount(1);
    if (kind === 'spread') {
      await expect(page.locator('.st-leaf .st-front')).toHaveCount(1);
      await expect(page.locator('.st-leaf .st-back')).toHaveCount(1);
    } else {
      await expect(page.locator('.st-leaf-phone')).toHaveCount(1);
    }
    await expect(page.locator('.st-flip')).toHaveCount(0, { timeout: 3000 });
    expect(await page.evaluate(() => document.querySelectorAll('[id="story-body"]').length)).toBe(1);
    expect(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth)).toBe(false);
    await page.locator('#story-prev').click();
    await expect(page.locator('.st-flip')).toHaveCount(1);
    await expect(page.locator('.st-flip')).toHaveCount(0, { timeout: 3000 });
  });
}
test('reduced motion: no leaf', async ({ page }, info) => {
  test.skip(info.project.name !== 'laptop');
  await page.emulateMedia({ reducedMotion: 'reduce' });
  await page.route(/google-analytics\.com/, r => r.fulfill({ status: 204 }));
  await page.goto('/maroun-story');
  await page.locator('#story-next').click();
  await expect(page.locator('.st-flip')).toHaveCount(0);
});
