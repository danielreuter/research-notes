#!/usr/bin/env bash
# vo_runbase.sh: the same derive commands as the row Build (`row_stages.SingleRow.derive_all`: step M=B pos0=8, request shapes under their
# launch contexts) on the shipped BASE tree (main, the verification merge's first parent), for each row's step Program and one request
# shape, under the same declared targets.  Their Program digests must equal the head Builds' (knobs unset) byte for byte.
set -u
L=$RESEARCH_RUN_DIR; T=$PWD; EV=$L/evidence; mkdir -p "$EV"
export PATH=/workspace/venv312/bin:$PATH HF_HOME=/workspace/hf HF_HUB_OFFLINE=1 VLLM_BATCH_INVARIANT=1 CUDA_VISIBLE_DEVICES="" TOKENIZERS_PARALLELISM=false
export PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src:$T/protocols/sampled_proofs
cd "$T/integrations/vllm"
derive() {  # LABEL ROW REPO REV TARGET WRAPPER [LP T]
  local out=/workspace/vo/base/$1 wl="workloads/$2.json" lc=()
  rm -rf "$out"
  if [ "$6" = step ]; then
    python -m verity_vllm.pipeline.cli build --model "$3" --revision "$4" --wrapper step --M 8 --pos0 8 --max-model-len 1152 --workload "$wl" \
      --out "$out" --target "$5" > "$L/base-$1.log" 2>&1
  else
    mapfile -t lc < <(python -m verity_vllm.pipeline.cli launch-context "$wl" "$7" "$8")
    python -m verity_vllm.pipeline.cli build --model "$3" --revision "$4" --wrapper request --LP "$7" --T "$8" --max-model-len 1152 \
      --workload "$wl" --out "$out" --target "$5" ${lc[0]:+--launch-max-seqlen-q "${lc[@]}"} > "$L/base-$1.log" 2>&1
  fi
  python -c "import json,sys; r=json.load(open('$out/result.json')); print(json.dumps({'label': '$1', 'ok': r.get('ok'), 'digest': (r.get('program') or {}).get('digest'), 'function': (r.get('program') or {}).get('function'), 'gates': (r.get('program') or {}).get('gates')}))" | tee "$EV/base-$1.json"
}
R73=qwen3-4b__bf16__h100__tp1__b8__i1024__o128__mixed__greedy__bi-eager; R57=gemma2-2b__bf16__l40s__tp1__b8__i1024__o128__mixed__greedy__bi-eager
R74=qwen3-4b-fp8__fp8__h100__tp1__b8__i1024__o128__mixed__greedy__bi-eager
Q=Qwen/Qwen3-4B-Instruct-2507; QR=cdbee75f17c01a7cc42f958dc650907174af0554; G=unsloth/gemma-2-2b; GR=25319945f7fd83b8b903e12081777b7eef2ba993
F=Qwen/Qwen3-4B-Instruct-2507-FP8; FR=8591804019c8b22094c3b5b4454e0edc05dffc98
H='{"compute_capability": [9, 0], "num_sms": 132}'; A='{"compute_capability": [8, 9], "num_sms": 142}'; H8='{"compute_capability": [9, 0], "fp8_block_gemm": "cutlass", "num_sms": 132}'
derive r73-step $R73 $Q $QR "$H" step &
derive r73-LP10_T8 $R73 $Q $QR "$H" request 10 8 &
derive r57-step $R57 $G $GR "$A" step &
derive r57-LP31_T52 $R57 $G $GR "$A" request 31 52 &
derive r74-step $R74 $F $FR "$H8" step &
derive r74-LP73_T1 $R74 $F $FR "$H8" request 73 1 &
wait
echo "RUNBASE-DONE $(date -u +%FT%TZ)"
