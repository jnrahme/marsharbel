/* Shared same-page contract for switcher tests.
 * Expectations derive from the BUILT same-page-manifest.js + the real resolver
 * (intl ruling 2026-10-11): option count = published locales; an option is
 * enabled exactly when the real resolver returns available for that route.
 * Never hardcode locale counts or per-route availability here. */
const fs = require('fs');
const path = require('path');

function repoRoot() { return path.resolve(__dirname, '../..'); }

function loadBuiltManifest(root) {
  const raw = fs.readFileSync(path.join(root, 'same-page-manifest.js'), 'utf8');
  return JSON.parse(raw.replace(/^window\.SC_SAME_PAGE_MANIFEST = /, '').replace(/;\s*$/, ''));
}

function loadResolver(root) { return require(path.join(root, 'same-page-resolver.js')); }

function loadCopy(root) {
  return JSON.parse(fs.readFileSync(path.join(root, 'locales/same-page-copy.draft.json'), 'utf8'));
}

/* Mirror of same-page-switcher.js option construction:
 * one option per manifest.languages entry, disabled = !resolve(...).available */
function optionExpectations(manifest, api, href, actual) {
  const enabled = {}, disabled = [];
  for (const lang of manifest.languages) {
    const r = api.resolve(manifest, href, lang, actual);
    if (r.available) enabled[lang] = { href: r.href, reason: r.reason };
    else disabled.push(lang);
  }
  return { count: manifest.languages.length, enabled, disabled };
}

/* Mirror of the switcher's nav.locale-nav rewrite for a given hreflang list. */
function navExpectations(manifest, api, href, actual, hreflangs) {
  const enabled = [], disabled = [];
  for (const lang of hreflangs) {
    const r = api.resolve(manifest, href, lang, actual);
    (r.available ? enabled : disabled).push(lang);
  }
  return { enabled, disabled };
}

function hreflangsOf(file) {
  const html = fs.readFileSync(file, 'utf8');
  // Attribute-order-independent: the opening tag may carry aria-label/data
  // attributes before class (generated PR3 nav) or class first (authored A1).
  const nav = html.match(/<nav\b[^>]*\bclass="[^"]*\blocale-nav\b[^"]*"[^>]*>[\s\S]*?<\/nav>/);
  if (!nav) return null; // no exact-page locale nav on this page
  return [...nav[0].matchAll(/hreflang="([^"]+)"/g)].map(m => m[1]);
}

/* PR3 generated locale-nav inventory, derived from the built manifest:
 * non-ar2 families with >=2 verified variants, excluding the certified A1
 * authored family. Mirrors scripts/qa/test_static_language_fallback.py
 * eligible(); the two must never drift apart. */
function generatedNavEligibleRoutes(manifest) {
  const routes = new Set();
  for (const [key, fam] of Object.entries(manifest.pages)) {
    if (key.startsWith('ar2-') || key === 'rosary-guide-equivalence') continue;
    const verified = Object.values(fam.variants || {}).filter(v => v.status === 'verified');
    if (verified.length >= 2) for (const v of verified) routes.add(v.path.replace(/\/$/, '') || '/');
  }
  return routes;
}

module.exports = { repoRoot, loadBuiltManifest, loadResolver, loadCopy, optionExpectations, navExpectations, hreflangsOf, generatedNavEligibleRoutes };
