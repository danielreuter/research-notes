---
cursor:
  subagentId: "bc-b139c29c-b0f6-5d6a-85d6-43e446d3b0c4"
lane: pous
kind: handoff
from: hash-cut change-3 worker (bc-b139c29c, for pous)
created: 2026-09-30T03:15Z
---

# hash-cut change 3 -> PoUW MVP lane (bc-dd22acf8; cc pous): #468 is ready for S2, and a proposal for the timing slot

**The relay is done.**
- The bundle's sha256 matched `ffa4eab5…162d1`, and `git bundle verify` passed.
- Its head is `58334c5e`, which descends from `641be6af`. I pushed it to `origin cursor/pouw-hash-cut-4f91` as a
  fast-forward, with no force. #464 now shows change 1.

**Change 3** is [#468](https://github.com/danielreuter/verity/pull/468), draft, head `bc73d402`, stacked on #464 at
`58334c5e`. It touches only `ncp2_tiles.cuh`, and the leaves, order and Z are unchanged.
- **Default:** 8 of 16 rows of each tile's running sums in registers, in 64-lane blocks with 32 KB of shared memory. That
  gives 6 warps (192 chains) per SM, against 3 today. The chain also has its own SHA-256 round, and the dp4a fold.
- **CPU twin:** every variant matches `pouw_native` on the 8 gate calls, Qwen2.5-0.5B's four linears included.
  `test_pouw_device.py`: 124 passed, 8 need a device.
- **nvcc 12.8.1, sm_89:**
  - `kf_tiles<1>` uses 255 registers, with no spills and 7,096 SASS instructions. Today's uses 128 registers and 3,704.
  - It is at the register ceiling, so the S2 build should re-read `--resource-usage`.
  - Unroll 4 spills, so skip it.

**The line:** `vy-pouw-hash-cut` is not in `budgets.toml` yet, as of `c96fcede`. RC's 02:52Z ACTION is still open, so
nothing launches.

**Proposal for S2, per the coordinator's 03:00Z direction change** (PoUW measured alone, on fixed matmul shapes, with no
served model):
1. **When:** right after S1, on the same line, inside its 1 h lease per pod. You hold the line and S1's setup, so the default
   is that you run S2 in that session. If you'd rather I run it, say so here, and I'll take it once the line is live, with
   gates before timing and artifacts before every terminate.
2. **Gate:** the fused gate against `pouw_native`, for every variant that gets timed.
3. **Timing:** the tile hashing rate on fixed shapes with `ncp2_gpu_bench`, against today's 0.42–0.49 TB/s and the plan's
   0.6–0.7. Drop S2's vLLM modes, per the direction change.
4. **Variants,** each a build flag. Set `pouw_device.NVCC_FLAGS += ("-DNCP2_TILE_REG_ROWS=8", "-DNCP2_TILE_REG_UNROLL=2",
   "-DNCP2_TILE_SHA=1")`, then call `configure()` to clear the cached builds. The flags are part of the build's key, so each
   variant gets its own library.
   - The default: rows 8, unroll 2, SHA 1.
   - Unroll 1.
   - Unroll 8 (15.7K instructions: the code-size end).
   - SHA 0 (nvcc's round).
   - Rows 0 (today's layout, as the control).

**One flag.** The bundle sits at the store's `internal/pouw/hash-cut-58334c5e.bundle`. The lane contract says git data
never goes under `internal/`; bundles go in the top-level `artifacts/`. Now that `58334c5e` is on origin it's redundant,
so please delete it. I didn't touch it.
