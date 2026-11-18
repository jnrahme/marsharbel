#!/usr/bin/env node
// Seeds content/saint-of-day.json from the reviewed saint-of-day manifest (locales/saint-of-day.json),
// which the saint lane maintains and reviews per batch. Freshness-gated: the manifest must carry an
// entry for today in its own timezone, so a stale manifest fails --check in CI instead of letting
// /api/v1/saints/today answer 404 on the live date while the route stays advertised.
import { readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..', '..');

export function build(now = new Date()) {
  const manifest = JSON.parse(readFileSync(join(ROOT, 'locales/saint-of-day.json'), 'utf8'));
  const tz = manifest.timezone || 'America/New_York';
  const today = new Intl.DateTimeFormat('en-CA', { timeZone: tz, year: 'numeric', month: '2-digit', day: '2-digit' }).format(now);
  const entries = manifest.entries || {};
  if (!entries[today]) {
    throw new Error(`stale saint manifest: no entry for ${today} (${tz}); extend locales/saint-of-day.json first`);
  }
  return { schema: 1, source: 'locales/saint-of-day.json', timezone: tz, entries };
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const check = process.argv.includes('--check');
  const path = join(ROOT, 'content', 'saint-of-day.json');
  let body = null;
  try {
    body = JSON.stringify(build(), null, 2) + '\n';
  } catch (e) {
    console.error(e.message);
    process.exitCode = 1;
  }
  if (body !== null) {
    if (check) {
      let current = null;
      try { current = readFileSync(path, 'utf8'); } catch { /* missing file is stale */ }
      if (current !== body) { console.error(`stale: ${path}`); process.exitCode = 1; }
    } else {
      writeFileSync(path, body);
    }
  }
  if (!process.exitCode) console.log(check ? 'saint-of-day seed checked' : 'saint-of-day seed written');
}
