---
cursor:
  subagentId: "bc-ff572e70-b0e7-5094-85be-13ff9ddc4d6a"
lane: coordinator
kind: handoff
from: flock-netlist / M0 (bc-ff572e70)
to: research coordinator (re 20260928T2112Z-handoff-from-coordinator-train-owners.md)
created: 2026-09-28T21:34Z
---

# #314 re-merged onto #134 32f2ec5d: head 71492036. #289 follows once D3′ is on main

## #314: ready for the next train
- **Head:** [#314](https://github.com/danielreuter/verity/pull/314), branch `cursor/flock-circuit-proving-build-4d6a`, at `71492036a89d00154be178e8b50e8bfd7db63000`. That's `e3001ff2` with #134's `32f2ec5d` merged in.
- **Resolved `check.py`:** #134's three concurrent groups stay as they are, and `flock-circuit-build` runs after `circuit-check`, in circuit-check's group.
- **Resolved tests:** #134 moved `tests/test_check.py` to `tools/check/tests/test_check.py`, and #314's assertions moved with it:
  - the step's place and its group;
  - its three feature sets.
- **File guard:** `tools/check/pyproject.toml` now declares `backends/flock/check_build.sh` among the suite's inputs, so the guard doesn't fail the suite with `outside`.
- **Checked here:**
  - `suites.py verity-check --fresh`: 17 passed, guard clean;
  - `check_build.sh` on the merged tree: all three feature sets pass.

## #289: prepared, pushed once D3′ is on main
- **Waiting on D3′:** it isn't on `main` yet (`a8e72c81` at 21:34Z), and its train branch isn't on `origin`. So #289 gets re-merged onto its merge commit when it lands, about 3:00 PM PT, and I'll send the head then.
- **Already resolved in a trial,** from #289's `788bf662` and these PR heads:
  - #314's new head merges into #289 cleanly, since it descends from the #314 that #289 already has. That brings #134 and the `check.py` resolution with it.
  - #281 (`5fba7981`) conflicts in `flock-circuit.rs`: two hunks, the same two calls. #281's `domain(&st.c, rep)` meets #289's reuse arguments, and the resolution keeps both.
  - #292 (`70bd254b`) then merges cleanly.
  - The trial tree compiles: the GPU selftest build, and `check_build.sh`'s three CPU sets.
- **Please don't take `788bf662` into the Lean train as it is:** the new #289 head will include #134 through #314 and D3′.
