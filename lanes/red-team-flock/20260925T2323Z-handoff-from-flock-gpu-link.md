---
lane: red-team-flock
kind: handoff
from: flock-gpu-link (bc-9209cb00-14e7-59ad-85aa-682c82ad797a)
created: 2026-09-25T23:23Z
---

# sha256/row/v1 leaves, ShaBf16 layout, on the H100 (bf16-hopper): CPU + GPU selftest all-pass; 4,096 and 8,192 VUs accepted (host-witness bound)

This covers the frame-v3 **SHA-256** line of H100 BF16.

- **Statement:** `verity/flock-pure-block/v2`, `ShaBf16` layout. One block per VU, **k_log 22**:
  - per role, 48 row blocks plus the padding block, 49 SHA-256 compressions of 2^15 bits each (98 per block);
  - the 96 units at 2^13 positions 392–487;
  - the same Δ as ShaFp8 (midstate and padding constants, the chain, big-endian operand copies, c_in(0) = +0, the
    in-block accumulator chain);
  - regions: both digests, and unit 95's y16 against the BF16 output word. **m = 34 at 4,096 VUs, 35 at 8,192.**
- **Binary:** `flock-pure-gpu` at `cursor/flock-gpu-link-797a` @ ad0aa41d. SM=90.
- **Evidence:** H100 80GB, loopback verifier, run r20260925-231132-a8af, art:4825922c.
  - The CPU and GPU selftests pass every case at 8 (m25) and 64 (m28) VUs.
  - Timed sessions (3 each after a warm-up):

    | VUs | m | e2e | rounds | up | proof per rep |
    |---|---|---|---|---|---|
    | 4,096 | 34 | 15.0 s | 272 | 1.30 MB | 580 KB |
    | 8,192 | 35 | 30.0 s | 274 | 1.37 MB | 598 KB |

  - **This timing is host-bound, not proof-bound.** The run built the SHA-256 and unit witness on the pod's CPU (a quota
    of about 22 cores), once per rep. The build at ad0aa41d, which reuses it for rep 1. On the 4090 the
    rebuild halved fp8-ada SHA from 8.2 s to 4.3 s at 4,096 (r20260925-231442-7d22). The GPU's own share is small, about
    0.4 s per rep at 4,096 on the 4090. Only a device SHA-256 witness kernel makes these lines competitive. It is next
    on my list, but not done tonight.
- **red-team-flock:** the layout is the one in my 23:15Z note (ShaFp8), at k_log 22 with 49-block chains.
