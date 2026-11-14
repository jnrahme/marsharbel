#!/usr/bin/env python3
"""Fail-closed semantics of the stage deploy admission snapshot.

The admission script lives as a heredoc inside .github/workflows/deploy-stage.yml
(written to $RUNNER_TEMP at job start). These tests EXTRACT that real body from
the workflow at test time - never a copy - and drive snapshot() with scripted
API fakes and a controlled clock. Scenarios locked to the observed 2026-10-23
failure (QA run 39905156534 completed between the run and attempt reads;
admission job 120255315789 hard-failed at 05:26:24Z on a healthy pipeline):

  transient mid-transition pair  -> bounded Pending retry, then admits
  changed attempt                -> still fails closed
  stable pair mismatch           -> fails closed after the grace is exhausted
  terminal failure conclusion    -> still fails closed
  exhaustion                     -> the retry allowance is per-run and bounded
"""
import importlib.util, json, re, tempfile, types, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WF = ROOT / '.github/workflows/deploy-stage.yml'
SHA = 'a' * 40
TREE = 'b' * 40
REPO = 'jnrahme/marsharbel'
QA_WID = 241818046


def load_admission():
    text = WF.read_text()
    # The marker appears twice: the admission job writes the heredoc and the
    # publication job re-extracts it from the checked-out workflow file.
    assert text.count("<<'ADMISSION_PY'") == 2, 'admission heredoc markers changed'
    body = text.split("<<'ADMISSION_PY'\n", 1)[1].split('\n          ADMISSION_PY', 1)[0]
    lines = body.split('\n')
    assert all(l.startswith(' ' * 10) or not l.strip() for l in lines), 'unexpected heredoc indent'
    source = '\n'.join(l[10:] for l in lines)
    tmp = Path(tempfile.mkdtemp()) / 'admission.py'
    tmp.write_text(source)
    spec = importlib.util.spec_from_file_location('admission_under_test', tmp)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_record(run_id, attempt, status, conclusion, wid=QA_WID, path='.github/workflows/qa.yml'):
    return {'id': run_id, 'run_attempt': attempt, 'workflow_id': wid, 'path': path,
            'repository': {'full_name': REPO}, 'head_repository': {'full_name': REPO},
            'head_sha': SHA, 'head_branch': 'stage', 'event': 'push',
            'head_commit': {'id': SHA, 'tree_id': TREE},
            'html_url': f'https://github.com/{REPO}/actions/runs/{run_id}',
            'status': status, 'conclusion': conclusion}


def job_record(run_id, attempt, job_id, name, conclusion='success'):
    return {'id': job_id, 'run_id': run_id, 'run_attempt': attempt, 'name': name,
            'head_sha': SHA, 'head_branch': 'stage', 'status': 'completed',
            'conclusion': conclusion,
            'html_url': f'https://github.com/{REPO}/actions/runs/{run_id}/job/{job_id}'}


class FakeAPI:
    """Scripted reads. current_script/attempt_script are lists of (status, conclusion)
    consumed one per read; the last entry repeats."""

    def __init__(self, current_script, attempt_script, job_names=('qa',), latest_attempt=1):
        self.current_script = list(current_script)
        self.attempt_script = list(attempt_script)
        self.job_names = list(job_names)
        self.latest_attempt = latest_attempt
        self.run_id = 9001

    def _next(self, script):
        return script.pop(0) if len(script) > 1 else script[0]

    def get(self, path):
        if path.startswith('/actions/workflows/'):
            p = '.github/workflows/' + path.rsplit('/', 1)[1]
            return {'id': QA_WID, 'path': p, 'state': 'active'}
        m = re.fullmatch(r'/actions/runs/(\d+)', path)
        if m:
            status, conclusion = self._next(self.current_script)
            return run_record(self.run_id, self.latest_attempt, status, conclusion)
        m = re.fullmatch(r'/actions/runs/(\d+)/attempts/(\d+)', path)
        if m:
            status, conclusion = self._next(self.attempt_script)
            return run_record(self.run_id, int(m.group(2)), status, conclusion)
        raise AssertionError('unexpected get ' + path)

    def pages(self, path, key):
        if key == 'workflow_runs':
            return [run_record(self.run_id, self.latest_attempt, 'in_progress', None)]
        if key == 'jobs':
            return [job_record(self.run_id, self.latest_attempt, 7000 + i, n) for i, n in enumerate(self.job_names)]
        raise AssertionError('unexpected pages ' + path)


