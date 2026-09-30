---
id: 20260930T2250Z-handoff-from-vllm-tp2-gpuless-build-tp2-builds-without-gpus
campaign: overnight-sep30
lane: vllm-coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: vllm-tp2-gpuless-build (bc-217501a5), for @old-circuits-and-proofs (bc-ecac3029) and @circuits (bc-b8aaadaa)
cursor:
  subagentId: "bc-217501a5-aa77-56c0-b6c5-dc3a7291ec1f"
---

# A TP2 Build now runs with no GPUs, and its digests equal a GPU-visible Build's

**Branch:** `cursor/tp2-gpuless-build-ec1f` @ `4009ec303`, against main `73eee4931`. It's pushed, but no PR is open:
`gh` here is read-only and returns 401. Open it from https://github.com/danielreuter/verity/pull/new/cursor/tp2-gpuless-build-ec1f.

**The change** (3 files, +41 −8; Build path only):
- `export_compat.select_cuda_platform(world)`: once #536's hook has resolved the CUDA platform for a declared target, the platform's
  `device_count()` answers `world` instead of the host's visible count.
- vLLM's only Build-time device check is `ParallelConfig.__post_init__` (`config/parallel.py:959`). It now passes on a GPU-free
  host, and the executor backend resolves to `mp`, as it does on a host with 2 GPUs.
- `build.run` passes `tp`. `row_tp.TpRow` already passed `--target` to every per-rank derive (including Match's served-shape
  derives), so nothing else changes. `manifest build-global` and `global-program` never read the device.
- Rows without a declared target still count the host's devices. The Commit and serving never reach `build.run`.

**Equality** (row `llama32-1b__bf16__rtxpro6000__tp2__b1__i256__o32__mixed__greedy__bi-eager`, the same tree `4009ec30`, vy-nebius-1):

| | CPU-only `r20260930-212809-14a0` | GPU-visible, Kueue `r20260930-220713-8e26` |
|---|---|---|
| Visibility | `CUDA_VISIBLE_DEVICES=`, libnvidia-ml refused 4×, `nvidia-smi` stubbed | 2 GPUs (`torch.cuda` 2) |
| vLLM platform | `NonNvmlCudaPlatform` | `NvmlCudaPlatform` |
| step Program r0 / r1 | `d29ee587…` / `c3765e95…` | the same |
| request Program r0 / r1 | `d58e82aa…` / `3b69d0fd…` | the same |
| correspondence digests (4) | `392a3269…`, `84b78372…`, `e6dabefc…`, `32dc4aab…` | the same |
| workload r0 / r1 | `f6383f05…` / `6ceecbaf…` | the same |
| manifest digest / Program digest | `bb87df12…` / `0b3c065e…` | the same |
| Build, word check | PASS in 220 s; 2/2 word lines | PASS in 191 s; the same |
| peak memory (PSS) | 14.3 GiB | 6.8 GiB |

The GPU-visible reference ran as a `prover-dev` job on `deployments-gpu` (2 GPUs). No earlier 2-GPU Build of this row was on a
recent tree: the 06:30Z ones predate #536 and have other digests. The CPU Attempt's rc=1 comes from the harness wrapper after the
digest print (#536's equality runs show the same). The row's Build stage exited 0.

**Tests:**
- New: `test_declared_build_target.py` (+3). Rank 0 and rank 1 of a declared TP2 target count 2 devices on a host showing 0. An
  undeclared TP2 Build keeps the host's count.
- Lints (P01 to P11), `test_config_run.py`, `test_tp_world_n.py` and `test_declared_build_target.py` pass.
- vLLM suite `-m "not pod"` (`-n 8`): 16 failures, none unexpected.
  - 13 fail on clean main too (the missing `topp_split_fixture` / GPU-fixture files, and `test_kernel_dump`).
  - 3 pass when rerun alone on this branch: `test_derive_transfer::test_transfer_summary_written`, `test_codec::test_v1_kv_cache…`, and
    `test_tp_moe_members[qwen3-30b-a3b…tp2…]`. They failed from `-n 8` contention.
- `test_tp_moe_members` passes for both pinned TP2 MoE records (qwen3-30b-a3b and olmoe on l40s), so no record digest moves.

**Needs a decision or an owner:**
1. Open the PR. I can't from here.
2. Only rows with a declared target build GPU-free: `__rtxpro6000__` rows, or a workload `target`. An l40s/h100 TP2 row's Build still
   needs its GPU, as before.
3. The first TP2 deployment through `config-run` (a 0-GPU Build, then a 2-GPU Commit) is the canary for the Commit half: `TpRow`
   reads `build/rank<r>/` and `manifest.json` from the shared `SWEEP_DIR/<row>`, but I haven't run that Commit.
