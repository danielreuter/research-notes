---
lane: agkr-table
kind: report
created: 2026-09-24T05:19Z
status: open
---

CHECKPOINT be2d8af4 (07:15Z) [open] art:03e21c7f is IN Table 2 (verify-night accepted 07:00Z). New registered result art:21d253bd (run-files art:1fbd535f): t.total 1.736s median (reps 1.754/1.717/1.736), same proof bytes f2c05851; only rejection = independent verification; follow-up handoff to verify-night. Improvements: opening q by evaluation (t_open_wq 0.80->0.085s; negatives 52/52 + Rust 44/44 rejected), gc.freeze after warm-up (-0.1s GC pause in timed reps), witness generator as one CUDA graph (0.34->0.072s; rows/bad identical on frozen + corrupted operands). next: LogUp Fiat-Shamir sponge on the device (t_lookup 0.79s, ~3000 host round trips)
CHECKPOINT 53bd441b (06:44Z) [open] 3-rep A100 cell registered: t.total 2.775s median, art:03e21c7f (run-files art:83324658), only rejection = independent verification; handoff to verify-night sent. next: NTT opening (w,q 0.80->0.07s, exact) recorded run
CHECKPOINT 0b0768ed (06:16Z) [open] SHA-512 Merkle (2^-130.2 live, interactive) + GPU witness gen (0.32s, byte-exact) done; Rust verifier 2/2 accept, 44/44 neg, 40/40 mut; prover 2.36s A100. next: contract emitter smoke -> research run 3 reps
CHECKPOINT 0b0768ed (05:19Z) [open] started 05:20Z; worktree lane/agkr-table@0b0768ed; pod vy-agkr-a100 (A100-SXM4-80GB) up; next: read gkr docs, bootstrap pod
