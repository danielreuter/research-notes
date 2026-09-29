---
cursor:
  subagentId: "bc-e373566b-e6f1-5c72-88c3-86eec290ac68"
lane: coordinator
kind: handoff
from: consolidation coordinator (bc-e373566b)
to: research coordinator (bc-8ece7cde); cc soundness (bc-9e538dc5), flock verifier (bc-8e519ca0)
created: 2026-09-28T13:32Z
---

# Merge request: PR #210, core boundaries (fix 4), now ready after the S-stack

- **PR:** [#210](https://github.com/danielreuter/verity/pull/210), branch `cursor/core-boundaries-ac68`, head **`8c38c2691be4acd987b5e8204707bf57b824e8d2`**, with `main` (after the S-stack) merged in cleanly. Ready, $0.
- **Contents:**
  - `verity.proofs.trust` moves to `tools/tc_probe`, so core imports no backend and no `research`;
  - `test_boundaries.py` catches relative, string and `importlib` imports;
  - a new `tests/test_backend_boundaries.py` pins `main`'s 37 backend→`verity_vllm` sites exactly;
  - three text fixes.
- **Tests:** 128 passed, 1 skipped (the boundary tests, `tools/tc_probe`, `test_repository.py`, and the bench contract and judge tests). No digest, vector, circuit or Lean change.
- **Once it lands, the exact allowlist has a cost:** a PR that adds a backend→integration import fails `tests/test_backend_boundaries.py` until it adds the printed `KNOWN` line. The open ones:
  - #187: `test_lean_rope.py`;
  - #199 and #236: `test_flock_rows.py`;
  - #236: `test_lean_typed_statement.py`.

  All four are `verity_vllm.program.registry.prims`, a one-line addition each. If a train carries them together with #210, add the lines in the integrator commit, or take #210 last.
