---
cursor:
  subagentId: "bc-b139c29c-b0f6-5d6a-85d6-43e446d3b0c4"
lane: pous
kind: note
from: hash-cut change-3 and PoUW-bench worker (bc-b139c29c, for the pous root)
to: sm_120 PoUW coordinator (bc-2aa33ad8), for GPU 1
created: 2026-09-30T11:00Z
---

# -> bc-2aa33ad8 (for GPU 1): A's commitment in A's producer, measured; attempts 43–46 logged

- **Decode, A's path** (run `r20260930-105308-b8ae`, verifier accepted all 12 transcripts), with the leaves, segment
  trees and seeds in the producer:
  - `-h3t` is 11.0 µs, against 15.4 µs for `-h3` on the matched producer;
  - `-h2t` with its seed is 17.2 µs, against 21.0 µs.
- **Decode, totals:** `-h2t`'s drops 4.1 µs. `-h3t`'s doesn't move (22.6 against 22.8 µs), because the post-GEMM tile
  hashing beside the GEMM now sets it. That is your epilogue digest fusion.
- **Prefill:** A's whole commitment inside the memory-bound producer costs 0.029 ms over the producer, against 0.266 ms
  as its own kernel. `-h2t`'s prefill estimate is 1.344× against 1.482×.
- **Panel:** attempts 43 (`v1-h2`), 44 (`v2-h2`), 45 (`v1-h3`) and 46 (`v2-h3`). They are kernel attempts, since
  the format is unchanged.
- **For GPU 1's real producer:**
  - It needs a thread, or a warp, to own each 256-byte segment (64 contiguous FP32 words of a row).
  - It calls `b3s_segment_key`, which needs the domain only, then `b3s_segment_regs(key, w[64], out)` on the words
    exactly as it stores them, and, if it owns a whole row, builds the segment tree in its block, as
    `derive_rows_b3s` mode 1 or 2 does.
  - At decode, a producer laid out a thread per segment is 2.7 µs slower than a wide one, so a warp-cooperative layout
    may be worth it there.
  - All of this is in `hash_h2.cuh` (#533) and `h1_standin.cu` ([#537](https://github.com/danielreuter/verity/pull/537)).
    I haven't touched GPU 1's code.
- **Details:** `internal/pouw/rtx-pro/a-commit-latency.md` §10.
