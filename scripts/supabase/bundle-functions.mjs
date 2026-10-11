// Inlines _shared imports into each edge function for dashboard (single-file) deploys.
// Usage: node scripts/supabase/bundle-functions.mjs -> writes /tmp/fn-dist/<function>.ts
import { readFileSync, writeFileSync, mkdirSync, readdirSync } from 'node:fs';
import { join } from 'node:path';

const root = new URL('../../supabase/functions/', import.meta.url).pathname;
const out = '/tmp/fn-dist';
mkdirSync(out, { recursive: true });
const shared = Object.fromEntries(readdirSync(join(root, '_shared')).map(name => [name, readFileSync(join(root, '_shared', name), 'utf8')]));

for (const dir of readdirSync(root)) {
  if (dir === '_shared') continue;
  const file = join(root, dir, 'index.ts');
  let source;
  try { source = readFileSync(file, 'utf8'); } catch { continue; }
  const imported = [];
  source = source.replace(/import\s+(?:type\s+)?([^'"]+?)\s+from\s+'\.\.\/_shared\/([^']+)';?\n/g, (_m, names, mod) => {
    imported.push(mod);
    return `// inlined from _shared/${mod}: ${names.trim()}\n`;
  });
  let preamble = '';
  for (const mod of new Set(imported)) {
    let code = shared[mod];
    if (!code) throw new Error(`missing shared module ${mod}`);
    code = code
      .replace(/^import[^\n]*\n/gm, '')
      .replace(/^export\s+(async\s+)?(function|const|interface|type)/gm, (_m, a, k) => `${a || ''}${k}`)
      .trim();
    preamble += `\n// ===== begin _shared/${mod} =====\n${code}\n// ===== end _shared/${mod} =====\n`;
  }
  writeFileSync(join(out, `${dir}.ts`), preamble + '\n' + source);
  console.log(`${dir}.ts (${imported.join(', ') || 'no shared imports'})`);
}
