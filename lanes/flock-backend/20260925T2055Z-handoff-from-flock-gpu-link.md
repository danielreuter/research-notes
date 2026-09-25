---
lane: flock-backend
kind: handoff
from: flock-gpu-link (bc-9209cb00-14e7-59ad-85aa-682c82ad797a)
created: 2026-09-25T20:55Z
---

# fp8-ada on the 4090 works: flock-pure-gpu @ 48045063, GPU selftest all-pass; 4,096 VUs in ≈ 0.49 s e2e (≈ 8.3k VU/s) loopback

**Binary:** `flock-pure-gpu`, `cursor/flock-gpu-link-797a` @ 48045063 (pushed).
- It is one binary for both lines: the layout is chosen from the instance file (`row_bytes`, `units`).
- **Build for the 4090 with `SM=89`** (`20-gpu-link.sh MODE=build SM=89`; CUDA 13.3, driver 580).
- The bf16-hopper statement digest is unchanged.

**The fp8-ada statement (`verity/flock-pure-block/v2`, fp8 layout), for the red-team request.** One block per VU,
`k_log` 21:
- x chunk 0 (16 compressions) and x chunk 1 (8, END at block 7) sit at 2^14 slots 0–23; W's at 24–47. The 48 units sit
  at 2^13 positions 96–143.
- **Per-slot constants (Δ rows):** the role key at each chunk's first block, the counter (the chunk index), block_len 64
  and the flags. Unit 0's c_in is forced to +0.
- **In-block copies:** the chunk chains, the operand bits to message bits, and the whole 48-unit accumulator chain.
- **Public claims**, each at two points: the four chunk chaining values (x c0, x c1, W c0, W c1), checked natively
  against the row digests at Commit, and unit 47's c_out against the output word (the FP32 accumulator). So the verifier
  needs no intermediate value at all.
- **Publics:** 136 bytes per VU (4 CVs, plus 2 unused u32 kept for a uniform layout).

**Evidence (all preserved), RTX 4090 24 GB, EPYC 7K62 host, loopback verifier:**
- r20260925-203313-60a7, art:0a6be58a: 2,048 and 4,096 VUs.
- r20260925-204653-be9b, art:e5cc3594: selftests CPU + GPU all-pass at 8 (m24) and 64 (m27) VUs, and 3 timed 4,096-VU
  sessions.

| VUs | m | e2e (timed) | VU/s | prove rep0 / rep1 | rounds | up / proof per rep | verify |
|---|---|---|---|---|---|---|---|
| 2,048 | 32 | 0.27–0.32 s | ≈ 6.9 k | 0.12–0.13 / 0.09 s | 252 | 1.48 MB / 540 KB | 0.37 s |
| 4,096 | 33 | 0.44–0.54 s (≈ 0.49) | ≈ 8.3 k | 0.22–0.25 / 0.17 s | 254 | 1.80 MB / 557 KB | 0.36–0.47 s |

- **x native (component):** 1.1e11/s ÷ 8.3k ≈ **1.3e7×**, against B-Ligero's 1.9e7× on the 4090 E4M3 line.
- **Memory:** 4,096 VUs (m33) is the largest one proof holds in 24 GB. Larger batches are sub-batches, so the per-proof
  plateau is 4,096 VUs.
- **Caveats:** loopback only. There was no time for a same-DC CPU pod next to a 4090; expect +0.1–0.2 s of wait at about
  1 ms RTT. `wait_s` in LIVE includes the verifier's final replay (the Finish call); `e2e_s` does not.
- The cell is yours: bench.py, the plateau, a non-producer verifier and Rule I.
