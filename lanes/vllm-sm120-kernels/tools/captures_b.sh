#!/usr/bin/env bash
# sm_120 kernel captures, job B (lane vllm-sm120-kernels), on the pod job A bootstrapped: the top-p drain at every split boundary of
# 188 SMs, the rotary and fused-MoE difftests (VLLM_BATCH_INVARIANT=1: the fused-MoE launch config the rows run), the twins on those
# captures, and the fused-MoE k16-step discrimination at volume.
# research run --on <pod> --project verity --custody-r2 --source <tree> --cwd source --send captures_b.sh --send sm120_b_diag.py \
#   --send sm120_moe_bulk.py -- bash -c 'bash "$RESEARCH_RUN_DIR/inputs/captures_b.sh"'
set -uo pipefail
T=$(pwd -P); IN=$RESEARCH_RUN_DIR/inputs; OUT=$RESEARCH_RUN_DIR/out; mkdir -p "$OUT"
VENV=/workspace/venv312; PY=$VENV/bin/python
export CUDA_HOME=/usr/local/cuda-12.9 PATH=$VENV/bin:/usr/local/cuda-12.9/bin:$PATH HF_HOME=/workspace/hf
export PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src:$T/protocols/sampled_proofs
cd "$T/integrations/vllm"
log() { echo "[sm120-b] $(date -u +%FT%TZ) $*" | tee -a "$OUT/steps.log"; }
declare -A V
step() { local name=$1; shift; log "BEGIN $name"; if "$@" >"$OUT/$name.log" 2>&1; then V[$name]=PASS; else V[$name]="FAIL rc=$?"; fi; log "END $name ${V[$name]} ($(tail -1 "$OUT/$name.log" | cut -c1-240))"; }
AD=verity_vllm.program.registry

step device verity-vllm epoch device --expect-sms 188 --expect-cc 12.0
[ "${V[device]}" = PASS ] || { log "DEVICE-GATE-FAIL"; exit 40; }
$PY -c "import verity_sampled_proofs, vllm, torch; print(verity_sampled_proofs.__file__, vllm.__version__, torch.__version__)" | tee -a "$OUT/steps.log"

step topp_probe_produce verity-vllm topp-split-probe produce --out "$OUT/topp_probe"
step topp_probe_check verity-vllm topp-split-probe check --dir "$OUT/topp_probe" --out "$OUT/topp_probe/check.json"

export VLLM_BATCH_INVARIANT=1
step rope_produce verity-vllm properties-admission produce --adapter $AD.rope_difftest --n 48 --seed 11 --out "$OUT/rope"
step rope_check verity-vllm properties-admission check --adapter $AD.rope_difftest --dir "$OUT/rope" --out "$OUT/rope/rope.json"
step moe_produce verity-vllm properties-admission produce --adapter $AD.moe_difftest --n 20 --seed 17 --out "$OUT/moe"
step moe_check verity-vllm properties-admission check --adapter $AD.moe_difftest --dir "$OUT/moe" --out "$OUT/moe/moe.json"
step diag $PY "$IN/sm120_b_diag.py" "$OUT/rope" "$OUT/moe" "$OUT/diag.json"
step moe_bulk $PY "$IN/sm120_moe_bulk.py" "$OUT/moe_bulk.json" 16

{ printf '{'; first=1; for k in "${!V[@]}"; do [ $first = 1 ] || printf ','; first=0; printf '"%s": "%s"' "$k" "${V[$k]}"; done; printf '}\n'; } > "$OUT/summary.json"
log "SUMMARY $(cat "$OUT/summary.json")"
echo "SM120-B-DONE"
