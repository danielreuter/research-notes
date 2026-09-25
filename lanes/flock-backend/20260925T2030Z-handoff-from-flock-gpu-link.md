---
lane: flock-backend
kind: handoff
from: flock-gpu-link (bc-9209cb00-14e7-59ad-85aa-682c82ad797a)
created: 2026-09-25T20:30Z
---

# Faster flock-pure-gpu (v2, bf16-hopper): 8,192 VUs in 1.23 s loopback (was 2.41 s); v2 GPU selftest all-pass. Use e8eedd80 or later

**Binary:** `flock-pure-gpu` at `cursor/flock-gpu-link-797a` @ **e8eedd80** (pushed). 4f7db693 adds the fp8-ada layout (CPU
only for now) and leaves the bf16 statement digest unchanged, so either commit works for the H100 cell. Build and CLI are
unchanged (`20-gpu-link.sh MODE=build`).

**What changed:**
- Honest `--gpu` sessions now build the witness inputs on the device from the instance rows and the recorded
  accumulators: the chunk-chain kernel, then the unit inputs. The Commit publics (chaining values, unit 31's c_out and
  y16) are read back from the device.
- Rep 1 reuses rep 0's unit-witness region (a device cache).
- Tampered witnesses (the GPU selftest's negatives) still take the host path.

**Validation:** run r20260925-202058-61f1, art:9b34fdb4 (H100 80GB, AP-IN-1, loopback verifier, because no CPU pod was in
stock in any DC that had an H100). v2 selftest passes on CPU and GPU at 8 and 64 VUs.

| VUs | m | e2e (median, 3 timed) | VU/s | prove rep0 / rep1 | witness rep0 / rep1 | wait | rows_s |
|---|---|---|---|---|---|---|---|
| 4,096 | 34 | 0.648 s | 6.3 k | 0.394 / 0.233 s | 0.195 / 0.045 s | 0.20 s | 0 |
| 8,192 | 35 | **1.233 s** | **6.64 k** | 0.756 / 0.451 s | 0.374 / 0.090 s | 0.24 s | 0 |

**Your earlier same-DC run for comparison:** at 8,192 VUs it paid about 0.15 s more wait than loopback (0.39 s against
0.24 s). So expect about 1.35–1.4 s against a same-DC verifier, which is about 6k VU/s, or about 5.3e7× at H100 BF16.
The cell is yours: bench.py, the plateau, and a non-producer verifier.

**Next:** fp8-ada on the GPU and a 4090 run (sm_89). I'll hand that over when it lands.
