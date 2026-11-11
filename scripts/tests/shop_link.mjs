import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, readdirSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { shopLinkConfig, composeShopLink } from '../lib/shop-link.mjs';

const fragment = readFileSync('partials/fragments/shop-link.html', 'utf8').replace(/\n$/, '');
const copy = JSON.parse(readFileSync('locales/en/shop-link-copy.json', 'utf8')).copy;
const hash = value => createHash('sha256').update(value).digest('hex');
function pages(dir) {
  return readdirSync(dir, { withFileTypes: true }).flatMap(entry => {
    const path = `${dir}/${entry.name}`;
    if (entry.name === '.git' || entry.name === 'node_modules') return [];
    return entry.isDirectory() ? pages(path) : path.endsWith('.html') ? [path] : [];
  });
}
test('default-off composition preserves every existing HTML byte', () => {
  assert.equal(shopLinkConfig({}), null);
  assert.equal(shopLinkConfig({ SHOP_LINK_ENABLED: '0', SHOP_LINK_URL: 'invalid' }), null);
  const files = pages('.');
  assert.ok(files.length > 600);
  for (const file of files) {
    const bytes = readFileSync(file);
    const result = composeShopLink(bytes, null, fragment, copy);
    assert.equal(result, bytes, file);
    assert.equal(hash(result), hash(bytes), file);
  }
});
test('pure renderer adds exactly one escaped footer link, never page noindex', () => {
  const html = '<html lang="en"><head><meta name="robots" content="index,follow"></head><body><footer>Credit</footer></body></html>';
  const result = composeShopLink(html, { url: 'https://example.invalid/?a=1&b=2' }, fragment, copy);
  assert.equal((result.match(/data-shop-link/g) || []).length, 1);
  assert.match(result, /rel="noopener nofollow"/);
  assert.match(result, /a=1&amp;b=2/);
  assert.match(result, /content="index,follow"/);
  assert.equal(result.includes('noindex'), false);
  assert.throws(() => composeShopLink(result, { url: 'https://example.invalid/' }, fragment, copy), /already present/);
});
test('enabled config fails before writes for missing or unsafe URL', () => {
  assert.throws(() => shopLinkConfig({ SHOP_LINK_ENABLED: '1' }), /required/);
  for (const url of ['invalid', 'http://example.invalid/', 'javascript:alert(1)', 'https://user:pass@example.invalid/']) {
    assert.throws(() => shopLinkConfig({ SHOP_LINK_ENABLED: '1', SHOP_LINK_URL: url }));
  }
});
test('missing copy and ambiguous footer fail closed', () => {
  assert.throws(() => composeShopLink('<footer></footer>', { url: 'https://example.invalid/' }, fragment, {}), /Missing/);
  assert.throws(() => composeShopLink('<body></body>', { url: 'https://example.invalid/' }, fragment, copy), /exactly one/);
});
