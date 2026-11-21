import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';

const source = readFileSync('analytics-init.js', 'utf8');
function setup(qa = false, hostname = 'marsharbel.com') {
  const listeners = {};
  const window = { __MARSHARBEL_QA__: qa };
  const document = { createElement: () => ({}), head: { appendChild() {} }, addEventListener(name, fn) { listeners[name] = fn; } };
  vm.runInNewContext(source, { window, document, location: { hostname, href: 'https://' + hostname + '/' }, URL });
  return { window, listeners, events: () => Array.from(window.dataLayer || []).filter(row => row[0] === 'event').map(row => [row[1], JSON.parse(JSON.stringify(row[2]))]) };
}
test('finite event names and no copied parameters or PII', () => {
  const s = setup();
  assert.equal(s.window.MarGrowth.event('daily_prayer_signup', 'email@example.invalid'), true);
  assert.equal(s.window.MarGrowth.event('testimony_submit', 'private story'), true);
  assert.equal(s.window.MarGrowth.event('unapproved', 'anything'), false);
  assert.equal(s.window.MarGrowth.event('share', 'email@example.invalid'), false);
  assert.deepEqual(s.events(), [['daily_prayer_signup', {}], ['testimony_submit', {}]]);
});
test('every existing share method once per explicitly reported action', () => {
  const s = setup();
  const methods = ['native', 'copy', 'facebook', 'x', 'whatsapp', 'telegram', 'viber', 'email', 'pinterest', 'line', 'vk'];
  for (const method of methods) assert.equal(s.window.MarGrowth.event('share', method), true);
  assert.deepEqual(s.events(), methods.map(method => ['share', { method }]));
});
test('QA flag suppresses all growth events even if flag becomes active later', () => {
  for (const qa of [true, { runner: 'QA' }]) {
    const s = setup(qa); s.window.MarGrowth.event('share', 'copy'); s.window.MarGrowth.event('testimony_submit'); assert.equal(s.events().length, 0);
  }
  const s = setup(); s.window.__MARSHARBEL_QA__ = true; s.window.MarGrowth.event('daily_prayer_signup'); assert.equal(s.events().length, 0);
});
test('exact YouTube hostname only, no URL/query/fragment transmission, once per click', () => {
  const s = setup();
  const click = (href, rest = {}) => s.listeners.click({ target: { closest: () => ({ href }) }, button: 0, ...rest });
  for (const href of ['https://youtube.com/watch?v=abc&private=not-sent', 'https://www.youtube.com/watch?v=x', 'https://m.youtube.com/watch?v=x', 'https://youtu.be/x']) click(href);
  assert.deepEqual(s.events(), Array.from({ length: 4 }, () => ['outbound_youtube', {}]));
  for (const href of ['https://youtube.com.evil.invalid/watch', 'https://notyoutube.com/', 'javascript:youtube.com', 'https://example.invalid/youtube.com']) click(href);
  click('https://youtube.com/', { defaultPrevented: true }); click('https://youtube.com/', { button: 2 });
  assert.equal(s.events().length, 4);
});
test('nonproduction hosts do not install growth tracking', () => { assert.equal(setup(false, 'localhost').window.MarGrowth, undefined); });
test('form hooks are downstream of confirmed accepted responses, never home draft navigation', () => {
  for (const [file, event, condition] of [['daily-prayer.js', 'daily_prayer_signup', 'if (result?.accepted !== true)'], ['submit-testimony.js', 'testimony_submit', 'if (result?.accepted !== true || !result.reference)']]) {
    const text = readFileSync(file, 'utf8');
    assert.ok(text.indexOf(condition) < text.indexOf("window.MarGrowth?.event('" + event + "')"));
    assert.equal(text.split("window.MarGrowth?.event('" + event + "')").length - 1, 1);
  }
  assert.equal(readFileSync('home-letter.js', 'utf8').includes("event('testimony_submit'"), false);
});
