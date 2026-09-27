---
lane: flock-zk
kind: report
created: 2026-09-27T06:09Z
status: open
---

CHECKPOINT f57138fe (07:03Z) [open] f57138fe: PROTOCOL.md (exact M1 layout for Lean + Ligerito design + M2 list) and test_zk_stats. Overhead (4-core VM, per rep): m=25 0.25->0.40 s, m=27 0.36->0.52 s; masking ~0, pads commit 18 ms, fixed 0.13 s = prover re-running the lincheck fold (removable). Next: decide Ligerito implementation attempt vs handoff; PR update. CPU only $0
CHECKPOINT 24a1900b (06:51Z) [open] 24a1900b: simulator + stats + audit. zkstat N=64: real vs simulated indistinguishable on all checked classes (p>0.02), unmasked control distinguished (p~0). zkaudit: masked/public/commitment checks pass, 0 unattributed; Ligerito openings+sumcheck+final vector still CLEAR (complete:false). Evidence lanes/flock-zk/evidence/20260927T0830Z-*. Next: Ligerito masking in upstream (per-lane padding + extra lane), then layout doc. CPU only $0
CHECKPOINT a413e598 (06:39Z) [open] a413e598 on cursor/flock-zk-m1-5659 (draft PR #123, stacked on #83): flock-circuit --zk masks every zerocheck+lincheck value with committed pads (VEIL), verifier replays checks as affine forms + inner dot-product proof, triple sacrifice for a*b, mask-slot words hide non-region s_hat_v (rank check). RoPE CPU selftest --zk 24/24. Next: Ligerito masking (per-lane RS padding + extra uniform lane), simulator + chi-square, transcript audit. CPU only, $0
CHECKPOINT e51e2b86 (06:09Z) [open] M1 zero-knowledge lane started (agent bc-2a9978cc-cafd-5d88-a4de-888a71d85659): branch cursor/flock-zk-m1-5659 stacked on #83 @ e51e2b86; reading M0 prover (circuit.rs, zk_hooks.rs, patched Flock) to place zerocheck/lincheck/Ligerito masks for RoPE on CPU; no pods
