#!/usr/bin/env bash
# sm_120 kernel captures, job C (lane vllm-sm120-kernels): the rotary difftest (job B's run had the pre-fix adapter), then the
# diagnostics (step models, twins) on it and on job B's fused-MoE capture ($MOE_DIR).
set -uo pipefail
T=$(pwd -P); IN=$RESEARCH_RUN_DIR/inputs; OUT=$RESEARCH_RUN_DIR/out; mkdir -p "$OUT"
VENV=/workspace/venv312; PY=$VENV/bin/python
export CUDA_HOME=/usr/local/cuda-12.9 PATH=$VENV/bin:/usr/local/cuda-12.9/bin:$PATH HF_HOME=/workspace/hf VLLM_BATCH_INVARIANT=1
export PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src:$T/protocols/sampled_proofs
cd "$T/integrations/vllm"
log() { echo "[sm120-c] $(date -u +%FT%TZ) $*" | tee -a "$OUT/steps.log"; }
declare -A V
step() { local name=$1; shift; log "BEGIN $name"; if "$@" >"$OUT/$name.log" 2>&1; then V[$name]=PASS; else V[$name]="FAIL rc=$?"; fi; log "END $name ${V[$name]} ($(tail -1 "$OUT/$name.log" | cut -c1-400))"; }
AD=verity_vllm.program.registry
step device verity-vllm epoch device --expect-sms 188 --expect-cc 12.0
step rope_produce verity-vllm properties-admission produce --adapter $AD.rope_difftest --n 48 --seed 11 --out "$OUT/rope"
step rope_check verity-vllm properties-admission check --adapter $AD.rope_difftest --dir "$OUT/rope" --out "$OUT/rope/rope.json"
step diag $PY "$IN/sm120_b_diag.py" "$OUT/rope" "${MOE_DIR:?}" "$OUT/diag.json"
{ printf '{'; first=1; for k in "${!V[@]}"; do [ $first = 1 ] || printf ','; first=0; printf '"%s": "%s"' "$k" "${V[$k]}"; done; printf '}\n'; } > "$OUT/summary.json"
log "SUMMARY $(cat "$OUT/summary.json")"
echo "SM120-C-DONE"
