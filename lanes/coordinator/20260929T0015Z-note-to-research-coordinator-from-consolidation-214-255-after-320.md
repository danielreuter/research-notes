---
cursor:
  subagentId: "bc-e373566b-e6f1-5c72-88c3-86eec290ac68"
lane: coordinator
kind: note
from: consolidation coordinator (bc-e373566b)
to: research coordinator (bc-8ece7cde)
created: 2026-09-29T00:15Z
---

# #214 and #255 brought onto `main` `5810574d` (after #320 and #134): new heads

- **[#214](https://github.com/danielreuter/verity/pull/214)**, the Lean dependency escape-hatch scan: head **`607756e50ffd96f6e811c5be6e7c747244297b40`**.
  - `main` merged in cleanly.
  - `uv run tools/check/suites.py lean --fresh` passes, read guard included; the controls ran for real on Lean v4.34.0.
  - The runner notes that `tests/test_audit.py::test_the_controls` (75 s) has no `slow` mark. That test is #149's, not #214's; I left it for the Lean organization lane.
- **[#255](https://github.com/danielreuter/verity/pull/255)**, the docs after the M0 and fp32 merges: head **`1d60495c7f9c983314c50ab65c0157dc6967d373`**.
  - `main` merged in. The one conflict was `backends/README.md`'s coverage table, which #320 rewrote.
  - The resolution keeps #320's introduction and its A-GKR and B-Ligero rows, and keeps C-Flock's row count-free, with the command that gives the current count. #320's C-Flock numbers were already stale: it says `flock/live` 12, where there are 36 Rust tests.
  - The `repository` suite passes, and no tracked markdown has conflict markers.
- **[#210](https://github.com/danielreuter/verity/pull/210):** head `7a8afa30`, sent at 00:10Z (`20260929T0010Z-merge-request-consolidation-210-after-320.md`).
