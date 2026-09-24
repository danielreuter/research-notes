#!/usr/bin/env bash
# agkr-table: LogUp micro-optimisations (Montgomery finish_round, the static [1 | lambda] coefficient buffer, O(1)
# round_consts from the eq prefix the device sponge keeps) -- bench_result with the working tree on the frozen vu-k1536
# [0, 4096), 3 reps: every proof must be byte-identical to recorded run r20260924-071929-6745's (commit bab91f23, same
# statement, deterministic Fiat-Shamir) and the Rust verifier must accept; timings next to the recorded run's.
set -uo pipefail
source /workspace/env.sh
cd /workspace/src/backends/gkr
export PYTHONPATH=/workspace/src/backends/gkr:$PYTHONPATH
REF=/workspace/research/runs/r20260924-071929-6745
export RESEARCH_RUN_DIR=/workspace/agkr-table/micro
rm -rf $RESEARCH_RUN_DIR
$PY bench_result.py /workspace/agkr-table/bb/stmt --instances /workspace/bench-instances/v1 --vus 4096 --reps 3 --warmup 1 \
    --verifier /workspace/bin/verity-gkr-verify --threads 15 > $RESEARCH_RUN_DIR.log 2>&1
echo "bench_result rc=$?"
grep -E '^\{"rep"|verify rep|"status"|contract_problems' $RESEARCH_RUN_DIR.log | cut -c1-160
for i in 0 1 2; do
    if cmp -s $RESEARCH_RUN_DIR/proofs/rep$i.bin $REF/proofs/rep$i.bin; then echo "rep$i: proof identical to $REF"; else echo "rep$i: PROOF DIFFERS"; fi
done
$PY - <<'EOF'
import json
for tag, d in (("recorded bab91f23", "/workspace/research/runs/r20260924-071929-6745"), ("working tree", "/workspace/agkr-table/micro")):
    reps = json.load(open(f"{d}/prove_reps.json"))["runs"]
    keys = ("t_total", "t_lookup", "t_arith", "t_open", "witness_gen", "to_bytes")
    print(f"{tag:18s}", " ".join(f"{k}={sorted(r[k] for r in reps)[len(reps) // 2]:.4f}" for k in keys))
EOF
