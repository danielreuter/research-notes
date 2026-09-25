#!/usr/bin/env bash
# agkr-bound: the bit link's prime side (tools/link_stub.py k=1) as a third segment of the real BF16 A100 proof (18_wrap.py),
# against the same cell without it; 1 warm-up + 3 reps each, Python verifier.
# research run ... --send 18_link_merged.sh --send 18_wrap.py -- bash -c 'exec bash "$RESEARCH_RUN_DIR/inputs/18_link_merged.sh"'
set -uo pipefail
HERE=$(pwd)
ROOT=$(cd ../.. && pwd)
export PYTHONPATH="$ROOT/packages/verity/src:$ROOT/backends/numerical/python:$ROOT/tools/research/src:$ROOT:$HERE"
export PATH="/workspace/venv312/bin:$HOME/.cargo/bin:/usr/local/cuda/bin:$PATH"
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
PY=/workspace/venv312/bin/python
read -r Q PER < /sys/fs/cgroup/cpu.max 2>/dev/null || { Q=max; PER=100000; }
NT=$([ "$Q" = max ] && nproc || echo $(( Q / PER )))
export OMP_NUM_THREADS=$NT MKL_NUM_THREADS=$NT OPENBLAS_NUM_THREADS=$NT VY_CPU_THREADS=$NT
RD=${RESEARCH_RUN_DIR:?}
H=/workspace/agkr-bound/link-merged; mkdir -p $H
S=$H/stmt; [ -f $S/circuit.txt ] || $PY -m gpu.v2.export circuits --model ampere_bf16_m16n8k16 --out $S > /dev/null
L=$H/k1; $PY tools/link_stub.py --out $L --units 64 --k 1 | cut -c1-120
for mode in base link; do
  echo "== $mode ($(date -u +%H:%M:%S))"
  O=$H/$mode; rm -rf $O; mkdir -p $O
  if [ $mode = link ]; then export LINK_DIR=$L; else unset LINK_DIR; fi
  RESEARCH_RUN_DIR=$O/run $PY "$RD/inputs/18_wrap.py" $S --instances /workspace/bench-instances/v1 --vus 4096 --reps 3 --warmup 1 \
      --verifier /workspace/bin/verity-gkr-verify-pinned --threads $NT > $O/bench.log 2>&1
  echo "bench rc=$? ($(date -u +%H:%M:%S))"
  grep -E '^18_wrap|Traceback|Error' $O/bench.log | head -5
  $PY - $O/run/prove_reps.json <<'EOF'
import json, sys
d = json.load(open(sys.argv[1]))
reps = d if isinstance(d, list) else d.get("reps", d)
for r in reps:
    if isinstance(r, dict) and "t_total" in r:
        print("  rep %s t_total %.4f prove %.4f commit %.4f lookup %.4f arith %.4f open %.4f py_verified %s py_verify_s %.2f committed %s rows %s depth %s proof_bytes %s peak %.1f GB" % (
            r["rep"], r["t_total"], r["prove"], r["t_commit"], r["t_lookup"], r["t_arith"], r["t_open"], r["python_verified"],
            r["python_verifier_s"], r["committed_elements"], r["ligero_rows"], r["sequential_depth"], r["proof_bytes"], r["peak_mem_bytes"] / 1e9))
EOF
done
echo "== done ($(date -u +%H:%M:%S))"
