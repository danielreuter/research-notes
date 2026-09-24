#!/bin/bash
for r in "$@"; do /tmp/fp4fast/ssh.sh "grep -E 'rep [123]:|Traceback' /workspace/research/runs/$r/stdout.log | cut -c1-160; python3 - <<'PY'
import json,os
p='/workspace/research/runs/$r/result.json'
if os.path.exists(p):
    r=json.load(open(p)); m={x['name']:x['value'] for x in r['measurements']}; s=r['workload_fingerprint']['security']
    print('$r', 't.total=%.3f'%m['t.total'], ' '.join('%s=%.3f'%(k[6:].replace('_seconds',''),v) for k,v in m.items() if k.startswith('split.') and k.endswith('seconds')), 'peak=%.2fGB'%(m['mem.peak_device_bytes']/2**30), 'bits=%.2f'%-s['achieved_log2'], 'l=%d'%s['rs_l'], 'R=%.3g'%m['rate.proved_flop_per_second'], 'ovh=%.3g'%m['overhead.vs_native_peak'], 'pipe', r['workload_fingerprint']['software']['backend'].get('pipeline'), r['validation']['status'])
else: print('$r', 'no result.json')
PY"; done
