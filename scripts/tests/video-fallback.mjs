import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {renderVideoFallback} from '../lib/video-fallback.mjs';
const copy = JSON.parse(await readFile('locales/en/video-playback.json', 'utf8'));
const html = renderVideoFallback(copy, 'tF8SYCuYKBE', './saint-charbel-encyclopedia');
// Reel-card copy shares the policy catalog but is not player-fallback output.
const reelKeys = new Set(['video.reelHeading', 'video.reelSub', 'video.reelBody', 'video.reelCta']);
const fallbackKeys = new Set(['video.original', 'video.read', 'video.help', 'video.unavailable', 'video.restricted', 'video.referrer', 'video.generic']);
assert.deepEqual(new Set(Object.keys(copy)), new Set([...fallbackKeys, ...reelKeys]));
for (const key of fallbackKeys) assert.ok(html.includes(copy[key].replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('"','&quot;')), key);
for (const key of reelKeys) assert.ok(typeof copy[key] === 'string' && copy[key].trim(), key);
assert.ok(html.includes('role="status"'));
assert.ok(html.includes('https://www.youtube.com/watch?v=tF8SYCuYKBE'));
assert.throws(() => renderVideoFallback(copy, 'bad', './visit-annaya'));
assert.throws(() => renderVideoFallback(copy, 'tF8SYCuYKBE', 'https://attacker.invalid'));
assert.throws(() => renderVideoFallback(copy, 'tF8SYCuYKBE', './bad" onclick="x'));
const escaped = renderVideoFallback({...copy, 'video.help':'<script>&"'}, 'tF8SYCuYKBE', './visit-annaya');
assert.ok(escaped.includes('&lt;script>&amp;&quot;'));
console.log('Video fallback catalog, escaping, source-link and invalid-target contracts passed.');
