import test from 'node:test';
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
const core = createRequire(import.meta.url)('../../search-core.js');

const rows = [
  ['/saint-charbel-prayer-for-healing', 'Prayer for Healing - Saint Charbel', 'A prayer asking Saint Charbel to intercede for healing.', 'Prayer for Healing · How to pray', 'Pray with trust. Saint Charbel healed many sick people at Annaya.', 0.8],
  ['/saint-charbel-novena', 'Saint Charbel Novena', 'Nine days of prayer.', 'Day one · Day two', 'Begin the novena on the 15th. Healing and peace.', 0.9],
  ['/annaya-tour', 'Annaya Tour', 'Visit the hermitage and tomb.', 'Hermitage', 'Walk to the hermitage above the monastery.', 0.7],
];
const idx = core.prepare(rows);

test('title match outranks body match', () => {
  const r = core.search(idx, 'healing');
  assert.equal(r[0].doc.url, '/saint-charbel-prayer-for-healing');
  assert.equal(r.length, 2);
});
test('every token must match', () => {
  assert.equal(core.search(idx, 'healing hermitage').length, 0);
  assert.equal(core.search(idx, 'novena healing')[0].doc.url, '/saint-charbel-novena');
});
test('accents, case and sharp s fold', () => {
  assert.equal(core.fold('Ärger Straße ŁÓDŹ Café'), 'arger strasse lodz cafe');
});
test('arabic diacritics, alef forms and ta marbuta fold', () => {
  assert.equal(core.fold('صَلاةٌ'), core.fold('صلاه'));
  assert.equal(core.fold('أنطونيوس'), core.fold('انطونيوس'));
});
test('indic combining signs are kept', () => {
  assert.notEqual(core.fold('प्रार्थना'), core.fold('प्रारथना'));
  assert.ok(core.fold('प्रार्थना').includes('\u094d'));
});
test('one typo is tolerated on longer words', () => {
  assert.equal(core.search(idx, 'hermitge')[0].doc.url, '/annaya-tour');
});
test('short query is ignored, single han char allowed', () => {
  assert.equal(core.search(idx, 'a').length, 0);
  const zh = core.prepare([['/zh', '圣沙贝尔祈祷', '', '', '治愈', 0.5]]);
  assert.equal(core.search(zh, '祈').length, 1);
  assert.equal(core.search(zh, '祈祷').length, 1);
});
test('thai substring matches without spaces', () => {
  const th = core.prepare([['/th', 'คำอธิษฐานนักบุญชาร์เบล', '', '', '', 0.5]]);
  assert.equal(core.search(th, 'อธิษฐาน').length, 1);
});
test('snippet maps highlight ranges to the original text', () => {
  const r = core.search(idx, 'sick')[0];
  const s = core.snippet(r.doc, r.tokens, 80);
  assert.ok(s.ranges.length >= 1);
  assert.equal(s.text.slice(s.ranges[0][0], s.ranges[0][1]).toLowerCase(), 'sick');
});
test('snippet ranges survive folded characters', () => {
  const d = core.prepare([['/x', 'Straße', 'Die Straße zur Einsiedelei führt über Fußwege.', '', '', 0.5]])[0];
  const s = core.snippet(d, ['strasse'], 80);
  assert.equal(s.text.slice(s.ranges[0][0], s.ranges[0][1]), 'Straße');
});
test('priority breaks ties', () => {
  const a = core.prepare([['/a', 'Prayer', '', '', '', 0.5], ['/b', 'Prayer', '', '', '', 0.9]]);
  assert.equal(core.search(a, 'prayer')[0].doc.url, '/b');
});
test('empty and punctuation-only queries return nothing', () => {
  assert.equal(core.search(idx, '').length, 0);
  assert.equal(core.search(idx, '  ?! ').length, 0);
});
