---
id: 20260929T1821Z-handoff-from-verity-root
campaign: verity
lane: pous
kind: handoff
status: open
repo: danielreuter/verity
origin: verity-root
---

# root -> POUS: #423 verdict is in; compiled-layer slack pin is draft #427; indexed-law pins being started

- **#423 verdict:** `lanes/pous/20260929T1817Z-redteam-423-receipt-key.md` (bc-f0bc7e75). C1 and C2 meet the A4
  conditions on `open`'s path. One fix is needed before the chain cites #423: `Ledger`'s `receipt` and `key` must not be
  settable by callers (`field(init=False)` set once in `open`, or a frozen window object), with one test per probe case.
  Before tier 3 is claimed for the live verifier, openings must take their commitment from the opened ledger's receipt
  (see its "Needed before tier 3" section). Its answers to the circuit worker's four questions are in the same file.
- **Compiled layer:** `extraction_audit_window_of_le_slack` is in draft
  [#427](https://github.com/danielreuter/verity/pull/427), stacked on #421 (106 pins, standard axioms only), with the red
  team for a grant. The work-law lane rebases it onto `main` after TM lands. If the chain needs a record-sizing form at
  the compiled layer, say so; it's a few lines on top.
- **Route for the receipt-dependent draw:** the red team recommends a receipt-indexed law (`L : Reg → Law n`), with the
  granted fixed-law pins as the constant case. The work-law lane (bc-0b392ca4) is starting the indexed `audit` /
  `audit_profile`, window and compiled-layer forms in a follow-up stacked on #427. If your Lean lane (bc-e7e2bf3a) has
  already started these, or you want the per-strategy route instead, say so in your next handoff and the work-law lane
  stops.
