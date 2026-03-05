#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const root = path.resolve(__dirname, '..');
const outRoot = path.join(root, 'manual-narration', 'full-audio-pack');
const rosaryOut = path.join(outRoot, 'rosary-en');
const storyOut = path.join(outRoot, 'storybook-en');

const context = { window: {} };
vm.createContext(context);
vm.runInContext(fs.readFileSync(path.join(root, 'mystery-data.js'), 'utf8'), context);
vm.runInContext(fs.readFileSync(path.join(root, 'mystery-library.js'), 'utf8'), context);

const mysteries = context.window.ROSARY_MYSTERIES || {};
const mysteryLibrary = context.window.ROSARY_MYSTERY_LIBRARY || {};

const orderedKeys = [
  'joyful_1', 'joyful_2', 'joyful_3', 'joyful_4', 'joyful_5',
  'luminous_1', 'luminous_2', 'luminous_3', 'luminous_4', 'luminous_5',
  'sorrowful_1', 'sorrowful_2', 'sorrowful_3', 'sorrowful_4', 'sorrowful_5',
  'glorious_1', 'glorious_2', 'glorious_3', 'glorious_4', 'glorious_5'
];

const normalizeReflectionText = value =>
  {
    let text = String(value || '')
      .replace(/^Pause(?:\s+for)?\s+[^.?!]*[.?!]\s*/i, '')
      .replace(/^(See|Picture|Watch|Imagine|Notice)\s+/i, 'Reflect on ')
      .replace(/^Hear\s+/i, 'Reflect on the words: ')
      .trim();

    const replacements = [
      [/\bJesus enter\b/g, 'Jesus enters'],
      [/\bJesus receive\b/g, 'Jesus receives'],
      [/\bJesus lead\b/g, 'Jesus leads'],
      [/\bJesus handed over\b/g, 'Jesus being handed over'],
      [/\bJesus stripped and nailed\b/g, 'Jesus being stripped and nailed'],
      [/\bGabriel arrive\b/g, 'Gabriel arriving'],
      [/\bHim ask\b/g, 'Jesus asks'],
      [/\bHim fall and rise\b/g, 'Jesus falls and rises'],
      [/\bHim entrust\b/g, 'Jesus entrusts'],
      [/\bHim cry\b/g, 'Jesus cries'],
      [/\bHim bow\b/g, 'Jesus bows'],
      [/\bHim bound\b/g, 'Jesus bound'],
      [/\bHim pray\b/g, 'Jesus prays'],
      [/\bsurrender His spirit\b/g, 'surrenders His spirit'],
      [/\bthe angel strengthen\b/g, 'the angel strengthens'],
      [/\bMary meet\b/g, 'Mary meets'],
      [/\bVeronica offer\b/g, 'Veronica offers'],
      [/\bHis face shine\b/g, 'His face shines'],
      [/\bthem press\b/g, 'soldiers press'],
      [/\bthe words:\s*Him\b/g, 'the words: Jesus']
    ];

    replacements.forEach(([pattern, next]) => {
      text = text.replace(pattern, next);
    });

    text = text
      .replace(/\bthe words:\s*the blows and feel the violence of sin\b/i, 'the words: the blows and the violence of sin')
      .replace(/\bReflect on soldiers mock\b/i, 'Reflect on soldiers mocking');

    return text;
  };

const storyVisualCues = {
  '01-a-boy-in-the-mountains.txt': 'Visualize snowy mountain air, a small village, and young Youssef quietly praying before dawn.',
  '02-he-chose-the-monastery.txt': 'Visualize Youssef walking toward Annaya at sunrise, leaving home with peace and courage.',
  '03-a-priest-of-the-altar.txt': 'Visualize Father Charbel at the altar, moving slowly and reverently during the liturgy.',
  '04-forty-three-years-of-monastic-life.txt': 'Visualize the hermitage at night, candlelight, silence, and steady prayer in solitude.',
  '05-his-final-mass.txt': 'Visualize the chapel in December, with deep stillness as he offers his final liturgy.',
  '06-hope-and-healing.txt': 'Visualize pilgrims arriving with tears and hope, lighting candles and praying at his tomb.',
  '07-a-saint-for-unity-in-christ.txt': 'Visualize people from many countries praying side by side in one spirit of faith.',
  '08-canonized-for-the-whole-church.txt': 'Visualize Saint Peter\'s Square as the Church proclaims his sainthood for the world.'
};

