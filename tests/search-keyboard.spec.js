const { test, expect } = require('@playwright/test');

async function openSearch(page, path, recent = []) {
  await page.addInitScript(list => localStorage.setItem('sc-search-recent', JSON.stringify(list)), recent);
  await page.goto(path);
  const trigger = page.locator('.scs-trigger');
  await trigger.focus();
  await page.keyboard.press('Enter');
  await expect(page.locator('a.scs-chip')).toHaveCount(7);
  await expect(page.locator('.scs-input')).toBeFocused();
}
for (const path of ['/', '/ar/']) {
  test(`empty search popular links tab in DOM order and return focus ${path}`, async ({page}) => {
    await openSearch(page, path);
    await page.keyboard.press('Tab');
    await expect(page.locator('.scs-close')).toBeFocused();
    const links = page.locator('a.scs-chip');
    for (let i = 0; i < 7; i++) {
      await page.keyboard.press('Tab');
      await expect(links.nth(i)).toBeFocused();
    }
    await page.keyboard.press('Tab');
    await expect(page.locator('.scs-input')).toBeFocused();
    await page.keyboard.press('Shift+Tab');
    await expect(links.last()).toBeFocused();
    await page.keyboard.press('Escape');
    await expect(page.locator('.scs-root')).toBeHidden();
    await expect(page.locator('.scs-trigger')).toBeFocused();
  });
  test(`recent search and clear work with keyboard ${path}`, async ({page}) => {
    await openSearch(page, path, ['novena', 'healing']);
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');
    await expect(page.locator('.scs-clear')).toBeFocused();
    await page.keyboard.press('Tab');
    await expect(page.locator('button.scs-chip').nth(0)).toBeFocused();
    await page.keyboard.press('Tab');
    await expect(page.locator('button.scs-chip').nth(1)).toBeFocused();
    await page.keyboard.press('Shift+Tab');
    await page.keyboard.press('Enter');
    await expect(page.locator('.scs-input')).toHaveValue('novena');
    await expect(page.locator('.scs-input')).toBeFocused();
    await expect(page.locator('.scs-row').first()).toBeVisible();
    await page.locator('.scs-input').fill('');
    await expect(page.locator('.scs-clear')).toBeVisible();
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');
    await expect(page.locator('.scs-clear')).toBeFocused();
    await page.keyboard.press('Enter');
    await expect(page.locator('.scs-clear')).toHaveCount(0);
    await expect(page.locator('button.scs-chip')).toHaveCount(0);
    await expect(page.locator('.scs-input')).toBeFocused();
    expect(await page.evaluate(() => JSON.parse(localStorage.getItem('sc-search-recent')))).toEqual([]);
    await page.keyboard.press('Tab');
    await page.keyboard.press('Enter');
    await expect(page.locator('.scs-trigger')).toBeFocused();
  });
  test(`result combobox keeps arrow navigation and excludes options from Tab ${path}`, async ({page}) => {
    await openSearch(page, path);
    await page.locator('.scs-input').fill('charbel');
    await expect(page.locator('.scs-row').nth(1)).toBeVisible();
    await expect(page.locator('.scs-input')).toHaveAttribute('aria-activedescendant', 'scs-o-0');
    await page.keyboard.press('ArrowDown');
    await expect(page.locator('.scs-input')).toHaveAttribute('aria-activedescendant', 'scs-o-1');
    await expect(page.locator('.scs-input')).toBeFocused();
    await page.keyboard.press('Tab');
    await expect(page.locator('.scs-close')).toBeFocused();
    await page.keyboard.press('Tab');
    await expect(page.locator('.scs-input')).toBeFocused();
  });
}
for (const path of ['/en/annaya', '/en/biography', '/en/novena', '/en/rosary']) {
  test(`English short guide search boots ${path}`, async ({page}) => {
    await openSearch(page, path);
    await expect(page.locator('.scs-trigger')).toHaveCount(1);
    await expect(page.locator('.scs-root')).toHaveCount(1);
  });
}
