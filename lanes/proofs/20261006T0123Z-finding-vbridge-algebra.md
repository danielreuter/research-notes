---
id: proofs/20261006T0123Z-finding-vbridge-algebra
campaign: proofs
lane: proofs
kind: finding
status: in-progress
repo: verity
origin: bc-6e8b6a34-9c5d-5cd2-aaa4-7238afa3674f (vbridge-algebra, for the proofs coordinator)
---

# VBridge E (the algebra): checkpoints

Plan: `note:proofs/20261005T2345Z-draft-vbridge-plan`, piece E. Python restated: `rec_algebra.py` at rec-step2 `b6139d9b6`
(991 lines).

- 01:23Z (6:23 PM PDT): scoped. `Structure` restates `run` over a value class (F or symbolic `Lin`), `_build`,
  `structure`, `verifier_rows` and `GfResiduals`' semantics, reusing the Lean verifier's coin-only functions; estimate
  600 to 750 lines, within the plan. Branch `cursor/vbridge-algebra-structure-95d4` off `17cfcdae8`.
- 01:48Z (6:48 PM PDT): `Structure` pushed, `5ac9230d9` (802 lines, 546 of code). Checked against Python at shape
  (25, 22, 8): `structureOf` equals `structure` exactly (5147 operands, 13 residuals); at random coins `verifierRows`' v
  (2710), `kappa`, the fold points, the query rows and `residuals` on a random w all equal Python's. Audit run
  `r20261006-014745-c8b8` on vy-nebius-1. Next: the lemmas (`residuals` on the built S is `run` over F), then the stages.
