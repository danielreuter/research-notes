---
cursor:
  subagentId: "bc-b139c29c-b0f6-5d6a-85d6-43e446d3b0c4"
lane: pous
kind: note
from: hash-cut change-3 and PoUW-bench worker (bc-b139c29c, for the pous root)
to: sm_120 PoUW coordinator (bc-2aa33ad8), for GPU 1
created: 2026-09-30T12:02Z
---

# -> bc-2aa33ad8 (for GPU 1): the epilogue digest fusion, prototyped; measure before fusing

- **The result** (run `r20260930-115511-6029`, verified, the negative control rejected). On a tile-shaped stand-in
  GEMM that leaves room beside it, deferring all tile hashing to a low-priority side stream gives `-h3` 1.3104×
  against today's 1.4326× form.
  - Fusing the message digests into the epilogue is worse: 1.3596×. A message's 4 serial compressions go onto the tail of
    a single-wave decode GEMM.
  - The old stand-in's 1,024 CTAs filled every SM, and that occupancy was the contention.
  - `-h2t`: 1.3683× deferred, 1.4564× fused.
- **Decide on GPU 1's real GEMM:**
  - time the GEMM alone;
  - time it with the previous call's tile hashing deferred on a low-priority stream (`USE_NODE_PRIORITY`);
  - fuse only if the pair costs more than about 3 µs over the GEMM alone.
- **If you fuse,** the interface in `hash_sm120.cuh` is unchanged:
  - `b3_msg_digest(c[32], u[32], key, out)`, the key blake3(`pearl-c/h1/message`), with the output at
    `dg + 32·(r·n/32 + h)`;
  - the message is row r's 32 C̃ words at columns 32h … 32h + 31, then the same 32 U words, FP32 little-endian, exactly as
    the epilogue stores them;
  - stage the CTA's C̃ and U block in shared memory, rows padded to 33 words (8.4 KB per 32 × 32 block, inside the tail
    stages), sync, and let one thread per row hash;
  - the tile leaves (`hash_leaf_p`) and the tile tree stay deferred, since a tile leaf is 17 serial compressions and
    doesn't belong in the epilogue.
  - The reference epilogue is `standin_gemm_tile`, in [#544](https://github.com/danielreuter/verity/pull/544).
- **Details:** `internal/pouw/rtx-pro/a-commit-latency.md` §11. It includes a costed sketch of a format with fewer
  serial compressions on A's path: −1.36 µs at best, not worth a new format now.
