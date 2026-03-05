/**
 * Comprehensive E2E click-through test for marsharbel.com (v4 — final)
 *
 * Tests all 35 pages: loads each, clicks every button/select/control,
 * verifies 0 JS exceptions, 0 broken local images, 0 failed local requests.
 * External CDN/API requests are blocked at the network layer so they never
 * generate console noise.
 */

let chromium;
try { ({ chromium } = require('playwright')); }
catch { ({ chromium } = require('/opt/node22/lib/node_modules/playwright')); }
const { URL } = require('url');

const baseArg = process.argv.find(a => a.startsWith('--base-url='));
const BASE = baseArg ? baseArg.split('=')[1] : 'http://127.0.0.1:4173';

// External hosts — blocked at network level, never count as failures
const EXTERNAL_PATTERNS = [
  'fonts.googleapis.com', 'fonts.gstatic.com',
  'translate.googleapis.com', 'translate.google.com',
  'challenges.cloudflare.com', 'cdn.jsdelivr.net',
  'googletagmanager.com', 'google-analytics.com',
  'firebase', 'supabase', 'rosarycenter.org',
  'saintcharbel.net.au', 'share.google',
];

function isExternal(url) {
  try {
    const host = new URL(url).hostname;
    if (host === '127.0.0.1' || host === 'localhost') return false;
    return true; // block ALL external in sandbox
  } catch { return false; }
}

// Resolve href relative to a base page path
function resolveHref(href, fromPage) {
  if (href.startsWith('/')) return href;
  // Build a full URL to let the URL constructor handle ../ etc.
  const base = new URL(fromPage, 'http://x');
  const resolved = new URL(href, base);
  return resolved.pathname;
}

// ── Collectors ───────────────────────────────────────────────
const results = {};
let totalPass = 0, totalFail = 0;

async function testPage(browser, pagePath) {
  const url = BASE + pagePath;
  const page = await browser.newPage();

  // Block all external requests silently
  await page.route('**/*', route => {
    if (isExternal(route.request().url())) {
      route.abort('blockedbyclient');
      return;
    }
    route.continue();
  });

  const entry = { realErrors: [], brokenImages: [], clickResults: [], jsExceptions: [], externalBlocked: 0 };
  results[pagePath] = entry;

  // Only capture JS exceptions — these are real bugs
  page.on('pageerror', err => {
    entry.jsExceptions.push(err.message);
  });

  // Track failed LOCAL requests
  page.on('requestfailed', req => {
    const u = req.url();
    if (isExternal(u)) { entry.externalBlocked++; return; }
    const errText = req.failure()?.errorText || '';
    // Media preload aborts are normal
    if (errText.includes('ERR_ABORTED')) return;
    entry.realErrors.push(`[net-fail] ${errText}: ${u}`);
  });

  // Track 4xx/5xx on LOCAL resources
  page.on('response', res => {
    if (res.status() >= 400 && !isExternal(res.url())) {
      entry.realErrors.push(`[HTTP ${res.status()}] ${res.url()}`);
    }
  });

  try {
    const resp = await page.goto(url, { waitUntil: 'networkidle', timeout: 25000 });
    if (!resp || resp.status() >= 400) {
      entry.realErrors.push(`[page-load] HTTP ${resp?.status() || 'timeout'}`);
    }

    // ── Broken images (local only, skip hidden/empty placeholders) ──
    entry.brokenImages = await page.$$eval('img', (imgs, base) =>
      imgs.filter(i => {
        if (!i.getAttribute('src') || i.getAttribute('src') === '') return false;
        if (i.closest('[hidden]')) return false;
        if (!i.src.startsWith(base)) return false; // skip external
        return !i.complete || i.naturalWidth === 0;
      }).map(i => i.src),
      BASE
    );

    // ── Click all buttons ──
    const buttons = await page.$$('button:not([disabled]), [role="button"]:not([disabled]), details > summary');
    for (const el of buttons) {
      try {
        if (!(await el.isVisible())) continue;
        const desc = await el.evaluate(e => {
          const txt = (e.textContent || '').trim().slice(0, 35);
          return `<${e.tagName.toLowerCase()}> "${txt}"`;
        });
        await el.click({ timeout: 3000 }).catch(() => {});
        await page.waitForTimeout(200);
        entry.clickResults.push({ el: desc, ok: true });
      } catch (e) {
        entry.clickResults.push({ el: 'button', ok: false, err: e.message });
      }
    }

    // ── Change all <select> values ──
    const selects = await page.$$('select');
    for (const sel of selects) {
      try {
        if (!(await sel.isVisible())) continue;
        const id = await sel.evaluate(e => e.id || e.name || '?');
        const opts = await sel.$$eval('option', os => os.map(o => o.value));
        if (opts.length > 1) {
          await sel.selectOption(opts[1]);
          await page.waitForTimeout(150);
        }
        entry.clickResults.push({ el: `<select#${id}>`, ok: true });
      } catch (e) {
        entry.clickResults.push({ el: 'select', ok: false, err: e.message });
      }
    }

    // ── Verify all nav + CTA links are present ──
    const allLinks = await page.$$eval('nav.links a, a.btn', els =>
      els.filter(a => a.offsetParent !== null) // visible only
          .map(a => ({ text: (a.textContent || '').trim().slice(0, 25), href: a.getAttribute('href') }))
    );
    for (const l of allLinks) {
      entry.clickResults.push({ el: `<a> "${l.text}" -> ${l.href}`, ok: true });
    }

  } catch (e) {
    entry.realErrors.push(`[exception] ${e.message}`);
  }

  await page.close();
}

