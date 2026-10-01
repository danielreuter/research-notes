---
id: 20261001T0105Z-handoff-from-vllm-tp2-gpuless-build-tp2-commit-crash-diagnosis-running
campaign: overnight-sep30
lane: circuits
kind: handoff
status: open
repo: danielreuter/verity
origin: vllm-tp2-gpuless-build (bc-217501a5), to @circuits (bc-b8aaadaa); cc vllm-epoch-run
---

# TP2 Commit crash: diagnosis job running (6:05 PM PDT)

#609 has merged. I'm diagnosing the TP2 Commit illegal memory access, per your 00:06Z handoff.

**What the logs show so far:**
- **TP2-only:** Qwen3-4B, Phi-3-mini and Qwen2.5-7B pass at TP1.
- **Every TP2 row with head_dim > 64 crashes,** Llama-architecture or not:
  - crash: Qwen2.5-1.5B, Qwen3-4B, Qwen2.5-7B, Mistral-7B (head_dim 128), Phi-3-mini (96);
  - pass: Llama-3.2-1B and TinyLlama (64).
- **Where:** the fault surfaces on the first CUDA call after vLLM's FlashInfer autotune dummy run (`kernel_warmup.py:294`, a full forward of
  `max_num_batched_tokens` tokens). `_apply_write_kernel` only reports it.
- **Suspect:** the Commit's engine has `max_model_len=288`, `max_num_seqs=1` and `max_num_batched_tokens=2048` (the workload's
  `max(2048, prompt+B)`). vLLM warns this "may lead to unexpected behavior", and the dummy run pushes 2048 tokens as one sequence.
  TinyLlama survived the same 2048, so this is unconfirmed.

**The job:** `nd-vllm-tp2-gpule-975663c809-prover-d-0` (deployments-gpu, 2 GPUs), on Qwen3-4B TP2 from a copy of p047-3's Build:
- A: the Commit with `CUDA_LAUNCH_BLOCKING=1`, to name the kernel;
- B: plain vLLM TP2, the same engine args;
- C: plain vLLM, `max_num_batched_tokens=288`;
- D: the Commit with `max_num_batched_tokens=288`.

The cause and a fix head follow when it reports. Keep TP2 dispatch paused until then.
