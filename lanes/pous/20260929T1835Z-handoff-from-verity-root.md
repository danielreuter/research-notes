---
id: 20260929T1835Z-handoff-from-verity-root
campaign: verity
lane: pous
kind: handoff
status: open
repo: danielreuter/verity
origin: verity-root
---

# root -> POUS: receipt-indexed law is draft #429, with the red team for a grant

Follows `20260929T1821Z-handoff-from-verity-root.md`.

- [#429](https://github.com/danielreuter/verity/pull/429), stacked on #427, adds `Audit/Indexed.lean` (7 pins): the
  audit with `L : Reg → Law n` at the oracle and compiled layers; indexed `audit_le`, `audit_profile` and
  `extraction_audit_le`; window bounds at both layers with one η for every receipt, plus the record-sizing form
  (2⁻⁴⁰ + η + ε_ks + δ_link); and a pinned `rfl` lemma that the constant law is the fixed-law audit.
- Kernel replay: 10,012 declarations, 113 pins, standard axioms only. No granted pin changes.
- Your Lean lane (bc-e7e2bf3a) need not build these. If the chain needs a different shape, say so in your next handoff.
- #427 and #429 stay stacked until TM lands, then rebase onto `main`.
