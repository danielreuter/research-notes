---
id: vllm-rf-b4/state
lane: vllm-rf-b4
kind: state
updated: 2026-09-25T12:17Z
---
# b4 (engine and hooks): state

> **Coordinator, 10:01Z: the vyv- pod deadline is now 2026-09-25T15:30Z (8:30 AM PT; updated 11:31Z)**, extended in steps of at most 4 h while the coordinator runs; register results as they land.

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
- Gate (b) at `0f71b5b4` (`r20260925-101530-aa45`) vs base (`r20260925-095250-e4e8`), same pod: 0 new failures, 0 new
  skips / skip reasons, 0 deleted or renamed; 17 new tests pass. Lints 47 passed. Evidence in `evidence/gate_b/`.
  `vyv-rf-b4-cpu` fetched, terminated and unregistered 10:37Z.
- #101 at head on L40S (FA2 matReq tap): build / match / commit PASS, program ccc21347..., manifest 90f81868...,
  run root 7adcef49... = record. properties.noninterference PASS 992/992 hashes, tokens equal, at head and base.
- construction_version.sources_sha256: base 53cfbe1c..., head 92aed410... (code identity; computed from git, equal
  to the pod's artifact.json).

- #101 base `r20260925-104202-d6d9`: head == base == record (run root, commit_pass), Program / manifest head == base.
- FA3 on H100 PCIe (`vyv-rf-b4-h100`, terminated 11:57Z): the H100 rows of record declare an H100 SXM (132 SMs), so
  `build_engine` refused the part (114 SMs) after the Build (`r20260925-104827-1825`, stopped by pgid). The canary's
  Llama-3.2-1B B1 256/32 greedy row instead (`r20260925-113014-592b`, target-family precheck waived by name as canary.sh
  does): head == base, run root f64a6611..., commit PASS, fa3_hidden_m1_stream committed.
- #70 TP2 (`vyv-rf-b4-tp2`, terminated 12:15Z, `r20260925-101142-d268`): Build program 64bee6d6e8264461, manifest
  1bb40895671dd791 (357,796), Match fold fails rc 11 with the base's counts, Commit FAIL pass False with tp run root
  0b91229f... = the base's; `tools/cmp70.py` 32/32 fields equal to f1's base Commit of record (per pair).

## Running (pods registered, guard 90)
- `vyv-rf-b4-g1` (17ez42q6mb3wo2, 1x L40S, 188 GB cgroup): gate (a) T0+T1 at `0f71b5b4` `r20260925-101742-278e`
  (GPU hidden; 26/26 fixtures prefetched, key deleted 10:13:34Z). 120/158 at 12:15Z (78% of a23b's per-test time),
  **ETA about 12:50Z**. A second copy on a cpu3m/cpu5m pod was not possible (no stock at 64 or 32 vCPU, 11:05Z).

## Next
1. Gate (a) jdiff vs a23b's base XML; fetch; terminate g1.
2. READY.md (drafted; gate (a) and spend left); final message.

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
- `tests/program/test_twins.py::test_check_writes_the_evidence_schema` depends on xdist scheduling (`LIBRARIES["openmp"]`
  appears only when the worker itself compiles tc_model). Failed at base, passed in head's rerun.
- The H100 rows of record declare an H100 SXM (num_sms 132); an H100 PCIe pod (114 SMs) builds them and then
  `build_engine` refuses the engine. Pick `NVIDIA H100 80GB HBM3` for them.
