#!/usr/bin/env python3
"""Opt-in live probe (not part of CI): unauthenticated (anon-key) reads of moderator-only tables must return no rows or be denied."""
import json, re, sys, urllib.request, urllib.error
cfg = open('testimony-config.js').read()
url = re.search(r"supabaseUrl: '([^']+)'", cfg).group(1)
key = re.search(r"supabaseAnonKey: '([^']+)'", cfg).group(1)
bad = 0
for table in ('testimony_controls', 'testimony_audit', 'testimony_reports', 'testimony_submissions'):
    req = urllib.request.Request(f'{url}/rest/v1/{table}?select=*&limit=1', headers={'apikey': key, 'Authorization': f'Bearer {key}'})
    try:
        body = json.loads(urllib.request.urlopen(req, timeout=20).read() or b'[]')
        status = 200
    except urllib.error.HTTPError as e:
        body, status = [], e.code
    ok = body == []
    bad += 0 if ok else 1
    print(f'{table}: HTTP {status}, rows={len(body)} {"OK" if ok else "LEAK"}')
sys.exit(1 if bad else 0)
