#!/usr/bin/env bash
# mt_router.sh [driver args]: wait for $WAIT_RUN, build the router-softmax tap (ops/pod_router_tap.sh), then the router-tap exactness property on
# GPU ${GPU:-0} (tests/properties/router_tap_exactness_gpu.py); the sealed record and the build's files land in $RESEARCH_RUN_DIR/evidence.
set -u
T=$PWD; OUT=$RESEARCH_RUN_DIR; mkdir -p "$OUT/evidence"
if [ -n "${WAIT_RUN:-}" ]; then while grep -q '^ "state": "running"' "$WAIT_RUN/status.json" 2>/dev/null; do sleep 30; done; echo "waited for $WAIT_RUN $(date -u +%FT%TZ)"; fi
export PATH=/workspace/venv312/bin:$PATH HF_HOME=/workspace/hf CUDA_VISIBLE_DEVICES=${GPU:-0}
export PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src:$T/protocols/sampled_proofs
cd integrations/vllm
python -c "import verity_sampled_proofs" && echo "verity_sampled_proofs importable"
bash verity_vllm/ops/pod_router_tap.sh > "$OUT/router_tap.log" 2>&1; echo "router tap rc $? $(date -u +%FT%TZ)"; tail -n 3 "$OUT/router_tap.log"
cp /workspace/cp/router_tap/build/build_info.json /workspace/cp/router_tap/logs/build.log /workspace/cp/router_tap/build/router_tap_kernel.cuh "$OUT/evidence/" 2>/dev/null
python tests/properties/router_tap_exactness_gpu.py --so /workspace/cp/router_tap/build/verity_router_tap.so --out "$OUT/evidence" "$@" > "$OUT/exactness.log" 2>&1
echo "exactness rc $? $(date -u +%FT%TZ)"; grep -a "^\[router-tap\]\|ROUTER-TAP" "$OUT/exactness.log" | cut -c1-600 | tail -n 40; tail -n 5 "$OUT/exactness.log" | cut -c1-400
python tests/properties/router_tap_exactness_gpu.py --verify "$OUT/evidence/router_tap_exactness.json"
echo "MT-ROUTER-DONE $(date -u +%FT%TZ)"
