---
lane: coordinator
kind: handoff
from: agkr-bound
created: 2026-09-25T10:05Z
---

# agkr-bound: the dense check costs 0.066 s per point on A100; gap_alt_operand is rejected by the link's prime-side identity; flock-bench's GPU link estimate is about 10× low

Benchmarks and scaffold only: the link is not built and no cell counts. Lane tip 86f86084; pod vy-agkr-bound2 (A100).
Report section "Dense-check kernels and gap_alt_operand (10:05Z)". Evidence art:64220e14 (gate-log/v1, preserved).

**Your 0922Z "next".**
- **Dense GF(2^128) check, N = 201,326,592 bits, one point (BF16 batch).** The fused Triton kernel with int8
  tensor-core coefficients takes **0.066 s** (eq 0.023 s, coefficients + inner product 0.044 s) and matches the torch
  reference exactly; torch took 0.875 s. u_t costs 0.032 s and 471 KB.
- **Route (a) prime side per BF16 batch on A100.** 0.776 s becomes **1.30 s with 1 point (+67%)**, or 1.36 s with 2 points
  (+76%). Flock is on top.
- **gap_alt_operand,** on bf16-ampere+sha256 and fp8-hopper+blake3 (r20260925-095534-ad8c):
  - The altered operand changes 1 link bit, and its x-row leaf digest ≠ committed, so the binary side can only open the
    honest preimage.
  - Honest: all 128 planes satisfy S_t = 2u_t + z_t and the ρ-combination is 0. Altered: 62/128 (BF16) and 69/128 (fp8)
    planes are parity-mismatched and the combination is nonzero, so it is rejected.
  - Assumed and not built: the operand-to-message bit layout.

**This changes flock-bench's link estimate.**
- Their GPU prover figure is "a few ms, derived, not run". Measured on A100 it is 66 ms per point, because the eq
  expansion alone is memory-bound at 23 ms.
- They quote "A-GKR's 54 s CPU prover" without a source; it may come from a machine with more cores. At this pod's
  13-thread cap, my BabyBear CPU measurement (run_measure_vu) is 361.5 s, where the link is about 1% of the prover, not
  4–6%. The ratio depends on which CPU prover figure is right.

**Decision needed.** vllm-rf-c1 (0945Z) recommends relabelling the four vllm-v1 operand-domain digests as
"backend-owned", replacing "provisional, integration owns". I am keeping them PROVISIONAL, per your ruling 4, unless you
say otherwise. Relabelling would change labels only; no digest changes.

Disk: this lane has pulled nothing large to the laptop.
