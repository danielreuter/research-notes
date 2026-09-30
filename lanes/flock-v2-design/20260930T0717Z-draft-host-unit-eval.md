---
id: 20260930T0717Z-draft-host-unit-eval
campaign: overnight-sep30
lane: flock-v2-design
kind: draft
status: open
repo: danielreuter/verity
origin: cursor/host-unit-eval-c9e2
cursor:
  subagentId: "bc-37a1971b-0899-57f3-995e-5b82e8b3c9e2"
---

# flock-m0-v3: the deep unit's host witness in one pass, written straight into the mapped host slots

For M0 (bc-ff572e70, lane `flock-netlist`), as a backlog item. Branch `cursor/host-unit-eval-c9e2`, merged with your
`1c1e90e5`. The lever touches `ir_block.rs`, `circuit.rs`, `gpu_circuit.rs`, `lookup.rs` and three call-site lines of
`bin/flock-circuit.rs`; `72-host-unit-eval.sh` is its measurement script. Line name `flock-m0-v3`, as your 07:01Z handoff asked.

**What changes.** A deep unit's slots are evaluated on the host, 64 units (a lane group) per thread.

1. `482c83d3` `IrUnitNet::eval64_flat`: one pass over flat u32 forms of the rows (built once per circuit, 0.1–0.6 s) instead
   of `eval64`'s three passes over `Vec<Vec<usize>>`. Every column a row reads is an earlier one or the constant's; an
   assertion row's own column is a parity bit. A net that reads a later column keeps `eval64`.
2. `c5ec5953` `HostSlots::pack_units`: a and b go straight from the bit-sliced rows into the mapped buffer, 8 transposed
   blocks (one cache line per lane) at a time. Before, `lanes()` allocated 3 × 64 fresh vectors per group (768 MB per
   K=2048 build) and `pack` copied them again. z = a & b is checked on the bit-sliced rows.
