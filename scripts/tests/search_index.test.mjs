import test from 'node:test';
import assert from 'node:assert/strict';
import { extract } from '../build-search-index.mjs';
import { mkdtemp, mkdir, copyFile, writeFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';

for (const [name, tag, want] of [
  ['apostrophe', `<meta name="description" content="The Church's prayer in Lebanon's mountains.">`, "The Church's prayer in Lebanon's mountains."],
  ['double quote', `<meta content='A "quiet" place for prayer.' name='description'>`, 'A "quiet" place for prayer.'],
  ['entities', `<meta name="description" content="The Church&#39;s &quot;prayer&quot; &amp; peace &gt; fear.">`, 'The Church\'s "prayer" & peace > fear.'],
]) {
  test(`description preserves ${name}`, () => {
    assert.equal(extract(`<html><head><title>Guide</title>${tag}</head><body><main>Prayer</main></body></html>`).desc, want);
  });
}
for (const [name, html] of [
  ['missing source', null],
  ['missing title', '<html><head></head><body>Prayer</body></html>'],
  ['noindex-reordered', '<html><head><title>Prayer</title><meta content="noindex" name="robots"></head><body>Prayer</body></html>'],
  ['noindex', '<html><head><title>Prayer</title><meta name="robots" content="noindex"></head><body>Prayer</body></html>'],
]) {
  test(`builder rejects unapproved sitemap skip: ${name}`, async () => {
    const root = await mkdtemp(path.join(tmpdir(), 'search-skip-'));
    try {
      await mkdir(path.join(root, 'scripts'));
      await copyFile(new URL('../build-search-index.mjs', import.meta.url), path.join(root, 'scripts/build-search-index.mjs'));
      await mkdir(path.join(root, 'search-index'));
      await copyFile(new URL('../../search-index/labels.json', import.meta.url), path.join(root, 'search-index/labels.json'));
      await writeFile(path.join(root, 'sitemap.xml'), '<urlset><url><loc>https://marsharbel.com/broken</loc></url></urlset>');
      if (html) await writeFile(path.join(root, 'broken.html'), html);
      for (const args of [[], ['--check']]) {
        const result = spawnSync(process.execPath, [path.join(root, 'scripts/build-search-index.mjs'), ...args], {encoding:'utf8'});
        assert.notEqual(result.status, 0);
        assert.match(result.stderr, /Unapproved sitemap skips: https:\/\/marsharbel.com\/broken/);
      }
    } finally { await rm(root, {recursive:true, force:true}); }
  });
}

test('check rejects stale excerpts even when URL coverage is unchanged', async () => {
  const root = await mkdtemp(path.join(tmpdir(), 'search-fidelity-'));
  try {
    await mkdir(path.join(root, 'scripts'));
    await copyFile(new URL('../build-search-index.mjs', import.meta.url), path.join(root, 'scripts/build-search-index.mjs'));
    await mkdir(path.join(root, 'search-index'));
    await copyFile(new URL('../../search-index/labels.json', import.meta.url), path.join(root, 'search-index/labels.json'));
    await writeFile(path.join(root, 'sitemap.xml'), '<urlset><url><loc>https://marsharbel.com/guide</loc></url></urlset>');
    await writeFile(path.join(root, 'guide.html'), `<html><head><title>Guide</title><meta name="description" content="The Church's prayer."></head><body><main>Prayer</main></body></html>`);
    const script = path.join(root, 'scripts/build-search-index.mjs');
    const run = args => spawnSync(process.execPath, [script, ...args], {encoding:'utf8'});
    assert.equal(run([]).status, 0);
    assert.equal(run(['--check']).status, 0);
    await writeFile(path.join(root, 'search-index/en.json'), JSON.stringify([['/guide', 'Guide', 'The Church', '', 'Prayer', 0.5]]));
    assert.notEqual(run(['--check']).status, 0);
  } finally { await rm(root, {recursive:true, force:true}); }
});
