#!/usr/bin/env bash
# agkr-table: bench_result.py smoke test (1 warm-up + 1 rep, not recorded) -- the contract envelope end to end
# (device witness generator -> prover -> statement/ + proof dump -> Python + Rust verifier -> result.json) before the
# `research run` reps.  bb/stmt = the Params-only statement files of the v2 export (no witness).
set -uo pipefail
source /workspace/env.sh
O=/workspace/agkr-table
mkdir -p $O/bb/stmt && cp $O/bb/pos4096/{circuit.txt,epilogue.txt,chain.txt,manifest.json} $O/bb/stmt/
ls -la $O/bb/stmt
cd /workspace/src/backends/gkr
export PYTHONPATH=/workspace/src/backends/gkr:$PYTHONPATH
echo "=== $(date -u +%H:%M:%S) smoke"
rm -rf $O/smoke
RESEARCH_RUN_DIR=$O/smoke $PY bench_result.py $O/bb/stmt --instances /workspace/bench-instances/v1 --vus 4096 --reps 1 --warmup 1 \
    --verifier /workspace/bin/verity-gkr-verify --threads 15 > $O/smoke.out 2>&1
echo "rc=$? $(date -u +%H:%M:%S)"
grep -v -i warn $O/smoke.out | grep -v searchsorted | cut -c1-600
