// XSS probes for the testimony surface: (1) no HTML-injection sinks in testimony client code,
// (2) hostile published rows render as inert text in a real browser.
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import http from 'node:http';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright';
const root = path.resolve(fileURLToPath(new URL('../../', import.meta.url)));

// 1. Static sink scan.
const files = ['testimony-client.js', 'testimonies.js', 'testimony-admin.js', 'submit-testimony.js', 'account.js'];
const sinks = [/\.innerHTML\b/, /\.outerHTML\b/, /insertAdjacentHTML/, /document\.write/, /\beval\s*\(/, /new Function\s*\(/, /setTimeout\s*\(\s*['"`]/, /\.srcdoc\b/];
for (const file of files) {
  const source = await readFile(path.join(root, file), 'utf8');
  for (const sink of sinks) assert.ok(!sink.test(source), `${file} uses banned HTML sink ${sink}`);
}

// 2. Browser probe with hostile rows from the (mocked) published table.
const hostile = [
  '<img src=x onerror="window.__xss=1">', '<script>window.__xss=2</script>', '"><svg onload="window.__xss=3">',
  'javascript:window.__xss=4', '<a href="javascript:window.__xss=5">click</a>', '</textarea><iframe srcdoc="<script>parent.__xss=6</script>">'
];
const types = { '.html': 'text/html', '.js': 'application/javascript', '.css': 'text/css' };
const server = http.createServer(async (req, res) => {
  let p = decodeURIComponent(new URL(req.url, 'http://x').pathname); if (p === '/') p = '/index.html';
  const file = path.join(root, p); if (!file.startsWith(root)) { res.writeHead(403).end(); return; }
  try { const body = await readFile(file); res.writeHead(200, { 'content-type': types[path.extname(file)] || 'application/octet-stream' }).end(body); }
  catch { res.writeHead(404).end(); }
}).listen(0, '127.0.0.1');
await new Promise(r => server.once('listening', r));
const base = `http://127.0.0.1:${server.address().port}`;
const browser = await chromium.launch();
try {
  const page = await browser.newPage({ serviceWorkers: 'block' });
  const dialogs = []; page.on('dialog', d => { dialogs.push(d.message()); d.dismiss(); });
  // The jsdelivr script is mocked, so its SRI digest cannot match; strip integrity from documents only in this run.
  await page.route(u => u.href.startsWith(base), async r => { if (r.request().resourceType() !== 'document') return r.fallback(); const resp = await r.fetch(); await r.fulfill({ response: resp, body: (await resp.text()).replace(/\sintegrity="sha384-[^"]+"/g, '') }); });
  await page.route('**/testimony-config.js*', r => r.fulfill({ contentType: 'application/javascript', body: "window.TESTIMONY_CONFIG={supabaseUrl:'https://test.supabase.co',supabaseAnonKey:'public-key',accountsEnabled:true,submissionsEnabled:true,moderationEnabled:true,moderatorMfaRequired:true};" }));
  await page.route('**/cdn.jsdelivr.net/**', r => r.fulfill({ contentType: 'application/javascript', body: `
    const rows=${JSON.stringify(hostile.map((s, i) => ({ id: 'row' + i, display_name: s, story: s + ' ' + s, country: s, event_date: '2020-01-01', published_at: '2026-01-01', label: s })))};
    window.supabase={createClient:()=>({auth:{getSession:async()=>({data:{session:null}}),getUser:async()=>({data:{user:null}}),onAuthStateChange:()=>{}},
      from(){const c={select(){return c},order(){return c},range(){return c},eq(){return c},limit(){return c},then(ok){return Promise.resolve({data:rows,error:null}).then(ok)}};return c},
      rpc:async()=>({data:null,error:null})})};` }));
  await page.route(u => !u.href.startsWith(base) && !/test\.supabase\.co|cdn\.jsdelivr/.test(u.href), r => r.abort());
  await page.goto(`${base}/testimonies.html`, { waitUntil: 'load' });
  await page.waitForSelector('#reader-testimony-list article', { timeout: 10000 });
  const result = await page.evaluate(() => {
    const list = document.getElementById('reader-testimony-list');
    return { cards: list.querySelectorAll('article').length, injected: list.querySelectorAll('img,script,svg,iframe,object,embed,a[href^="javascript"]').length,
      onAttrs: [...list.querySelectorAll('*')].filter(e => [...e.attributes].some(a => /^on/i.test(a.name))).length, flag: window.__xss ?? null, text: list.textContent };
  });
  assert.equal(result.cards, hostile.length);
  assert.equal(result.injected, 0, 'hostile markup must not become elements');
  assert.equal(result.onAttrs, 0, 'no inline handler attributes');
  assert.equal(result.flag, null, 'no payload executed');
  assert.equal(dialogs.length, 0, 'no dialogs');
  assert.ok(result.text.includes('<img src=x onerror='), 'payload shown as literal text');
} finally { await browser.close(); server.close(); }
console.log('Testimony XSS probes passed: no HTML sinks in client code; hostile rows render as inert text.');