def expected():
    return {'repo': REPO, 'sha': SHA, 'tree': TREE,
            'sources': {'.github/workflows/qa.yml': {'blob': 'c' * 40}}}


class FakeTime:
    def __init__(self):
        self.now = 1000.0

    def monotonic(self):
        return self.now

    def sleep(self, seconds):
        self.now += seconds


class AdmissionSnapshot(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.adm = load_admission()

    def setUp(self):
        # Single-workflow, single-job world: snapshot logic under test, not workflow constants.
        self.adm.WORKFLOWS = {'.github/workflows/qa.yml': ['qa']}
        self.clock = FakeTime()
        self._real_time = self.adm.time
        self.adm.time = self.clock
        # Each snapshot gets a fresh settle budget.
        self.adm.settle_first_seen = {}

    def tearDown(self):
        self.adm.time = self._real_time

    def test_transient_mid_transition_pair_retries_then_admits(self):
        # The observed failure: run read in_progress, attempt read completed/success.
        api = FakeAPI(current_script=[('in_progress', None), ('completed', 'success')],
                      attempt_script=[('completed', 'success')])
        with self.assertRaises(self.adm.Pending, msg='mid-transition pair must retry, not hard-fail'):
            self.adm.snapshot(api, expected())
        # The retry window re-reads; consistent records admit with full identity.
        self.adm.settle_first_seen = {}
        result = self.adm.snapshot(api, expected())
        self.assertEqual(result[0]['run_id'], 9001)
        self.assertEqual(result[0]['attempt'], 1)
        self.assertEqual([j['name'] for j in result[0]['jobs']], ['qa'])

    def test_changed_attempt_still_fails_closed(self):
        api = FakeAPI(current_script=[('completed', 'success')], attempt_script=[('completed', 'success')],
                      latest_attempt=2)
        # Listing/current say attempt 2; force the current record to read attempt 1.
        original_get = api.get
        def stale_current(path):
            record = original_get(path)
            if re.fullmatch(r'/actions/runs/\d+', path):
                record['run_attempt'] = 1
            return record
        api.get = stale_current
        with self.assertRaises(self.adm.Closed) as ctx:
            self.adm.snapshot(api, expected())
        self.assertIn('attempt moved backwards', str(ctx.exception))

    def test_stable_pair_mismatch_exhausts_grace_then_fails_closed(self):
        api = FakeAPI(current_script=[('in_progress', None)], attempt_script=[('completed', 'success')])
        # First mismatch consumes into the grace window -> Pending...
        with self.assertRaises(self.adm.Pending):
            self.adm.snapshot(api, expected())
        # ...but a pair that NEVER stabilises outlives the bounded allowance.
        self.clock.now += self.adm.SETTLE_GRACE_SECONDS + 1
        with self.assertRaises(self.adm.Closed) as ctx:
            self.adm.snapshot(api, expected())
        self.assertIn('attempt changed during read', str(ctx.exception))

    def test_terminal_failure_still_fails_closed(self):
        api = FakeAPI(current_script=[('completed', 'failure')], attempt_script=[('completed', 'failure')])
        with self.assertRaises(self.adm.Closed) as ctx:
            self.adm.snapshot(api, expected())
        self.assertIn('dependency not successful', str(ctx.exception))

    def test_grace_allowance_is_bounded_and_per_run(self):
        api = FakeAPI(current_script=[('in_progress', None)], attempt_script=[('completed', 'success')])
        # Repeated mismatches inside the window keep retrying (bounded by the clock)...
        for _ in range(3):
            with self.assertRaises(self.adm.Pending):
                self.adm.snapshot(api, expected())
            self.clock.now += 60
        # ...and the allowance is still the single shared per-run budget.
        self.assertIn(9001, self.adm.settle_first_seen)
        self.clock.now += self.adm.SETTLE_GRACE_SECONDS + 1
        with self.assertRaises(self.adm.Closed):
            self.adm.snapshot(api, expected())


if __name__ == '__main__':
    unittest.main()
