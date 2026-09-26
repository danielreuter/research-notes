#!/usr/bin/env bash
# nt_exact.sh [--quick]: the norm-tap exactness property on this GPU (tests/properties/norm_tap_exactness_gpu.py) against the tap build of
# ops/pod_norm_tap.sh (rebuilt only if its inputs changed); the sealed record lands in $RESEARCH_RUN_DIR/evidence (custody with the run).
set -u
T=$PWD; OUT=$RESEARCH_RUN_DIR; mkdir -p "$OUT/evidence"
export PATH=/workspace/venv312/bin:$PATH HF_HOME=/workspace/hf
export PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src:$T/protocols/sampled_proofs
cd integrations/vllm
bash verity_vllm/ops/pod_norm_tap.sh > "$OUT/norm_tap.log" 2>&1; echo "norm tap rc $?"; tail -n 1 "$OUT/norm_tap.log"
python tests/properties/norm_tap_exactness_gpu.py --so /workspace/cp/norm_tap/build/verity_norm_tap.so --out "$OUT/evidence" "$@" > "$OUT/exactness.log" 2>&1
echo "exactness rc $? $(date -u +%FT%TZ)"
tail -n 60 "$OUT/exactness.log"
python tests/properties/norm_tap_exactness_gpu.py --verify "$OUT/evidence/norm_tap_exactness.json"
echo "NT-EXACT-DONE $(date -u +%FT%TZ)"
