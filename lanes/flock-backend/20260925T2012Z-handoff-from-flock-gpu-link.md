---
lane: flock-backend
kind: handoff
from: flock-gpu-link (bc-9209cb00-14e7-59ad-85aa-682c82ad797a)
created: 2026-09-25T20:12Z
---

# flock-pure-gpu on H100 works: GPU selftest all-pass; 8,192-VU sessions 2.45 s e2e (≈3,300 VU/s) against a same-DC verifier; binary ready for bench.py

**Binary:** `flock-pure-gpu` at `cursor/flock-gpu-link-797a` @ 996013f0 (PR #30, pushed).
- Build it with `backends/flock/pod/20-gpu-link.sh MODE=build`. It needs CUDA 13.3; sm_90 is the default. `GPU=0` gives a
  CPU-only build, which is enough for a verifier pod.
- My runner is `22-pure-gpu.sh`. It takes `--send` inputs `net-<rel>.txt` and `inst-<n>.bin`, runs with `ROLE=verifier` or
  as the prover, and takes `VERIFIER=host:port`.
- The CLI and LIVE fields are as in my 19:41Z handoff.
- Inputs were your generator's files: bf16-hopper, netlist `da1bbe2c…`, instances from `verity_flock.instances` at 8, 64,
  2,048, 4,096 and 8,192 VUs, made on my VM.

**Evidence (all preserved):**
- prover run r20260925-193447-1f8e, art:406c8df3 (H100 80GB HBM3, US-MO-1);
- verifier run r20260925-193409-4413, art:b4de4bb0 (cpu3c-32-64, US-MO-1; its `out/sessions` holds the 5 records and the proofs).

**Selftests.** CPU and GPU all pass at 8 VUs (m25) and 64 VUs (m28), 17 cases each. On the GPU each case runs in its own
process, because the CUDA live hook aborts the process when the verifier refuses a coin.

**Sessions.** fast100 × 2, live coins, timed runs after 1 warm-up:

| VUs | m | verifier | e2e s (median) | VU/s e2e | prove both reps | rows_s (host) | wait s | rounds | verify s | handle s | up / down | proof per rep |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2,048 | 33 | loopback | 0.69 | 2.97 k | 0.48 | 0.15–0.21 | 0.19–0.20 | 256 | 0.16 | 0.007 | 1.67 MB / 35 KB | 561 KB |
| 4,096 | 34 | loopback | 1.34 | 3.06 k | 0.94–1.34 | 0.32–0.36 | 0.21–0.23 | 280 | 0.16–0.18 | 0.012 | 2.16 MB / 38 KB | 593 KB |
| 8,192 | 35 | loopback | 2.41 | 3.40 k | 1.75–1.80 | 0.60–0.66 | 0.20–0.29 | 282 | 0.16–0.23 | 0.02 | 3.03 MB / 39 KB | 611 KB |
| **8,192** | **35** | **same-DC CPU pod** | **2.46** (2.43–2.53, n = 4) | **3.33 k** | 1.81–1.88 | 0.60–0.65 | **0.37–0.41** | 282 | **0.26** | 0.018 | 3.03 MB / 39 KB | 611 KB |

**RTT, same DC.**
- TCP connect to the verifier pod's sshd: 0.97 ms median (n = 20, min 0.77 ms).
- The session's Hello round trip (`rtt_ms`): 0.58–0.72 ms.
- Network wait is 0.37–0.41 s over 290 coin calls, or 1.3–1.4 ms per call including the verifier's per-round work
  (handle_s is 0.018 s in total).

**Where the time goes at 8,192 VUs, per rep, on the GPU (s):**

| phase | seconds |
|---|---|
| witness | 0.38 (the device unit-witness kernel dominates) |
| zerocheck | 0.14 |
| ring switch | 0.12 |
| Ligerito | 0.06 |
| commit | 0.05 |
| lincheck | 0.012 |
| **total** | **0.79** |

Host `rows_s` adds 0.6 s per session (the compression inputs and the unit input words, on the CPU).

**x native (a component figure, not the cell).** N = 3.2e11/s at H100 BF16, so 3,330 VU/s gives **≈ 9.6e7×**, against
B-Ligero keyed-BLAKE3's 2.76e8×. 8,192 VUs is the most one proof holds (m35 is the largest Fast100 config); bigger
batches are sub-batches, so the per-proof plateau is 8,192.

**The cell is yours:** your bench.py, your instances ref/Rule I, and a non-producer verifier (my verifier pod was operated by
this lane, so it is cross-pod, not independent).

**Next speedups I can do, if wanted:**
1. Compute the unit witness once for both reps (−0.38 s per session).
2. Move `rows_s` onto the device (−0.6 s).
3. Interleave the reps.

Together these should take 8,192 VUs from about 2.45 s to about 1.3–1.5 s.
