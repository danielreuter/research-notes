---
cursor:
  subagentId: "bc-75fd4007-9f21-5dd1-a0b2-c7e19b282622"
lane: coordinator
kind: handoff
from: vllm-epoch-run (bc-75fd4007)
to: research coordinator (bc-8ece7cde)
cc: vllm-coordinator (bc-ecac3029)
created: 2026-09-29T01:27Z
---

# Merge request: PR #351, the call-boundaries stop lifted into the row driver (follow-up prerequisite 5)

- **The PR:** [#351](https://github.com/danielreuter/verity/pull/351), branch `cursor/call-boundaries-gate-2622`, head `a5b3b222`, on main `5810574d`. It's
  independent of #346 and #347. #346's `epoch_row.sh` already dropped the unconditional stop and handles this PR's exit 21.
- **The change:**
  - `verity-vllm gate call-boundaries <row dir>` (`acquire/gate.py`) fails when an unclaimed `call_boundaries` identity is uncovered by
    `call_boundary_source.plan_of`, or when a `CLAIMS` entry names a source that `taps.attached(manifest)` doesn't list.
  - The row driver runs the gate right after a PASS Build. A failing row stops with exit 21 and a `build-call-boundaries FAIL … first: <identity>`
    line, with no Match and no Commit.
- **#74's stored Build on CPU** (`art:39d08c35`): 145,728 identities, all covered, with 0 uncovered and 0 unattached. It passes (1731 s, 13.8 GB).
- **Tests:** `test_gate_call_boundaries.py` is new (6 tests), and `test_row.py` has new driver tests.
  - `test_row.py`: 33 passed, 1 failed. The failure needs torch and fails the same way on `main`.
  - `test_plan.py`, `test_cli.py` and `tests/lint` pass.
  - `test_call_boundary_source.py` needs torch; only its helpers moved.
- **No digest moves.** No pods were used. It needs a recorded `check` of `a5b3b222` before `research merge`.
