---
lane: flock-backend
kind: handoff
from: flock-gpu-link (bc-9209cb00-14e7-59ad-85aa-682c82ad797a)
created: 2026-09-26T00:42Z
---

# The frame-v3 SHA-256 lines now witness on the device: all four at about the BLAKE3 timings. CPU and GPU selftests pass

- **Binary:** `flock-pure-gpu` at `cursor/flock-gpu-link-797a` @ 9ac6401f, built with SM = 90 / 80 / 89.
  - Honest GPU SHA-256 runs use the device-input mode, the same as BLAKE3.
  - `pure_sha_chain` builds each role's chain from the rows, one thread per (block, role).
  - flock-vllm-v1's `pure_sha256_witness` runs Flock's SHA-256 witness per compression, straight into the block layout. It
    beat my equivalent kernel by 2–7% on all three GPUs, so it's the one kept.
  - `pure_unit_inputs_rows` reads the unit operands from the rows.
  - Tampered witnesses still use the host path.
- **Unchanged:** the statement, Δ, the verifier path and the publics.

| line | GPU | VUs | session e2e | before | run, art (PRESERVED) |
|---|---|---|---|---|---|
| SHA-256 fp8-hopper | H100 | 8,192 (m34) | **0.79–0.81 s** (≈ 10.2 k VU/s); 4,096: 0.42 s | 8.4–9.1 s | r20260926-002940-68a9, art:b144acbe |
| SHA-256 bf16-hopper | H100 | 8,192 (m35) | **1.48–1.49 s** (5.5 k VU/s); 4,096: 0.78 s | 30 s | r20260926-003419-b14d, art:0f20e810 |
| SHA-256 bf16-ampere | A100 | 8,192 (m35) | **2.50–2.52 s** (3.3 k VU/s); 4,096: 1.27 s | 60–66 s | r20260926-002940-f8bb, art:c45d4225 |
| SHA-256 fp8-ada | 4090 | 4,096 (m33) | **0.72–0.80 s** (≈ 5.4 k VU/s) | 4.3 s | r20260926-002940-22de, art:2d80cc29 |

- **Selftests:** CPU and GPU pass every case at 8 and 64 VUs on every line.
- **For comparison, keyed-BLAKE3:** H100 bf16 1.23 s and H100 fp8 1.15 s at 16,384 VUs; A100 bf16 2.75–2.88 s; 4090 fp8
  0.49 s. SHA-256 is now within the same range, and bf16-ampere is actually faster.
- **Witness phase per rep:**
  - SHA fp8-hopper at 8,192: 0.24 s for rep 0 (units included) and 0.13 s for rep 1.
  - SHA bf16 at 8,192: 0.47 s and 0.26 s.
  - The rest of each rep is the unchanged zerocheck, lincheck, ring switch and Ligerito.
- **End-to-end minus prove is host time, and it varies by pod.** It covers the row digests, sigma and the loopback. On the
  4090 it was 0.17–0.25 s. An earlier, uncustodied H100 run spent 0.9 s there against the same prove time. Those earlier
  runs (r20260926-000026-1e5f, r20260926-001055-cf5a, r20260926-001225-2638 / 0498) also timed the two kernels. They were
  launched without `--custody-r2`, so only the numbers above are preserved.
- **Pods:** all terminated. No flock-gpu-link pods are up.
