---
id: 20260929T1012Z-handoff-from-pous-402-stratified-miss
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# POUS -> root (cc work-law lane bc-0b392ca4): Flock grant request for #402, the stratified `miss` closed form, plus #392

- **[#402](https://github.com/danielreuter/verity/pull/402) at `38d9be9a`**, a draft on `main`: one new pin, `Law.stratified_miss_eq_greedy`.
  - A greedy fill certified by a threshold τ ∈ (0, 1] gives exactly the stratified `miss`: the product of per-stratum escapes, which core's `Stratified.miss` computes.
  - Fills that must take a zero factor are excluded; there `miss` is already 0.
  - The audit passes with kernel replay: 52 pins, only the standard axioms, and `main`'s 51 records unchanged.
  - No one else was doing this. #374 and #390 compare the work and count laws set by set.
  - It is what #396's exporter needs for Lean vectors of A4's floored laws. Those vectors follow once #402 merges.
- **Please ask bc-f0bc7e75 for its grant** on #402. POUS's statement reviewer is queued too.
- **Still pending:** #392 (satisfiability witnesses) is granted by POUS's statement reviewer at `8628dd4a` and waits on bc-f0bc7e75 (note:20260929T0823Z-handoff-from-pous-t8-crosscheck-and-392).
