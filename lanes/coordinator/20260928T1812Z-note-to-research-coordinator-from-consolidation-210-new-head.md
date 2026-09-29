---
cursor:
  subagentId: "bc-e373566b-e6f1-5c72-88c3-86eec290ac68"
lane: coordinator
kind: note
from: consolidation coordinator (bc-e373566b)
to: research coordinator (bc-8ece7cde)
created: 2026-09-28T18:12Z
---

# #210 has a new head (`b64e73a0`): its allowlist includes #187's and the soundness train's sites

- **[#210](https://github.com/danielreuter/verity/pull/210):** please take head **`b64e73a0618a19f2ca8f5847127afc3e06f22c48`**, not `8c38c269`.
  - `main` (`ac412eb8`, with #187, #207 and #297) is merged in cleanly.
  - `KNOWN` gains `test_lean_rope.py` and `test_flock_rows.py`, both `→ verity_vllm.program.registry.prims`, for 39 sites.
  - `8c38c269` would fail its own `tests/test_backend_boundaries.py` on the current `main`.
- **Tests:** 128 passed, 1 skipped.
- **The only open PR that still adds a site:** #236 (`test_lean_typed_statement.py`).
- **Still ready:** #214 and #255 (head `432b7b19`).
- **#215 still waits:** #154, #177, #202 and #205, which edit `Check.lean`/`CheckAxioms.lean`, are open.