const cleanDir = dir => {
  if (fs.existsSync(dir)) {
    fs.rmSync(dir, { recursive: true, force: true });
  }
  fs.mkdirSync(dir, { recursive: true });
};

cleanDir(rosaryOut);
cleanDir(storyOut);

const rows = [['type', 'source_text_file', 'target_audio_path']];

for (const key of orderedKeys) {
  const mystery = mysteries[key];
  const details = mysteryLibrary[key] || {};
  if (!mystery || !Array.isArray(mystery.steps) || mystery.steps.length < 10) continue;

  const fruit = (mystery.fruit || 'the grace for this mystery').replace(/\.$/, '');
  const scriptureRef = details.readingTitle || 'Gospel reading';
  const scriptureText = details.reading || 'Remain in silence and attention before the Lord.';
  const stageTexts = [
    [
      `${mystery.title}.`,
      '',
      `Reflect on this mystery with attention.`,
      `Listen to the Gospel: ${scriptureRef}. ${scriptureText}`,
      `${details.explanation || 'Keep your heart attentive to what God reveals here.'}`,
      `Ask for ${fruit}.`
    ].join('\n'),
    [
      `Scripture reading: ${scriptureRef}.`,
      `${scriptureText}`,
      'Reflect on this Word in silence.',
      'Now pray one Our Father with attention.'
    ].join('\n')
  ];

  mystery.steps.forEach((stepText, i) => {
    stageTexts.push([
      `Meditation ${i + 1}. ${normalizeReflectionText(stepText)}`,
      'Speak to Christ now about what you need in this mystery.',
      `Ask for ${fruit}.`
    ].join('\n'));
  });

  stageTexts.push([
    'Remain in this scene with gratitude for this decade.',
    'Pray the Glory Be, and the Fatima prayer if desired.',
    'Then move to the next mystery with peace.'
  ].join('\n'));

  stageTexts.forEach((text, idx) => {
    const step = String(idx + 1).padStart(2, '0');
    const filename = `${key}-step-${step}.txt`;
    const rel = `rosary-en/${filename}`;
    fs.writeFileSync(path.join(rosaryOut, filename), `${text}\n`, 'utf8');
    rows.push(['rosary', rel, `media/rosary/${key}/step-${step}.mp3`]);
  });
}

const storySource = path.join(root, 'manual-narration', 'storybook-en');
const storyFiles = fs.readdirSync(storySource).filter(name => /^\d\d-.*\.txt$/.test(name)).sort();

for (const name of storyFiles) {
  const text = fs.readFileSync(path.join(storySource, name), 'utf8').trim();
  const cue = storyVisualCues[name] || 'Visualize the scene gently before reading this page.';
  const upgraded = `${text}\n\nAs you listen, picture this clearly: ${cue}\n`;
  fs.writeFileSync(path.join(storyOut, name), upgraded, 'utf8');
  const step = name.slice(0, 2);
  rows.push(['story', `storybook-en/${name}`, `media/storybook/en/page-${step}.mp3`]);
}

const toCsv = record => record.map(value => {
  const cell = String(value);
  return /[",\n]/.test(cell) ? `"${cell.replace(/"/g, '""')}"` : cell;
}).join(',');

fs.mkdirSync(outRoot, { recursive: true });
fs.writeFileSync(path.join(outRoot, 'master-file-map.csv'), `${rows.map(toCsv).join('\n')}\n`, 'utf8');

const readme = [
  '# Full Manual Narration Pack',
  '',
  'This pack contains one text file per audio clip with richer visualization guidance.',
  '',
  '## Counts',
  `- Rosary clips: ${rows.filter(r => r[0] === 'rosary').length}`,
  `- Story clips: ${rows.filter(r => r[0] === 'story').length}`,
  `- Total clips: ${rows.length - 1}`,
  '',
  '## How To Use',
  '1. Open a text file in ElevenLabs.',
  '2. Generate and export audio as mp3.',
  '3. Rename/move to the exact output path in master-file-map.csv.',
  '4. Repeat until all required clips are replaced.'
].join('\n');

fs.writeFileSync(path.join(outRoot, 'README.md'), `${readme}\n`, 'utf8');

console.log(`Built full narration pack with ${rows.length - 1} files.`);
