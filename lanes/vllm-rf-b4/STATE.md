---
id: vllm-rf-b4/state
lane: vllm-rf-b4
kind: state
updated: 2026-09-25T09:22Z
---
# b4 (engine and hooks): state

Coordinator: vLLM coordinator bc-ba6cec03. Agent: bc-95aa165d. Worktree `~/projects/verity-wt/rf-b4`, branch
`lane/vllm-rf-b4`. **a4 base: 10996616.** Budget $25 of pod spend. Deadline (coordinator 09:03Z): 13:00Z.

## Scope (SYNTHESIS §6 B4, behavior-preserving part of D12)
- `engine/` builds vLLM from the pinned record; `engine/env.py` is the only writer of vLLM env pins, at construction.
- `engine/hooks.py` owns every vLLM/torch patch (FA taps, Triton hook, collective hooks, observer install, setattr on
  vLLM/torch objects); each hook uninstalls; a test shows uninstall restores the originals.
- P9 `runtime-patch` allowlist entries cleared as sites move.
- Engine build entry point signature stays stable (a5 builds `verity_vllm.LLM` on it).
- No identity changes (C3's).

## Done
- `5ddb68f8` (pushed) `engine/hooks.py`: `patch`/`wrap`/`append`/`patched`/`Hooks` (LIFO uninstall), `triton_launch`.
  Every patch site moved onto it: Triton launch hook (observe/triton_adapter, program/frontend/triton_capture),
  FA2 `varlen_fwd` / FA3 `fwd` taps (hidden_source), moe/partial/compiled/compiled_kernel sources, sampler install,
  vllm_adapter Capture, rank_worker collectives + forwards, native_host / native_collect, export_compat
  (target profile, moe_ops_traced, tensor_data_as_detach, tuned-table cache), export_ops (tp_group_override,
  vocab-parallel binding), pipeline/build + commit. All **43** P9 `runtime-patch` entries deleted; P9 now requires
  `setattr` on imported objects to live in `engine/hooks.py` only. `tests/engine/test_hooks.py`: uninstall restores
  originals (plain, class attr, inherited, by-value torch config, real Triton `JITFunction.run`, torch/vLLM targets).
  Not yet run: lints and tests run on the CPU pod next.

## Running
- (nothing yet) CPU pod `vyv-rf-b4-cpu` for lints + gate (b) head vs base next.

## Next
1. CPU pod: lints + gate (b) at head and at 10996616 side by side.
2. `engine/env.py`: move the vLLM env-pin writers (engine_profile.apply_env, vllm_meta import-time setdefaults,
   `os.environ.update(target.env())` in vllm_adapter/pipeline, VLLM_DISABLE_COMPILE_CACHE) behind it; P7 ENV_OWNERS.
3. Gate (a) on a big-memory pod; GPU rows #101 (L40S, FA2 tap + non-interference), TP2 #70 (2x L40S).

## Open questions (none blocking)
- `engine.hooks` sits in the `core` P9 layer (stdlib only; a test asserts it imports nothing from `verity_vllm`), so
  observe/program/commit can call it without an engine<->observe package cycle. The package-cycle check treats it as
  its own package. Say if you want it elsewhere.
- P9 `_constructs` refinement: `setattr` on an object the function itself constructed (CapWords call or `fresh`) isn't
  a runtime patch; that cleared 7 false positives (registry `PrimitiveDefinition(...)`, generic `types.ModuleType`).
- `build_engine` / `engine_kwargs_for` signatures unchanged. The vllm_adapter -> build.py file split is left to B5
  (39 importers).
- Code identity: `construction_version` moves (export_compat, export_ops, triton_capture, pipeline/build.py are
  construction sources). Before/after values go in READY.md; no Program/manifest/commitment digest change intended.

## Found, not fixed
- none
