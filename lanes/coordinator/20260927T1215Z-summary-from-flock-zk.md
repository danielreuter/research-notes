---
cursor:
  subagentId: "bc-2a9978cc-cafd-5d88-a4de-888a71d85659"
---

**flock-zk status** (CPU only, no pods, $0; updated 14:40Z):
- **The red team granted both milestones, with every condition met.** M1 (masked `flock-circuit --zk`) at `fe35d67d`, #123.
  M2 (the verifier's coin commitment and the Goldreich–Kahan single-rewind simulator) at `2798c21a`, #138. What stands is
  the Lean ZK statement.
- **The same checks on the GEMM coordinate** (m = 26): #150 at `b27551b5`. Selftest 33/33, audit clean, statistics pass.
- **GEMM's open statistics question is answered.** On one verifier tape, the real side's p-values had leaned low.
  - A permutation test showed the lean isn't an artifact of dependence between tests.
  - A pre-registered replication with 128 views on that tape came back clean. By its pre-registered rule the verdict is
    chance, with no sign of a leak. It is with the red team (details in `private/`).
- **The soundness lane's padded table theorem** gives 2^-196.5 per table on M1's level 0. Its restart-weight question is
  answered in `lanes/flock-soundness/`.

**Overheads and next:**
- **Prove time vs M0 on 4 CPU cores:** +21–32% at m = 25, +24–27% at m = 27. The proof grows from 560 to 865 KB per rep
  at m = 25.
- **Estimate for M0's GPU prover on an L40S:** +10–25% end to end (`private/flock-zk-gpu-estimate.md`, no pod).
- **Next:** the red team's read of the replication. Then, on your go-ahead, the GPU port and about one L40S-hour to
  measure it.
