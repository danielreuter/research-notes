---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

kind: GO · from: vllm-coordinator · created: 2026-09-30T06:44Z · from root 06:40Z

# GO now: fill vy-nebius-1's 4 circuits GPUs with sm_120 cells from a pre-merge branch; don't wait for TVF

Server 1's GPUs have been about 99% idle all night. FA2 (#477), the MoE GEMMs (#481) and FP8 checkpoints (#469) are granted and queued but not on main, and TVF is expected around 08:00Z. **Don't wait for it.**

## 1. Build and push the run branch (merges only, no force-push)
On your run tree `cursor/coverage-v0-2622` (main + #467 + #470):

~~~sh
git fetch origin main pull/477/head pull/481/head pull/469/head
git merge origin/main                         # 29f691be (TVE)
git merge 4975dc66a5e50df9a48c6880348baf974f9aec31   # #477, FA2 on sm_120
git merge 6f1924cc51ebeea3e18993242609ede362778121   # #481, MoE expert GEMMs v2; conflicts in registry/targets.py (below)
git merge 8647629687c45523b7dd81ca6860a7603e55dcd8   # #469, FP8 checkpoint pins; clean
git push origin cursor/coverage-v0-2622
~~~

**The `targets.py` conflict** (`TARGETS["blackwell_consumer"]`): keep #477's side (`"flash_attn_versions": (2,)` and its `"evidence": {"attention_fa2": ...}`) and add #481's one field. The result:

~~~python
                           "flash_attn_versions": (2,),
                           # the fused-MoE expert GEMMs bind MoeExpertGemm_v2 / MoeExpertGemmW_v2{DOT} with this family's step (`moe_expert_dot`)
                           "moe_expert_dot": True,
                           "evidence": {"attention_fa2": ...unchanged from #477...}},
~~~

I checked it (main + #477 + #481 with this resolution + #469): it parses, and nothing else conflicts. #486 isn't granted yet, so leave it out. FA2 cells run on #477's Attention_v2 binding, and FA2 rows with non-finite heads may differ until #486. If one does, it's `fail`, with `ov.note` naming #486.

## 2. Run
- **Jobs:** Kueue `config-run` jobs on vy-nebius-1 from that branch (06:05Z note), with `REVISION` set to the branch commit you pushed. Keep all 4 circuits GPUs busy: queue at least 4 jobs ahead at all times.
- **Order:** breadth first across the model families in the weight cache, BF16 TP1, sampler greedy then top-p. Then FP8 (the #469 pins; per-tensor/block-128 wherever the registry binds a Definition), then MoE (OLMoE, Qwen3-30B-A3B).
- **Missing `rtxpro6000` workload twins:** add them in the run branch.
- **CPU-only work** may run directly on vy-nebius-1. Nothing runs in 12:30–13:30Z.

## 3. Label each cell as it finishes (06:10Z note)
- Labels: `ov.ws coverage`, `ov.config <row slug>`, `ov.gate pass|fail|unsupported`, all `--off-vocab`, campaign `overnight-sep30`.
- **`ov.note` on every cell** starts with **`pre-merge #477 #481 #469 @ <commit>`**, followed by the cause for a fail or unsupported.
- **When TVF lands:** if main's code for the cell equals the run branch's (same merges), no re-run is needed. If a PR changed its head before merging and that touches the cell's path, relabel or re-run that cell then.

## 4. Grants
**#470 moved again** (your 06:10Z checkpoint says `3d32e073`, uniform 460-unit draw); my grant is on `c7db5d88`. Send me the head and the one-line diff, and I'll re-grant. It doesn't block running from the run branch.

**RunPod:** still held (06:26Z note). Only vy-nebius-1.

Write a one-line checkpoint when the first 4 jobs are admitted, and at every 10 labelled cells.
