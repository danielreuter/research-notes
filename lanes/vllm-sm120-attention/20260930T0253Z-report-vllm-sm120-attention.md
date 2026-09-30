---
lane: vllm-sm120-attention
kind: report
created: 2026-09-30T02:53Z
status: open
---

CHECKPOINT cfcbfcef (03:52Z) [open] WAITING gate (b)+lints on vy-sm120-attention-2 (pod x8zpxecwqjekb5): base r20260930-034927-48b4 (f740c1d5) and head r20260930-035219-a82d (cfcbfcef), concurrent after the base bootstrap; r20260930-035023-a534 stopped while waiting (no tests ran). check after 04:15Z; agent bc-366317cb-3bc9-590d-bc5e-9b9bc9940ec6; PR #477 draft; next: jdiff, handoff
CHECKPOINT cfcbfcef (03:48Z) [open] pod estimate (revised: no CPU stock at 8 or 16 vCPU in any flavor): vy-sm120-attention-2 (RTX PRO 6000 Server Edition, SECURE on-demand, $2.09/h, --max-hours 3) for gate (b) + lints, base f740c1d5 and head cfcbfcef on the same pod: ~1.5 GPU-h, ~$3.1; lane total then ~$4.4 of $12
CHECKPOINT cfcbfcef (03:46Z) [open] pod estimate: vy-sm120-attention-cpu-1 (RunPod CPU cpu3g, 16 vCPU, --max-hours 3) for gate (b) + lints, base f740c1d5 (PR #465 tip) and head cfcbfcef on the same pod: ~1.5 h, ~$1; lane spend so far ~$1.30
CHECKPOINT b5c84fa4 (03:38Z) [open] captures done, pod vy-sm120-attention-1 terminated 03:38Z (~0.62 GPU-h, ~$1.30). FA2 on sm_120 = Attention_v2{DOT=Hopper,INV=Fa2InvSum} on all 122,228 finite heads (Attention_v3: 997 heads differ); MUFU = core tables; tile = fa2_kblock_n; FA2 taps exact 76/76 x2. Runs r20260930-033258-f611 (art:d342a748), r20260930-030755-9aab (art:592bc0ae). Next: registration commit
CHECKPOINT 08658275 (03:08Z) [open] WAITING r20260930-030444-c4b5 (FA2 capture) and r20260930-030755-9aab (FA2 tap build + fa_tap_exactness, default + guarded) on vy-sm120-attention-1, check after 03:28Z; agent bc-366317cb-3bc9-590d-bc5e-9b9bc9940ec6; next: read both, registration PR
CHECKPOINT 08658275 (03:06Z) [open] WAITING r20260930-030444-c4b5 on vy-sm120-attention-1 (pod 2c11k8o7d6xu7y), check after 03:28Z; agent bc-366317cb-3bc9-590d-bc5e-9b9bc9940ec6; next: read the FA2 capture (MUFU, tile, v2_hopper/v3_ampere/fa2_check_inf rows, engine), then the registration on cursor/vllm-sm120-attention-0ec6
CHECKPOINT 08658275 (03:01Z) [open] pod estimate: vy-sm120-attention-1 (RTX PRO 6000 Blackwell Server Edition, SECURE on-demand, 1 GPU, $2.09/h, --max-hours 3): ~1.5 GPU-h, ~$3.1 (bootstrap ~15 min, FA2 capture + MUFU + engine check ~30-45 min); lane share $12; capture script at cursor/vllm-sm120-attention-0ec6@08658275
CHECKPOINT d993873f (02:53Z) [open] source read of vLLM d9105ea8 + vllm-flash-attn 506341a: cc12 selects FLASH_ATTN/FA2, num_splits=1 under batch invariance, FA2 is 8.0+PTX so sm_120 runs a driver JIT, kBlockN arch-free; Check_inf only in masking steps. Next: capture script, then pod vy-sm120-attention-1