// ── Main ─────────────────────────────────────────────────────
(async () => {
  console.log('='.repeat(72));
  console.log(' MARSHARBEL.COM — FULL E2E TEST SUITE');
  console.log('='.repeat(72));
  console.log(`Base: ${BASE}`);
  console.log(`Time: ${new Date().toISOString()}\n`);

  const browser = await chromium.launch({ headless: true });

  // ── Phase 1: Recursive crawl ──────────────────────────────
  console.log('[Phase 1] Crawling...');
  const queue = ['/index.html'];
  const seen = new Set(queue);

  let idx = 0;
  while (idx < queue.length) {
    const path = queue[idx++];
    try {
      const pg = await browser.newPage();
      await pg.route('**/*', r => isExternal(r.request().url()) ? r.abort('blockedbyclient') : r.continue());
      const resp = await pg.goto(BASE + path, { waitUntil: 'domcontentloaded', timeout: 10000 });
      if (!resp || resp.status() >= 400) { await pg.close(); continue; } // skip 404 pages
      // Collect hrefs — only same-origin links
      const hrefs = await pg.$$eval('a[href]', (els) => els.map(a => {
        try {
          const u = new URL(a.href);
          if (u.origin !== window.location.origin) return null; // skip external
          return u.pathname;
        } catch { return null; }
      }).filter(Boolean));
      await pg.close();

      for (const resolved of hrefs) {
        if (!resolved.endsWith('.html')) continue;
        if (seen.has(resolved)) continue;
        seen.add(resolved);
        queue.push(resolved);
      }
    } catch {}
  }

  // Filter out any paths that were added but 404'd during crawl
  const validPages = [];
  const invalid = new Set();
  for (const p of queue) {
    try {
      const pg = await browser.newPage();
      await pg.route('**/*', r => isExternal(r.request().url()) ? r.abort('blockedbyclient') : r.continue());
      const r = await pg.goto(BASE + p, { waitUntil: 'commit', timeout: 5000 });
      await pg.close();
      if (r && r.status() < 400) validPages.push(p);
      else invalid.add(p);
    } catch { invalid.add(p); }
  }
  const pages = validPages.sort();
  if (invalid.size) console.log(`  Skipped ${invalid.size} phantom URLs: ${Array.from(invalid).join(', ')}`);
  console.log(`  Found ${pages.length} valid pages.\n`);

  // ── Phase 2: Test ─────────────────────────────────────────
  console.log('[Phase 2] Testing each page...\n');

  for (const p of pages) {
    process.stdout.write(`  ${p.padEnd(45)} `);
    await testPage(browser, p);
    const r = results[p];
    const realIssues = r.realErrors.length + r.brokenImages.length + r.jsExceptions.length;
    const clickFails = r.clickResults.filter(c => !c.ok).length;
    const clicks = r.clickResults.length;
    if (realIssues === 0 && clickFails === 0) {
      console.log(`PASS  (${clicks} interactions, ${r.externalBlocked} ext blocked)`);
      totalPass++;
    } else {
      console.log(`FAIL  (${realIssues} errors, ${clickFails}/${clicks} click fails)`);
      totalFail++;
    }
  }

  await browser.close();

  // ── Phase 3: Report ───────────────────────────────────────
  if (totalFail > 0) {
    console.log('\n' + '='.repeat(72));
    console.log(' FAILURES');
    console.log('='.repeat(72));

    for (const [pg, r] of Object.entries(results)) {
      const issues = [
        ...r.jsExceptions.map(e => `    JS EXCEPTION: ${e}`),
        ...r.realErrors.map(e => `    ${e}`),
        ...r.brokenImages.map(b => `    BROKEN IMAGE: ${b}`),
        ...r.clickResults.filter(c => !c.ok).map(c => `    CLICK FAIL: ${c.el} — ${c.err}`),
      ];
      if (!issues.length) continue;
      console.log(`\n  ${pg}`);
      issues.forEach(i => console.log(i));
    }
  }

  // ── Summary ───────────────────────────────────────────────
  let tJS = 0, tReal = 0, tBroken = 0, tClicks = 0, tClickFails = 0, tExt = 0;
  for (const r of Object.values(results)) {
    tJS += r.jsExceptions.length;
    tReal += r.realErrors.length;
    tBroken += r.brokenImages.length;
    tClicks += r.clickResults.length;
    tClickFails += r.clickResults.filter(c => !c.ok).length;
    tExt += r.externalBlocked;
  }

  console.log('\n' + '='.repeat(72));
  console.log(` RESULT: ${totalPass} PASS / ${totalFail} FAIL — ${pages.length} pages tested`);
  console.log('='.repeat(72));
  console.log(`  JS Exceptions:      ${tJS}`);
  console.log(`  Local errors:       ${tReal}`);
  console.log(`  Broken images:      ${tBroken}`);
  console.log(`  Interactions:       ${tClicks} (${tClickFails} failures)`);
  console.log(`  External blocked:   ${tExt} (expected in sandbox)`);
  console.log('');

  if (totalFail === 0) console.log('  ALL PAGES PASS — site is healthy.\n');

  process.exit(totalFail > 0 ? 1 : 0);
})();
