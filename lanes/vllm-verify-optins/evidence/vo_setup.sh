#!/usr/bin/env bash
# vo_setup.sh: the CPU pod for vllm-verify-optins.  (1) pod_bootstrap.sh --cpu (venv312, vLLM d9105ea80 + torch cu129, the checkpoints of
# rows #57 / #73 / #74, readiness.json); (2) the smoke Build: the step Program of #73 (FA3, sm_90 / 132 SMs) and of #57 (FA2, sm_89 /
# 142 SMs) derived on this GPU-less host under the record's device target, each checked against the record's step digest and for a
# FlashAttention backend (the one risk: a non-CUDA platform choosing another attention backend).  Last line SMOKE-OK or SMOKE-FAIL.
set -u
L=$RESEARCH_RUN_DIR; EV=$L/evidence; mkdir -p "$EV"; T=$PWD
(cd integrations/vllm && bash verity_vllm/ops/pod_bootstrap.sh --cpu --cases GEMMA2_2B,QWEN3_4B,QWEN3_4B_FP8 --out /workspace/bootstrap) > "$L/bootstrap.log" 2>&1
echo "bootstrap rc=$? $(date -u +%FT%TZ) $(tail -1 "$L/bootstrap.log")"
cp /workspace/bootstrap/readiness.json "$EV/" 2>/dev/null
export PATH=/workspace/venv312/bin:$PATH HF_HOME=/workspace/hf HF_HUB_OFFLINE=1 VLLM_BATCH_INVARIANT=1 CUDA_VISIBLE_DEVICES="" TOKENIZERS_PARALLELISM=false
export PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src:$T/protocols/sampled_proofs
python -c "import verity_sampled_proofs, vllm, torch; from vllm.platforms import current_platform as p; print('platform', type(p).__name__, getattr(p, 'device_name', None), 'vllm', vllm.__version__, 'torch', torch.__version__, 'cuda', torch.cuda.is_available())"
cd integrations/vllm
ok=1
smoke() {  # LABEL ROW REPO REV TARGET RECORD_STEP_DIGEST
  local out=/workspace/vo/smoke/$1
  rm -rf "$out"
  python -m verity_vllm.pipeline.cli build --model "$3" --revision "$4" --wrapper step --M 8 --pos0 8 --max-model-len 1152 \
    --workload "workloads/$2.json" --out "$out" --target "$5" > "$L/smoke-$1.log" 2>&1
  echo "smoke $1 rc=$? $(date -u +%FT%TZ)"
  python - "$out/result.json" "$6" "$1" "$EV/smoke-$1.json" <<'PY' || ok=0
import json, sys
r = json.load(open(sys.argv[1]))
impls = sorted({str(v.get("impl")) for v in (r.get("attention_impls_observed") or {}).values()})
backs = sorted({str(v.get("backend")) for v in (r.get("attention_impls_observed") or {}).values()})
favs = sorted({str(v.get("vllm_flash_attn_version")) for v in (r.get("attention_impls_observed") or {}).values()})
facts = (r.get("target") or {}).get("consulted") or {}
s = {"label": sys.argv[3], "ok": r.get("ok"), "program_digest": (r.get("program") or {}).get("digest") or r.get("program_digest"),
     "record_step_digest": sys.argv[2], "attention_impls": impls, "attention_backends": backs, "flash_attn_versions": favs,
     "platform": facts.get("platform"), "platform_class": facts.get("platform_class"), "cuda_available": r.get("cuda_available"),
     "unsupported": r.get("unsupported"), "exception": (str(r.get("exception"))[:400] if r.get("exception") else None),
     "wall_secs_total": r.get("wall_secs_total"), "max_rss_mb": r.get("max_rss_mb")}
s["digest_equal"] = s["program_digest"] == s["record_step_digest"]
s["flash_attention"] = impls == ["vllm.v1.attention.backends.flash_attn.FlashAttentionImpl"]
json.dump(s, open(sys.argv[4], "w"), indent=1)
print(json.dumps(s))
sys.exit(0 if (s["ok"] and s["digest_equal"] and s["flash_attention"]) else 1)
PY
}
smoke r73-step qwen3-4b__bf16__h100__tp1__b8__i1024__o128__mixed__greedy__bi-eager Qwen/Qwen3-4B-Instruct-2507 cdbee75f17c01a7cc42f958dc650907174af0554 \
  '{"compute_capability": [9, 0], "num_sms": 132}' 72b2fabb4c89d17770b32f1a1faac36a37492cff3d3ae20b4ef7cea081fbd047
smoke r57-step gemma2-2b__bf16__l40s__tp1__b8__i1024__o128__mixed__greedy__bi-eager unsloth/gemma-2-2b 25319945f7fd83b8b903e12081777b7eef2ba993 \
  '{"compute_capability": [8, 9], "num_sms": 142}' 30d7b1acac4b3cff9b3bdfe2f3af81468dc9be00023fcbf331e229d4046c7134
[ $ok = 1 ] && echo "SMOKE-OK $(date -u +%FT%TZ)" || echo "SMOKE-FAIL $(date -u +%FT%TZ)"
