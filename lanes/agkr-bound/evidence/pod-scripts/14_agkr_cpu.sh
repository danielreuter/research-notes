#!/usr/bin/env bash
# agkr-bound: same-pod A-GKR CPU reference for the hash spike (12/13): the BF16 relation (bench-instances/v1 tier vu-k1536)
# at B = 4096 VUs through the Rust CPU prover (run_measure_vu.sh, FIELD=babybear), with the spike's thread cap.
# research run --on vy-agkr-bound2 --project verity --source . --cwd source/backends/gkr --send 14_agkr_cpu.sh \
#     -- bash -c 'exec bash "$RESEARCH_RUN_DIR/inputs/14_agkr_cpu.sh"'
set -uo pipefail
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
read -r Q PER < /sys/fs/cgroup/cpu.max 2>/dev/null || { Q=max; PER=100000; }
NT=$([ "$Q" = max ] && nproc || echo $(( Q / PER )))
export OMP_NUM_THREADS=$NT MKL_NUM_THREADS=$NT OPENBLAS_NUM_THREADS=$NT VY_CPU_THREADS=$NT RAYON_NUM_THREADS=$NT
echo "cpu threads $NT ($(date -u +%H:%M:%S))"
FIELD=babybear VERITY_GKR_THREADS=$NT PROCS=$NT CARGO_TARGET_DIR=/workspace/cargo-target-gkr \
  INSTANCES_ROOT=/workspace/bench-instances/v1 bash run_measure_vu.sh ${B:-4096} 2>&1 | tail -30
echo "rc=$? ($(date -u +%H:%M:%S))"
/workspace/venv312/bin/python - "$RESEARCH_RUN_DIR/result.json" <<'EOF'
import json, sys
d = json.load(open(sys.argv[1]))
m = {x["name"]: x["value"] for x in d["measurements"]}
for k in ["units", "columns_per_unit", "t.total", "t.arithmetic", "t.lookup", "t.encoding_commitment", "t.witness", "verifier.seconds",
          "proof_bytes", "ligero_rows", "rounds.sequential_depth", "threads", "peak_rss_bytes"]:
    print(f"  {k} {m.get(k)}")
print("  status", d["validation"]["status"], "|", d["validation"]["detail"][:200])
EOF
