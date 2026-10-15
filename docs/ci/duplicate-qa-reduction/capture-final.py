from pathlib import Path
import subprocess,os,json,collections,hashlib,shlex,yaml,datetime
root=Path(os.environ.get('WORKTREE_ROOT', '.')).resolve();out=Path(os.environ.get('EVIDENCE_OUT', '/tmp/duplicate-qa-coverage'));out.mkdir(parents=True,exist_ok=True);base=os.environ.get('QA_EQUIVALENCE_BASE','136de2bd3507066d8f33af564fc49483eacae9fa');src=(root/'scripts/qa/run_full_qa.sh').read_text()
a=src.index('  local start end\n',src.index('qa_step() {'));b=src.index('\n}\nqa_report()',a)
src=src[:a]+'''  printf '%s\\0' "$idx" >> "$CAPTURE"
  printf '%s\\0' "$@" >> "$CAPTURE"
  printf '\\0' >> "$CAPTURE"'''+src[b:]
a=src.index('qa_report() {');b=src.index('\nqa_step ',a);src=src[:a]+src[b:];src=src.replace('ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"','ROOT='+str(root));script=out/'capture.sh';script.write_text(src)
def capture(name,args):
 f=out/(name+'.nul');f.write_bytes(b'');subprocess.run(['bash',str(script),*args],env={**os.environ,'CAPTURE':str(f)},check=True,stdout=subprocess.DEVNULL);rows=[]
 for item in f.read_bytes().split(b'\0\0'):
  if item:
   vals=item.strip(b'\0').decode().split('\0');rows.append({'index':int(vals[0]),'argv':vals[1:]})
 return rows
full=capture('unsharded',['--ci']);shards=[capture('shard'+str(i),['--ci','--shard',str(i)+'/8','--skip-i18n-test']) for i in range(8)];i18n=[r for r in full if r['argv']==['npm','run','i18n:test']];assert len(i18n)==1
union=sorted(sum(shards,[])+i18n,key=lambda x:x['index']);assert union==full
q=yaml.safe_load((root/'.github/workflows/qa.yml').read_text());b=yaml.safe_load((root/'.github/workflows/quality.yml').read_text());old=yaml.safe_load(subprocess.check_output(['git','show',base+':.github/workflows/deploy-stage.yml'],cwd=root,text=True))
gates=[{'name':s['name'],'run':s['run'],'if':s.get('if')} for s in q['jobs']['qa-gates']['steps'] if 'run' in s]
v=[s['run'] for s in gates if 'test_verify_deployment.py' in s['run']];oldv=[s['run'] for s in old['jobs']['qa']['steps'] if 'test_verify_deployment.py' in s.get('run','')];assert v==oldv
assert q['jobs']['qa']['needs']==['qa-shard','qa-gates','i18n-test'];assert '--skip-i18n-test' in next(s['run'] for s in q['jobs']['qa-shard']['steps'] if s.get('name')=='Run QA suite shard');assert next(s['run'] for s in q['jobs']['i18n-test']['steps'] if s.get('name')=='i18n unit tests')=='npm run i18n:test'
files=['.github/workflows/qa.yml','.github/workflows/quality.yml','.github/workflows/deploy-stage.yml','scripts/qa/run_full_qa.sh','scripts/qa/test_verify_deployment.py','scripts/qa/verify_deployment.py','package.json'];sources={}
for f in files:sources[f]={'base_blob':subprocess.check_output(['git','rev-parse',base+':'+f],cwd=root,text=True).strip(),'candidate_blob':subprocess.check_output(['git','hash-object',f],cwd=root,text=True).strip(),'sha256':hashlib.sha256((root/f).read_bytes()).hexdigest()}
x={'label':'DUPLICATE-QA REDUCTION ONLY; cancellation unchanged','observed_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'exact_base_sha':subprocess.check_output(['git','rev-parse',base],cwd=root,text=True).strip(),'exact_base_tree':subprocess.check_output(['git','rev-parse',base+'^{tree}'],cwd=root,text=True).strip(),'full':full,'shards':shards,'dedicated_i18n':i18n,'exact_union':union==full,'count':len(full),'coverage':[dict(r,coverage='i18n-test' if r in i18n else 'qa-shard (%s/8)'%(r['index']%8)) for r in full],'qa_gates':gates,'duplicate_verifier_unit_argv':v,'qa_aggregate_needs':q['jobs']['qa']['needs'],'browser_matrix':b['jobs']['browser-quality-shard']['strategy']['matrix'],'sources':sources,'limitations':'Selection and source equivalence only, not runtime passes. Final base is actual #817 squash. No historical d27 receipt used.'};(out/'post817-command-coverage.json').write_text(json.dumps(x,indent=2)+'\n');print('FINAL',x['exact_base_sha'],len(full),'commands,i18nindex',i18n[0]['index'],'exactunion',union==full,'verifieridentical',v==oldv)
