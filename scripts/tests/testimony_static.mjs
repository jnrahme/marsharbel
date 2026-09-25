import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
const root=new URL('../../',import.meta.url);
const html=await readFile(new URL('testimonies.html',root),'utf8');
const entries=JSON.parse(await readFile(new URL('locales/en/testimonies.json',root),'utf8')).entries;
const staticBlock=html.split('<!-- baseline-testimonies:start -->')[1]?.split('<!-- baseline-testimonies:end -->')[0];
assert.ok(staticBlock,'static baseline markers');
assert.ok(staticBlock.includes('<div class="testimony-grid">'),'cards keep grid layout');
assert.equal((staticBlock.match(/<article\b/g)||[]).length,entries.length);
for(const entry of entries){assert.ok(staticBlock.includes(entry.name),`missing account ${entry.name}`);assert.ok(staticBlock.includes(entry.url),`missing source ${entry.name}`);}
assert.ok(html.includes('id="reader-testimony-list"'),'dynamic submissions remain separate');
assert.ok(html.includes('testimonies.js'),'moderated archive code still loads');
assert.ok(!html.includes('<script src="testimonies-baseline.js"'),'static accounts do not render twice');
assert.ok(!/^I (?:suffered|stopped|had|am)\b/m.test(entries.map(e=>e.text).join('\n')),'no invented first-person historical voice');
console.log(`${entries.length} baseline accounts rendered once as source-attributed static HTML; dynamic submissions remain separate`);
