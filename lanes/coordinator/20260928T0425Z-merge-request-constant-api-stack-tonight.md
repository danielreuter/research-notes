---
cursor:
  subagentId: "bc-613ddf45-fed1-53ca-a89a-924df383525d"
lane: coordinator
kind: handoff
from: constant-API rollout (bc-613ddf45)
to: research coordinator (bc-8ece7cde), for tonight's merges; cc coordinator
created: 2026-09-28T04:25Z
---

# Merge request: the constant-API stack (#190 → #191 → #194 → #200 → #206), all on current `main`

> **Superseded, 08:11Z,** by `20260928T0750Z-merge-request-constant-api-stack-on-main-0728.md`. #190 and #191 are merged.
> #194 → #200 → #206 → #225 → #248 now carry `main` `3ba4d8b3` and #194's and #200's pins re-recorded for `main`'s audit
> hardening (the same statements, printed differently), with `check` passed on the top, `883ece7c`.

This supersedes the heads in `20260928T0140Z-merge-request-constant-api-core-types-wellformed.md`.

**Every branch now has `main` at `51878fab` (train L) merged in.** Each PR's head contains its predecessors, so the stack
lands either PR by PR in this order, or in one `research merge` of #206's head, which lands all five.

| Order | PR | Branch | Head | Review | Contents |
|---|---|---|---|---|---|
| 1 | [#190](https://github.com/danielreuter/verity/pull/190) | `cursor/constant-library-binding-525d` | `dbae1787` | no pins | `verity.ml.library` (library list v1), `verity.ir.constants` (binding times) |
| 2 | [#191](https://github.com/danielreuter/verity/pull/191) | `cursor/circuit-types-525d` | `5ed50173` | no pins | `verity_flock.circuit_types`, the shared circuit type |
| 3 | [#194](https://github.com/danielreuter/verity/pull/194) | `cursor/circuit-type-lean-525d` | `df01950a` | **GRANT** (red team, at `b7b7b42f`) | `Flock/CircuitType.lean`, `WellFormed`, `check_ok` (pinned) |
| 4 | [#200](https://github.com/danielreuter/verity/pull/200) | `cursor/layout-parser-525d` | `d0257d0c` | **GRANT** (red team re-review, at `56936c35`) | `Flock/Layout.lean`, `Layout.check_ok` (pinned), `verity_flock.layouts` |
| 5 | [#206](https://github.com/danielreuter/verity/pull/206) | `cursor/derive-rows-525d` | `24b583f4` | no pins | `verity_flock.derive` and `derive_vectors.json` |

**Since the reviews, only `main` merges changed.** Not one line in the reviewed files moved.
- #194's and #200's Lean audit on the merged head: PASS, 2,919 declarations in 37 modules, standard axioms, 13 pins, with
  the same pin records the red team reviewed.
- `test_layouts.py`, `test_circuit_types.py`, `test_table_library.py`, `test_lean_verifier.py` and
  `tests/test_repository.py`: 44 passed, 1 skipped.
- #206's `test_derive.py`: 13 passed on its head.

**#206 supersedes #203.** It's the same `derive` commit, re-cut onto #200 without #192 merged in, since `derive` never
needed #192. That lets it land before M0's prover PR. Please close #203.

**`check`:** this VM has no `research` CLI or evidence store, so it can't record. I'm running `tools/check/check.py` on
#206's head `24b583f4`, which holds all five; the result follows below. `research merge` needs its own recorded run of
that exact commit: `research run --tool check` on it.

**#195 is not in this stack,** because it changes #192's inline read (`ir_lower._Read`). It merges the moment #192 is on
`main`: I'll merge `main` into it, rerun its tests and `check`, and hand it over here.

## `check` on `24b583f4`: PASSED (local run, 50m57s on 4 cores)

`uv run python tools/check/check.py` on #206's head, which holds all five PRs on `main` `51878fab`:

| Step | Result |
|---|---|
| pytest | passed: 3,197 passed, 31 skipped, 821 deselected (`circuit_suite`), in 1,254 s |
| circuit-check | passed (`circuit-check --all`) |
| lean-build | passed |
| lean-unit-cut | passed: 500 of 500 cuts agree |
| lean-audit | passed: the controls; the verifier (2,919 declarations, 13 pins), level3 (999, 50 pins), soundness (4,638, 9 pins); standard axioms, kernel replay |
| lean-agreement | skipped, as in every run without the upstream bundle (`flock_agreement` is the cross-check) |

**Against train M:** a trial merge of `24b583f4` with `main` `6746f408` is clean. It brings only two `views` files, and none
of this stack's. So the stack can ride the next train exactly as checked.
