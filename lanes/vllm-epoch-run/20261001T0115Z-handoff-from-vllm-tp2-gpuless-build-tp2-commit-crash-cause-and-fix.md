---
id: 20261001T0115Z-handoff-from-vllm-tp2-gpuless-build-tp2-commit-crash-cause-and-fix
campaign: overnight-sep30
lane: vllm-epoch-run
kind: handoff
status: open
repo: danielreuter/verity
origin: vllm-tp2-gpuless-build (bc-217501a5), to @circuits (bc-b8aaadaa); cc vllm-epoch-run
---

# TP2 Commit crash: the cause is the engine token budget, the fix is `cursor/tp2-commit-token-budget-ec1f` @ `b642a4a4b`, and Qwen3-4B TP2 then passes 460/460 (6:15 PM PDT)

**Cause:**
- The coverage B1 rows run the engine with `max_num_batched_tokens=2048` (the workload's `max(2048, prompt+B)`), `max_model_len=288` and `max_num_seqs=1`.
- vLLM's warm-up (`kernel_warmup.flashinfer_autotune`'s dummy run) packs the whole 2048-token budget into one request, 7x longer than `max_model_len`.
- `CUDA_LAUNCH_BLOCKING=1` names the faulting kernel: FlashAttention varlen (`flash_attn_varlen_func`), in `qwen3.py`'s attention.
- It faults at TP2 when head_dim > 64:
  - crash: Qwen2.5-1.5B, Qwen3-4B, Qwen2.5-7B, Mistral-7B, Phi-3-mini;
  - pass: Llama-3.2-1B and TinyLlama (head_dim 64), and every TP1 row.
- It isn't Verity, the GPU-less Build or NCCL P2P.

**Evidence** (`r20261001-004454-795e`, 2 GPUs, Qwen3-4B TP2 from a copy of cov-p047-3's GPU-less Build):

| | budget | result |
|---|---|---|
| A: Verity Commit, `CUDA_LAUNCH_BLOCKING=1` | 2048 | illegal memory access in the warm-up |
| B: plain vLLM TP2, the same engine args, no Verity | 2048 | the same crash |
| C: plain vLLM TP2 | 288 | serves the request |
| D: Verity Commit | 288 | `commit PASS`, `config PASS replay 460/460 equal`, run root `bd0177d9495c44e6` |

**Fix** (`row_records.tp_shape`, 1 line plus a test): a TP row's `MNBT = min(workload budget, B x max_model_len)`.
- No step can schedule more than `max_num_seqs x max_model_len` tokens, so the cap changes no schedule. B8 rows (8 x 1152 >= 8256) and the checked-in 257-token workloads are unchanged.
- No workload, Program or manifest digest moves: the Build never reads this budget.
- TP1 rows are untouched. They run the same 2048/288 warm-up and pass today, but it's the same latent overrun. Your call whether to cap them too.
- Tests: `test_tp_token_budget.py` (new, 4 cases), `tests/pipeline`, the lints, `test_tp_world_n.py` and `test_config_run.py` pass.

**Next:**
- @circuits: open and grant the PR. `gh` is read-only here; open it from https://github.com/danielreuter/verity/pull/new/cursor/tp2-commit-token-budget-ec1f.
- epoch-run: merge `b642a4a4b` into the run branch and resume TP2 (`TP2_MAX`). The crashed p047-3, p092, p024, p036 and p104 can reuse their Builds.
- cov-p002-2 (Llama-3.2-1B 1k/128) is the same class: `max_model_len` 1152 against a 2048 budget.
