// Axe cannot resolve a background color over gradients, so it lists those text nodes as "incomplete" and never
// fails them. This gate takes every such node, hides all text, samples the real pixels behind it and checks
// the WCAG contrast ratio itself: translucent text is composited over every sampled pixel and the lowest ratio counts.
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
    const unique = [...new Set(selectors)];
    expect(unique.length, `too many gradient-backed nodes to sample on ${path}; raise the limit on purpose`).toBeLessThanOrEqual(2000);
    // One pass: collect colors and page rectangles for every node, hide text, take one full-page screenshot, sample it.
    const nodes = await page.evaluate(list => list.map(selector => {
      const node = document.querySelector(selector);
      if (!node || !node.closest('main')) return null; // header and nav sit over layered translucent backgrounds
      const cs = getComputedStyle(node);
      const m = cs.color.match(/[\d.]+/g).map(Number);
      let opacity = m[3] === undefined ? 1 : m[3];
      for (let n = node; n && n.nodeType === 1; n = n.parentElement) opacity *= Number(getComputedStyle(n).opacity);
      const rect = node.getBoundingClientRect();
      const disabled = Boolean(node.closest('[disabled],[aria-disabled="true"]'));
      return { selector, disabled, color: m.slice(0, 3), alpha: opacity, size: parseFloat(cs.fontSize), bold: Number(cs.fontWeight) >= 700,
        text: node.textContent.trim().slice(0, 40), x: rect.left + scrollX, y: rect.top + scrollY, w: rect.width, h: rect.height,
        hidden: cs.visibility === 'hidden' || cs.display === 'none' };
    }), unique);
    await page.addStyleTag({ content: '*{color:transparent!important;text-shadow:none!important;-webkit-text-fill-color:transparent!important}' });
    const wanted = nodes.filter(n => n && !n.disabled && !n.hidden && n.text && n.w >= 2 && n.h >= 2);
    // Very tall pages crash a single full-page screenshot, so sample in bands of 3000 CSS px.
    const { width, height } = await page.evaluate(() => ({ width: document.documentElement.scrollWidth, height: document.documentElement.scrollHeight }));
    // Text scrolled out of view inside an overflow container sits outside the document box; it cannot be sampled and is skipped.
    const grids = new Array(wanted.length).fill(null);
    wanted.forEach((n, k) => { if (n.y + n.h / 2 >= height || n.y + n.h / 2 < 0) grids[k] = 'skip'; });
    for (let top = 0; top < height; top += 3000) {
      const bandH = Math.min(3000, height - top);
      const inBand = wanted.map((n, k) => ({ n, k })).filter(({ n, k }) => grids[k] !== 'skip').filter(({ n }) => n.y + n.h / 2 >= top && n.y + n.h / 2 < top + bandH);
      if (!inBand.length) continue;
      const shot = (await page.screenshot({ fullPage: true, scale: 'css', clip: { x: 0, y: top, width, height: bandH } })).toString('base64');
      const out = await page.evaluate(async ({ b64, boxes, top: bandTop }) => {
        const img = await createImageBitmap(await (await fetch('data:image/png;base64,' + b64)).blob());
        const c = document.createElement('canvas'); c.width = img.width; c.height = img.height;
        const x = c.getContext('2d', { willReadFrequently: true }); x.drawImage(img, 0, 0);
        return boxes.map(n => {
          const px0 = Math.min(img.width - 1, Math.max(0, Math.floor(n.x))), py0 = Math.min(img.height - 1, Math.max(0, Math.floor(n.y - bandTop)));
          const w = Math.max(1, Math.min(img.width - px0, Math.ceil(n.w))), h = Math.max(1, Math.min(img.height - py0, Math.ceil(n.h)));
          const d = x.getImageData(px0, py0, w, h).data; const step = Math.max(1, Math.floor(Math.sqrt((w * h) / 300))); const px = [];
          for (let yy = 0; yy < h; yy += step) for (let xx = 0; xx < w; xx += step) { const i = (yy * w + xx) * 4; px.push([d[i], d[i + 1], d[i + 2]]); }
          return px;
        });
      }, { b64: shot, boxes: inBand.map(({ n }) => n), top });
      inBand.forEach(({ k }, j) => { grids[k] = out[j]; });
    }
    const failures = [];
    wanted.forEach((n, k) => {
      const need = (n.size >= 24 || (n.size >= 18.66 && n.bold)) ? 3 : 4.5;
      // Composite translucent text over each sampled background pixel, then take the lowest ratio.
      const over = (fg, back) => fg.map((v, j) => Math.round(v * n.alpha + back[j] * (1 - n.alpha)));
      if (grids[k] === 'skip') return;
      if (!grids[k] || !grids[k].length) { failures.push(`${n.selector} could not be sampled`); return; }
      const worst = Math.min(...grids[k].map(back => ratio(over(n.color, back), back)));
      if (worst < need) failures.push(`${n.selector} "${n.text}" ${worst.toFixed(2)}:1 < ${need}`);
    });
    expect(failures, `gradient-backed text below WCAG AA on ${path}`).toEqual([]);
  });
}
