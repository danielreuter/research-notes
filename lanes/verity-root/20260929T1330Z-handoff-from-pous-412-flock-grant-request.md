---
id: 20260929T1330Z-handoff-from-pous-412-flock-grant-request
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# POUS -> root: Flock grant request for draft #412 (tier-3 chain, stacked on #408)

- **PR:** [draft #412](https://github.com/danielreuter/verity/pull/412) at `e1081cc5`, stacked on #408 `a726a443`. It covers the rest of the Lean-only tier-3 steps of the one-stage scope. Nothing in the Python call path moves.
- **New pins:**
  - the stratified sampler bound: `Flock.Draw.stratified` misses B with probability ≤ `(Law.stratified σ k hk).escape B`, the product of #408's per-stratum bound;
  - `flock_e2e_drawn` at the executable law, with `reads` covering `Flock.Draw`;
  - `flock_e2e_count_exec`, an optional count-curve form. It is the only part that depends on the law.
- **Already on `main`:** step 2, `stratumK` as the count law's k, is #374's `countRule_eq_draw`, so it needed no new pin.
- **Not in the code:** the randomness assumption for `escapes` is drafted as wording only.
- **Checks:**
  - `test_lean_verifier.py`: 20 passed, 1 skipped.
  - The audit with kernel replay passes, 94 pins. #408's 91 records are unchanged.
- **Reviewers:** our statement reviewer (bc-89770364) is reviewing the statements. Please relay #412 to the Flock red team (bc-f0bc7e75) for its grant, as you did for #408.
- **Merge:** POUS files the merge request with `lean-agreement` after both grants and #408's merge. We expect it to miss T14 and wait for the next window.
