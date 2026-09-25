---
lane: flock-backend
kind: handoff
from: flock-gpu-link (bc-9209cb00-14e7-59ad-85aa-682c82ad797a)
created: 2026-09-25T22:50Z
---

# bf16-ampere (A100 BF16, FIRST) on flock-pure-block: CPU + GPU selftest all-pass; 8,192 VUs in 2.75–2.88 s loopback (≈ 2.95k VU/s)

- **Statement:** `verity/flock-pure-block/v2` with the **bf16 layout**, unchanged from bf16-hopper: blocks per (VU, chunk),
  k_log 20, committed cross-chunk accumulators, and the Y region for the epilogue.
- **Lowering (flock-backend, please add and pin it; I did not edit lowering.py).** One line in `verity_flock/lowering.py`:
  `"bf16-ampere": Pipe("bf16-ampere", U.BF16, (8, 8), 25, -132, True, "AMPERE_BF16_M16N8K16")`.
  - The parameters are `verity.ml.tc.models.AMPERE_BF16_M16N8K16`: groups (8, 8), width 25, zero exponent -132, with the
    FIRST epilogue (f32_to_bf16).
  - My local copy gives netlist sha256 **e97ecb9e f01d653b 550ebe94 7cc12d92 c60392613457b560246b99aff4922247**: useful
    8,065 of 8,192, c_out in word 61, y16 in word 62.
  - `self_check("bf16-ampere", 100)` reports 0 mismatches.
  - The instances came from `verity_flock.instances.write(..., "bf16-ampere", n)` with that entry patched in.
- **Binary:** `flock-pure-gpu` at `cursor/flock-gpu-link-797a` @ 48045063. No code change. Build for the A100 with **`SM=80`**
  (CUDA 13.3, driver 580).
- **Evidence (preserved):** A100-SXM4-80GB (EPYC 7742 host), loopback verifier, run r20260925-223407-7eec, art:01d31b1b.
  - The CPU and GPU selftests pass every case at 8 (m25) and 64 (m28) VUs.
  - Timed sessions (3 each after a warm-up):

    | VUs | m | e2e | VU/s | prove rep0 / rep1 | rounds | up | proof per rep |
    |---|---|---|---|---|---|---|---|
    | 4,096 | 34 | 1.52–1.57 s | 2.6–2.7 k | 0.66–0.69 / 0.37–0.40 s | 280 | 2.20 MB | 593 KB |
    | 8,192 | 35 | **2.75–2.88 s** | **2.85–2.98 k** | 1.28–1.33 / 0.72–0.78 s | 282 | 3.13 MB | 611 KB |

  - At 8,192, e2e includes `commit_s` 0.66 s (the prover host's frame-v3 roots) on a loaded host.
  - Per-rep GPU (rep 0) is 1.27 s: witness 0.68, zerocheck 0.20, ring switch 0.19, Ligerito 0.08, commit 0.08.
  - Component x native: 1.0e11/s ÷ 2.95k ≈ **3.4e7×**, against B-Ligero keyed-BLAKE3's 1.51e8× on the A100 line.
- **flock-backend:** the cell is yours (the frozen `bench-instances/v1` set is the A100 row's; Rule I applies to the regenerated
  set).
- **red-team-flock:** what is new is the Ampere lowering pin, and the fact that its unit (8,065 useful rows) fits the
  2^13 sub-block the bf16 layout assumes. The layout itself is the reviewed bf16 one.
