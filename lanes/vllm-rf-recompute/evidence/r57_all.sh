#!/bin/bash
set -e
cd /workspace
for s in LP1024_T18 LP10_T127 LP179_T30 LP453_T106 LP531_T10 LP719_T80 LP779_T1; do
  PYTHONPATH=tools/research/src timeout 900 python3 -m research data fetch art:5e925a59d73127305b8f6065c2ee519097c22b45c1e9d3452db338a39b65122d --to $HOME/ev/r57 --path "build_request_${s}/*" >/dev/null
done
cd $HOME/wt/fp8x98
for d in $HOME/ev/r57/build_request_LP*; do
  n=$(basename $d)
  [ -f $HOME/ev/r57once/$n/instances.json.gz ] || python3 $HOME/ev/once_rewrite.py $d $HOME/ev/r57once/$n
  for p in $d $HOME/ev/r57once/$n; do
    PYTHONPATH=$PPX python3 -c "
import sys, json, time
from verity_vllm.query import cross_call as X
t=time.time(); r = X.check_program(sys.argv[1] + '/instances.json.gz', strict=False)
print(json.dumps({'program': sys.argv[1], 'ok': r['ok'], 'calls': r['calls'], 'recomputed_gates': r['recomputed_gates'], 'classes': [(a['definition'], a['level'], a['calls'], a['gates']) for a in r['recomputes']], 'refined': r['refined'], 'unrefined': r['unrefined'], 's': round(time.time()-t)}), flush=True)
" $p
  done
done
echo ALL-DONE
