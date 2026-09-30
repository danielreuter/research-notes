---
cursor:
  subagentId: "bc-b139c29c-b0f6-5d6a-85d6-43e446d3b0c4"
lane: pous
kind: note
from: hash-cut change-3 and PoUW-bench worker (bc-b139c29c, for the pous root)
to: sm_120 PoUW coordinator (bc-2aa33ad8), for GPU 1
created: 2026-09-30T11:44Z
---

# -> bc-2aa33ad8: fused-producer layouts for A's commitment; best is -h3tc, −2.2 µs on A's path; attempts 51–54

- **Four layouts** (run `r20260930-113848-ba94`, verified with the new poisoning and the negative control rejected).
  For `-h3`'s A path against the chain's usual producer, the best is `-h3tc`: 12.6 µs against 14.8 µs unfused.
- **`-h3tc`'s layout:** coalesced 16-byte stores, a CTA a row, the pieces staged in shared memory, and 128 threads that
  hash on a named barrier.
- **Why not more:** the format fixes 13 serial compressions (8.8 µs), and every faster-storing layout hashes slower.
- **Totals barely move:** the tile hashing beside the GEMM sets them.
- **Prefill keeps `-h3t`'s kernel** (attempts 43 and 45).
- **For GPU 1's padding copy as A's producer:**
  - At decode: a CTA a row, coalesced stores staged in shared memory, and 4 hashing warps on a named barrier
    (`derive_rows_b3s_coal`).
  - At prefill: a thread a 256-byte segment (`derive_rows_b3s` mode 1 or 2).
  - Both are in [#541](https://github.com/danielreuter/verity/pull/541) and #537, and `b3s_segment_regs` is unchanged.
- **Details:** `internal/pouw/rtx-pro/a-commit-latency.md` §10.
