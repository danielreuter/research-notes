---
lane: vllm-sm120-attention
kind: report
created: 2026-09-30T02:53Z
status: open
---

CHECKPOINT 08658275 (03:06Z) [open] WAITING r20260930-030444-c4b5 on vy-sm120-attention-1 (pod 2c11k8o7d6xu7y), check after 03:28Z; agent bc-366317cb-3bc9-590d-bc5e-9b9bc9940ec6; next: read the FA2 capture (MUFU, tile, v2_hopper/v3_ampere/fa2_check_inf rows, engine), then the registration on cursor/vllm-sm120-attention-0ec6
CHECKPOINT 08658275 (03:01Z) [open] pod estimate: vy-sm120-attention-1 (RTX PRO 6000 Blackwell Server Edition, SECURE on-demand, 1 GPU, $2.09/h, --max-hours 3): ~1.5 GPU-h, ~$3.1 (bootstrap ~15 min, FA2 capture + MUFU + engine check ~30-45 min); lane share $12; capture script at cursor/vllm-sm120-attention-0ec6@08658275
CHECKPOINT d993873f (02:53Z) [open] source read of vLLM d9105ea8 + vllm-flash-attn 506341a: cc12 selects FLASH_ATTN/FA2, num_splits=1 under batch invariance, FA2 is 8.0+PTX so sm_120 runs a driver JIT, kBlockN arch-free; Check_inf only in masking steps. Next: capture script, then pod vy-sm120-attention-1