3. `b822c538` `FC_HOST_PREPIN=1` (off by default: it changes how your metric's timed builds start). It builds the first
   session's witness before the pipeline's others and pins `depth` more buffers of its size. Today, with WARM=1 RUNS=3
   and depth 4, all four witnesses are built in one cold burst. Each pays a serialized `cudaHostAlloc` of 0.5–1 GB (about
   0.25 s per 512 MB, chained 4 deep) and waits for the flat forms, which a prover past its first sessions never pays.

`FC_UNIT_FLAT=0` / `FC_UNIT_FUSED=0` restore the old paths. `72-host-unit-eval.sh BASE=1` times them in the same job.

**Byte identity.** Nothing changes in the statement, pins, circuits, relation or protocol, so there is nothing for circuit-check.

- The gate's `gpu_paths_agree` compares the host path (now eval64_flat and the fused write) with the device-evaluated units
  (your code, untouched): proofs and transcripts are equal, and `gpu_proofs_match_cpu` passes.
- The gate's statement digests equal yours: `86b48502…` and `72ba2879…` untiled, and `4998fffc…` for the 4×4 tile.
- `FC_UNIT_CHECK=1` asserts `eval64 == eval64_flat` on every group and that the fused host slots equal `host_slots`' packed.
- Unit tests cover random nets and every lookup net, the fused layout (with stale buffers), and a failed assertion falling
  back.

**Measured** (Kueue `prover-bench`, 18 vCPU, `ov.noisy=true`; your attempts ran at 48 vCPU):

| attempt | config | prefill | decode | K=2048 build / prove (s) | K=8192 build / prove (s) |
|---|---|---|---|---|---|
| your v1 #2 `r20260930-070055-209f` | depth 4, untiled | 2.17e7 | 4.90e5 | 1.01 / 0.52 | 5.16 / 0.61 |
| v3 #1 `r20260930-072120-266c` | + one pass | **1.95e7** | **4.53e5** | 1.16 / 0.54 | 3.13 / 0.58 |
| v3 #2 `r20260930-075003-e1f6` | depth 4, 4×4 tile, + one pass | 2.36e7 | 5.49e5 | 5.43 / 0.36 | 3.21 / 0.64 |
| v3 #3 `r20260930-075001-a713` | + fused write | **1.38e7** | **3.08e5** | 2.61 / 0.37 | 3.40 / 0.58 |
| v3 #4 `r20260930-080425-c735` | + `FC_HOST_PREPIN=1` | **8.23e6** | **1.81e5** | 0.33 / 0.36 | 1.05 / 0.58 |
| #4's same-job BASE | old eval, unfused, prepin on | 1.00e7 | 2.20e5 | 1.74 / 0.37 | 2.84 / 0.59 |
| v3 #5 `r20260930-083954-c727` | #4 + `FC_DEV_PREFETCH=1` | 9.07e6 | 2.01e5 | 0.54 / 0.41 | 0.90 / 0.61 |
| #5's same-job BASE | #4's config | 8.75e6 | 1.92e5 | 0.32 / 0.38 | 1.06 / 0.64 |
| v3 #6 `r20260930-090428-7cdb` | #5 at depth 2, RUNS=8 (steady state) | 8.79e6 | 1.94e5 | 0.17 / 0.39 | 0.55 / 0.61 |
| #6's same-job BASE | #4's config at depth 2, RUNS=8 | 8.74e6 | 1.93e5 | 0.15 / 0.39 | 0.43 / 0.59 |

- "build" is `witness_prebuilt_s`; the metric reads it divided by 4.
- Device-bound would be prefill 8.36e6 / decode 1.84e5 (#3's prove-only). Every row above is host-bound only through the
  cold burst: #1's unpipelined sweep builds K=8192 in 0.56 s (your nopipe `2cb6`: 2.69 s) and K=2048 in 0.19 s.
- Profile (UNITPROF, steady state, K=8192): eval 0.2 s and `lanes()` 0.23 s per group; `pack` 0.03 s with the pool
  warm, 0.7–2 s cold.

**#4 is at the device bound** (its overhead equals its prove-only), as predicted (8.4e6 / 1.9e5). The host witness is off the
critical path; what is left is the prove, 2 sessions per statement (the second reuses the first's commitment).

**#5: prefetch the host slots to the device (`0375d7cf`, `FC_DEV_PREFETCH=1`, off by default).** Plan §4's upload floor is the
first session's `t.witness_comp`: the device reading 1.14 GB of mapped host slots over PCIe beside the compressions, plus the
compression rows' pageable copy (11–45 MB). It was 0.054–0.069 s at K=8192 and 0.032 s at K=2048 tile. The pipeline's builds
have slack, so the build thread copies both to pooled device buffers (`DevBuf`, at most `FC_DEV_PREFETCH_GB`, default 16). The
kernel reads the device pointers, which `prove_circuit.cuh` recognizes with `cudaPointerGetAttributes`. Same words and kernels.

- **Byte identity:** the gate passes, with `gpu_paths_agree` on `device-ab` against the pageable path, and the digests are
  yours. `FC_UNIT_CHECK=1` reads the copies back and compares them.
- **Measured, same job:** `t.witness` falls 0.051 → 0.028 s at K=2048 and 0.093 → 0.065 s at K=8192, in every run.
- **Not visible in the metric:** the Ligerito and zerocheck phases vary by ±0.03–0.05 s from run to run, on both paths and in
  the reused second session too, so #5's median-of-3 came out above its control.
- **#6, the steady state:** depth 2 and RUNS=8, so most timed proves run beside the next build and its copies.
  - The saving holds (K=2048 0.051 → 0.028 s), but Ligerito and the reused session slow down beside the 1.2 GB copies, most
    likely because the prove's `cudaFree` calls synchronize the device.
  - Net: proves of 0.387 vs 0.391 s at K=2048 and 0.613 vs 0.593 s at K=8192. **Neutral, so it stays off.**
  - Hiding the floor would need the copies to leave the prove's device syncs alone, e.g. with `cudaMallocAsync` pools in the
    prove, which is your allocator.
- **#4's config holds the device bound in steady state too** (#6's BASE): K=8192 builds in 0.43 s beside a 0.59 s prove. At
  depth 1 it would also fit.

**Backlog, design only: unit-slot slack (a statement change).** This needs a named statement reviewer and circuit-check, and may
need Daniel if the layout rules in `verity/ir/PROTOCOL.md` change. Nothing here is prototyped.

- **The slack now.** At K=2048 with a 4×4 tile, the block is 2^26 rows.
  - The 16 unit slots are 2^21 rows each, half the block. Each unit uses 1,169,281 rows (56%), so 22% of the block is zero
    rows inside unit slots.
  - The ranges end at 58.5M rows (hm96 8 × 2^18 at slot 128, the mask in the 2^18 gap at 136, sha512x3 86 × 2^18 from 137),
    so another 13% lies past the last range.
  - At K=8192 (untiled, k_log 25), the one unit slot is 2^23 rows. If a unit's rows grow with K (about 4.7M), it is 56%
    used. The 86 sha512x3 slots are 67% of the block.
  - The prover's work is dense over 2^m, so a zero row costs what a used row costs.
- **Why the tile stops at 4×4.** A unit takes a power-of-two slot, so 16 × 2^21 fills half the block, and a 5×4 tile's slots
  plus its hashing exceed 2^26. `_tile_fits` (ands · P · C ≤ 2^25) is necessary, not sufficient. At K=8192, a 2×2 tile
  needs 2^27, which gives no gain per coordinate; that's why K=8192 stays untiled.
- **The lever.** Lay out unit slots at their row count rounded up to 2^14 (1,179,648 rows at K=2048, 0.9% waste), with
  slot i at pos0 + i · stride.
  - The fold's row-to-slot map (`fc_comb_expand`, `FcRanges`) divides by the stride in place of a shift, and the verifier's
    layout does the same.
  - Assume the hashing grows with a tile's P + C, as 86 sha512x3 slots for 4 + 4 suggest. Then a 6×4 tile at K=2048 fits
    2^26: 24 units at 28.3M, about 108 sha512x3 slots at 28.3M and 12 hm96 at 3.1M. That is 24 coordinates per block
    instead of 16, so K=2048's cost per coordinate goes ×0.67.
  - A 2×2 tile at K=8192 fits 2^26 as well: 4 units at about 18.7M and about 172 sha512x3 slots at 45.1M. That is 4
    coordinates per 2^26 instead of 1 per 2^25, so K=8192's cost per coordinate goes ×0.5.
- **Predicted**, from #4's costs per coordinate (K=2048 1.76e-4 s, K=8192 1.13e-3 s) and Llama-3.2-1B's mix per layer:
  - The mix is 21,504 coordinates at K=2048 per token and 2,048 at K=8192, so K=2048 carries 62% of the prove and K=8192 38%.
  - The 6×4 tile alone gives prefill about 6.5e6 and decode about 1.4e5.
  - With the 2×2 tile at K=8192 as well, prefill is about 4.9e6 and decode about 1.1e5.
  - This is an upper bound: it assumes the prove is linear in block rows at fixed m, and that decode's coordinates fill
    their tiles (decode below 4 tokens doesn't fill a 4-row tile).

**For you to decide.**

1. Whether the metric should keep timing the cold burst. The alternatives are `FC_HOST_PREPIN=1`, or WARM ≥ depth + 1.
   Prepin alone, on the old eval and unfused write (#4's BASE), takes prefill to 1.00e7 at 18 vCPU. (Decided, 09:10Z: don't
   time the burst; v1 takes prepin.)
2. Merging the branch. It merges cleanly onto your `1c1e90e5`.
