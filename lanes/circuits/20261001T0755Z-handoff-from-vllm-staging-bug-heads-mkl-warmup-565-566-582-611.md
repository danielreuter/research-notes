---
id: 20261001T0755Z-handoff-from-vllm-staging-bug-heads-mkl-warmup-565-566-582-611
campaign: verity
lane: vllm-staging-bug
kind: handoff
status: open
repo: danielreuter/verity
origin: vllm-staging-bug (bc-07a1f06e)
---

# vllm-staging-bug: the MKL warm-up is on `cursor/mkl-warmup-125e` at 0a75581c0; #565, #566 and #582 are merged with main and pushed; #611 is ready and waits only for your vLLM grant

All heads below merge cleanly into main as of 12:50 AM PDT, `aac153709` (train T49). On each of those merged trees, the vllm lint suite and the import, dead-module and by-name tests pass. Nothing was force-pushed. Every update is a merge commit or a new commit on top.

| What | Branch | Head |
|---|---|---|
| MKL warm-up (new, no PR yet) | `cursor/mkl-warmup-125e` | `0a75581c0` |
| [#565](https://github.com/danielreuter/verity/pull/565) | `cursor/vllm-sm120-fp8-noswap-422d` | `49859b522` |
| [#566](https://github.com/danielreuter/verity/pull/566) (base #565) | `cursor/vllm-sm120-nvfp4-linear-v2-422d` | `ef2634973` |
| [#582](https://github.com/danielreuter/verity/pull/582) (base #565) | `cursor/vllm-sm120-fp8-block-dot-422d` | `41c036021` |
| [#611](https://github.com/danielreuter/verity/pull/611) | `cursor/gumbel-idle-splits-c646` | `5db618fcf` (unchanged) |

## 1. The MKL first-call warm-up (your 5:11 PM PDT handoff)

- **The helper.** `compiled_relations.warm_vml()` returns False without torch. With torch, it sets intra-op threads to 1, makes one `torch.exp(torch.zeros(1))` call and restores the thread count, even if `exp` raises. Later calls do nothing. It checks for torch with `importlib.util.find_spec`, because P7 counts a swallowed `ImportError` as a violation.
- **Where it's called:**
  - `cpu_replay.main`, the `commit-replay` process, before `replay(o)`.
  - `CompiledKernelCheck.__init__` and `CompiledValueCheck.__init__`. They warm at construction rather than in `run`, because `CompiledKernelCheck.run` is already at its P10 cap.
- **`row stage replay` gets no call.** That process only spawns the `commit-replay` subprocess, which warms at its own entry point. A call in the parent would import torch for nothing.
- **Thread pools: no replay path calls a torch transcendental from a Python thread.**
  - The pools in `row_stages`, `row_tp` and `tp/fold_match` run subprocess CLIs.
  - The pools in `cpu_replay.open_weights`, `store_dump` and `replay_bundle` only hash bytes.
  - Both compiled checks run on the Commit's main thread.
  - The bi-eager replay modules use no torch transcendentals.

  So there is no pool to warm ahead of.
- **The race doesn't reproduce on this VM.** On 4 CPUs with MKL 2024.2, I got 0 of 120 cold processes and 0 of 120 warm. The fix rests on accounting's node-1 evidence: 16 of 200 cold processes, 0 of 200 warm.
- **Tests.** `tests/program/test_compiled_relations_warm_vml.py` checks four things:
  - It is a no-op without torch.
  - It makes exactly one `exp` call on one thread and restores the thread count, and a second call makes no calls.
  - The thread count is restored when `exp` raises.
  - `commit-replay` warms before it replays, and both compiled checks warm when they are constructed.
- **Suite result.** The full vllm suite (`suites.py integrations/vllm`) gave 4652 passed and 6 failed. The VM was shared with two other agents' suites, and the kernel's out-of-memory killer killed 8 processes during the run.
  - Five failures were workers killed for memory. All five pass when rerun, together with the warm-up tests: 42 passed (`mkl-rerun.log`).
  - The sixth was `test_tp_moe_members[olmoe]`, whose subprocess died with "the build process died". circuits-build-speed saw the same on this 15 GB VM (note:20261001T0618Z-handoff-from-circuits-build-speed-pr-639-grant).

## 2. #565, #566 and #582 merged with main (your 7:02 PM PDT handoff)

Each was updated with a merge commit. The step Definitions came from main untouched.

- **#565 → `49859b522`** merges main `72aacf9b2`.
  - Conflict in `program/registry/targets.py`: I kept #565's `scaled_mm_fp8_spec(profile, K, N, bias)` and main's `attention_spec(..., own_rows=None, cap=None)`.
  - The circuit-check `targets.py` merged automatically, with both sides' rows.
  - The diff against main is #565's own 5 files, +177/−6.
- **#566 → `ef2634973`** merges the new #565.
  - Same `targets.py` conflict: I kept `_fp4_dot`, `nvfp4_quant_spec` and `nvfp4_gemm_spec`, plus main's `attention_spec(cap=...)`.
  - The diff against #565 is #566's own 5 files, +288/−7.
- **#582 → `6745c6cba`, then `f5995efba` and `41c036021`.** Its GitHub base is #565, not #566, so I merged the new #565 into it.
  - Conflict in `frontend/rules/vocab.py`: I kept both #582's `scaled_mm_fp8_block_dot` and main's `layer_norm_aten`, in both `kinds` and `notes`.
  - **Two follow-up commits after the merge:**
    - `f5995efba`: main's `rows.py` plus #582's +27 lines came to 806 lines, over P10's 800-line cap. I moved #582's provenance dict verbatim into `fp8_dot_rows.py`, beside the e4m3 k32 twins it records, and `rows.py` imports it. `rows.py` is now 797 lines, and `EVALUATOR_PROVENANCE` is unchanged.
    - `41c036021`: I renamed the moved dict `CC12_TWIN_PROVENANCE`, because P8 read `sm_120` in its `__all__` string as an architecture literal.
  - Neither commit touches a Definition.
- **#566 and #582 conflict with each other.** Both append a row to the same tuples in `gemm_targets.py` and `targets.py`, and they did so before these merges too. Whichever lands second needs a merge that keeps both rows. I can do that when you say which goes first.

**circuit-check** (`uv run circuit-check <fully bound id>`, reports at art:77c534123a305d6a5b5c4f755254c67d8893e350667ae10e87edc437dd85c24b, to paste into the PR bodies):

| PR | Definition | Result |
|---|---|---|
| #565 | `ScaledMmFp8NoSwap_v1{K=64,N=2,BIAS=True,DOT=BlackwellE4m3QmmaDot32_v1}` | ok: 14 gates, 52,310 ANDs, 64 of 64 vectors equal, 2 units per call, warning redundant-gates/boolean 4254 |
| #565 | the same with `BIAS=False` | ok: 12 gates, 48,456 ANDs, 64 of 64 equal, warning 4080 |
| #566 | `QuantLinearNvfp4_v1{K=64,N=2,DOT=BlackwellNvf4OmmaDot64_v1}` | ok: 440 gates, 24 units per call, warning redundant-gates/ir 3 |
| #566 | `Nvfp4ActQuant_v1{K=64}` | ok: 432 gates, 24 units per call, warning redundant-gates/ir 3 |
| #566 | `ScaledMmNvfp4_v1{K=64,N=2,DOT=BlackwellNvf4OmmaDot64_v1}` | ok: 8 gates, 18,144 ANDs, 64 of 64 equal, warning 865 |
| #582 | `ScaledMmFp8BlockCoordinate_v2{K=256,G=128,DOT=BlackwellE4m3QmmaDot32_v1}` | ok: 16 gates |
| #582 | `ScaledMmFp8BlockSharedScale_v2{K=128,N=128,G=128,DOT=…}` | ok: 1025 gates, 11 of 11 equal, 129 units per call |
| #582 | `ScaledMmFp8Block_v2{K=128,N=128,G=128,DOT=…}` | the known `partition/gate-recomputed` (127 gates), as in the author's `r20260930-171125-33d9`. 0 new failures. |

**Tests.** Logs are at art:bc92953c8149e1061130eaa742b83e5c3d1766ee675c27cabbe1685720d858eb. I ran them in `/tmp/wt-rebase`, with that tree's packages first on `PYTHONPATH`.

- **Targeted sets**, run before the worktree had its fixtures; the full suites ran with them. These cover each PR's own tests, the cc 12.0 binding tests (`test_vllm_bindings_pins`, `test_gemm_target_correspondence`, `test_gemm_targets`, `test_target_family`, `test_declared_build_target`, `test_required_profile`, `linear/test_api`), the kernel self-check, lint and the import, dead-module and by-name tests.
  - #565: 250 passed, 3 skipped.
  - #566: 259 passed, 3 skipped.
  - #582 at `41c036021`: 308 passed, 3 skipped.
- **The whole vllm `tests/`**, after `research data fetch-fixtures --repo /tmp/wt-rebase` and without `test_tp_moe_members`, which needs more memory than this VM has:
  - #582 at `41c036021`: 4656 passed and 3 failed.
    - `test_codec` was a worker killed for memory. It passes alone.
    - `test_derive::test_hf_greedy_request_reference_mode_tokens_match_torch` failed once, with `[13, 13, 13]` against torch's `[13, 28, 21]`. It passes 3 of 3 alone, and it passed in the #566 and MKL full suites.
    - `test_pod_bootstrap::test_readiness_cpu_mode_record` is an artifact of running from a worktree: it fails the same way on main in that worktree.
  - #566 at `ef2634973`: 4663 passed and 1 failed, the same `test_pod_bootstrap` artifact.
  - #565 is contained in both of these trees.

## 3. #611 is ready

It's unchanged at `5db618fcf` and merges cleanly into `aac153709`, and lint plus `test_native_collect_splits` pass on that merged tree. It is in train C5B (`r20261001-061246-974b`). The coordinator's log at 11:39 PM PDT says "#611 #640 need vllm grant", and the PR has no labels, so your grant is the only thing it waits on.

**Next, when asked:** wire `prescribe_idle_splits` into the TP rank path (`taps.attach_rank`), so that TP2 Gumbel with B>1 binds its splits. I'm holding that until you say. I'm leaving the worktrees `/tmp/wt-rebase` and `/tmp/wt-611` in place.
