---
id: 20260930T2039Z-handoff-from-compute-accounting-carry-out-daniel-rulings
campaign: pouw
lane: pous
kind: handoff
status: open
repo: danielreuter/verity
origin: compute-accounting (bc-e90634dd)
---

# @old-accounting: Daniel ruled on the beacon, `-h2` and the registered weights (1:36 PM PDT); please have your workers carry them out

The rulings are in `note:20260930T2039Z-rulings-from-daniel-pouw-decisions`. Your agents own every piece, so please relay these to them. Their
results come to me as usual.

- **The beacon is drand quicknet.**
  - The assessor (bc-d7d4b0d1) rates `beacon-unpredictability` for it.
  - The assumptions table (bc-69c09d42) updates, and the panel recomputes each line's weakest rating.
  - Your store's `docs/pouw/assumptions.md` and `notes.md` record it as decided.
  - I'll name it in `protocols/pouw/PROTOCOL.md` after the Pearl-C chain lands, because every Pearl-C PR edits that file. If a
    PR already defines the draw's beacon round, tell me which.
- **`-h2` goes on the served path.**
  - bc-ccd30e80 takes #596 forward: re-check it on main, and file its merge request in `lanes/coordinator/`.
  - bc-b139c29c takes #572.
  - bc-dd22acf8 folds `-h2` into the MVP's served windows, window 7 on.
  - bc-2aa33ad8 updates the panel lines.
- **Registered weights use the keyed 8-block rotation** for FP8 v1 and v2 now.
  - bc-8412d697 and bc-6289d8b0 mark it adopted in `docs/pouw/approved-weights.md`.
  - Pearl-C4 follows once #580 enforces F1′ (bc-71c6ab78 and bc-a8466279). The curated list is the fallback.
- **`-h3` is still open.** It waits on M3's statement review (bc-824e54a2).

**Priority:** these don't outrank Daniel's priority 1. bc-2aa33ad8's freeze-list sign-off for the node-2 cutover comes first (Slack
thread `1790799684.670839`, due 2:30 PM PDT).
