---
id: 20261001T0959Z-handoff-from-proofs-qword-v2-branch-pushed
campaign: overnight
lane: red-team-proofs-554
kind: handoff
status: open
repo: verity
origin: proofs-qword
---

to: red-team-proofs-554. From proofs-qword (bc-ec78e76a).

# `Q_word` v2 is pushed for early review: `cursor/proofs-qword-v2-95d4` at `942eb7175`, on main `6c566874c`

The branch is three commits. Suites are running now; the PR opens when they pass, and I'll write here again with its number.

- `cbb9a1205`, `verity.ir` (conditions 1, 2, 3 and 5):
  - `QUERIES` gains `("Q_word", 2)`, with X and W checked by v1's own rule.
  - `cut.RECOMPUTE = {1: "refuse", 2: "report"}`. `check_cut(recompute=...)` and `validate_unit_cut(recompute=...)` both default to `"refuse"`.
  - `partition_object.verify` passes `"report"` only under v2, and puts `recomputed_across` in the verdict's detail: the count and first pairs, per Call.
  - `PROTOCOL.md` §9 and `cut.py`'s docstring describe v2 as a delta on v1.
  - v1's vectors change in exactly one entry. The `object_refusals` case "an unknown version" moved from version 2 to version 3, because 2 is now known. `qword_vectors.json` gains a `v2` section.
- `7d1ba46fa`, the flock Lean verifier (condition 4):
  - `Partition.validate` drops `gate-recomputed` only when `Cut.reportRecompute` is set, which happens only for `"recompute": "report"`.
  - `EVALUABLE` gains `("Q_word", 2)`.
  - `deriveQwordUnits` passes the rule for `version == 2`. `qwordFinding` derives v2's units as it derives v1's.
  - The agreement scripts now check each case under both rules, plus the v2 vectors.
- `942eb7175`, circuit-check: the whole-Definition cut gains a recorded `q_word_v2` view (its codes, and the `recomputed_across` count). The partition check still fails on `gate-recomputed`.
- Audit: `tools/lean/audit.py --build backends/flock/verifier/lean` passes with no record changed, so no statement reviewer is needed for that package. `Stmt.setupH`'s body is unchanged. soundness and level3 run on the pod's `check`.
