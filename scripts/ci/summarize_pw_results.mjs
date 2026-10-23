#!/usr/bin/env node
// Summarizes Playwright's built-in JSON report into a slowest-first per-spec
// duration table (milliseconds, retry attempts included). Instrumentation only:
// reads output/playwright/pw-results.json, writes a TSV next to it, prints the
// top rows, and mirrors them to GITHUB_STEP_SUMMARY when set. No dependencies.
import fs from 'node:fs';
import path from 'node:path';

const input = process.argv[2] || 'output/playwright/pw-results.json';
const out = process.argv[3] || 'output/playwright/pw-spec-timings.tsv';

if (!fs.existsSync(input)) {
  console.log(`[pw-timings] no JSON report at ${input}`);
  process.exit(0);
}

const report = JSON.parse(fs.readFileSync(input, 'utf8'));
const rows = [];
const walk = (suite) => {
  for (const spec of suite.specs || []) {
    const file = spec.file || suite.file || '';
    for (const test of spec.tests || []) {
      const ms = (test.results || []).reduce((acc, r) => acc + (r.duration || 0), 0);
      rows.push([ms, `${file} > ${spec.title} [${test.projectName || 'default'}]`]);
    }
  }
  for (const child of suite.suites || []) walk(child);
};
for (const suite of report.suites || []) walk(suite);

rows.sort((a, b) => b[0] - a[0]);
const body = rows.map(([ms, name]) => `${ms}\t${name}`).join('\n') + '\n';
fs.mkdirSync(path.dirname(out), { recursive: true });
fs.writeFileSync(out, body);

console.log(`[pw-timings] per-spec durations (ms, slowest first, ${rows.length} rows, retries included):`);
for (const [ms, name] of rows.slice(0, 40)) console.log(`  ${ms}\t${name}`);

if (process.env.GITHUB_STEP_SUMMARY) {
  const top = rows.slice(0, 60).map(([ms, n]) => `${ms}\t${n}`).join('\n');
  fs.appendFileSync(
    process.env.GITHUB_STEP_SUMMARY,
    `### Playwright per-spec durations (ms, retries included)\n\`\`\`\n${top}\n\`\`\`\n`
  );
}
