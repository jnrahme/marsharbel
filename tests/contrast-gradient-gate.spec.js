// Axe cannot resolve a background color over gradients, so it lists those text nodes as "incomplete" and never
// fails them. This gate takes every such node, hides all text, samples the real pixels behind it and checks
// the WCAG contrast ratio itself.
const { test, expect } = require('@playwright/test');
const AxeBuilder = require('@axe-core/playwright').default;

// Text-over-photo sections (home news, gallery) are out of scope: a flat average of a photo is not a fair background.
const pages = ['/story', '/stories', '/pio-story', '/peter-story', '/accessibility', '/voice-testimony', '/prayer-library'];

const lum = ([r, g, b]) => {
  const f = v => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
  return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b);
};
const ratio = (a, b) => { const [hi, lo] = [lum(a), lum(b)].sort((x, y) => y - x); return (hi + 0.05) / (lo + 0.05); };

for (const path of pages) {
  test(`gradient contrast ${path}`, async ({ page }, info) => {
    test.skip(!['phone', 'laptop'].includes(info.project.name), 'phone and laptop cover the gate');
    test.setTimeout(120_000);
    await page.route(url => !['127.0.0.1', 'localhost'].includes(new URL(url).hostname), route => route.abort());
    await page.emulateMedia({ reducedMotion: 'reduce' });
    await page.goto(path, { waitUntil: 'load' });
    await page.waitForTimeout(300);
    const results = await new AxeBuilder({ page }).withRules(['color-contrast']).analyze();
    const selectors = results.incomplete.filter(v => v.id === 'color-contrast')
      .flatMap(v => v.nodes.filter(n => /gradient/i.test(n.any.map(a => a.message).join(' '))).map(n => n.target[n.target.length - 1]));
    const failures = [];
    for (const selector of [...new Set(selectors)].slice(0, 60)) {
      const el = page.locator(selector).first();
      if (!(await el.isVisible().catch(() => false))) continue;
      // Sticky header and nav sit over layered translucent backgrounds that a flat pixel sample misreads; this gate covers page content.
      if (!(await el.evaluate(node => Boolean(node.closest('main'))))) continue;
      await el.scrollIntoViewIfNeeded();
      const info2 = await el.evaluate(node => {
        const cs = getComputedStyle(node);
        const m = cs.color.match(/[\d.]+/g).map(Number);
        const rect = node.getBoundingClientRect();
        return { color: m.slice(0, 3), alpha: m[3] === undefined ? 1 : m[3], size: parseFloat(cs.fontSize), bold: Number(cs.fontWeight) >= 700,
          text: node.textContent.trim().slice(0, 40), w: rect.width, h: rect.height };
      });
      if (!info2.text || info2.w < 2 || info2.h < 2) continue;
      await page.addStyleTag({ content: '*{color:transparent!important;text-shadow:none!important;-webkit-text-fill-color:transparent!important}' });
      const png = await el.screenshot();
      await page.evaluate(() => document.querySelectorAll('style').forEach(s => { if (s.textContent.startsWith('*{color:transparent')) s.remove(); }));
      const bg = await page.evaluate(async b64 => {
        const img = await createImageBitmap(await (await fetch('data:image/png;base64,' + b64)).blob());
        const c = document.createElement('canvas'); c.width = img.width; c.height = img.height;
        const x = c.getContext('2d'); x.drawImage(img, 0, 0);
        const d = x.getImageData(0, 0, c.width, c.height).data; const n = d.length / 4;         let r = 0, g = 0, b = 0;
        for (let i = 0; i < d.length; i += 4) { r += d[i]; g += d[i + 1]; b += d[i + 2]; }
        const avg = [r / n, g / n, b / n].map(Math.round);
        return { avg };
      }, png.toString('base64'));
      const need = (info2.size >= 24 || (info2.size >= 18.66 && info2.bold)) ? 3 : 4.5;
      const worst = ratio(info2.color, bg.avg);
      if (worst < need) failures.push(`${selector} "${info2.text}" ${worst.toFixed(2)}:1 < ${need}`);
    }
    expect(failures, `gradient-backed text below WCAG AA on ${path}`).toEqual([]);
  });
}
