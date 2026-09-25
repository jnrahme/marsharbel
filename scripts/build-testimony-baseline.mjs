#!/usr/bin/env node
// Render the already-public, source-labeled baseline accounts into HTML so
// visitors and crawlers without JavaScript can read them. Never fetch or
// export private submissions or moderator data from the publishing system.
import {readFile,writeFile} from 'node:fs/promises';
const check=process.argv.includes('--check');
const root=new URL('../',import.meta.url);
const file=(name)=>new URL(name,root);
const catalog=JSON.parse(await readFile(file('locales/en/testimonies.json'),'utf8'));
const entries=catalog.entries;
if(!Array.isArray(entries)||!entries.length)throw new Error('Missing baseline accounts');
const escape=(s)=>String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;');
const card=(e)=>{
  if(!e.name||!e.meta||!e.text||!e.source||!e.url)throw new Error('Incomplete baseline account');
  const url=new URL(e.url);
  if(!['http:','https:'].includes(url.protocol))throw new Error('Invalid source URL');
  return `        <article class="card testimony-card"><p class="kicker">${escape(catalog.entryLabel)}</p><h3>${escape(e.name)}</h3><p class="source-meta">${escape(e.meta)}</p><p class="testimony-text">${escape(e.text)}</p><a href="${escape(url.href)}" target="_blank" rel="noopener noreferrer">${escape(e.source)}</a></article>`;
};
const start='<!-- baseline-testimonies:start -->', end='<!-- baseline-testimonies:end -->';
let html=await readFile(file('testimonies.html'),'utf8');
const original=html;
const metadata=[
  ['title',/<title>[^<]*<\/title>/g,`<title>${catalog.title}</title>`],
  ['description',/<meta name="description" content="[^"]*" \/>/g,`<meta name="description" content="${escape(catalog.description)}" />`],
  ['og-description',/<meta property="og:description" content="[^"]*" \/>/g,`<meta property="og:description" content="${escape(catalog.description)}" />`],
  ['twitter-description',/<meta name="twitter:description" content="[^"]*" \/>/g,`<meta name="twitter:description" content="${escape(catalog.description)}" />`],
  ['og-title',/<meta property="og:title" content="[^"]*" \/>/g,`<meta property="og:title" content="${catalog.title}" />`],
  ['twitter-title',/<meta name="twitter:title" content="[^"]*" \/>/g,`<meta name="twitter:title" content="${catalog.title}" />`],
  ['introduction',/(<h1>Testimonies<\/h1>\s*<p>)[^<]*(<\/p>)/,(_m,open,close)=>open+escape(catalog.introduction)+close],
  ['initial',/(<p id="testimony-empty" class="section-sub">)[^<]*(<\/p>)/,(_m,open,close)=>open+escape(catalog.readerInitial)+close],
];
for(const [key,pattern,replacement] of metadata){if(!pattern.test(html))throw new Error(`Missing ${key} in testimonies.html`);html=html.replace(pattern,replacement);}
const schemaRe=/(<script type="application\/ld\+json">\s*)(\{[\s\S]*?\})(\s*<\/script>)/;
if(!schemaRe.test(html))throw new Error('Missing WebPage schema');
html=html.replace(schemaRe,(_all,open,json,close)=>{const data=JSON.parse(json);if(data['@type']!=='WebPage')throw new Error('Unexpected schema');data.name=catalog.title;data.description=catalog.description;return open+JSON.stringify(data,null,2)+close;});
const begin=html.indexOf(start),finish=html.indexOf(end);
if(begin<0||finish<begin||html.indexOf(start,begin+1)>=0||html.indexOf(end,finish+1)>=0)throw new Error('Missing/duplicate baseline markers');
const next=html.slice(0,begin+start.length)+'\n        <h2>'+escape(catalog.archiveHeading)+'</h2>\n        <p class="section-sub">'+escape(catalog.archiveIntroduction)+'</p>\n        <div class="testimony-grid">\n'+entries.map(card).join('\n')+'\n        </div>\n      '+html.slice(finish);
const js='// Generated from locales/en/testimonies.json. Do not edit.\nwindow.TESTIMONY_COPY = '+JSON.stringify({readerUnavailable:catalog.readerUnavailable,readerSuccess:catalog.readerSuccess,readerError:catalog.readerError},null,2)+';\n';
const oldJs=await readFile(file('testimonies-copy.js'),'utf8').catch(()=>null);
if(check){if(oldJs!==js)throw new Error('testimonies-copy.js is stale');if(original!==next)throw new Error('Baseline HTML is stale. Run node scripts/build-testimony-baseline.mjs');console.log(`Baseline HTML is current: ${entries.length} source-published accounts`);}
else {if(original!==next)await writeFile(file('testimonies.html'),next);if(oldJs!==js)await writeFile(file('testimonies-copy.js'),js);console.log(`Rendered ${entries.length} accounts`);}
