---
id: proofs/20261006T0122Z-finding-vbridge-gf
campaign: proofs
lane: proofs
kind: finding
status: in-progress
repo: verity
origin: bc-2babccd5-7012-5fdb-b7b2-2d24012bfa79 (vbridge-gf, for the proofs coordinator)
---

# VBridge B1 (Karatsuba) and B2 (residuals): checkpoints

Plan: `note:proofs/20261005T2345Z-draft-vbridge-plan`, pieces B1 and B2.

- 01:20Z (6:20 PM PDT): B1 `FlockVBridge.sound_mul128` (#1090's Karatsuba, post-move imports) builds locally, pushed on
  `cursor/vbridge-gf-95d4` at `f5ff75fa2`; audit run `r20261006-012013-995c` on vy-nebius-1.
- 01:43Z (6:43 PM PDT): B2 `FlockVBridge.sound_residualForms` (`residualForms` = `rec_residuals.residual_forms`;
  new step `polyOf_recomb`, Karatsuba's recombination is linear in its leaves) builds locally, axioms propext,
  Classical.choice, Quot.sound only; pushed on `cursor/vbridge-residuals-95d4` at `8a00edeea`; audit run
  `r20261006-014233-86bc` on vy-nebius-1 (started before B1's record lands: the trees differ only in `lean-audit.json`).
- 02:25Z (7:25 PM PDT): B1's audit `r20261006-012013-995c` PASS (6873 declarations, 217 modules, 1749 guarantees; one
  guarantee new, none changed; 42 min, pod load ~168). Record committed unchanged on `cursor/vbridge-gf-95d4` at
  `9a87c37ac`; merged into B2's branch (`7e59941e1`, clean). PR file `internal/proofs/vbridge-gf-b1-pr.md`.
