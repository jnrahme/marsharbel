const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const source = fs.readFileSync(path.join(__dirname, '../../stories-shelf.js'), 'utf8');

// Execute the actual shelf IIFE, including input events, card filtering and reset.
function shelf(script) {
  const labels = ['رفقا شربل لبنان', '玛利亚 圣人', 'นักบุญ ไทย', 'Thérèse Lisieux', 'रात', 'रत'];
  const cards = labels.map(text => ({textContent: text, hidden: false, getAttribute: () => text}));
  const section = {hidden: false, querySelectorAll: q => q === '.promo-card' ? cards : []};
  const events = {}, clearEvents = {};
  const input = {value: '', addEventListener: (name, fn) => { events[name] = fn; }, focus() {}};
  const count = {textContent: ''}, empty = {hidden: true};
  const tools = {hidden: true, dataset: {one: 'book', many: 'books', match: 'match', none: 'No matches'}};
  const clear = {addEventListener: (name, fn) => { clearEvents[name] = fn; }};
  const document = {
    querySelector: q => ({'[data-shelf-tools]': tools, '.shelf-jump': null, '[data-shelf-clear]': clear})[q],
    querySelectorAll: () => [section],
    getElementById: id => ({'shelf-q': input, 'shelf-count': count, 'shelf-empty': empty})[id]
  };
  vm.runInNewContext(script, {document, location: {search: ''}, URLSearchParams, Map});
  assert.equal(tools.hidden, false);
  return {
    query(q) {input.value = q; events.input(); return cards.filter(c => !c.hidden).length;},
    clear() {clearEvents.click(); return cards.filter(c => !c.hidden).length;},
    input, count, empty
  };
}
const queries = [['رفقا', 1], ['رِفْقَا', 1], ['شربل', 1], ['غيرموجود', 0], ['玛利亚', 1], ['นักบุญ', 1], ['therese', 1], ['रात', 1], ['रत', 1], ['', 6]];
const current = shelf(source);
for (const [query, expected] of queries) {
  assert.equal(current.query(query), expected, `query ${JSON.stringify(query)}`);
  assert.equal(current.empty.hidden, expected !== 0, 'empty state follows results');
}
assert.equal(current.clear(), 6, 'clear restores every card');
assert.equal(current.input.value, '');
// Negative control: the original Latin-only implementation must fail non-Latin cases.
const latinOnly = source.replace(/function fold\(s\) \{[\s\S]*?\n  \}/, `function fold(s) {
    return String(s).toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g, '').replace(/[^a-z0-9 ]+/g, ' ').replace(/\\s+/g, ' ');
  }`);
assert.notEqual(latinOnly, source, 'negative control replaced the production fold');
const old = shelf(latinOnly);
assert.equal(queries.filter(([query, expected]) => old.query(query) !== expected).length, 8, 'old script fails all eight non-Latin cases');
console.log('stories shelf Unicode: 10/10 queries, clear/empty state, 8 original-failure controls PASS');
