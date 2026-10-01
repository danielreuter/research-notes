---
id: 20261001T0810Z-report-from-vllm-config-run-tp2-p051-staging-fix-pass
campaign: overnight-sep30
lane: circuits
kind: report
status: open
repo: danielreuter/verity
origin: vllm-config-run-tp2 (bc-35ab914e), follows note:20261001T0735Z-report-from-vllm-config-run-tp2-tp2-gaps-staging-fixed-three-diagnosed
cursor:
  subagentId: "bc-35ab914e-d276-5d3b-bab0-9f87a3ef3847"
---

@circuits: **the staging fix is proven.**

- **Run:** `vllm-config-run-tp2/cov-p051-gaps1` (Qwen3-4B TP2 B8, the epoch tree `5bab849b1` plus `cursor/tp2-gaps-3847` @ `d6d1e2aa1`).
- **Result:** commit PASS rc 0 (612 s); config PASS, replay 460/460 equal, run root `313770563ba7b123`.
- **What changed:** the warm-up learned step 0's plan on both ranks with 0 errors. Before the fix, p051-3 failed there at 4352/4096 MiB.
- **Preemptions:** it finished at 07:28Z inside the termination grace of the second preemption. I deleted the third requeued attempt so it couldn't overwrite the record. The record is copied to `/workspace/research/runs/cfgtp2-cpu/p051-gaps1-pass/` on node 1.
- **p108 and p040** have the same cause, and the epoch run can resubmit them on a tree with `d6d1e2aa1`. I didn't spend GPUs on them tonight.
- **Gemma-2, OLMoE and Qwen3-MoE:** the 0735Z note has the diagnoses. I'm waiting on who owns the manifest/capture changes for Gemma-2 and OLMoE; Qwen3-MoE is next on my side.
