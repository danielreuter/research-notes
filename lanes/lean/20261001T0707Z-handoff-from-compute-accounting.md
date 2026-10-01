---
id: 20261001T0707Z-handoff-from-compute-accounting
campaign: verity
lane: lean
kind: handoff
status: open
repo: danielreuter/verity
origin: compute-accounting (bc-e90634dd)
---

# For lean (bc-19c498a8): the cutover for PoUW's Lean, from the Project store to `protocols/pouw/lean/`

From compute accounting, PoUW's owner, at 12:10 AM PDT. Daniel gave you the move. These are the cutover terms I propose; tell me
in `lanes/accounting` if any doesn't work for you.

**1. The freeze is now, at M3b.** The store package at `internal/pouw-lean/lean/submissions/pouw/` (Project store) has 665 pins,
`lean-audit.json` `43ba801d…`, snapshot `art:0d156c69…` (`r20261001-055859-b6e8`). From 12:10 AM PDT, pouw-lean (bc-dd9ede96)
writes nothing more to the store copy. Its README gets one line, "moved to `protocols/pouw/lean/`; read-only", when your
import lands.

**2. You import that snapshot** into `protocols/pouw/lean/` in the contract's shape (`Protocol/`, `Assumptions`, `Properties`,
`SecurityProof/`), with its own `lean-audit.json`.
- Its toolchain (`leanprover/lean4:v4.34.0`) and its Mathlib (`5ed29652`, the same manifest revisions) already match the
  repo's other packages, so no bump is needed.
- Use the repo's `tools/lean/audit.py`, and drop the store's vendored copy (`lean/tools/lean/`, VENDORED-FROM `6746f408`).
- The 665 records must reproduce. Module and namespace renames change records, so record them with `audit.py --update`. The
  named statement reviewer for the move is bc-d545bc2a, the PoUW Lean red team: it confirms every signature is unchanged
  except for names.
- The store's rule that `Pouw/PearlC/Gamma.lean` stays `593e4e43…` carries over, as content after any rename.
- Update `protocols/pouw/PROTOCOL.md`'s citations (`Pouw.Proofs.endToEnd`, …) to the pinned names in the same PR, and record
  its `check`.

**3. M5 lands on the repo copy, not the store.** M5 is the FP4 fix restaged to #556, plus `fp4-delta/`'s 59 records, which
come to 731 pins. Its restage is still with the red team's statement review and the assessor's re-grant.
- pouw-lean rebases it onto your import branch, or onto `main` once the import lands. It works in its own checkout and its own
  `.lake`.
- It runs its merge prediction (`verify_merge.py`) against the repo layout.
- M5 lands as its own PR after your import, unless you'd rather take it on your branch.
- If M5 is ready before the import, it waits; it never goes back into the store.
- M2b, v2-hot's piece, stays held, since v2-hot is parked.

**4. No GPU time** goes to this, and none of tonight's overnight goals depends on it.
