---
id: vllm-rf-b4/state
lane: vllm-rf-b4
kind: state
updated: 2026-09-25T10:19Z
---
# b4 (engine and hooks): state

> **Coordinator, 10:01Z: the vyv- pod deadline is now 2026-09-25T14:00Z (7 AM PT)**, extended in steps of at most 4 h while the coordinator runs; register results as they land.

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
- `619b7451` (pushed) `engine/env.py`: the one writer of vLLM's env pins (ENGINE table = engine_profile.DECLARED_ENV,
  EXPORT table = vllm_meta's five, apply_target for `TargetProfile.env()`, compiled per-process Inductor dir +
  VLLM_DISABLE_COMPILE_CACHE). Callers write at the same points as before. P7: env.py is ENV_OWNERS, 17 environ
  entries deleted, new check that no other library module writes a VLLM_/HF_/TORCHINDUCTOR_/TOKENIZERS_ switch.
  `construction_version` also hashes engine/env.py.
- `3bdcd0ad` (pushed) P11: the moved docstring loses its board tag (2 entries deleted).
- Lints at head `3bdcd0ad`: 47 passed; at base 45 passed (vyv-rf-b4-cpu).
- `0f71b5b4` (pushed) tests: the MoE export shim test imports vLLM's fused_moe before it records the packet.

## Running (pods registered, guard 90)
- `vyv-rf-b4-cpu` (eroe8y957ahhjr, cpu3g 32 vCPU / 128 GB): gate (b) at 3bdcd0ad `r20260925-095236-2684` (57 F / 11 E
  / 286 S; the one new failure was my own test's expectation, fixed in `0f71b5b4`) and base `r20260925-095250-e4e8`
  (56 F / 11 E / 286 S). Rerun at `0f71b5b4` in a fresh tree: `r20260925-101530-aa45`.
- `vyv-rf-b4-g1` (17ez42q6mb3wo2, 1x L40S, 188 GB cgroup): `r20260925-100039-940f` = bootstrap OK, #101
  build,match,commit (FA2 tap) at head, then properties.noninterference at head and base. Gate (a) T0+T1 at `0f71b5b4`
  beside it: `r20260925-101742-278e` (26/26 fixtures prefetched, key deleted 10:13:34Z).
- `vyv-rf-b4-tp2` (19vmzfvh0x589w, 2x L40S, 377 GB cgroup): `r20260925-101142-d268` = bootstrap OLMOE, then #70
  build / match / commit (PAIRS=1) at 3bdcd0ad (0f71b5b4 differs only in tests/engine/test_hooks.py).

## Next
1. Collect: gate (b) jdiff at 0f71b5b4; #101 vs record; noninterference head vs base; gate (a) vs a23b's base; #70 vs
   f1/f56's record (program 64bee6d6e8264461, manifest 1bb40895671dd791, tp run root 0b91229f..., commit FAIL).
2. READY.md; terminate every pod after fetch.

## Open questions (none blocking)
- `engine.hooks` sits in the `core` P9 layer (stdlib only; a test asserts it imports nothing from `verity_vllm`), so
  observe/program/commit can call it without an engine<->observe package cycle. The package-cycle check treats it as
  its own package. Say if you want it elsewhere.
- P9 `_constructs` refinement: `setattr` on an object the function itself constructed (CapWords call or `fresh`) isn't
  a runtime patch; that cleared 7 false positives (registry `PrimitiveDefinition(...)`, generic `types.ModuleType`).
- `build_engine` / `engine_kwargs_for` signatures unchanged. The vllm_adapter -> build.py file split is left to B5
  (39 importers).
- Env pins "at construction": the engine path pins inside `build_engine` / `engine_kwargs_for`. Three pipeline CLIs
  (m1_capture, tp/capture, commit) still call `prof.apply_env()` at module import, and vllm_meta pins at import
  (both now through engine/env.py), because huggingface_hub reads HF_HOME / HF_HUB_OFFLINE once at import: moving
  those later would change what a process sees. Proposal: they move when a5's `pipeline/cli.py` owns process startup.
- Code identity: `construction_version` moves (export_compat, export_ops, triton_capture, pipeline/build.py are
  construction sources). Before/after values go in READY.md; no Program/manifest/commitment digest change intended.

## Found, not fixed
- none
