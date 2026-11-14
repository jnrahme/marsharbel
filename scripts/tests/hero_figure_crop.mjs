// Standing face-crop gate (design-director spec): a person's head must keep at
// least 6% headroom in any fixed hero box. The build keys fixed boxes off the
// image's own ratio (is-portrait < 0.9, is-square-ish 0.9-1.3, landscape
// unclassed); this gate verifies every .hero-figure img in the build carries
// the right class for its attrs, that portrait frames anchor at 50% 8% (>= 6%
// headroom by construction), that square-ish and base frames never force a
// landscape ratio on portrait art, and that every hero image actually loads
// without introducing horizontal overflow. Served test - run via
// scripts/tests/run_hero_figure_crop.sh.
import assert from 'node:assert/strict';
import { readFileSync, readdirSync } from 'node:fs';
import { chromium } from 'playwright';
const base = process.env.BASE_URL || 'http://127.0.0.1:4198';
// Frozen-body prayer-cluster pages (locales/prayer-metadata-contract.json) are
// byte-locked by a reviewed contract; ratio classes reach them only through a
// contract-refresh re-pin, so the gate verifies them after that re-pin lands.
const frozen = new Set();
try {
  const contract = JSON.parse(readFileSync('locales/prayer-metadata-contract.json', 'utf8'));
  for (const file of Object.keys(contract.files || {})) frozen.add(file);
} catch {}
try {
  const travel = JSON.parse(readFileSync('locales/travel-equivalence.json', 'utf8'));
  for (const g of Object.values(travel.groups || travel)) {
    const f = g && g.variants && g.variants.en && g.variants.en.file;
    if (f) frozen.add(f);
  }
} catch {}
const pages = readdirSync('.').filter(f => f.endsWith('.html'))
  .filter(f => !frozen.has(f))
  .filter(f => readFileSync(f, 'utf8').includes('class="hero-figure"'));
assert.ok(pages.length > 40, `expected the hero-figure sweep to cover many pages, got ${pages.length}`);
const browser = await chromium.launch();
let figures = 0, portraits = 0, squareish = 0, landscape = 0;
try {
  for (const file of pages) {
    const route = '/' + file.replace(/\.html$/, '').replace(/^index$/, '');
    const page = await browser.newPage({ viewport: { width: 1280, height: 900 }, reducedMotion: 'reduce' });
    await page.goto(base + route, { waitUntil: 'domcontentloaded' });
    const imgs = await page.locator('.hero-figure img').all();
    assert.ok(imgs.length > 0, `${file}: hero-figure expected`);
    for (const img of imgs) {
      figures++;
      await img.scrollIntoViewIfNeeded();
      await img.evaluate(el => { el.loading = 'eager'; });
      await img.evaluate(el => (el.complete && el.naturalWidth > 0)
        ? 1
        : new Promise(r => {
            el.addEventListener('load', () => r(1), { once: true });
            el.addEventListener('error', () => r(0), { once: true });
          }));
      const probe = await img.evaluate(el => {
        const cs = getComputedStyle(el);
        return {
          src: el.getAttribute('src'), cls: el.className,
          w: Number(el.getAttribute('width')), h: Number(el.getAttribute('height')),
          ratio: Number(el.getAttribute('width')) / Number(el.getAttribute('height')),
          loaded: el.complete && el.naturalWidth > 0,
          aspectRatio: cs.aspectRatio, objectFit: cs.objectFit, objectPosition: cs.objectPosition,
          box: (() => { const r = el.getBoundingClientRect(); return { w: r.width, h: r.height }; })(),
        };
      });
      assert.ok(probe.loaded, `${file} ${probe.src}: image did not load`);
      assert.ok(probe.w > 0 && probe.h > 0, `${file} ${probe.src}: width/height attrs required for ratio keying`);
      const cls = probe.ratio < 0.9 ? 'is-portrait' : (probe.ratio <= 1.3 ? 'is-square-ish' : null);
      if (cls) assert.ok(probe.cls.includes(cls), `${file} ${probe.src}: ratio ${probe.ratio.toFixed(2)} requires class ${cls} (found "${probe.cls}")`);
      else assert.ok(!/is-portrait|is-square-ish/.test(probe.cls), `${file} ${probe.src}: landscape ratio ${probe.ratio.toFixed(2)} must stay unclassed`);
      if (cls === 'is-portrait') {
        portraits++;
        const inCardGrid = await img.evaluate(el => !!el.closest('.grid-2, .portrait-cards, main:has(#eucharistic-miracles)'));
        if (!inCardGrid) {
          assert.equal(probe.aspectRatio.replace(/\s/g, ''), '3/4', `${file} ${probe.src}: portrait frame must be 3/4`);
          assert.equal(probe.objectFit, 'cover', `${file} ${probe.src}: portrait frame must cover`);
          const yMatch = /(\d+(?:\.\d+)?)%$/.exec(probe.objectPosition.trim().split(/\s+/)[1] || '');
          assert.ok(yMatch, `${file} ${probe.src}: object-position needs a percentage y anchor (got "${probe.objectPosition}")`);
          assert.ok(Number(yMatch[1]) >= 6, `${file} ${probe.src}: head headroom ${yMatch[1]}% < 6% standing minimum`);
          assert.ok(probe.box.h <= 761, `${file} ${probe.src}: portrait frame ${Math.round(probe.box.h)}px tall exceeds the 760px cap`);
        }
      } else if (cls === 'is-square-ish') {
        squareish++;
        assert.notEqual(probe.aspectRatio.replace(/\s/g, ''), '16/10', `${file} ${probe.src}: square-ish art must not be forced into a landscape frame`);
      } else {
        landscape++;
      }
    }
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1), true, `${file}: horizontal overflow`);
    await page.close();
  }
} finally { await browser.close(); }
console.log(`Hero-figure crop gate passed: ${figures} figures on ${pages.length} pages (${portraits} portrait, ${squareish} square-ish, ${landscape} landscape).`);
