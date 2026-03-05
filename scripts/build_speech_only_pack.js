#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');
const srcDir = path.join(root, 'manual-narration', 'full-audio-pack', 'rosary-en');
const outDir = path.join(root, 'manual-narration', 'full-audio-pack', 'rosary-en-speech-only');

const files = fs.readdirSync(srcDir).filter(f => f.endsWith('.txt')).sort();
fs.rmSync(outDir, { recursive: true, force: true });
fs.mkdirSync(outDir, { recursive: true });

for (const file of files) {
  const src = fs.readFileSync(path.join(srcDir, file), 'utf8');
  const mysteryTitlePattern = /^(First|Second|Third|Fourth|Fifth)\s+(Joyful|Sorrowful|Glorious|Luminous)\s+Mystery\s*-\s*/i;
  const lines = src
    .split(/\r?\n/)
    .map(line => line.trim())
    .filter(Boolean)
    .filter(line => !mysteryTitlePattern.test(line))
    .filter(line => !/^Stage\s*:/i.test(line))
    .filter(line => !/^Scripture\s*focus\s*:/i.test(line))
    .filter(line => !/^Scripture\s*reading\s*:/i.test(line))
    .filter(line => !/^Place\s*cue\s*:/i.test(line))
    .filter(line => !/^Picture\s+the\s+place\s*:/i.test(line))
    .filter(line => !/^Visual\s*direction\s*:/i.test(line))
    .filter(line => !/^Visual\s*focus\s*:/i.test(line))
    .filter(line => !/^Prayer\s*cue\s*:/i.test(line))
    .filter(line => !/^##\s*STEP/i.test(line))
    .filter(line => !/^---+$/.test(line));

  const text = lines.join('\n\n').replace(/\n{3,}/g, '\n\n').trim() + '\n';
  fs.writeFileSync(path.join(outDir, file), text, 'utf8');
}

console.log(`Built speech-only files: ${files.length}`);
