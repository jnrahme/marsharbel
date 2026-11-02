#!/usr/bin/env node
// Fail-closed completeness/no-collision proof for the duration-balanced
// browser-quality shard lists in scripts/ci/bq-shards/.
//
// The --test-list selection design (identity = full title path + project)
// decides which tests each shard runs, so a stale or tampered list would
// silently drop browser coverage. This script collects the suite with
// `npx playwright test --list --reporter=json`, builds the canonical identity
// "[project] > file > describe... > title" for every collected test, then
// asserts the eight lists partition the collection:
//   (a) every collected test is selected by exactly one list line;
//   (b) every list line resolves to at least one collected test, and an
//       individual (fully-specified) entry to exactly one; suite-level
//       entries ("[project] > file") expand to all that file+project's tests;
//   (c) identities are unique in the collection itself.
// Any drift (renamed/added/removed test, describe restructure, edited line)
// fails the job with "regenerate the shard lists". No dependencies.
import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '../..');
const LIST_DIR = path.join(ROOT, 'scripts/ci/bq-shards');
const SHARDS = 8;
const SEP = '\u203A'; // Playwright accepts both ">" and the single-guillemet separator.

const fail = (msg) => {
  console.error(`[bq-shards] FAIL: ${msg}`);
  console.error('[bq-shards] regenerate the shard lists from a fresh collection (see scripts/ci/bq-shards header).');
  process.exit(1);
};

let collection;
try {
  const raw = execFileSync('npx', ['playwright', 'test', '--config', 'playwright.config.cjs', '--list', '--reporter=json'],
    { cwd: ROOT, encoding: 'utf8', maxBuffer: 64 * 1024 * 1024, stdio: ['ignore', 'pipe', 'inherit'] });
  collection = JSON.parse(raw);
} catch (err) {
  fail(`could not collect the test list: ${err.message}`);
}

// Canonical identity per collected test.
const tests = new Map(); // identity -> true (assert uniqueness)
const bySuitePrefix = new Map(); // "[project] SEP file" -> [identities]
const walk = (suite, prefix) => {
  const here = suite.title ? [...prefix, suite.title] : prefix;
  for (const spec of suite.specs || []) {
    const specPath = [...here, spec.title].join(` ${SEP} `);
    for (const test of spec.tests || []) {
      const project = test.projectName || 'default';
      const id = `[${project}] ${SEP} ${specPath}`;
      if (tests.has(id)) fail(`duplicate identity in collection: ${id}`);
      tests.set(id, true);
      // Suite-level list entries are file+project ("[project] > file.spec.js")
      // and expand to every collected test of that file in that project.
      const suiteKey = `[${project}] ${SEP} ${here[0]}`;
      if (!bySuitePrefix.has(suiteKey)) bySuitePrefix.set(suiteKey, []);
      bySuitePrefix.get(suiteKey).push(id);
    }
  }
  for (const child of suite.suites || []) walk(child, here);
};
for (const suite of collection.suites || []) walk(suite, []);

if (tests.size === 0) fail('collection is empty');

// Each list line selects identities; track coverage exactly-once.
const covered = new Map(); // identity -> shard number
let listLines = 0;
for (let k = 1; k <= SHARDS; k++) {
  const file = path.join(LIST_DIR, `shard-${k}.txt`);
  if (!fs.existsSync(file)) fail(`missing shard list ${file}`);
  for (const raw of fs.readFileSync(file, 'utf8').split('\n')) {
    const line = raw.trim();
    if (!line || line.startsWith('#')) continue;
    listLines++;
    let selected;
    if (tests.has(line)) {
      selected = [line];
    } else if (bySuitePrefix.has(line)) {
      selected = bySuitePrefix.get(line);
    } else {
      fail(`shard-${k}.txt line resolves to no collected test: ${line.slice(0, 140)}`);
    }
    for (const id of selected) {
      if (covered.has(id)) fail(`test selected by both shard ${covered.get(id)} and shard ${k}: ${id.slice(0, 140)}`);
      covered.set(id, k);
    }
  }
}

for (const id of tests.keys()) {
  if (!covered.has(id)) fail(`collected test not selected by any shard list: ${id.slice(0, 140)}`);
}

console.log(`[bq-shards] PASS: ${tests.size} collected tests partition across ${SHARDS} lists (${listLines} lines, disjoint, complete).`);
