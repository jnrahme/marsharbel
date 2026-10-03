const { test, expect } = require('@playwright/test');
const { readFileSync } = require('node:fs');
// Discover the library instead of freezing a roster: incoming books share this contract.
const books = [...new Set([...readFileSync('stories.html', 'utf8').matchAll(/href=["']\.\/(story|[a-z-]+-story(?:-v2)?)["']/g)].map(m => m[1]))];
for (const book of books) for (const width of [360, 1280]) test(`${book} art stays centered at ${width}`, async ({ page }, info) => {
  test.skip(info.project.name !== 'laptop');
  test.setTimeout(60000);
  await page.setViewportSize({ width, height: 900 });
  await page.emulateMedia({ reducedMotion: 'reduce' });
  await page.addInitScript(() => { window.__MARSHARBEL_QA__ = { kind: 'monitoring', runner: 'storybook-art-frame' }; });
  await page.route(/google-analytics\.com/, r => r.fulfill({ status: 204 }));
  await page.goto(`/${book}`);
  if (width === 360) await page.evaluate(() => document.documentElement.style.fontSize = '125%');
  const count = Number((await page.locator('#story-step').textContent()).match(/of (\d+)/)[1]);
  for (let n = 1; n <= count; n++) {
    if (n > 1) await page.locator('#story-next').click();
    await expect(page.locator('#story-step')).toHaveText(`Page ${n} of ${count}`);
    await page.locator('.scene-photo').evaluate(img => img.decode());
    const g = await page.evaluate(() => {
      const img = document.querySelector('.scene-photo'), frame = document.querySelector('.storybook-illustration');
      const i = img.getBoundingClientRect(), f = frame.getBoundingClientRect();
      return { overflow: document.documentElement.scrollWidth > innerWidth,
        ratio: Math.abs(i.width / i.height - img.naturalWidth / img.naturalHeight),
        center: Math.abs(i.left + i.right - f.left - f.right),
        contained: i.left >= f.left - .5 && i.right <= f.right + .5 && i.top >= f.top - .5 && i.bottom <= f.bottom + .5,
        filter: getComputedStyle(img).filter };
    });
    expect(g.overflow).toBe(false); expect(g.ratio).toBeLessThan(.02);
    expect(g.center).toBeLessThan(1); expect(g.contained).toBe(true); expect(g.filter).toBe('none');
  }
});
test('page hinge is bounded, interruptible, and skipped for keyboard / reduced motion', async ({ page }, info) => {
  test.skip(info.project.name !== 'laptop');
  await page.addInitScript(() => { window.__MARSHARBEL_QA__ = { kind: 'monitoring' }; });
  await page.goto('/peter-story');
  await page.locator('#story-next').click();
  const animation = await page.locator('.scene-art').evaluate(e => e.getAnimations().map(a => ({ duration: a.effect.getTiming().duration, frames: a.effect.getKeyframes() })));
  expect(animation[0].duration).toBe(240); expect(animation[0].frames[0].transform).toContain('rotateY');
  await page.locator('#story-next').click();
  await expect(page.locator('#story-step')).toHaveText('Page 3 of 10');
  await page.keyboard.press('ArrowRight');
  expect(await page.locator('.scene-art').evaluate(e => e.getAnimations().length)).toBe(0);
  await page.emulateMedia({ reducedMotion: 'reduce' });
  await page.locator('#story-next').click();
  expect(await page.locator('.scene-art').evaluate(e => e.getAnimations().length)).toBe(0);
});
