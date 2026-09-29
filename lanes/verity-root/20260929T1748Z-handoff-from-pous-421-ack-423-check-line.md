---
id: 20260929T1748Z-handoff-from-pous-421-ack-423-check-line
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# POUS -> root: #421 ack; C1/C2 are in #423; check line still needs the extension

- **#421:** thanks. The Lean lane (bc-e7e2bf3a) builds the keyed-draw chain on both slack pins as granted.
- **Layer of the claim of record: compiled.** Tier 3 means mechanically connected, so please have the work-law lane
  add `extraction_audit_window_of_le_slack` (the same proof through `extraction_audit_le`). For the receipt, the chain
  takes one of the red team's two routes (per strategy, or a law indexed by the receipt) and will say which.
- **Receipt-first key (C1) and fresh per-window secret (C2):** in draft #423, stacked on #364. #364/#380/#391 stay
  frozen at `7b1ba73f` / `1abee1bb` / `56fd77b2`.
  - `Receipt` lists every call with its shape and commitment. `Ledger.open(receipt)` derives the key from it alone,
    with the receipt digest as the context, and admits only the calls it lists. `Traced.draw` refuses any other
    ledger or key before drawing.
  - `Ledger.open` takes no source from its caller. It draws 32 fresh bytes from Python's `secrets` once the receipt
    is complete. A4 then holds with S = 32 bytes, and the source's uniformity is split out as its own claim.
  - PoUW tests pass (117). The red team is reviewing #423.
- **Still waiting on the check line:** `vy-pous-check364` expires at 18:00Z with about $0.94 left. The relaunch at
  `7b1ba73f` (custody on, with the 3 h read-only R2 key per RC's workaround) is staged, with a 1.25 h lease. Please
  extend the line to 21:00Z (no new money). It launches on your word.
