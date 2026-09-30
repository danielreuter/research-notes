---
id: 20260930T2308Z-handoff-from-circuits-tp2-canary
campaign: verity
lane: vllm-epoch-run
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# @circuits: TP2 comes back as ONE canary in config-run's split form (0-GPU Build, then a 2-GPU Commit); the subset only if it passes

The GPU-less 2-rank Build works: `cursor/tp2-gpuless-build-ec1f` @ `4009ec303`. The CPU-only Build `r20260930-212809-14a0` has digests
equal to a GPU-visible one (`r20260930-220713-8e26`): 220 s, 14.3 GiB. Details are in
`lanes/nebius-infra/20260930T2250Z-handoff-from-vllm-tp2-gpuless-build-tp2-can-use-config-run-split.md`.

1. **Merge `cursor/tp2-gpuless-build-ec1f` into your run branch** (`cursor/coverage-v1-2622`); pre-merge is fine.
2. **One canary:** `llama32-1b__bf16__rtxpro6000__tp2__b1__i256__o32__mixed__greedy__bi-eager` as
   `{"template": "config-run", "class": "tp2", …}` (Build on CPU, node 2 eligible; Commit on 2 GPUs of node 1, `NCCL_P2P_DISABLE=1`
   via `row_tp`). Research question: *does a TP2 Commit on sm_120 run from a CPU-built 2-rank Program, and replay 460/460 summed over
   ranks?* This also retests `cov-p002-2`'s Commit crash (rank 1, illegal memory access; the P2P setting wasn't the cause).
3. **If it passes:** the owner-approved TP2 subset, in the same form: ~10 models × B1/B8 at 256/32, plus OLMoE and Qwen3-30B-A3B. Keep
   `TP2_MAX` small (2 at a time) and the 150 GB bundle hold.
   **If it fails:** hold TP2 again, and send the Commit log to me and `lanes/vllm-tp2-gpuless-build/`.
4. No `config-run-row` TP2 again: that's the form that held 2 GPUs through the Build.

Good to see the first #557 Qwen2.5 passes (k03, n093, n086) and g142.
