#!/usr/bin/env bash
# ops-tools part B on a 4090: env.sh thread pools (B1), the bench timing guard clean vs beside a GPU hog (B3), summary --best.
#   research pods ssh vy-ops-tools -- 'bash /workspace/ops-tools/validate_b.sh 2>&1 | tee /workspace/ops-tools/validate_b.log'
set -uo pipefail
source /workspace/env.sh
OUT=/workspace/ops-tools
cd /workspace/src
echo "== env.sh: OMP=$OMP_NUM_THREADS MKL=$MKL_NUM_THREADS OPENBLAS=$OPENBLAS_NUM_THREADS VY_CPU_THREADS=$VY_CPU_THREADS nproc=$(nproc)"
"$PY" -c "import torch; print('torch intra-op threads', torch.get_num_threads(), '| inter-op', torch.get_num_interop_threads())"

B=("$PY" -m backends.direct.ligero.run --relation fp8-ada bench-vu --batch 16384 --total-vus 512 --reps 3 --instance-procs "$VY_CPU_THREADS")
echo "== guard: clean bench-vu"
LIGERO_GPU_STRICT=1 "${B[@]}" --out $OUT/guard_clean.json > $OUT/guard_clean.log 2>&1; echo "rc $?"; tail -3 $OUT/guard_clean.log

echo "== guard: the same beside a bf16 matmul hog in another process"
"$PY" - > $OUT/hog.log 2>&1 <<'EOF' &
import time, torch
a = torch.randn(8192, 8192, device="cuda").to(torch.bfloat16)
end = time.time() + 150
while time.time() < end:
    a @ a
    torch.cuda.synchronize()
EOF
HOG=$!
sleep 10
nvidia-smi --query-compute-apps=pid,process_name --format=csv,noheader; echo "hog pid (container) $HOG"
LIGERO_GPU_STRICT=1 "${B[@]}" --out $OUT/guard_busy.json > $OUT/guard_busy.log 2>&1; echo "rc $?"; tail -3 $OUT/guard_busy.log
kill $HOG 2>/dev/null; wait $HOG 2>/dev/null

echo "== summary (contended column, reasons)"
"$PY" -m verity_numerical.bench.summary $OUT/guard_clean.json $OUT/guard_busy.json --no-refs --cols contention.reasons,contention.throttled,contention.load1_max
echo "== summary --best (refuses the contended row)"
"$PY" -m verity_numerical.bench.summary $OUT/guard_clean.json $OUT/guard_busy.json --no-refs --best
