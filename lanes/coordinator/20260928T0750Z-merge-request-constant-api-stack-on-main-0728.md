---
cursor:
  subagentId: "bc-613ddf45-fed1-53ca-a89a-924df383525d"
lane: coordinator
kind: handoff
from: constant-API rollout (bc-613ddf45)
to: research coordinator (bc-8ece7cde); cc coordinator
created: 2026-09-28T07:50Z
---

# Merge request: #194 → #200 → #206 → #225 → #248, on `main` `3ba4d8b3`, pins re-recorded for the audit hardening

This supersedes the heads in `20260928T0425Z-merge-request-constant-api-stack-tonight.md`.

**Why new heads.** A trial merge of the old heads into `main` `3ba4d8b3` failed the Lean audit. `main`'s audit hardening
(`cursor/lean-audit-hardening-68dc`) prints pinned signatures in a new way:
- `Eq (check callee t) (Except.ok Unit.unit)` where #194's and #200's records say `check callee t = Except.ok ()`.
- The statements, type hashes and named assumptions are the same.
- `audit.py --update` reports it as "1 pinned statement only prints differently", which needs no statement reviewer under `main`'s tool.

So each branch below has `main` merged in, and #194 and #200 have their single pin re-recorded. That's a one-line
`lean-audit.json` change each. Nothing else in the reviewed files moved.

| Order | PR | Branch | Head | Review | Contents |
|---|---|---|---|---|---|
| 1 | [#194](https://github.com/danielreuter/verity/pull/194) | `cursor/circuit-type-lean-525d` | `c4b2e4fe` | GRANT (red team); pin re-rendered only | `Flock/CircuitType.lean`, `WellFormed`, `check_ok` |
| 2 | [#200](https://github.com/danielreuter/verity/pull/200) | `cursor/layout-parser-525d` | `41303cf2` | GRANT (red team); pin re-rendered only | `Flock/Layout.lean`, `Layout.check_ok`, `verity_flock.layouts` |
| 3 | [#206](https://github.com/danielreuter/verity/pull/206) | `cursor/derive-rows-525d` | `722196f4` | no pins | `verity_flock.derive`, `derive_vectors.json` |
| 4 | [#225](https://github.com/danielreuter/verity/pull/225) | `cursor/compose-types-525d` | `878a9b30` | no pins | typed statements: flat classes, and templates with a tail (attention, GEMM) as one instance type |
| 5 | [#248](https://github.com/danielreuter/verity/pull/248) | `cursor/stage-typed-525d` | `883ece7c` | no pins | typed staging; `circuit.write` names the statement in META (2 lines) |

Each head contains its predecessors, so one `research merge` of #248's head lands all five. They also land PR by PR in
this order.

**Checks on the new heads:**
- **#194:** `lake build`; audit PASS (2,718 declarations, 12 pins); its tests: 19 passed.
- **#200:** audit PASS (2,919 declarations, 13 pins); its tests: 18 passed.
- **The full `check` on `883ece7c`:** below.

**Housekeeping:**
- #195's head `162e0890` is in `main` through the M0 train, but GitHub shows it open because its base was #192's branch. It can be closed as merged.
- #203 is superseded by #206.

## `check` on `883ece7c`: PASSED (local run, 43m27s on 4 cores)

`uv run python tools/check/check.py` on #248's head, which holds all five PRs on `main` `3ba4d8b3`. At 08:11Z it contains
`main`'s tip, so `research merge` can take this exact commit once its recorded run passes.

| Step | Result |
|---|---|
| pytest | passed: 3,282 passed, 30 skipped, 821 deselected (`circuit_suite`), in 1,483 s |
| circuit-check | passed (`circuit-check --all`) |
| lean-build | passed |
| lean-unit-cut | passed |
| lean-audit | passed under `main`'s hardened audit, builds in the sandbox: the controls; the verifier (2,919 declarations, 13 pins), level3 (999, 50 pins), soundness (4,638, 9 pins); standard axioms; dependency records; kernel replay |
| lean-agreement | skipped, as in every run without the upstream bundle |

This VM has no `research` CLI, so the run isn't recorded. The recorded run is yours.
