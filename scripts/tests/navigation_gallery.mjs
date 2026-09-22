#!/usr/bin/env node
import assert from 'node:assert/strict';
import { chromium } from 'playwright';

const baseArg = process.argv.find(arg => arg.startsWith('--base-url='));
const baseUrl = baseArg ? baseArg.slice('--base-url='.length) : 'http://127.0.0.1:4173';
const browser = await chromium.launch();
try {
  for (const [width, height] of [[375, 667], [667, 375], [1366, 900]]) {
    const page = await browser.newPage({ serviceWorkers: 'block', viewport: { width, height } });
    await page.goto(`${baseUrl}/index.html`);
    const group = page.locator('.nav-group').first();
    const parent = group.locator('.nav-parent');
    const panel = group.locator('.nav-sub');
    if (width > 820) await parent.hover();
    else await parent.click();
    assert.equal(await panel.isVisible(), true, 'Navigation opens');
    assert.equal(await parent.getAttribute('aria-expanded'), 'true', 'Open state is announced');
    await page.keyboard.press('Escape');
    await page.waitForTimeout(350);
    assert.equal(await panel.isVisible(), false, 'Escape closes even a hovered menu');
    assert.equal(await parent.getAttribute('aria-expanded'), 'false');
    if (width <= 820) {
      for (let i = 0; i < 2; i++) {
        await parent.click();
        assert.equal(await panel.isVisible(), true, 'Touch menu can reopen');
        await parent.click();
        await page.waitForTimeout(350);
        assert.equal(await panel.isVisible(), false, 'Second tap closes');
      }
    }
    await page.mouse.move(0, 500);
    await page.keyboard.press('Tab');
    await parent.focus();
    await page.keyboard.press('Tab');
    assert.equal(await group.evaluate(e => e.contains(document.activeElement)), true, 'Keyboard can enter submenu');
    await page.keyboard.press('Escape');
    assert.equal(await parent.evaluate(e => e === document.activeElement), true, 'Escape returns focus to parent');

    await page.goto(`${baseUrl}/gallery.html`);
    const first = page.locator('.gallery-item').first();
    await first.focus();
    await page.keyboard.press('Enter');
    const lightbox = page.getByRole('dialog', { name: 'Gallery image viewer' });
    assert.equal(await lightbox.isVisible(), true);
    assert.equal(await page.locator('#lightbox-close').evaluate(e => e === document.activeElement), true);
    for (const key of ['Shift+Tab', 'Tab', 'Tab', 'Tab', 'Tab']) {
      await page.keyboard.press(key);
      assert.equal(await lightbox.evaluate(e => e.contains(document.activeElement)), true, 'Focus remains inside viewer');
    }
    const original = await page.locator('#lightbox-image').getAttribute('src');
    await page.keyboard.press('ArrowRight');
    assert.notEqual(await page.locator('#lightbox-image').getAttribute('src'), original);
    await page.keyboard.press('ArrowLeft');
    assert.equal(await page.locator('#lightbox-image').getAttribute('src'), original);
    for (let i = 0; i < await page.locator('.gallery-item').count(); i++) {
      await page.locator('#lightbox-image').evaluate(image => image.decode());
      const outside = await lightbox.evaluate(element => [...element.querySelectorAll('img, button')].filter(control => {
        const rect = control.getBoundingClientRect();
        return rect.left < 0 || rect.top < 0 || rect.right > innerWidth + 1 || rect.bottom > innerHeight + 1;
      }).map(control => control.id));
      assert.deepEqual(outside, [], 'Every gallery image and control fits the screen');
      await page.keyboard.press('ArrowRight');
    }
    await page.keyboard.press('Escape');
    assert.equal(await lightbox.isVisible(), false);
    assert.equal(await first.evaluate(e => e === document.activeElement), true, 'Focus returns to selected photo');
    assert.equal(await page.evaluate(() => document.body.style.overflow), '');
    await page.close();
    console.log(`Navigation and gallery keyboard checks passed at ${width}px`);
  }
} finally {
  await browser.close();
}
