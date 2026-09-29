---
id: 20260929T1618Z-handoff-from-pous-416-drawos-grants
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# POUS -> root: #416 (live `drawOS` bound, named uniform-bytes assumption) needs the statement grant and the Flock red team

Daniel approved both tightenings of #408/#412 this morning. They're in draft
[#416](https://github.com/danielreuter/verity/pull/416), stacked on #412, head `8aed7908`. #408 and #412 are unchanged
and still filed for the next Lean train.

- **Proved:** `drawOS`, the live draw including its extend-and-rerun loop, misses a set B with at most #408's and #412's
  escapes. That holds for the subset, stratified and work draws, on byte streams and as a law.
  - The audit passes with kernel replay, using only standard axioms.
  - There are 101 pins: #412's 95 are unchanged, plus 6 new ones.
  - `test_lean_verifier.py` passes on the rebuilt `flock-verify`.
- **Assumed:** A3 is named `uniform/io-getrandombytes`, in `verity.claims` and `ASSUMPTIONS.md`, with an upstream watch
  entry.
  - In Lean it's `Assumptions.UniformRandomBytes`, stated over an abstract byte source, since a statement about `IO` would
    be vacuous.
  - `drawOS_def` is a `rfl` proof that `drawOS` is `drawWith` with its bytes from `IO.getRandomBytes`.
- **Decision for you: a change to `Flock/Draw.lean`.** `drawOS` now goes through an abstract byte source (`onWith`,
  `stratifiedWith`, `drawWith`). At `IO` it makes the same calls in the same order. Please have the Flock red team review
  this alongside the six new pins.
- **Correction to the #412 red-team note:** the live OS-randomness draw never refuses; it extends and reruns. Only
  `draw --stream` refuses.
- **Still open, as stated in the PR:**
  - Each bound holds for every number of bytes read per stream; that the unbounded run's escape is their limit is argued
    in the docs, not proved in Lean.
  - The Bernoulli law and keyed `verity.randomness` draws aren't covered.
- **Ask:** the statement reviewer's grant on the six new pins and the named assumption, plus the Flock red team on #416.
  We'll file the merge request once both are in and #408/#412 have landed. It touches `backends/flock/`, so the train's
  recorded `check` with `lean-agreement` applies.
