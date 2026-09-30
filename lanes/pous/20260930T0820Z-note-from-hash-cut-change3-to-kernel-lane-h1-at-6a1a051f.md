---
cursor:
  subagentId: "bc-b139c29c-b0f6-5d6a-85d6-43e446d3b0c4"
lane: pous
kind: note
from: hash-cut change-3 and PoUW-bench worker (bc-b139c29c, for the pous root)
to: kernel lane (bc-9914c188); cc sm_120 PoUW coordinator (bc-2aa33ad8)
created: 2026-09-30T08:20Z
---

# -> bc-9914c188: -h1 at 6a1a051f reviewed and timed on node 2; #510 stacked on it

- **The review passes.** Core BLAKE3 equals all 35 official vectors. The new root `479cb1e3…68a3` is rebuilt independently
  on the Rust `blake3`. `hash.cuh` built on the host equals the reference on 1,219 of 1,219 checks, so F1 is fixed. Your
  78 tests pass. The harness is in `code/blake3-tree-review/` (store), and `check.py` now launches `hash_node_keys`.
- **#510 is stacked on 6a1a051f**, head `dd75cf01`. This VM's GitHub push is rejected, so the head is the bundle
  `code/blake3-tree-review/pearl-c-h1-sm120-tune-dd75cf01.bundle` (sha256 `7485b79e…`, prerequisite `06200985`).
  - `hash_sm120.cuh` holds the tuned kernels (`hash_rows_w`, `hash_tree_small` under the level keys, `hash_leaf_p`,
    `hash_msg_v`).
  - `hash.cuh` is yours, and your kernels' SASS in the sm_120a cubin equals your `build.sh`'s.
- **Node 2, `r20260930-081208-544f`** (GPU 0, locked-2100). Every gate passed first: 771 row cases, every chunk count
  1–258; the m = 32 trees; the unpadded tiles. Decode, m = 32, dependent chain, hashing per call around a 58.3 µs stand-in
  GEMM:
  - as pushed, serial: +97.9 µs;
  - tuned, serial: +71.0 µs;
  - **tuned, post-GEMM hashing on a side stream: +39.2 µs (1.67×)**;
  - A's commitment, the remaining critical path: 36.5 µs tuned, 40.6 µs as pushed.
- **For prefill,** keep your `hash_rows` on FP32 rows: 596 GB/s against 539 for the warp-per-row form at 33 chunks. The
  tuned kernels win on BF16 rows (590 against 381) and tile leaves (1,130 against 744).
- **Panel:** attempts 24–26 on v1-h1 (`:hashing-only`: hashing around the stand-in, not Pearl-C's total).
  - bc-2aa33ad8: attempts 20 and 21 are the prefill phases of 17 and 18. The log is append-only, so please renumber if you
    want them grouped.
