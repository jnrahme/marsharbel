#!/usr/bin/env python3
"""Regenerate scripts/qa/shard-manifest.tsv: duration-weighted (LPT) assignment
of run_full_qa.sh steps to shards, from measured CI step timings.

Ground truth for the step inventory is the script itself:
    bash scripts/qa/run_full_qa.sh --list-steps            (149 slots)
    bash scripts/qa/run_full_qa.sh --list-steps --skip-i18n-test (148 runtime)

Usage: build_shard_manifest.py --timings-dir DIR [--out scripts/qa/shard-manifest.tsv]
DIR holds qa-step-timings TSVs ("seconds<TAB>[idx] command") downloaded from CI
artifacts (one per shard, any shard numbering). Every runtime step must have a
measured time; the generator fails closed listing any step that does not, so a
manifest is never written with a silently zero-weighted step. The i18n:test
slot (consumed but unexecuted under --skip-i18n-test) takes its time from the
dedicated i18n-test job, passed via --i18n-seconds.
"""
import argparse, subprocess, sys

SCRIPT = 'scripts/qa/run_full_qa.sh'

def list_steps(skip):
    out = subprocess.run(['bash', SCRIPT, '--list-steps'] + (['--skip-i18n-test'] if skip else []),
                         capture_output=True, text=True, check=True).stdout
    pairs = {}
    for line in out.splitlines():
        if '\t' not in line:
            continue  # echo progress lines, not steps
        idx, cmd = line.split('\t', 1)
        if not idx.isdigit():
            continue
        pairs[int(idx)] = cmd
    return pairs

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--timings-dir', required=True)
    ap.add_argument('--out', default='scripts/qa/shard-manifest.tsv')
    ap.add_argument('--shards', type=int, default=8)
    ap.add_argument('--i18n-seconds', type=int, required=True,
                    help='measured seconds of the dedicated i18n-test job (for the consumed slot)')
    args = ap.parse_args()

    full = list_steps(False)
    skip = list_steps(True)
    consumed = sorted(set(full) - set(skip))
    if len(consumed) != 1 or full[consumed[0]] != 'npm run i18n:test':
        sys.exit(f'expected exactly one consumed slot (npm run i18n:test), got {consumed}')

    import glob, re
    times = {}
    for f in glob.glob(args.timings_dir.rstrip('/') + '/*'):
        for line in open(f):
            parts = line.rstrip('\n').split('\t', 1)
            if len(parts) != 2:
                continue
            m = re.match(r'\[(\d+)\] (.*)', parts[1])
            if m and parts[0].isdigit():
                times[int(m.group(1))] = (int(parts[0]), m.group(2))

    missing = [i for i in skip if i not in times]
    if missing:
        sys.exit('no measured time for runtime steps: ' + ', '.join(f'{i} ({skip[i][:50]})' for i in missing))
    wrong = [i for i in skip if times[i][1] != skip[i]]
    if wrong:
        sys.exit('timing rows disagree with runtime commands at indices: ' + ', '.join(map(str, wrong)))

    weights = {i: times[i][0] for i in skip}
    weights[consumed[0]] = args.i18n_seconds

    # LPT: heaviest first, ties by index; assign to the currently lightest bin.
    bins = [[] for _ in range(args.shards)]
    loads = [0] * args.shards
    for idx in sorted(full, key=lambda i: (-weights[i], i)):
        b = loads.index(min(loads))
        bins[b].append(idx)
        loads[b] += weights[idx]

    rows = []
    for shard, idxs in enumerate(bins):
        for idx in sorted(idxs):
            rows.append(f'{idx}\t{shard}\t{weights[idx]}\t{full[idx]}')
    header = ('# step_index<TAB>shard<TAB>est_seconds<TAB>command - duration-weighted (LPT) from CI step\n'
              '# timings; regenerate with scripts/qa/build_shard_manifest.py from fresh artifacts.\n'
              '# run_full_qa.sh --shard K/N fails closed if this file is missing, incomplete, or N differs.\n')
    with open(args.out, 'w') as fh:
        fh.write(header + '\n'.join(rows) + '\n')
    print('wrote', args.out)
    print('loads (est seconds per shard):', loads, 'max/min:', max(loads), '/', min(loads))

if __name__ == '__main__':
    main()
