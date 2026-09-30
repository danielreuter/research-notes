---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-epoch-run · kind: checkpoint · created: 2026-09-30T06:40Z

**23 cells labelled, all `unsupported`, each with the refusal quoted from the code in `ov.note`.** 10 are one attempt each (u01-u10: top-k, FP8 off Hopper x2, per-tensor FP8, NVFP4, TP4 over 9 heads, TP2/TP4 matching your 06:09Z rows, Qwen1.5-MoE, phi-2). The 13 sm_120 twins share `r20260930-063524-f1d7` with a `--ref` each: every one refuses "flash_attn_version 2 on blackwell_consumer (12.0): no registered attention chain" until FA2 #477/#486 lands. The 14 RunPod run cells are held and unlabelled.
