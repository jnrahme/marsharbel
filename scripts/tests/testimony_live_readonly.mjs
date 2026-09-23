import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import vm from 'node:vm';
const context={window:{}};
vm.runInNewContext(await readFile('testimony-config.js','utf8'),context);
const config=context.window.TESTIMONY_CONFIG;
assert.ok(config.supabaseUrl&&config.supabaseAnonKey,'Public project configuration is required');
const headers={apikey:config.supabaseAnonKey};
async function get(path){const response=await fetch(config.supabaseUrl+path,{headers,signal:AbortSignal.timeout(15000)});return {status:response.status,body:await response.json()};}
const publications=await get('/rest/v1/testimony_publications?select=id&limit=1');
assert.equal(publications.status,200);assert.ok(Array.isArray(publications.body));
for(const table of ['testimony_submissions','testimony_controls','testimony_audit','testimony_budgets','testimony_reports']){
 const result=await get(`/rest/v1/${table}?select=*&limit=1`);
 assert.ok([401,403].includes(result.status),`Anonymous access to ${table} must be denied`);
 assert.equal(result.body.code,'42501');
}
const auth=await get('/auth/v1/settings');assert.equal(auth.status,200);assert.equal(auth.body.mailer_autoconfirm,false);
console.log('Live read-only checks passed: public publication reads, anonymous denial on all five private tables, and email confirmation. No accounts or stories were created.');
