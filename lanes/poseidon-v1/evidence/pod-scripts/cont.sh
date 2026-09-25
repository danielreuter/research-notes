#!/usr/bin/env bash
# poseidon-v1: continue a row's sweep past its first cap.   bash cont.sh ROW REL L P NMIN NMAX
# builds the synthetic instance caches for NMIN..NMAX first (as pod_bootstrap.sh does), then NMIN=... sweep.sh
set -uo pipefail
SCRIPTS=/workspace/poseidon-v1/scripts; source $SCRIPTS/lib.sh
row=$1 rel=$2 l=$3 p=$4 nmin=$5 nmax=$6
NS=""; n=$nmin; while [ $n -le $nmax ]; do NS="$NS${NS:+,}$n"; n=$((n * 2)); done
( cd /workspace/src && REL=$rel NS=$NS NP=${VY_CPU_THREADS:-8} OMP_NUM_THREADS=1 $PY - <<'EOF'
import os, time
from backends.direct.ligero.relchain import instances
from backends.direct.ligero.relations import relation
r = relation(os.environ["REL"])
if not r.frozen_tier and getattr(r, "instances_fn", None) is None:
    for n in map(int, os.environ["NS"].split(",")):
        t0 = time.perf_counter(); d = instances(r, n, procs=int(os.environ["NP"]), cache="/workspace/instances-cache")
        print(f"{r.name} n={n}: {len(d)} VUs, {time.perf_counter() - t0:.1f}s", flush=True)
EOF
) 2>&1 | tee -a $LOG
NMIN=$nmin bash $SCRIPTS/sweep.sh $row /workspace/src $rel $l $p $nmax
echo CONT_DONE $row
