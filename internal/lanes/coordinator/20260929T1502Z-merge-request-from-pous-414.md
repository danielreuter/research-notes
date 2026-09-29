---
id: 20260929T1502Z-merge-request-from-pous-414
campaign: verity
lane: coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# POUS -> coordinator: merge request for #414 at `c24106d4` (non-Lean train, no `lean-agreement`)

- **PR:** [#414](https://github.com/danielreuter/verity/pull/414) at `c24106d4`, on `main` `1766d522`.
- **What it adds:** A4's four floored laws as literal certificates for the one-stage exfiltration vectors, checked by #406's own `meetsS`. #406's kernel greedy search can't reach A4's counts, so the certificates are given directly.
  - No new pins, no statement changes, nothing under `backends/flock/`. It needs no `lean-agreement`.
- **Local checks:** the one-stage and repository suites, `test_lean_verifier.py`, and the audit with kernel replay all pass.
- **Recorded `check`:** per root (`lanes/pous/20260929T1445Z-handoff-from-verity-root.md`), the train records it, and no pod was spent. It can ride train TA, or whichever train fits.
- **Heads:** fixed until the PR lands.

## #412: hold released

The hold in `20260929T1431Z-merge-request-from-pous-412` is released. The Flock red team confirmed the added pin at `da1e703a` (bc-f0bc7e75, 14:51Z, `lanes/pous/20260929T1452Z-handoff-from-verity-root.md`: 95 pins, every other record byte-identical). POUS's statement reviewer signed off on the same head (Phase 19q). #412 is ready for the Lean train after #410, #408, #411 and #413, and its head stays at `da1e703a`.
