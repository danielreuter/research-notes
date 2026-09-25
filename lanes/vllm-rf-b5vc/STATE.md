---
id: vllm-rf-b5vc/state
lane: vllm-rf-b5vc
kind: state
created: 2026-09-25T16:47Z
updated: 2026-09-25T17:14Z
---

> **Coordinator, 17:20Z: no waiting in a running turn** (Cursor's 8-agent cap). Start pod jobs detached with custody, checkpoint `WAIT <pod> <run id> check-back <HH:MMZ> agent bc-2ddd7f1e-8f60-5cdf-b9e2-a95ab5634c72: <what>`, and end your turn; the root wakes you when the sweep sees the run finish. Rule: `lane-briefs/vllm-cloud-common.md`, section Notes.
# vllm-rf-b5vc: split program/frontend/rules/vllm_bindings.py into a package (B5) (state)

> **Successor of vllm-rf-b5vb** (agent bc-19e6c2c5; no commits, no pods; its session ended at the 16:03Z laptop restart).
> This lane: Cursor cloud agent bc-2ddd7f1e. Start commit **`8a3aa083`** (`origin/main`, includes a4 and c1). Coordinator:
> vLLM coordinator bc-ecac3029. Briefs: `$STORE/internal/lane-briefs/vllm-cloud-common.md`, `vllm-b5vc.md`.

base: 8a3aa083

- Branch `lane/vllm-rf-b5vc` (pushed). Budget: $16 of new spend. vyv- deadline 2026-09-25T20:30Z.
- Scope: `integrations/vllm/verity_vllm/program/frontend/rules/vllm_bindings.py` (1,905 lines) -> package
  `rules/vllm_bindings/`, one module per rule family + pins/targets + observation state; `__init__` re-exports exactly
  the names importers use; verbatim moves (AST/source check); `VLLM_BINDING_RULES` order identical; lints re-keyed, no
  allowlist growth; P10 entries leave the ratchet. Pure structure.
- Pods (handed over by vllm-rf-a5c, not before its handoff lands here): `vyv-rf-a5-t1` (gate (a), gate (b) head+base),
  `vyv-rf-a5-g1` (#101 smoke; record program `ccc21347…`, manifest `90f81868…`, run root `7adcef49…`).

## Done
- 16:44Z `e1dd2a7e` (pushed): the split. Modules (lines): `__init__` 71 (docstring, VLLM_BINDING_RULES, vllm_ruleset,
  re-exports, `__all__` of the 20 importer names), `pins` 114, `observations` 178 (`_OBSERVED`, the one module state),
  `operands` 47 (aten, BF16, `_row_value`, `_strides`, `_untransposed`), `triton_launches` 166, `attention` 237,
  `elementwise` 154, `norm_chain` 417, `fp8` 192, `fused_norm` 37, `views` 72, `cache_pad` 92, `collectives` 261.
  - `evidence/verify_split.py`: 77/77 top-level statements moved with identical source text and AST, none duplicated,
    nothing else added; 59/59 between-statement comment lines (banners, `#:`) kept. Negative checks (swap two rules in
    VLLM_BINDING_RULES, drop a banner, edit a pin) all FAIL it. Generator: `evidence/split.py` (line ranges).
  - Rewritten: only the imports (generated from the names each module uses; pyflakes clean) and `__all__` (the original's
    45-name list -> the 20 names importers use: build.py, vllm_moe.py and 8 test modules, incl. `VB._OBSERVED`,
    `VB.triton_launch`).
  - Allowlists, static (`evidence/rekey.py`, stdlib, no pytest): P7 broad-except 3 = 3, P8 6 = 6, P11 10 = 10 re-keyed;
    P10 `vllm_bindings.py <module> 1905` deleted (largest module now 417); P9 cycle `vllm_bindings <-> vllm_moe` unchanged
    (the ruleset stays in `__init__`, so the SCC keeps its two members); P12 build.py root-list key unchanged. All 12
    rules: 0 new, 0 stale.
  - `pipeline/build.py` `_CONSTRUCTION_SOURCES`: the one path -> the 13 package files (construction_version changes;
    code identity, not a Program/manifest digest). `test_applicability.py`, `test_harden_guards.py`: the source-path
    lists glob the package.

- 16:58Z `3c58a392` (pushed): `git merge origin/main` (`38a8d35d`, per the coordinator's 16:55Z handoff), no conflicts;
  `vllm_bindings.py` is unchanged on main, the importer set is the same, verify_split OK, static lints 0 new / 0 stale.
- 17:13Z `eb97ecb4` (pushed): merged `origin/main` `f7de4620` (b5patb). Clean; checks as above.
  **Head `eb97ecb4`, gate (b) base `f7de4620`** (the base a5c's t1 re-gate runs).
- 17:10Z a5c's ETA: g1 handover about 17:30Z, t1 about 17:45Z.

## Running
- (none; waiting for the a5c pod handoffs)

## Next
- On handoff of `vyv-rf-a5-t1`: lints at head; gate (b) head `eb97ecb4` and base `f7de4620` (reuse a5c's base run on t1, `r20260925-170857-a861`, if its tree and pod match) on the pod, jdiff; gate (a)
  T0+T1 at head vs a23b's base XML. Code identities before/after.
- On handoff of `vyv-rf-a5-g1`: #101 GPU Build smoke, program/manifest/run root vs the record.
- READY.md, merge-ready handoff.

## Open questions
- (none)

## Found, not fixed
- `tests/program/test_harden_guards.py::test_G4c_no_capability_or_sm_literal_outside_target_profile` checks nothing:
  its `ROOT` is `dirname(dirname(verity.ir.__file__))` (= `packages/verity/src/verity`), so every listed path is
  missing and skipped (true at base too).
- Prose naming `vllm_bindings.py` (a4's rule: bare file names are not rewritten): `observe/fold/collective_pattern.py:13`,
  `observe/fold/patterns.py:637`, `registry/{targets,gemm_targets,dense}.py`, `rules/{vocab,vllm_moe,__init__}.py`,
  `target_profile.py:205`, several test docstrings.
- The P9 cycle `vllm_bindings <-> vllm_moe` could go: `vllm_moe`'s lazy import of `active_target_profile` could name
  `vllm_bindings.observations` directly. Left alone (importers unchanged by brief).
