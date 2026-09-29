---
cursor:
  subagentId: "bc-ea1c2c4f-07dd-56b4-afdd-10e38e1a866f"
lane: coordinator
kind: handoff
from: workstream-3 backend stress test (bc-ea1c2c4f)
to: research coordinator (bc-8ece7cde), for the next train
created: 2026-09-27T19:35Z
---

# Merge request: PR #178, `verity.ir.units` and `verity_flock.partition_units`

- **The PR:** [#178](https://github.com/danielreuter/verity/pull/178), branch `cursor/workstream-interfaces-866f`, head `6054f205`. It's marked ready, CPU only, $0.
  - It merges cleanly onto `main` and with #179.
  - The branch history holds the annotation module's add and remove commits (#179 took it), so they net to nothing.
- **What it is:**
  - `verity.ir.units` (core, stdlib only): each unit of a partition as a standalone word circuit, classed by a SHA-256 shape. It takes any query `partition_object` evaluates, or an owner function.
  - `verity_flock.partition_units`: one C-Flock lowering per class, checked on synthetic inputs lifted through each flat Definition, plus two deliberately odd owner functions that are not queries.
- **Nothing existing changes.** No digest, format, query or circuit moves.
- **Gates:**
  - `packages/verity/tests` in full, `tests/test_repository.py` and the new backend test: 1,253 passed;
  - `test_boundaries` passes;
  - no circuit, so no circuit-check report;
  - `check` not run here: the merger re-runs it.
- **Finding, not fixed here:** on `main`, the `F32Mul` and `F32Add` pieces aren't bit-exact on NaN payloads. PR #104 fixes that. The odd partitions surfaced it.
