---
id: 20260929T0148Z-handoff-from-pous-311-head-1a4bd3f0
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# #311's head is now `1a4bd3f0`, on `main` with train D4 (#208, #218). Recorded check PASSED. #312 and #315 can merge it

Follow-up to `20260929T0028Z-handoff-from-pous-311-head-1cbc750a`. For bc-13eada34 (#312) and bc-dd22acf8 (#315).

- **Head `1a4bd3f0`** on `cursor/vllm-protocol-composition-9924` (https://github.com/danielreuter/verity/pull/311).
  - It is `1cbc750a` merged with `main` `4b75ba16`, which includes train D4 (`0ed643f1`: #208, #218, #298, #301).
  - It's a merge, so nothing was force-pushed.
  - The one conflict was the one prepared against D3: two imports added at the same place in `pipeline/tp/commit.py`.
    Both are kept, and P10 is unchanged.
  - No other file changed beyond `main`'s. `interface.py` is as it was at `1cbc750a`, so the adapters still just drop
    `outside_program=`.
- **Recorded check: `r20260929-012847-abf3` on `1a4bd3f0`, PASSED** (01:46Z, preserved on the remote).
  - pytest: 19 suites passed, all run fresh with none reused; `verity-vllm` was skipped, as `check` does.
  - `circuit-check --all`, `lean-build`, `lean-unit-cut` and `lean-audit`: passed. `lean-agreement` was skipped by name
    (no upstream build sent).
  - It ran in `check`'s normal parallel mode, with a 16 GB swapfile added to this 15 GB VM so the Lean replay and the
    suites no longer run out of memory.
- **The vLLM tests under torch 2.14 on `1a4bd3f0`:** `r20260929-012722-ed9c`, done rc 0. That covers
  `tests/protocol_options`, the hooks, `LLM`, row, CLI and `TargetProfile` tests, the lints, and the dead-module and
  import checks. The dead-module failure from #309 is gone on this `main`.
- **Merge:** the verdict's timing condition (after D3′, now D4, and after tonight's rows) is met. `research merge
  cursor/vllm-protocol-composition-9924`, then #312 and #315 on top, once they have merged `1a4bd3f0` and re-run
  `check`.
