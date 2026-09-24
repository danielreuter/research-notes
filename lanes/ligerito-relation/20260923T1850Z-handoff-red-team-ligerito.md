---
lane: red-team-ligerito
to: ligerito-relation
kind: handoff
created: 2026-09-23T18:50Z
severity: SOUNDNESS-LOSS (x2, in the glue) + BREAK (ZK, in the glue)
---

# Three traps that land exactly where you glue pcs + sumcheck + zk

You own prove.py / proof.py / run.py, so these land on you. Details: `~/.research/notes/lanes/red-team-ligerito/20260923T1830Z-report-red-team-ligerito.md`.
Scripts: `backends/direct/ligerito/redteam_soundness.py`, `redteam_libra_bivariate.py` @ 9182132 on `lane/red-team-ligerito`.

1. **SOUNDNESS-LOSS: set B's |S| (239/173/174/174/176) are sized for the radix-3 shapes with NO column padding, and have 0.01 bits of
   margin.** On the pow2 committed polynomial the sumcheck layout produces (N = 2^30, rates exactly 1/2, 1/4) they give **2^-99.19**.
   pow2 needs fp8 `[312,192,192,194,194]` (721.8 KiB). With ligerito-zk's `T_PAD = 256` padding on every column they give **2^-119.34**
   (fp8; L5's rate 3/16 goes to 1/4). ZK needs `[240,173,174,176,194]` (659.2 KiB incl. 30 KiB `ybar`) or rates (1,2,2,3,3) with
   `[239,172,174,158,163]` (651.3 KiB). Derive |S| per proof from `params` for the actual shape and t_pad; never copy set B.
2. **BREAK (ZK): don't combine the sumcheck's bivariate opening round with `zk.SumcheckMask` as is.** The Libra mask has no X1·X2
   terms, so 9 witness-dependent coefficients of the first zero-check message go out in the clear (demo: identical across mask draws,
   different across witnesses). Either unpack the opening round when ZK is on, or wait for ligerito-zk's cross-term block. Under ZK,
   every zero-check round must also send the full degree-3 `s(X)`, not Gruen's `q`: `eq q + rho G` is not of the form `eq q'`.
3. **Job accounting (PROTOCOL.md batch rule, lane b-batch-bound).** A 4096-VU job is ONE Ligerito proof today. If a device
   splits it into N proofs, each needs 2^-(128 + log2 N). N = 2: fp8 `[242,174,175,176,176]`. Bind `n_proofs` into the statement
   as Ligero does, and make the Rust verifier's `--target-bits 128` the default: today `verify` reports `soundness_log2` for a
   single proof but does not reject a proof carrying |S| = 1.
