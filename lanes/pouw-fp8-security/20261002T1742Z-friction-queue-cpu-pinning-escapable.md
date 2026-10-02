---
id: pouw-fp8-security/20261002T1742Z-friction-queue-cpu-pinning-escapable
campaign: pouw
lane: pouw-fp8-security
kind: friction
status: open
repo: danielreuter/verity
origin: pouw-fp8-security (bc-4323a347)
---

# On node 2, a queued CPU job can leave the queue's cores, because the executor pins it with `taskset`

`research run --queue` starts a CPU-phase job on vy-nebius-2 under `taskset -c 48-95`, with `MemoryMax` set on its
systemd scope. The CPU set isn't held by the scope, so the workload can replace it.

My wrapper carried `taskset -c 96-191` (from the instruction to keep off cores 0–47). At 10:31 AM PDT it moved
`r20261002-173047-deea`'s 48 workers, and the smoke `r20261002-172745-9118`'s 12, onto cores 96–123. Node 2's user
cgroup allows 0–123, so that is all `96-191` could reach: 28 cores, outside the queue's pool. I cancelled both runs
3 minutes in and relaunched without the inner `taskset` (`r20261002-173355-4eef`, on 48–95).

The same wrapper ran my bitsets jobs on Oct 1 (`r20261001-192440-83f1`, `r20261001-205558-eee7`,
`r20261001-225552-a4a7`). They will have run on 96–123 too.

- **For lanes:** on node 2 a queued CPU job is already off cores 0–47. Add no `taskset`.
- **The fix (infra's, `tools/cluster`):** hold the pool in the scope, with `-p AllowedCPUs=48-95` beside `MemoryMax`, so
  a workload can't leave it. A guard should not fail open.
