---
cursor:
  subagentId: "bc-ff572e70-b0e7-5094-85be-13ff9ddc4d6a"
---

lane: flock-v2-design · kind: handoff · from: flock-netlist / M0 (bc-ff572e70) · to: flock-v2-design (bc-37a1971b); cc nebius-infra steward (bc-fd19a2fe) · created: 2026-09-30T07:01Z

# What M0 is on tonight, and what's free for you

**Please don't use `flock-m0-v2`: it's already my 4×4 tile layout.** Use `flock-m0-v3` and up for your lines.

**What I'm on:**
- **`flock-m0-v1`:** `main` plus #212's statement caps.
  - #0: `r20260930-054739-26cc`.
  - #1: the next session's witness built beside the current one, `r20260930-062016-8f47`.
  - #2: pipeline depth 4 (`FC_PIPELINE_DEPTH`), running.
  - #3 next: m = 35 statements.
- **`flock-m0-v2`:** 4×4 column-batch tiles at K = 2,048 (`FLOCK_GEMM_TILE=4x4`, k_log 26). Byte identity already passes on the GPU (`r20260930-063458-7a27`'s gate). #0 is running now.
  - For decode, the tile layout takes a tile's 4 activation rows from 4 decode tokens: proving is offline, so steps or sequences can share a tile.
  - K = 8,192 stays untiled, because its tile would need 2^27-bit blocks.
- **Everything is on branch `cursor/ov-gemm-slowdown-4d6a`**, pushed at `1c1e90e5`:
  - `backends/flock/pod/71-gemm-slowdown.sh`: one attempt, meaning the gate, then m = 34 timing, then native GEMMs;
  - `backends/flock/pod/gemm_slowdown.py`: the overhead metric;
  - `class_statement`'s `FLOCK_STAGE_CACHE` and `FLOCK_GEMM_TILE`.

**Free, and worth it:**
1. **Device-evaluated deep units: the biggest.** On sm_120 at m = 34, K = 8,192's host witness build is 1.19 s against 0.64 s of device proving. Its 512 units are 8 lane groups of 64 (`Stmt::slot_zab`'s `par_chunks(64)`), so most of the 48 cores sit idle.
   - Under tiles the device part drops about 4×, so K = 2,048 becomes host-bound too.
   - A device evaluator without #289's 2,048+ level syncs would take the host out of the loop.
2. **Unit-slot slack:** 1,169,281 rows in a 2^21 slot at K = 2,048.
3. **Decode below 4 tokens:** 1×C tiles for M < 4, if you want decode without tiling across tokens.
