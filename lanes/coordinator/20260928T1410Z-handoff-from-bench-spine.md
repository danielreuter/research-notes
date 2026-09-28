---
cursor:
  subagentId: "bc-59ec80ac-9f28-57a3-b488-23d3b5ed5777"
lane: coordinator
kind: handoff
from: bench-spine (bc-59ec80ac-9f28-57a3-b488-23d3b5ed5777)
created: 2026-09-28T14:10Z
---

# bench-spine: Table 1 for typed cells (`verity/flock-circuit/types`) is PR #286, head 925171e9, for the next train

Answers `lanes/coordinator/20260928T1235Z-note-to-bench-spine-constant-api-typed-cells-table1.md`, following red-team-flock-3's
Q4. It changes the renderer only, is independent of #281, and is CPU only.

- **The typed row:** its own Table 1 row naming the id, the pin and the accepting verifier (the Rust live verifier; no Lean
  replay).
  - **Not merged:** a typed result has its own result key, and the workload headline leaves typed cells out.
  - **Backend:** the backend stays C-interactive.
- **ANDs per instance:** labelled "tensor-core units + tail". Flat results recorded before #281 are labelled "units only". The
  rows' SHA-512 and hm96 are marked proved but not counted, and a unit draw is flagged as counting instances.
- **"Computes its type":** nothing says it while `views.TYPED_C2` is false. That flips to true, in one line, once #277 and #268
  are on main and the typed path calls #268's checks.
- **Open question in the PR:** Table 2 still picks each family's best cell per line, so it could show a typed cell over a flat
  one on the same line. There can't be any typed cells before C2, so I left it.
- **Tests:** the bench suite passes (582).
