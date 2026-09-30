---
id: 20260930T1713Z-handoff-from-pous-one-cluster-to-nebius-infra-steward-gpu-lease-usage
campaign: overnight-sep30
lane: nebius-infra
kind: handoff
status: open
repo: danielreuter/verity
origin: pous one-cluster design (bc-c3ade0aa), for the nebius-infra steward (bc-fd19a2fe), owner of `gpu_lease.sh`; cc pous infra (bc-efe47341)
---

# Please ship: `gpu-lease` reports each lease's held and busy GPU time at release (report-only)

Daniel wants per-lease GPU utilization in the observability layer. At release, report held time against busy time per GPU
to whoever held the lease, and record it with the lease or run in the evidence store, so panels and the scheduler can see
patterns. **It is report-only: never kill or refuse a lease on it,** because interactive and debugging leases are
legitimately bursty. The kernel skill (#577, "No CPU work inside a GPU lease": "none planned; a candidate for `gpu-lease`")
proposed it, and it's the only planned check for CPU preparation inside GPU leases. Node 2 ran at 38% busy over the last
hour; at 17:11Z its sampler showed GPU 0 leased by bc-18346d9c at 0% SM activity.

A minimal version doesn't constrain the one-cluster design: the design's ledger takes the same fields
(`cluster.ledger.gpu_usage` on branch `cursor/cluster-foundation-7e9f`), so it can ship on `infra/nebius` now. You own
`gpu_lease.sh`; pous infra deploys it on node 2. Either of you may ship it under the sharing rule, with a one-line note here.

## What it does

1. **When CMD exits** (any status, 124 and 143 included), for each leased GPU it computes over `[since, end)`:
   - `held_s`: the lease's length;
   - `busy_s` and `sampled_s`: from the node's sampler log, each reading covering one cadence. On node 2 that's
     `/workspace/pouw/infra/util/*.jsonl` (10 s, per GPU `uuid`, `util`, `smact`). Busy means `util > 0` or `smact >= 0.01`,
     the compute plan's definition.
2. **It never queries NVML or `nvidia-smi` for this,** so a timed window stays quiet. The sampler skips windows, so a
   `--timed` lease shows `sampled_s` near 0, never as idle.
3. **It prints one line to the holder** on stderr, for example
   `gpu-lease: GPU 3 (GPU-9f1f172d) held 14m02s, busy 3m10s of 12m00s sampled (26%)`. It adds
   `; prepare on the CPU outside the lease` when the busy share is under 50% of at least 5 sampled minutes.
4. **It appends one JSON record,** `gpu-lease/usage/v1`, to two places:
   - `$RESEARCH_RUN_DIR/gpu-lease-usage.jsonl` when that's set, so custody publishes it with the run's Attempt;
   - `${GPU_LEASE_USAGE_LOG:-/workspace/research/lease-usage.jsonl}` on the node, for leases outside a recorded run (fill
     jobs, SSH sessions). The hourly backup (node 2) or `util_collect.py` (node 1) takes it to the store.
5. **Nothing changes for the lease:** its exit status is unchanged, and nothing is refused, delayed or killed. A missing or
   unreadable sampler log gives one warning line and a record with `sampled_s: 0`.

~~~json
{"schema": "gpu-lease/usage/v1", "host": "vy-nebius-2", "pid": 1924800, "scope": "gpu-lease-1924800",
 "who": "bc-18346d9c", "run": "r20260930-170417-10dd", "timed": false, "preemptible": false,
 "since": "2026-09-30T17:04:46Z", "end": "2026-09-30T17:18:46Z", "rc": 0, "cmd": "bash -c ...",
 "gpus": [{"index": 0, "uuid": "GPU-5f1149a4-e5f5-1007-ec78-7cd350a69a4f", "held_s": 840, "busy_s": 120, "sampled_s": 840}]}
~~~

**The source is configurable:** `GPU_LEASE_UTIL_LOG` (a glob) names the sampler log. On node 1, point it at whatever
per-GPU series you already keep; without one, a lease records `held_s` alone.

**Tests** go beside the existing `gpu-lease` tests in `tools/research/tests/`, with a fake sampler log and
`GPU_LEASE_UUID_TABLE`, and no host path (the 07:46Z lesson).

Please reply here with the commit and the deployed sha256, or say if you'd rather I write it. The design keeps the rule
that utilization is reported, never enforced. Its structural fixes for chronic idle time are preemptible fill wherever GPUs
are free, and CPU preparation in a GPU-less step before the GPU step.
