#!/usr/bin/env bash
# poseidon-v1 plateau sweep (kb/TABLES.md "Sweep"): total batch doubled from 1024 at the configuration's per-proof settings
# (l, p) until two successive doublings together raise the median throughput P = n / e2e.seconds by less than 2 %
# (P(n) < 1.02 * P(n/4)), memory runs out (a failed point), or n exceeds NMAX. Plateau = the point with the highest P.
#   bash sweep.sh SWEEP_ID TREE REL L P [NMAX=32768]      -> $PV/sweeps/SWEEP_ID.jsonl (one JSON point per line) + .done
#   NMIN=N bash sweep.sh ...                                continues SWEEP_ID from n = N (appends)
source ${SCRIPTS:-/workspace/poseidon-v1/scripts}/lib.sh
sid=$1 tree=$2 rel=$3 l=$4 p=$5 nmax=${6:-32768}
mkdir -p $PV/sweeps; J=$PV/sweeps/$sid.jsonl
# NMIN set: continue an existing sweep (append; the stop rule reads every point so far)
[ -n "${NMIN:-}" ] || : > $J
rm -f $J.done
echo "$(date -u +%H:%M:%SZ) SWEEP $sid tree=$tree rel=$rel l=$l p=$p nmin=${NMIN:-1024} nmax=$nmax" | tee -a $LOG
n=${NMIN:-1024}
while [ $n -le $nmax ]; do
  tag=$sid-n$n
  if run $tag $tree $rel $l $p $n; then
    $PY $SCRIPTS/line.py $O/$tag --json >> $J
  else
    echo "{\"tag\": \"$tag\", \"n\": $n, \"failed\": true, \"why\": $(grep -E 'out of memory|OutOfMemory|Error' $O/$tag/log | tail -1 | $PY -c 'import json,sys;print(json.dumps(sys.stdin.read().strip()[:300]))')}" >> $J
    break
  fi
  stop=$($PY - $J <<'EOF'
import json, sys
pts = [json.loads(l) for l in open(sys.argv[1]) if l.strip()]
ok = [p for p in pts if not p.get("failed") and p.get("P")]
print("stop" if len(ok) >= 3 and ok[-1]["P"] < 1.02 * ok[-3]["P"] else "go")
EOF
)
  [ "$stop" = stop ] && break
  n=$((n * 2))
done
$PY - $J <<'EOF' | tee -a $LOG
import json, sys
pts = [json.loads(l) for l in open(sys.argv[1]) if l.strip()]
ok = [p for p in pts if not p.get("failed") and p.get("P")]
best = max(ok, key=lambda p: p["P"]) if ok else None
print("SWEEP_DONE", sys.argv[1], "points", [(p["n"], round(p["P"], 1) if p.get("P") else None) for p in pts],
      "plateau", best and best["n"], best and round(best["P"], 1))
EOF
touch $J.done
