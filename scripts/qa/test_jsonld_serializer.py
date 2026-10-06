"""Characterize the shared JSON-LD serializers against committed served HTML."""
import os
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class JsonLdSerializerTest(unittest.TestCase):
    def check_serialized_bytes(self, tamper=False):
        result = subprocess.run(
            ['node', '--input-type=module', '-'], cwd=ROOT,
            input=r'''
import assert from 'node:assert/strict';
import { readFileSync, readdirSync } from 'node:fs';
import { renderWebPage, renderWebPageArticle, renderWebPageAudience, renderFaq } from './scripts/lib/jsonld.mjs';
const escapeText = value => String(value).replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;');
function resolveCopy(source) {
  return source.replace(/\{\{copy ([a-z0-9-]+) ([a-zA-Z0-9.-]+)\}\}/g, (_, name, key) => {
    const copy = JSON.parse(readFileSync(`locales/en/${name}-copy.json`, 'utf8')).copy;
    assert.ok(Object.hasOwn(copy, key), `missing ${name} copy key: ${key}`);
    return escapeText(copy[key]);
  });
}
assert.equal(escapeText('A & <B> "C"'), 'A &amp; &lt;B&gt; &quot;C&quot;');
assert.throws(() => resolveCopy('{{copy prayer-errata missing-key}}'), /missing.*copy key/);
let count = 0, audienceCount = 0;
for (const file of readdirSync('src/pages').filter(f => f.endsWith('.html'))) {
  const source = resolveCopy(readFileSync(`src/pages/${file}`, 'utf8'));
  const marker = source.match(/\{\{> ld-webpage-article((?: "(?:[^"\\]|\\.)*")*)\}\}/);
  const audienceMarker = source.match(/\{\{> ld-webpage-audience((?: "(?:[^"\\]|\\.)*")*)\}\}/);
  if (!marker && !audienceMarker) continue;
  const args = [...(marker || audienceMarker)[1].matchAll(/ "((?:[^"\\]|\\.)*)"/g)].map(m => m[1]);
  const served = readFileSync(file, 'utf8').replace(process.env.SERIALIZER_TEETH === '1' ? /twenty-nine invocations/g : /$^/, 'tampered invocations');
  const blocks = [...served.matchAll(/<script type="application\/ld\+json">\n[\s\S]*?\n  <\/script>/g)];
  const block = blocks.find(m => JSON.parse(m[0].replace(/^.*?\n|\n  <\/script>$/g, ''))['@type'] === 'WebPage');
  assert.ok(block, `${file}: missing WebPage`);
  assert.equal((marker ? renderWebPageArticle : renderWebPageAudience)(args), block[0], `${file}: serialized bytes changed`);
  if (marker) count++; else audienceCount++;
}
assert.ok(count >= 47, `expected at least 47 characterized articles; got ${count}`);
assert.ok(audienceCount >= 18, `expected at least 18 characterized audiences; got ${audienceCount}`);

// Characterize every new long-tail include against the exact served block.
const fragments = Object.fromEntries(['ld-person', 'ld-place', 'ld-video', 'ld-webpage-plain'].map(name =>
  [name, readFileSync(`partials/fragments/${name}.html`, 'utf8').replace(/\n$/, '')]));
let longTail = 0;
for (const file of readdirSync('src/pages').filter(f => f.endsWith('.html'))) {
  const source = resolveCopy(readFileSync(`src/pages/${file}`, 'utf8'));
  const served = readFileSync(file, 'utf8').replace(process.env.SERIALIZER_TEETH === '1' ? /twenty-nine invocations/g : /$^/, 'tampered invocations');
  for (const marker of source.matchAll(/\{\{> (ld-person|ld-place|ld-video|ld-webpage-plain|ld-webpage-article-modified)((?: "(?:[^"\\]|\\.)*")*)\}\}/g)) {
    const args = [...marker[2].matchAll(/ "((?:[^"\\]|\\.)*)"/g)].map(m => m[1]);
    const rendered = marker[1] === 'ld-webpage-article-modified'
      ? renderWebPageArticle(args.slice(1), args[0])
      : fragments[marker[1]].replace(/\{\{(\d+)\}\}/g, (_, i) => args[Number(i) - 1]);
    assert.ok(served.includes(rendered), `${file}: ${marker[1]} changed bytes`);
    longTail++;
  }
}
assert.equal(longTail, 30);
assert.throws(() => renderWebPageAudience([]), /needs language/);
const audienceArgs = ['en', 'Children', '6', '12', 'n', 'd', 'u', 'Home', '/'];
for (const ages of [['12', '6'], ['-1', '12'], ['6.5', '12'], ['6', 'NaN'], ['06', '12']]) {
  assert.throws(() => renderWebPageAudience([...audienceArgs.slice(0, 2), ...ages, ...audienceArgs.slice(4)]), /integer ages/);
}
assert.throws(() => renderWebPageArticle([]), /needs headline/);
assert.throws(() => renderWebPage(['n', 'd', 'u']), /breadcrumb/);
assert.throws(() => renderWebPage(['n', 'd', 'u', 'odd']), /breadcrumb/);
assert.throws(() => renderFaq([]), /question\/answer/);
assert.throws(() => renderFaq(['odd']), /question\/answer/);
const escaped = renderWebPageArticle(['He said \\"hello\\"', 'image', 'date', 'name', 'description', 'url', 'home', '/']);
assert.ok(escaped.includes('He said \\"hello\\"'));
console.log(`${count} article and ${audienceCount} audience serializers matched served bytes; boundary cases passed.`);
''',
            text=True, capture_output=True,
            env={**os.environ, 'SERIALIZER_TEETH': '1' if tamper else '0'},
        )
        return result

    def test_article_bytes_and_invalid_inputs(self):
        result = self.check_serialized_bytes()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_changed_schema_is_still_rejected(self):
        result = self.check_serialized_bytes(tamper=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('serialized bytes changed', result.stdout + result.stderr)


if __name__ == '__main__':
    unittest.main()
