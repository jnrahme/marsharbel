import collections,copy,importlib.util,json,os,subprocess,sys,tempfile,time,types,unittest
from pathlib import Path
from unittest.mock import patch
import yaml
W=Path(os.environ.get('WORKFLOW_PATH', '.github/workflows/deploy-stage.yml')).resolve()
workflow=yaml.safe_load(W.read_text())
run=workflow['jobs']['qa']['steps'][1]['run']
script=run.split("<<'ADMISSION_PY'\n",1)[1].split('\nADMISSION_PY\n',1)[0]+'\n'
P=Path(tempfile.mkdtemp(prefix='admission-test-'))/'actual-embedded.py';P.write_text(script)
spec=importlib.util.spec_from_file_location('embedded',P);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
REPO='jnrahme/marsharbel';SHA='a'*40;TREE='b'*40
EXPECTED={'repo':REPO,'sha':SHA,'tree':TREE,'sources':{p:{'blob':'c'*40,'sha256':'d'*64} for p in m.SOURCE_PATHS}}

def make_run(path,ident=20,attempt=1,status='completed',conclusion='success'):
 return {'id':ident,'run_attempt':attempt,'workflow_id':m.WORKFLOW_IDS[path],'path':path,'repository':{'full_name':REPO},'head_repository':{'full_name':REPO},'head_sha':SHA,'head_branch':'stage','event':'push','head_commit':{'id':SHA,'tree_id':TREE},'html_url':f'https://github.com/{REPO}/actions/runs/{ident}','status':status,'conclusion':conclusion}
def make_jobs(run):
 return [{'id':1000+k,'name':name,'run_id':run['id'],'run_attempt':run['run_attempt'],'head_sha':SHA,'head_branch':'stage','status':'completed','conclusion':'success','html_url':run['html_url']+'/job/'+str(1000+k)} for k,name in enumerate(m.WORKFLOWS[run['path']])]
class Fixture(m.API):
 def __init__(self):
  self.repo=REPO;self.deadline=time.monotonic()+120;self.runs={};self.current={};self.attempt={};self.jobs={};self.metadata={};self.head=SHA;self.compare={'status':'ahead','ahead_by':1};self.calls=[]
  for k,path in enumerate(m.WORKFLOWS):
   r=make_run(path,20+k);self.runs[path]=[r];self.current[r['id']]=copy.deepcopy(r);self.attempt[(r['id'],1)]=copy.deepcopy(r);self.jobs[(r['id'],1)]=make_jobs(r);self.metadata[path]={'id':m.WORKFLOW_IDS[path],'path':path,'state':'active'}
 def get(self,path):
  from urllib.parse import urlsplit,parse_qs
  self.calls.append(path);split=urlsplit(path);s=split.path;query=parse_qs(split.query);page=int(query.get('page',['1'])[0])
  if s=='/git/ref/heads/stage':return {'object':{'sha':self.head}}
  if s.startswith('/compare/'):return self.compare
  if s.startswith('/commits/'):return {'sha':SHA,'commit':{'tree':{'sha':TREE}}}
  if s.startswith('/actions/workflows/'):
   tail=s[len('/actions/workflows/'):]
   if not tail.endswith('/runs'):
    return copy.deepcopy(next(v for p,v in self.metadata.items() if p.endswith('/'+tail)))
   wid=int(tail.split('/')[0]);key=next(p for p,x in m.WORKFLOW_IDS.items() if x==wid);r=self.runs[key];return {'total_count':len(r),'workflow_runs':copy.deepcopy(r[(page-1)*100:page*100])}
  parts=s.strip('/').split('/');rid=int(parts[2])
  if len(parts)==3:return copy.deepcopy(self.current[rid])
  attempt=int(parts[4])
  if len(parts)==5:return copy.deepcopy(self.attempt[(rid,attempt)])
  rows=self.jobs[(rid,attempt)];return {'total_count':len(rows),'jobs':copy.deepcopy(rows[(page-1)*100:page*100])}

