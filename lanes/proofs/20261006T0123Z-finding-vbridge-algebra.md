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
- 02:50Z (7:50 PM PDT): `residuals_eq_run` proved: on `structureOf`'s S and `verifierRows`' v, `GfResiduals` at w is
  `run` over F on the messages w holds, at the rep's coins, when each running-sum pair adds to `kappa`'s component.
  Four stacked branches, pushed: `structure` `34cefd872` (`_build` as straight binds, comb slots counted first; same S,
  v, kappa as Python again at (25, 22, 8)), `sim` `383856439` (`run_sim`, 572 lines), `build` `c28092c68`
  (`buildAll_spec`, 611), `eval` `e3898fe2b` (`residuals_eq_run`, 134). `r20261006-014745-c8b8` PASS on `5ac9230d9`
  (record unchanged: no pin). Audits `r20261006-024951-946b` (sim) and `r20261006-024951-26c0` (eval) running.
  Next: `Zerocheck` (V*'s residual zero ⇒ the two `check`s of `bindAndZerocheck`, its loop as `Refine.zStep`'s fold).
- 03:25Z (8:25 PM PDT): three stages pushed, each stacked on the last. `zerocheck` `07eb94a35`
  (`zerocheck_of_residuals`: V*'s zerocheck residual zero gives `bindAndZerocheck`'s `v_C` check and its round loop
  as `Refine.zStep`'s fold ending at `fA·fB`, with `finalC := zc.vc`), `lincheck` `8ee0fd2d3`
  (`lincheck_of_residuals`: the loop as `Refine.lStep`'s fold ending at `dot comb zPartial`; `folded_size` gives the
  comb's 64 from `FlockLevel3.folded_eq`), `ringswitch` `5fbee7d2e` (`ringSwitch_of_residuals`: each claim's value
  check on the decoded ring switches, and Ligerito's `T` = `Σ γ_k·β_k` over the verifier's bit transposes `tOf`).
  Next: `Ligerito`, then audits of the new heads and the PR files.
