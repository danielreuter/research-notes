---
lane: b-ligero-standard-hash
kind: handoff
from: flock-glue
created: 2026-09-25T12:15Z
---

# flock-glue: Flock-CUDA e2e at 4096 VUs vs B-Ligero bare: A100 BF16 1.18x, H100 BF16 1.58x, H100 FP8 1.42x (was 3.26x / 12.3x / 6.04x). Profile Flock b684b12 `Fast` ~2^-100, NOT CLEARED; r2 stand-in (`Fast100` x2, NOT GRANTED) 2.18x / 2.87x / 2.59x

Report: `lanes/flock-glue/20260925T1011Z-report-flock-glue.md` (FINAL).

Final runs, PRESERVED on R2:
- A100 r20260925-114930-2278 (art:863fbebf…)
- H100 r20260925-114930-aed8 (art:40698799…)

Bare baselines are the brief's: 0.2374 s (A100 BF16), 0.1131 s (H100 BF16) and 0.0706 s (H100 FP8). Every proof
verified. The planted-NaN and tamper negatives rejected.

## What changed
1. **GPU PoW grinding** saved 0.20–0.33 s per batch, the largest item. Flock-CUDA's `FsChallenger` ground every site on
   the host with single-thread SHA-256. It is now hooked to `pow_grind.cuh`, which gives the same nonce, so the proofs
   don't change. Sites under 8 bits stay on the host.
2. **Device unit witness** saved 0.13–0.92 s. A 10–47 ms kernel, built from the instance operands and the netlist,
   replaces the 2.15 GB pageable upload. For r2, one device witness serves both reps: 0.325 s on H100 BF16, against
   flock-128's 0.51 s upload-once estimate.
3. **Side-stream overlap** saves 19 ms on A100 and nothing on H100 at 4096 VUs, where the witness competes for SMs. It
   required changing every `cudaDeviceSynchronize` to a legacy-stream sync.

Kernel-only, before and after (after includes the witness kernel): 1.00x to 1.11x, 1.24x to 1.41x, and 1.05x to 1.18x.

## Still open
- **Flock proof kernels at 1.00x / 1.24x / 1.05x.** This is the floor for the profile.
- **Witness kernel at +0.14x to +0.20x.** It's latency-bound, at about 1,700 cycles per level with 96 units in series.
- **About 16–17 ms of idle GPU time per batch.** These are host FS round trips and launches, so they need a
  device-side or live challenger, or CUDA graphs.
- **Not built:** BLAKE3 leaves from device-resident rows, and the unit-to-leaf bit glue.
- **No clearable profile:** r2 needs R1–R8 from red-team-flock.

Pods: A100 56nan0h04ho1u9 and H100 oypxgunobip13f, both terminated at 12:11Z. Spend about $7.4.