class EmbeddedTests(unittest.TestCase):
 def setUp(self):self.a=Fixture();self.path=list(m.WORKFLOWS)[0];self.rid=20
 def test_happy_snapshot_real_job_names(self):
  x=m.stable(self.a,EXPECTED);self.assertEqual([len(r['jobs']) for r in x],[11,9]);self.assertTrue(any('/attempts/1/jobs' in x for x in self.a.calls))
 def test_all_terminal_run_conclusions(self):
  for state in ['failure','skipped','cancelled','timed_out','neutral','action_required','stale',None,'unknown']:
   with self.subTest(state=state):
    a=Fixture();a.current[20]['conclusion']=a.attempt[20,1]['conclusion']=state
    with self.assertRaises(m.Closed):m.snapshot(a,EXPECTED)
 def test_all_pending_run_states(self):
  for state in ['queued','in_progress','waiting','requested','pending']:
   with self.subTest(state=state):
    a=Fixture();a.current[20].update(status=state,conclusion=None);a.attempt[20,1]=copy.deepcopy(a.current[20])
    with self.assertRaises(m.Pending):m.snapshot(a,EXPECTED)
 def test_all_job_states_fail_closed(self):
  for state in ['failure','skipped','cancelled','timed_out','neutral',None,'unknown']:
   with self.subTest(state=state):
    a=Fixture();a.jobs[20,1][0]['conclusion']=state
    with self.assertRaises(m.Closed):m.snapshot(a,EXPECTED)
 def test_wrong_run_identities(self):
  for field,value in [('workflow_id',1),('path','.github/workflows/7-quality.yml'),('repository',{'full_name':'fork/repo'}),('head_repository',{'full_name':'fork/repo'}),('head_sha','d'*40),('head_commit',{'id':SHA,'tree_id':'e'*40}),('html_url','https://wrong'),('run_attempt',0),('id',None)]:
   with self.subTest(field=field):
    a=Fixture();a.runs[self.path][0][field]=value
    with self.assertRaises(m.Closed):m.snapshot(a,EXPECTED)
 def test_wrong_event_branch_are_never_admitted(self):
  for field,value in [('event','pull_request'),('head_branch','main')]:
   a=Fixture();a.runs[self.path][0][field]=value
   with self.assertRaises(m.Pending):m.snapshot(a,EXPECTED)
 def test_wrong_current_or_attempt_identity(self):
  for which in ['current','attempt']:
   for field,value in [('id',99),('run_attempt',2),('head_sha','f'*40),('head_commit',{'id':SHA,'tree_id':'f'*40}),('event','pull_request'),('head_branch','main')]:
    with self.subTest(which=which,field=field):
     a=Fixture();(a.current[20] if which=='current' else a.attempt[20,1])[field]=value
     with self.assertRaises(Exception):m.snapshot(a,EXPECTED)
 def test_wrong_workflow_same_display_name(self):
  for field,value in [('path','.github/workflows/7-quality.yml'),('id',361787275),('state','disabled_manually')]:
   a=Fixture();a.metadata[self.path][field]=value
   with self.assertRaises(Exception):m.snapshot(a,EXPECTED)
 def test_jobs_missing_duplicate_mixed_attempt_wrong_identity(self):
  changes=[lambda j:j.pop(),lambda j:j.append(copy.deepcopy(j[0])),lambda j:j[0].update(id=j[1]['id']),lambda j:j[0].update(name=j[1]['name']),lambda j:j[0].update(run_attempt=2),lambda j:j[0].update(head_sha='b'*40),lambda j:j[0].update(run_id=99),lambda j:j[0].update(head_branch='main'),lambda j:j[0].update(html_url='https://wrong')]
  for change in changes:
   a=Fixture();change(a.jobs[20,1])
   with self.assertRaises(Exception):m.snapshot(a,EXPECTED)
 def test_missing_dependency(self):
  self.a.runs[self.path]=[]
  with self.assertRaises(m.Pending):m.snapshot(self.a,EXPECTED)
 def add_later(self,a,status,conclusion):
  r=make_run(self.path,22,status=status,conclusion=conclusion);a.runs[self.path].append(r);a.current[22]=copy.deepcopy(r);a.attempt[22,1]=copy.deepcopy(r);a.jobs[22,1]=make_jobs(r)
 def test_coherent_older_run_returned_by_selected_url_rejected(self):
  older=make_run(self.path,19)
  self.a.current[20]=copy.deepcopy(older)
  self.a.attempt[19,1]=copy.deepcopy(older)
  self.a.jobs[19,1]=make_jobs(older)
  # Every alternative lookup is coherent and successful. Rejection must be
  # the explicit selected/current ID predicate, not a KeyError downstream.
  with self.assertRaisesRegex(m.Closed,'current run ID differs from selected latest run'):
   m.snapshot(self.a,EXPECTED)
  self.assertFalse(any('/runs/19/attempts/' in p for p in self.a.calls))
  with self.assertRaisesRegex(m.Closed,'current run ID differs from selected latest run'):
   m.stable(self.a,EXPECTED)
 def test_latest_selected_before_status(self):
  for state,conclusion in [('queued',None),('completed','failure'),('completed','success')]:
   a=Fixture();self.add_later(a,state,conclusion)
   if conclusion=='success':self.assertEqual(m.snapshot(a,EXPECTED)[0]['run_id'],22)
   else:
    with self.assertRaises(m.Closed):m.snapshot(a,EXPECTED)
 def test_newer_pending_or_failed_attempt_blocks_old_success(self):
  for state,conclusion in [('in_progress',None),('completed','failure'),('completed','success')]:
   a=Fixture();a.current[20].update(run_attempt=2,status=state,conclusion=conclusion);a.attempt[20,2]=copy.deepcopy(a.current[20]);a.jobs[20,2]=make_jobs(a.current[20])
   if conclusion=='success':self.assertEqual(m.snapshot(a,EXPECTED)[0]['attempt'],2)
   else:
    with self.assertRaises(m.Closed):m.snapshot(a,EXPECTED)
 def test_partial_rerun_must_rerun_all_jobs(self):
  a=self.a;a.current[20]['run_attempt']=2;a.attempt[20,2]=copy.deepcopy(a.current[20]);a.jobs[20,2]=make_jobs(a.current[20])[0:1]
  with self.assertRaisesRegex(m.Closed,'rerun all jobs'):m.snapshot(a,EXPECTED)
 def test_current_attempt_race(self):
  self.a.current[20]['run_attempt']=2
  self.a.attempt[20,2]=copy.deepcopy(self.a.current[20]);self.a.attempt[20,2]['status']='in_progress'
  with self.assertRaises(m.Closed):m.snapshot(self.a,EXPECTED)
 def test_between_snapshots_race(self):
  get=self.a.get;n=[0]
  def race(path):
   if path.startswith('/actions/workflows/qa.yml'):
    n[0]+=1
    if n[0]==2:self.add_later(self.a,'completed','success')
   return get(path)
  self.a.get=race
  with self.assertRaisesRegex(m.Closed,'changed during admission'):m.stable(self.a,EXPECTED)
 def test_stage_supersession_only_confirmed_newer(self):
  self.a.head='f'*40
  with self.assertRaises(m.Superseded):m.current_stage(self.a,SHA)
  for value in [{'status':'diverged','ahead_by':1},{'status':'ahead','ahead_by':0},{}, {'status':'ahead','ahead_by':'1'}]:
   self.a.compare=value
   with self.assertRaises(m.Closed) as c:m.current_stage(self.a,SHA)
   self.assertNotIsInstance(c.exception,m.Superseded)
  self.a.head=None
  with self.assertRaises(m.Closed):m.current_stage(self.a,SHA)
 def test_source_tree_sha_blob_scope_identity(self):
  def g(*a):return SHA if a==('rev-parse','HEAD') else TREE if a==('rev-parse','HEAD^{tree}') else 'c'*40
  with patch.object(m,'git',side_effect=g),patch.object(m.Path,'read_bytes',return_value=b'x'):
   x=m.source_identity(self.a,REPO,SHA);self.assertEqual(x['tree'],TREE);self.assertEqual(x['sources'][self.path]['blob'],'c'*40)
  with patch.object(m,'git',return_value='f'*40):
   with self.assertRaises(m.Closed):m.source_identity(self.a,REPO,SHA)
 def test_pagination_101_results(self):
  r=self.a.runs[self.path][0];self.a.runs[self.path]=[{**r,'id':i+1} for i in range(101)]
  x=self.a.pages('/actions/workflows/241818046/runs?head_sha='+SHA,'workflow_runs');self.assertEqual(len(x),101);self.assertTrue(any('page=2' in s for s in self.a.calls))
 def test_pagination_truncation_duplicate_missing_malformed(self):
  for val in [{'total_count':1000,'jobs':[]},{'total_count':1001,'jobs':[]},{'total_count':2,'jobs':[{'id':1}]},{'total_count':2,'jobs':[{'id':1},{'id':1}]},{'total_count':'0','jobs':[]},{'total_count':0,'jobs':None},{'total_count':1,'jobs':[{}]},{'total_count':0,'jobs':[{'id':1}]}]:
   a=m.API(REPO,time.monotonic()+60)
   with patch.object(a,'get',return_value=val):
    with self.assertRaises(m.Closed):a.pages('/x','jobs')
 def test_page_count_changed(self):
  a=m.API(REPO,time.monotonic()+60)
  with patch.object(a,'get',side_effect=[{'total_count':101,'jobs':[{'id':i+1} for i in range(100)]},{'total_count':102,'jobs':[{'id':101},{'id':102}]}]):
   with self.assertRaises(m.Closed):a.pages('/x','jobs')
 def test_pagination_jobs_101_and_999_runs(self):
  for key,count in [('jobs',101),('workflow_runs',999)]:
   a=m.API(REPO,time.monotonic()+60);calls=[]
   def get(path):
    import urllib.parse
    page=int(urllib.parse.parse_qs(urllib.parse.urlsplit(path).query)['page'][0]);calls.append(page)
    return {'total_count':count,key:[{'id':i+1} for i in range((page-1)*100,min(page*100,count))]}
   with patch.object(a,'get',side_effect=get):self.assertEqual(len(a.pages('/x',key)),count)
   self.assertEqual(calls,list(range(1,(count+99)//100+1)))
 def test_run_list_duplicates_malformed_and_zero_count(self):
  a=self.a;a.runs[self.path].append(copy.deepcopy(a.runs[self.path][0]))
  with self.assertRaises(m.Closed):m.snapshot(a,EXPECTED)
  a=m.API(REPO,time.monotonic()+60)
  for raw in [{},[],{'total_count':1,'jobs':[None]},{'total_count':1,'jobs':[{'id':True}]}]:
   with patch.object(a,'get',return_value=raw):
    with self.assertRaises(Exception):a.pages('/x','jobs')
 def test_post_successful_new_attempt_still_new_evidence(self):
  def rerun(a):
   a.current[20]['run_attempt']=2;a.attempt[20,2]=copy.deepcopy(a.current[20]);a.jobs[20,2]=make_jobs(a.current[20])
  rc,x=self.main_scan(mutation=rerun);self.assertEqual(rc,1);self.assertEqual(x['publication'],'unverified')
 def test_post_api_error_never_superseded(self):
  def error(a):
   def get(_):raise m.Closed('HTTP401 read access refused')
   a.get=get
  rc,x=self.main_scan(mutation=error);self.assertEqual(rc,1);self.assertEqual(x['publication'],'unverified')
 def test_source_identity_rejects_wrong_tree_and_dirty_blob(self):
  def g(*args):
   if args==('rev-parse','HEAD'):return SHA
   if args==('rev-parse','HEAD^{tree}'):return TREE
   if args[0]=='hash-object':return 'e'*40
   return 'c'*40
  with patch.object(m,'git',side_effect=g),patch.object(m.Path,'read_bytes',return_value=b'x'):
   with self.assertRaisesRegex(m.Closed,'source blob mismatch'):m.source_identity(self.a,REPO,SHA)
  with patch.object(m,'git',side_effect=lambda *args:SHA if args==('rev-parse','HEAD') else 'e'*40):
   with self.assertRaisesRegex(m.Closed,'tree mismatch'):m.source_identity(self.a,REPO,SHA)
 def test_network_fail_auth_malformed_timeout(self):
  a=m.API(REPO,time.monotonic()+30)
  for result in [subprocess.CompletedProcess([],22,'','401'),subprocess.CompletedProcess([],0,'not json',''),subprocess.TimeoutExpired([],1)]:
   with patch.dict(os.environ,GH_TOKEN='fixture'),patch.object(m.subprocess,'run',side_effect=result if isinstance(result,Exception) else None,return_value=result):
    with self.assertRaises(m.Closed):a.get('/x')
  a.deadline=time.monotonic()-1
  with self.assertRaises(m.Closed):a.get('/x')
 def test_curl_has_hard_deadline_and_token_only_stdin(self):
  a=m.API(REPO,time.monotonic()+30)
  with patch.dict(os.environ,GH_TOKEN='fixture'),patch.object(m.subprocess,'run',return_value=subprocess.CompletedProcess([],0,'{}','')) as call:
   self.assertEqual(a.get('/x'),{});args=call.call_args;self.assertNotIn('fixture',str(args.args));self.assertIn('max-time',args.kwargs['input']);self.assertLessEqual(args.kwargs['timeout'],16)
 def main_scan(self,mutation=None,exit_code=0,pre_mutation=None):
  a=Fixture();deps=m.stable(a,EXPECTED);env={'GITHUB_REPOSITORY':REPO,'PUSH_SHA':SHA,'GITHUB_RUN_ID':'500','GITHUB_RUN_ATTEMPT':'1'}
  with tempfile.TemporaryDirectory() as d:
   admission={'identity':EXPECTED,'dependencies':deps,'admission':'success','run_id':'500','run_attempt':'1'}
   if pre_mutation:pre_mutation(admission,a)
   Path(d,'admission.json').write_text(json.dumps(admission))
   def scan(*args,**kwargs):
    if mutation:mutation(a)
    return subprocess.CompletedProcess([],exit_code)
   fake=types.SimpleNamespace(frontend_files=lambda _:[])
   with patch.dict(os.environ,env),patch.object(m,'API',return_value=a),patch.object(m,'source_identity',return_value=EXPECTED),patch.dict(sys.modules,verify_deployment=fake),patch.object(m.subprocess,'run',side_effect=scan):rc=m.main('scan',d)
   return rc,json.loads(Path(d,'publication.json').read_text())
 def test_scan_success_and_failure(self):
  rc,x=self.main_scan();self.assertEqual(rc,0);self.assertEqual(x['publication'],'verified-existing-scope')
  rc,x=self.main_scan(exit_code=1);self.assertEqual(rc,1);self.assertEqual(x['publication'],'unverified')
 def test_scan_pre_post_attempt_run_blob_races(self):
  for mutation in [lambda a:self.add_later(a,'completed','success'),lambda a:a.current[20].update(run_attempt=2),lambda a:a.current[20].update(conclusion='failure')]:
   rc,x=self.main_scan(mutation=mutation);self.assertEqual(rc,1);self.assertEqual(x['publication'],'unverified')
  for change in [lambda r,a:r['identity']['sources'][self.path].update(blob='WRONG'),lambda r,a:r.update(run_attempt='2'),lambda r,a:self.add_later(a,'completed','success')]:
   # source object must not share identity with the admitted fixture during mutation
   rc,x=self.main_scan(pre_mutation=lambda r,a:(r.update(identity=copy.deepcopy(r['identity'])),change(r,a)));self.assertEqual(rc,1);self.assertEqual(x['publication'],'unverified')
 def test_scan_post_stage_superseded_vs_unreadable(self):
  rc,x=self.main_scan(mutation=lambda a:setattr(a,'head','f'*40));self.assertEqual(rc,1);self.assertEqual(x['publication'],'superseded/unverified')
  rc,x=self.main_scan(mutation=lambda a:setattr(a,'head',None));self.assertEqual(rc,1);self.assertEqual(x['publication'],'unverified')
 def test_abc_supersession_actual_main(self):
  # At A's post-scan check, stage advances to C. A gets no publication;
  # B's pending run likewise cannot borrow a success from A or C.
  rc,x=self.main_scan(mutation=lambda a:setattr(a,'head','c'*40));self.assertEqual(x['publication'],'superseded/unverified')
  b=copy.deepcopy(EXPECTED);b['sha']='b'*40
  with self.assertRaises(m.Closed):m.snapshot(Fixture(),b)
  self.assertEqual(self.main_scan()[1]['publication'],'verified-existing-scope')
 def test_verifier_timeout_record(self):
  def boom(a):raise subprocess.TimeoutExpired('verifier',720)
  rc,x=self.main_scan(mutation=boom);self.assertEqual(rc,1);self.assertEqual(x['publication'],'unverified')
 def test_wait_pending_is_bounded_and_error_closed(self):
  env={'GITHUB_REPOSITORY':REPO,'PUSH_SHA':SHA,'GITHUB_RUN_ID':'500','GITHUB_RUN_ATTEMPT':'1'}
  with tempfile.TemporaryDirectory() as d,patch.dict(os.environ,env),patch.object(m,'API',return_value=self.a),patch.object(m,'source_identity',return_value=EXPECTED),patch.object(m,'stable',side_effect=m.Pending('wait')),patch.object(m.time,'monotonic',side_effect=[0,2690]):
   self.assertEqual(m.main('wait',d),1);self.assertEqual(json.loads(Path(d,'admission.json').read_text())['publication'],'unverified')
 def test_all_scripts_compile_and_artifact_source_exact(self):
  for job in workflow['jobs'].values():
   for step in job['steps']:
    s=step.get('run','')
    if "<<'PY'\n" in s:
     block=s.split("<<'PY'\n",1)[1].rsplit('\nPY',1)[0];compile(block,'inline','exec')
  # Run actual source-validation step against exact extracted code.
  with tempfile.TemporaryDirectory() as d:
   Path(d,'stage-admission').mkdir();Path(d,'stage-admission/admission.py').write_text(script)
   validate=workflow['jobs']['verify-deployment']['steps'][2]['run']
   res=subprocess.run(['bash','-c',validate],cwd=W.parents[2],env={**os.environ,'RUNNER_TEMP':d},capture_output=True,text=True);self.assertEqual(res.returncode,0,res.stderr)
   Path(d,'stage-admission/admission.py').write_text(script+'#tamper')
   res=subprocess.run(['bash','-c',validate],cwd=W.parents[2],env={**os.environ,'RUNNER_TEMP':d},capture_output=True,text=True);self.assertNotEqual(res.returncode,0)

if __name__=='__main__':unittest.main(verbosity=2)
