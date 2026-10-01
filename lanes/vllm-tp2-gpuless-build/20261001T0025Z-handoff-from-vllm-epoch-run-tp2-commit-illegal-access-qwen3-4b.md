---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
---

lane: vllm-epoch-run · kind: handoff · to: vllm-tp2-gpuless-build, cc @circuits · created: 2026-10-01T00:25Z

# TP2 Commit crash: Qwen3-4B TP2 B1 (cov-p047-3), CUDA illegal memory access in vLLM's kernel warm-up; the split form otherwise holds

In the TP2 subset (config-run split: your GPU-less 2-rank Build, then a 2-GPU Commit; tree `cursor/coverage-v1-2622` @ `9d7189fa`, which has
your branch @ `4009ec30`), three deployments have finished:

| deployment | row | Commit |
|---|---|---|
| cov-p000 | llama32-1b TP2 B1 256/32 greedy | pass, `r20260930-234646-6dab`, 460/460 summed over the ranks |
| cov-p012-3 | tinyllama-11b TP2 B1 256/32 greedy | pass, `r20261001-000824-8e44` |
| **cov-p047-3** | **qwen3-4b TP2 B1 256/32 greedy** | **fail**, `r20261001-001247-8a51` |

**p047, what happened:**
- The Build passed GPU-less: step `dff20b55…`/`98620d04…`, manifest `1f59ff16…`, 49830 identities, 0 unbound peer bindings.
- The Commit died 54 s in, during vLLM's `compile_or_warm_up_model` → `warmup_kernels` → the warm-up prefill, before the instrumented run.
- The CUDA illegal memory access is reported asynchronously, so the kernel that faulted isn't in the traces:
  - rank 0: `RuntimeError: Triton Error [CUDA]: an illegal memory access`, at `model_runner.add_requests` → `apply_staged_writes` →
    `_apply_write_kernel`'s `load_binary`;
  - rank 1: `torch.AcceleratorError … illegal memory access`, at `model_runner.shutdown`'s synchronize.
- Settings are identical to the passing p012: custom all-reduce off, CUDA graphs off, FLASH_ATTN, taps `norm_tap` and `vocab_tap`, and
  `NCCL_P2P_DISABLE=1` via `row_tp`.
- This is the error class of cov-p002-2's rank-1 crash: Llama-3.2-1B TP2 B1, but 1k/128, while Llama-3.2-1B at 256/32 passes.

**Logs:** on vy-nebius-1, `/workspace/jobs/cov/cov-p047-3/qwen3-4b__bf16__rtxpro6000__tp2__b1__i256__o32__mixed__greedy__bi-eager/`.
- `commit.log` has both ranks' tracebacks, from line 62.
- `row.log` and `stages.txt` are beside it.
- The attempt is `r20261001-001247-8a51`.

A `CUDA_LAUNCH_BLOCKING=1` rerun of that Commit would name the kernel; I haven't run one.

**Update 00:35Z: two more crashed the same way, and I have paused new TP2 dispatch** (`TP2_MAX` 0).

| deployment | row | Commit |
|---|---|---|
| cov-p092 | qwen25-15b TP2 B1 256/32 greedy | fail, `r20261001-002007-5d78`, 51 s in; the Build passed (step `9887ad34…`/`81ad892c…`) |
| cov-p024 | phi3-mini TP2 B1 256/32 greedy | fail, `r20261001-002307-7394`, 57 s in; the Build passed (step `3d45ab66…`/`5aa5119f…`) |

- Both crashed in the same warm-up path (`warmup_kernels`), with the same illegal memory access on both ranks.
- **The pattern so far is by architecture, not size:** the two Llama-architecture models pass (Llama-3.2-1B, TinyLlama-1.1B), and Qwen2.5-1.5B,
  Qwen3-4B and Phi-3-mini crash.
- Two deployments are still in flight and will test it: cov-p036 (Mistral-7B, Llama-like) and cov-p104 (Qwen2.5-7B).
- The logs are in the same place for each row: `/workspace/jobs/cov/<cov-id>/<row>/commit.log`.
- The rest of the TP2 subset (OLMoE and Qwen3-30B B1, and every B8) waits until you or @circuits say otherwise.
