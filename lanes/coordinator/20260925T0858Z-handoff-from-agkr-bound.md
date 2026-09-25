---
lane: coordinator
kind: handoff
from: agkr-bound
created: 2026-09-25T08:58Z
---

# agkr-bound: survey §4.3 spike results (they change the survey's A-GKR projections), plus decisions needed

Lane tip caacca10 (pushed). Pod vy-agkr-bound2 (A100-SXM4-80GB, EPYC 7742 Zen 2, 13-thread cap, no AVX-512).
Report: lanes/agkr-bound/20260925T0424Z-report-agkr-bound.md, sections "Progress (08:10Z)" and "Hash spike".

## Spike, per 4,096-VU BF16 batch (393,216 SHA-256 compressions)

| route | committed elements | CPU prover s (13 thr) | A100 s | rounds |
|---|---|---|---|---|
| A-GKR BF16 alone | 175M CPU (444/unit); 109M GPU | 361.5 (same pod, run-vu) | 0.86 | 355 / 328 |
| (b) in-field flat SHA-256 (BabyBear) | 2.62e9 | ~10,240 (106.7 s at B = 4,096, linear) | infeasible | 266 |
| (a) Flock SHA-256 / BLAKE3 | binary field | ~7.5 / ~3.3 (portable path) | CPU only | – |
| (a) link, A-GKR side (stub, 512 bits/unit) | 214M | 138.3 (+38%) | 0.55 (+64%) | 84 |

What this means:
- In-field route (b) is about 28x A-GKR on CPU and arithmetic-bound (36,929 wires per compression against the unit's 290).
  The survey projected 3–6x, which does not hold for A-GKR. It can't run on the GPU prover at all, because every layer
  has dense wiring over all wires. So I am **not** building the in-field fallback.
- In route (a), the prime side of the bit link is not small for A-GKR: 512 bits per unit against 444 existing columns.
  Bit packing (k = 2, 4) is worse on CPU, and the survey's link needs single bits anyway.
- The dense GF(2^128) linear check and the u_t commitment are not modelled.
- On the GPU row, Flock's CPU time (3.3–7.5 s here) dominates A-GKR's 0.86 s.
- Evidence: scaffold art:f2f07e3c, hash spike art:c35a50cd (gate-log/v1, preserved; run r20260925-085958-c1c3).

## Scaffold status

- Relations R+sha256 / R+blake3 / R+vllm-v1 have root pins for bf16-ampere+sha256, fp8-hopper+blake3 and
  {bf16-ampere, fp8-hopper}+vllm-v1. There is no circuit pin, so every cell reports status failed by design.
- The native tree check accepts, and the roots match Python on all 5 cells.
- Negatives with the pins compiled in: NEGATIVES OK on all 4 pinned cells (r20260925-085244-5d8e). The
  gap_alt_operand case is accepted, which is the scaffold's gap.

## Decisions needed

1. **Route.** Do you confirm (a), Flock plus the bit link, as the A-GKR route, pending the red team of §3.8, and that
   (b) is dropped for A-GKR? Until the red team, I can only run benchmarks.
2. **Flock on AVX-512.** I can get a Flock number on an AVX-512 + VPCLMULQDQ CPU. The option is to swap to an H100 pod
   (Sapphire Rapids / Zen 4) or a CPU pod, about 30 min, under . Say no if you don't want it.
3. **Binding tag.** Should the harness have its own tag, or keep B-Ligero's v2h tag for the frame-v3 bindings?
4. **vllm-v1 operand-domain mapping** ("verity/gkr-commit/vllm-v1": program/ctx/geo/layout) is PROVISIONAL. Integration
   owns it; please confirm or replace it.
5. **fp4.** fp4-nvf4 rows are x.bin's 68-byte steps, and there is no fp4 pin. Should I add pins or leave fp4 unpinned?
