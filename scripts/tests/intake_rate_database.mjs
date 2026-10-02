import {PGlite} from '@electric-sql/pglite';
import {readFile} from 'node:fs/promises';
import assert from 'node:assert/strict';
const db=new PGlite();
await db.exec('create role anon;create role authenticated;create role service_role;');
const migration=await readFile('supabase/migrations/202610020002_intake_rate_limits.sql','utf8');
await db.exec(migration);await db.exec(migration);
const hash='a'.repeat(64);
for(let i=0;i<30;i++)assert.equal((await db.query('select testimony_check_intake_rate($1) allowed',[hash])).rows[0].allowed,true);
assert.equal((await db.query('select testimony_check_intake_rate($1) allowed',[hash])).rows[0].allowed,false);
assert.equal((await db.query('select testimony_check_intake_rate($1) allowed',['b'.repeat(64)])).rows[0].allowed,true);
await db.exec("insert into testimony_intake_rates values(repeat('c',64),0,1)");
await db.query('select testimony_check_intake_rate($1)',['b'.repeat(64)]);
assert.equal((await db.query('select count(*)::int n from testimony_intake_rates where window_start=0')).rows[0].n,0);
for(const role of ['anon','authenticated']){
 assert.equal((await db.query('select has_function_privilege($1,\'testimony_check_intake_rate(text)\',\'EXECUTE\') allowed',[role])).rows[0].allowed,false);
 await db.exec('set role '+role);await assert.rejects(()=>db.query('select * from testimony_intake_rates'),/permission denied/);await db.exec('reset role');
}
assert.equal((await db.query("select has_function_privilege('service_role','testimony_check_intake_rate(text)','EXECUTE') allowed")).rows[0].allowed,true);
await assert.rejects(()=>db.query('select testimony_check_intake_rate($1)',['raw-address']),/invalid_hash/);
await db.close();console.log('Persistent limiter: burst, independent buckets, TTL cleanup, idempotent migration, server-only RPC and no public rows pass.');
