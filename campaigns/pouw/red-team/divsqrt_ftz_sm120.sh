#!/usr/bin/env bash
# The `.FTZ` allowlist for nvcc's correctly rounded div, rcp and sqrt, on one red-team GPU of vy-nebius-2, under a named lease:
#   research run --on vy-nebius-2 --project verity --source <tree> --campaign pouw-red-team --send divsqrt_ftz_sm120.cu \
#     --send divsqrt_ftz_sm120.sh --send divsqrt_ftz_check.py -- gpu-lease 1 --wait --on 6 --max-min 15 -- bash inputs/divsqrt_ftz_sm120.sh GPU-...
set -euo pipefail
UUID=${1:?gpu uuid}
OUT=${RESEARCH_RUN_DIR:-$PWD}
TREE=/workspace/research/src/${RESEARCH_SOURCE_SHA:?}
cd "$OUT"
[ "${GPU_LEASE_UUID:-}" = "$UUID" ] || { echo "run under gpu-lease on $UUID (got ${GPU_LEASE_UUID:-none})" >&2; exit 3; }
/usr/local/cuda/bin/nvcc --version | tail -1 > nvcc.txt
/usr/local/cuda/bin/nvcc -O3 -std=c++17 -gencode arch=compute_120a,code=sm_120a inputs/divsqrt_ftz_sm120.cu -o divsqrt
# per kernel: every FP op in its SASS, so the .FTZ ones inside each allowed sequence are on record
/usr/local/cuda/bin/cuobjdump -sass divsqrt | awk '/Function :/{f=$3} {for(i=1;i<=NF;i++) if ($i ~ /^(FADD|FFMA|FMUL|MUFU|FSETP|FCHK|CALL)/) c[f" "$i]++} END{for(k in c) print k, c[k]}' | sort > sass-fp-ops.txt
py() { (cd "$TREE" && PYTHONPATH=packages/verity/src uv run --no-dev python "$OUT/inputs/divsqrt_ftz_check.py" "$@"); }
{
  ./divsqrt sqrt
  ./divsqrt rcp
  ./divsqrt div
  py mk "$OUT/pairs.bin"; ./divsqrt dump "$OUT/pairs.bin" "$OUT/dev.bin" > /dev/null
  py cmp "$OUT/pairs.bin" "$OUT/dev.bin"
} > summary.jsonl
rm -f pairs.bin dev.bin
cat summary.jsonl sass-fp-ops.txt
