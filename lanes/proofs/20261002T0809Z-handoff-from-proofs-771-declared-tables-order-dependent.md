---
id: proofs/20261002T0809Z-handoff-from-proofs-771-declared-tables-order-dependent
campaign: value-hiding
lane: proofs
kind: handoff
status: open
repo: danielreuter/verity
origin: cursor/flock-hidden-outputs-95d4@3fd8c447f (worker bc-ad312479 for proofs bc-8416bc72)
---

# Train f38a: #771's `test_every_registered_primitive_declares_the_tables_it_reads` fails in the circuit-check suite

- Check `r20261002-063333-9f82` (#757 at `3fd8c447f`, which merges train f38a `597e355d5`) failed in `verity-circuit-check`
  only: 34 passed, 1 failed. Every other suite passed, and the Lean group was stopped by that failure. #757 changes nothing
  under `tools/` or `integrations/vllm/verity_vllm/program/` against f38a, so f38a's own check should fail the same way.
- The test walks the whole live `REGISTRY`. In the suite it runs after `test_circuit_check.py`, whose targets make
  `Lifted[...]` primitives on demand and pull in a quarantine module. On its own, after `TG.load_registries()` alone, it
  passes (checked locally at `3fd8c447f`). Run locally in the suite's order, it fails with the same ten entries the pod
  reported:
  - `Lifted[MufuEx2Ftz_v1]_v1` (`ex2`), `Lifted[DivFullRcp_v1]_v1` (`rcp`), `Lifted[MufuSqrtFtz_v1]_v1` (`sqrt`),
    `Lifted[Fa2InvSum_v1]_v1` (`rcp`), `Lifted[RsqrtApprox_v1]_v1` (`rsq`): "reads the table … and does not declare it".
    `lifted.py`'s `_strict_wrapper` builds `Lifted[P]` without `tables=p.tables`, so the guard
    (`constants.program_data`) can't see a lifted primitive's table. That is a real gap: a lifted primitive that holds a
    `registered` table would pass the guard.
  - `Lifted[AmpereBF16TcDot16_v2]_v1`, `_v2` and `_v2{ORD=4}`: "1 unnamed table(s)". This one is a false positive. The
    original reaches no table (`_reach` = 0); the wrapper's `_widths` default, the 33 operand leaf widths, passes
    `_is_table` (an int list of at least 16 entries).
  - `GeluErfBf16_v1` (quarantine `ln`): its evaluator reads `TABLE_WORDS`, the measured exhaustive table, and declares
    nothing. `load_registries` skips quarantine, so it is in `REGISTRY` only once another test has imported it.
- Suggested fix, for #771's owner: (1) fix the test's population: lift each registered primitive explicitly and import
  quarantine explicitly, or check `TG.REGISTERED` only, rather than whatever earlier tests left in `REGISTRY`;
  (2) `_strict_wrapper` passes `tables=p.tables` and `_enable_wrap` passes `tables=lp.tables`. `_v2` has the same gap, and
  the test can't see it: no word of `WORDS`, masked to the enable's two bits, is 1, so the inner evaluator never runs. (3) keep `_widths` from
  reading as a table, or have `_reach` skip a wrapper's own defaults; (4) `GeluErfBf16` declares
  `("gelu_erf_bf16", "registered")`, as `GeluTanhBf16` does. `tables` enters no descriptor, so no pinned digest moves.
- #757's re-run with `--keep-going` (`r20261002-080739-e373`) records the rest of the check (the flock suite, the Lean
  audit and `lean-agreement`) on the same head.
