#!/usr/bin/env bash
# agkr-nvf4: VERITY_GPU_QC_CHUNK sweep (open_w_qc_eval row chunks) with 05_profile.sh timing-only runs; prints t_open_wq
# and t_total medians per chunk.  bash 14_qcsweep.sh "0 32 64 104 160"
cd /workspace/agkr-nvf4
for c in ${1:-0 32 64 104 160}; do
  VERITY_GPU_QC_CHUNK=$c bash pod-scripts/05_profile.sh 4096 5 tqc$c > /dev/null 2>&1
  grep '^{"rep"' prof-tqc$c/prof.log | python3 -c "
import json, statistics, sys
r = [json.loads(l) for l in sys.stdin]
print('chunk $c', 'wq', round(statistics.median(x['t_open_wq'] for x in r) * 1e3, 2), 'ms  total',
      round(statistics.median(x['t_total'] for x in r), 4), 'sha', {x['proof_sha256'][:8] for x in r})"
done
echo sweep-done
