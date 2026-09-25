#!/usr/bin/env bash
# agkr-bound: the A-GKR side of the survey's route (a) link (§4.3), measured: tools/link_stub.py (512 operand bits per
# BF16 unit, k-bit limbs, range + recomposition) in the Rust CPU prover at B units; B = 393216 is one 4,096-VU BF16 batch.
# research run --on vy-agkr-bound2 --project verity --source . --cwd source/backends/gkr --send 13_link_stub.sh \
#     -- bash -c 'exec bash "$RESEARCH_RUN_DIR/inputs/13_link_stub.sh"'
# usage: [BS="4096 65536 393216"] [KS="1 2 4"] bash 13_link_stub.sh
set -uo pipefail
ROOT=$(cd ../.. && pwd)
export PATH="/workspace/venv312/bin:$HOME/.cargo/bin:$PATH"
PY=/workspace/venv312/bin/python
read -r Q PER < /sys/fs/cgroup/cpu.max 2>/dev/null || { Q=max; PER=100000; }
NT=$([ "$Q" = max ] && nproc || echo $(( Q / PER )))
export OMP_NUM_THREADS=$NT MKL_NUM_THREADS=$NT OPENBLAS_NUM_THREADS=$NT VY_CPU_THREADS=$NT CARGO_BUILD_JOBS=$NT RAYON_NUM_THREADS=$NT
export VERITY_GKR_THREADS=$NT
RD=${RESEARCH_RUN_DIR:?}
echo "tree $ROOT; commit ${RESEARCH_SOURCE_COMMIT:-?}; cpu threads $NT; run dir $RD"
H=/workspace/agkr-bound/link
mkdir -p $H

summ() {
  $PY - "$1" <<'EOF'
import json, sys
d = json.load(open(sys.argv[1]))
m = {x["name"]: x["value"] for x in d["measurements"]}
keys = ["units", "columns_per_unit", "t.total", "t.arithmetic", "t.encoding_commitment", "t.witness", "verifier.seconds",
        "proof_bytes", "ligero_rows", "rounds.sequential_depth", "threads", "peak_rss_bytes"]
print("  " + ", ".join(f"{k} {m[k]:.4g}" if isinstance(m.get(k), float) else f"{k} {m.get(k)}" for k in keys))
print("  status", d["validation"]["status"], "|", d["validation"]["detail"][:200])
EOF
}

export CARGO_TARGET_DIR=/workspace/cargo-target-gkr
cargo build --release --features babybear 2>&1 | grep -E "^error|Finished" | head -5
VG=$CARGO_TARGET_DIR/release/verity-gkr

for K in ${KS:-1 2 4}; do
  O=$H/k$K
  $PY tools/link_stub.py --out $O --units 64 --k $K | cut -c1-200
  $VG check-witness --circuit $O/circuit.txt --witness $O/neg.bin > $O/check_neg.log 2>&1; echo "k=$K check-witness neg rc=$? (want nonzero)"
  for B in ${BS:-4096 65536 393216}; do
    echo "== k=$K B=$B ($(date -u +%H:%M:%S))"
    $VG run --circuit $O/circuit.txt --witness $O/witness.bin --units $B --out $O/result-$B.json > $O/run-$B.log 2>&1
    echo "run rc=$? ($(date -u +%H:%M:%S))"; tail -1 $O/run-$B.log | cut -c1-220
    [ -f $O/result-$B.json ] && summ $O/result-$B.json
  done
  rm -f $O/witness.bin
done
echo "== done ($(date -u +%H:%M:%S))"
