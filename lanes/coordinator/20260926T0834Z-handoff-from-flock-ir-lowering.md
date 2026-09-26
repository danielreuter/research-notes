---
lane: coordinator
kind: handoff
from: flock-ir-lowering (bc-9916bbb1-de98-5d21-a511-aafa5255c78f)
created: 2026-09-26T08:34Z
---

# Merge request: PR #54 (cursor/flock-ir-lowering-c78f @ 2f55d2d3). red-team-flock-2 granted IR3 (`verity/flock-ir-frame/v2`) and IR4/IR5 are met. IR6 (leaf maps pinned with the netlist) has landed and is sent for confirmation

**What to merge:** https://github.com/danielreuter/verity/pull/54, tip **2f55d2d3**.
- `origin/main` was merged in at cdc11514 (main e3a2d81d). One conflict, in `test_cell.py`, resolved to keep both sides.
- `pytest backends/flock/tests/test_ir_lowering.py backends/numerical/tests/bench/test_lowerings.py backends/numerical/tests/bench/test_cell.py`: 95 passed, 2 skipped. The full `backends/flock/tests` + `backends/numerical/tests/bench` suite passed at c53d9148 (468).

**Review state** (`lanes/flock-ir-lowering/20260926T0755Z-handoff-from-red-team-flock-2.md`):
- RoPE and SiLU·mul (`verity/flock-ir-block/v1`) and both RMSNorms are granted with conditions.
- IR1, IR2, IR4 and IR5 are MET.
- IR3, `verity/flock-ir-frame/v2` at c53d9148, is **GRANTED WITH CONDITIONS at NON_ZK_PROOF**.
- The four cells are labelled `proof_class=NON_ZK_PROOF`: art:dd27fdab (RoPE), art:8a07b80f (SiLU·mul), art:9563d2c8 (RMSNorm fused), art:63553a6c (RMSNorm Triton).
- **IR6**, red-team's hardening condition before any producer-staged file is verified or the next statement version, has landed at 2f55d2d3:
  - the leaf maps are a LEAVES line in the pinned netlist;
  - `flock-ir-frame` checks the wiring, output mapping, block assignment and row key against them, and requires 16-bit outputs;
  - four negatives; 119/119 selftest cases.

  The confirmation request is `lanes/red-team-flock-2/20260926T0832Z`. Pins move by the LEAVES line only; the rows are unchanged. The attention work (overnight goal 1) builds on this frame after red-team confirms IR6.

**Still open, and not blocking the merge in red-team's note:**
- IR2 stays mandatory: the verifier stages its own file.
- A non-producer replay of the four cells (a verify-* lane) is pending.
