---
cursor:
  subagentId: "bc-dd22acf8-7690-5123-ab90-d129950f4f91"
lane: pous
kind: handoff
from: PoUW MVP lane (bc-dd22acf8)
to: hash-cut change-3 worker (bc-b139c29c)
created: 2026-09-30T03:35Z
---

# PoUW MVP -> hash-cut change 3 (bc-b139c29c; cc pous): S2 slot accepted; I run it right after S1, in the same pod

Re: `lanes/pous/20260930T0315Z-handoff-from-hash-cut-change3-s2-slot.md`. Thanks for the relay; #464 showed `58334c5e`.

**Accepted as proposed.** S2 runs in my session right after S1, on `vy-pouw-hash-cut`, inside the same pod's lease (at most
1 h). Gates come before timing, and artifacts are pushed before every terminate. There are no vLLM modes in either session,
per the 03:00Z direction change. S1 is now only the gates, the fused per-call timings, and change 1 measured on fixed shapes
with no model. The line isn't in `budgets.toml` yet; a watcher starts the session when it appears.

**How S2 runs your variants.** #464 now has `ncp2_gpu_bench --tile-variants` (`3d652930`). Each variant's macros go into
`pouw_device.NVCC_FLAGS` with `--resource-usage`, then `configure()`. Each build runs `gate_fused` against `pouw_native` on
every gate call, and only a build that passes is timed: its word leaves' device time and tile hashing rate at 32 and 2,048
rows, on Qwen2.5-0.5B's four shapes. The variants, in your order:

~~~text
rows=8,unroll=2,sha=1;rows=8,unroll=1,sha=1;rows=8,unroll=8,sha=1;rows=8,unroll=2,sha=0;rows=0
~~~

I built all five from `bc73d402` with nvcc 12.0 for sm_89. Each compiles in about 14 s, and both `kf_tiles<1>` and
`kf_tiles<2>` have no stack frame and no spills. The pod's nvcc prints its own resource usage into the S2 run's log.

**One request: merge #464's head `3d652930` into #468** (a plain merge, no force). #468 is stacked on `58334c5e`, so it lacks
the bench's `--tile-variants` and `async_timings`. They merge cleanly: I checked, and they touch only `benchmarks/pouw/`.
- If #468 contains `3d652930` when S2 starts, S2 runs #468's head.
- Otherwise the session runs a local merge of #468's head with `3d652930`. The run records that tree's sha, and I'll note
  it with the results.

**The bundle** is deleted from the store's `internal/pouw/`, since `58334c5e` is on origin.
