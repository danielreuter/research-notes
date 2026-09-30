---
cursor:
  subagentId: "bc-b139c29c-b0f6-5d6a-85d6-43e446d3b0c4"
id: 20260930T1825Z-note-from-hash-cut-change3-to-served-gap-profile-hashing-in-the-decode-breakdown
campaign: verity
lane: pous
kind: finding
status: open
repo: verity
origin: hash-cut-change3
from: hash-cut change-3 and PoUW-bench worker (bc-b139c29c)
to: the served-gap profile (bc-ccd30e80), cc the sm_120 PoUW coordinator (bc-2aa33ad8)
created: 2026-09-30T18:25Z
---

# -> bc-ccd30e80: where hashing sits in the served decode, graph-timed per kernel, and two GPU levers

All figures are diagnostic. They come from two runs on node 2 under preemptible fill leases, which agree within 0.3 µs a call: `r20260930-180200-7e2f` (GPU 4) and `r20260930-181438-6e9e` (GPU 2). The bench is `benchmarks/pouw/pearl_c/decode_served.py` on draft #591.

Each variant is replayed as a CUDA graph of 32 calls, on GPU 1's pipeline as `8ca97148` serves it, at Llama-3.1-8B's four linears with m = 32. Every variant was first held to its default's bytes from poisoned outputs, with no-write controls rejected. Figures are GPU ms a decode step, summed over 32 layers.

**Your decode table checks out.**
- The served call with hashing is 21.20 ms and without it 10.33, so hashing is 10.87 ms of GPU a step.
- By kernel: A's commitment is 7.09 (`hash_rows_w` 5.70, tree 0.77, seed 0.43, node keys 0.24), the tile hashing 2.92 (`hash_leaf_p` 2.21, `hash_msg_v` 0.70), and E_A's lines key 0.35. Your nsys has 7.14 + 2.93.
- Hashing is 7 launches a call: node keys, rows, tree, seed, `lines_ea`, msg and leaf.

**Two GPU levers, same committed bytes (#591, on #572):**
1. **The row and tile leaves spread over more SMs** (`run.spread`). Decode's 32 rows go one a CTA, on 32 SMs instead of 4 with two chains per SMSP. A's `-h1` commitment falls from 7.09 to 5.06 ms, and the served call from 21.20 to 19.06 ms. The tile leaves are fixed 16-block chains, so spreading them gains 0.1 ms. Prefill's grids are unchanged.
2. **`-h2`'s segment keys inside `hash_rows_b3s`.** `-h2`'s A commitment is 3.14 ms (3.31 with the separate key launch), and the call is 16.95 ms, so hashing is 6.63 ms a step. On your eager path, the fold also removes one ctypes launch a call, about 17 µs by your figure, so about 2 ms of host a step. `-h2` stays at 7 hashing launches a call.

**For your ranked fixes:**
- **Fix 7** (`-h2` A rows, keys folded) is measured: A's commitment is −3.95 ms a step on the GPU against the served `-h1`, and −1.92 against `-h1` spread.
- **The spread is a new GPU item:** −2.1 ms a step, integration-free (a launch configuration in GPU 1's `run.py`).
- Both only show once the host is gone (your fix 12, or 1 + 2 driven far enough), since decode is host-bound at 70 ms eager and 42 ms with graphs against 27 ms of GPU.
- **Correctness:** both runs' served-path checks under `pearl-c-sm120-v1-h1` and `-h2` ACCEPT the honest retained passes and REJECT the negative controls, with transcript roots equal to #572's.

Details and the per-shape table: research store `internal/pouw/rtx-pro/sm120-h2-switch.md`, section "Decode: the leaves spread over more SMs".
