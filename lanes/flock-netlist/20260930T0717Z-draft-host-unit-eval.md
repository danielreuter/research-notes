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
- **Next:** #6 (steady state: depth 2, RUNS=8, so most timed proves have a build and its copies beside them), then the quiet
  hour's A/B.

**For you to decide.**

1. Whether the metric should keep timing the cold burst. The alternatives are `FC_HOST_PREPIN=1`, or WARM ≥ depth + 1.
   Prepin alone, on the old eval and unfused write (#4's BASE), takes prefill to 1.00e7 at 18 vCPU.
2. Merging the branch. It merges cleanly onto your `1c1e90e5`.
