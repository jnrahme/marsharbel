const { test, expect } = require('@playwright/test');
const AxeBuilder = require('@axe-core/playwright').default;

const pages = ['/index.html', '/story.html', '/rosary-visual-guide.html', '/gallery.html', '/saint-charbel-novena.html', '/saint-charbel-feast-day.html', '/visit-annaya.html', '/22nd-of-the-month.html', '/miracles.html'];

for (const path of pages) {
  test.describe(path, () => {
    test('renders without overflow, broken images, console errors, or serious accessibility issues', async ({ page }) => {
      const consoleErrors = [];
      page.on('console', message => {
        if (message.type() === 'error') consoleErrors.push(message.text());
      });

      const response = await page.goto(path, { waitUntil: 'networkidle' });
      expect(response?.ok(), `HTTP failure for ${path}`).toBeTruthy();

      const layout = await page.evaluate(() => ({
        viewportWidth: document.documentElement.clientWidth,
        documentWidth: document.documentElement.scrollWidth,
        brokenImages: [...document.images]
          .filter(image => image.complete && image.naturalWidth === 0)
          .map(image => image.currentSrc || image.src)
      }));
      expect(layout.documentWidth, `Horizontal overflow on ${path}`).toBeLessThanOrEqual(layout.viewportWidth + 1);
      expect(layout.brokenImages, `Broken images on ${path}`).toEqual([]);

      const accessibility = await new AxeBuilder({ page })
        .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
        .analyze();
      const serious = accessibility.violations.filter(result => ['serious', 'critical'].includes(result.impact));
      expect(serious, `Serious accessibility violations on ${path}`).toEqual([]);
      expect(consoleErrors, `Console errors on ${path}`).toEqual([]);
    });
  });
}
