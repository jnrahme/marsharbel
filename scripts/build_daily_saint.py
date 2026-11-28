#!/usr/bin/env python3
"""Daily-card entrypoint: preserve history before home pruning, then build both."""
import argparse,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
from build_saint_day_archive import merge_daily_history,output
from i18n.refresh_saint_archive_bindings import refresh

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');parser.add_argument('--prune',action='store_true');args=parser.parse_args()
 merge_daily_history(ROOT,check=args.check)
 if args.check:
  path,text=output(ROOT)
  if path.read_text()!=text:raise ValueError('Archive source stale')
  subprocess.run([sys.executable,'scripts/build_saint_of_day.py','--check'],cwd=ROOT,check=True);return
 if args.prune:subprocess.run([sys.executable,'scripts/build_saint_of_day.py','--prune'],cwd=ROOT,check=True)
 subprocess.run([sys.executable,'scripts/build_saint_of_day.py'],cwd=ROOT,check=True)
 path,text=output(ROOT);path.write_text(text)
 subprocess.run(['node','scripts/build-pages.mjs','--pages=saint-of-the-day.html'],cwd=ROOT,check=True)
 refresh(ROOT)
if __name__=='__main__':main()
