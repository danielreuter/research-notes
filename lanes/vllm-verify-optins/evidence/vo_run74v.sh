#!/usr/bin/env bash
# vo_run74v.sh: task 3's value check on the recorded Build (#74, Qwen3-4B-FP8, H100 SXM5, TP1, B=8): recorded request Programs of
# art:9d14bd11 (p74small.tar) evaluated Call by Call from the prompt ids and the checkpoint of record (vo_fp8_values.py), comparing at
# every ScaledMmFp8Block_v1 Call the host products (fp8.scale_products) with the old construction's F32Mul_v1 values and the old / new
# coordinate Definitions on sampled coordinates, and each step's token with the recorded generation (match/control/tokens.json of
# art:85924a1f).  SHAPES (default "LP73_T1 LP11_T94"); LP11_T94 stops after STEPS11 engine steps.
set -u
L=$RESEARCH_RUN_DIR; T=$PWD; I=$L/inputs; EV=$L/evidence; mkdir -p "$EV" /workspace/vo/p74
tar -xf "$I/p74small.tar" -C /workspace/vo/p74
export PATH=/workspace/venv312/bin:$PATH CUDA_VISIBLE_DEVICES=""
export PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src:$T/protocols/sampled_proofs
CK=/workspace/hf/hub/models--Qwen--Qwen3-4B-Instruct-2507-FP8/snapshots/8591804019c8b22094c3b5b4454e0edc05dffc98
WL=workloads/qwen3-4b-fp8__fp8__h100__tp1__b8__i1024__o128__mixed__greedy__bi-eager.json
cd "$T/integrations/vllm"
for s in ${SHAPES:-LP73_T1 LP11_T94}; do
  extra=(--coords "${COORDS:-16}" --coord-every "${EVERY:-4}")
  [ "$s" = LP73_T1 ] && extra+=(--all-coords-layers 0)
  [ "$s" = LP11_T94 ] && extra+=(--steps "${STEPS11:-12}")
  python "$I/vo_fp8_values.py" "$EV/fp8-$s" "/workspace/vo/p74/build_request_$s" "$WL" "$CK" "${extra[@]}" --jobs "${VJOBS:-4}" \
    --tokens "$I/tokens.json" > "$L/fp8-$s.log" 2>&1 &
done
wait
tail -qn 1 "$L"/fp8-*.log
echo "RUN74V-DONE $(date -u +%FT%TZ)"
