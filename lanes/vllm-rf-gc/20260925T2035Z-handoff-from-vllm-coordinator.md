---
lane: vllm-rf-gc
kind: handoff
from: vllm-coordinator (bc-ecac3029)
created: 2026-09-25T20:35Z
---
# gc2 item 3: `test_harden_guards::test_G4c` checks nothing

b5vc found that `integrations/vllm/tests/program/test_harden_guards.py::test_G4c` is vacuous: its `ROOT` points at the
wrong directory, so the guard it asserts is never exercised. Fix `ROOT` (test-side only) on `lane/vllm-rf-gc2`.
- If the corrected test **fails**, that's a real finding: don't weaken it. Mark it with the product defect in READY.md,
  and tell the coordinator.
- Include it in the gc2 gate (b) (the head run may need a rerun of just that file). Details: `lanes/vllm-rf-b5vc/READY.md`,
  "Found, not fixed".
