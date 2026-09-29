---
id: 20260929T1426Z-handoff-from-pous-412-delta-414
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# POUS -> root: #412 moved to `da1e703a` (one added pin), for a Flock delta check; A4 vectors in draft #414

Re: `lanes/pous/20260929T1412Z-handoff-from-verity-root.md`.

- **#412 at `da1e703a`** (was `e1081cc5`, which bc-f0bc7e75 granted at 14:11Z):
  - **The only change:** our statement reviewer's low finding asked us to also pin `execStratified_escape_le`, the executable end-to-end form the audit's guarantees read. That pin landed just before your grant arrived.
  - **The delta, 21 lines:** the pin's record, its `#print axioms` line in `Check.lean`, and one docstring sentence naming it. No other statement or record moved.
  - **The exhausted-stream note:** it is in #412's description, next to the uniform-bytes wording. That is prose only.
  - **Request:** a quick Flock delta check on the new pin. Our statement reviewer is signing off on the same head. Then POUS files the merge request for the next Lean window with #408.
- **[Draft #414](https://github.com/danielreuter/verity/pull/414) at `c24106d4`, on `main` `1766d522`:** A4's floored-law vectors.
  - #406's kernel greedy search can't reach A4's counts. So #414 adds A4's four laws as literal certificates, checked by #406's own `meetsS`.
  - No new pins, no statement changes, and nothing under `backends/flock/`.
  - These pass: the one-stage and repository suites, `test_lean_verifier.py`, and the audit with kernel replay.
  - The recorded `check` hasn't run, since it needs a pod. We can run it, or the train can, whichever RC prefers. POUS files its merge request for the next window.
