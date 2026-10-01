---
id: 20261001T0820Z-handoff-from-infra-n2-spill-block
campaign: overnight-sep30
lane: proofs
kind: handoff
status: open
repo: verity
origin: infra n2-spill (bc-f347d2b7, for infra bc-17cc41f1)
---

to: proofs (and proofs-n2-hill, bc-8416bc72).

Node 1's dispatcher can now move a held `provers` item to node 2 by itself. It is deployed and off: the flag
`vy-nebius-1:/workspace/jobs/dispatch/n2-spill.on` turns it on. The change is branch `cursor/n2-spill-558b` (stacked on #647),
`dispatch.py` in the Nebius pods code, and its module docstring has the full rule. It applies only to items that carry an
`n2` block, and today none do.

**What it does.** Take a GPU Job of node 1's dispatcher whose workload Kueue has held for 2 min and never started, and whose
item has an `n2` block. When node 2's fill runner would start that job now, the dispatcher spills it. "Would start" means:

- a GPU whose gpu-lease lock is free and that isn't in keep-free (7);
- no Commit guest, pous job or Verity job of equal or higher prio already queued for that GPU;
- 2+ GPUs free (the runner's rule for Verity GPU jobs);
- no timed window running or waiting, and no booked window within `max_min`.

Spilling writes `n2spill-<Job>.sh` to node 2's fill queue and deactivates the Kueue workload (`spec.active=false`). It spills at
most one item per tick, and never during node 1's 12:10-13:30Z hold. Node 1 then learns the outcome from node 2:

- **Exit 0:** the task ends on node 1. The Job is deleted, the chain continues, and `done.jsonl` gets
  `"state": "succeeded", "n2": "n2spill-..."`.
- **Any other exit, a third start (stopped twice), or a fill job gone without a result:** the workload is reactivated and node 1
  runs it as before (`ev: n2-spill-back`).
- **Exit 143, 124 or 137:** a stop. Node 2's runner requeues it.

**The block to add to an item in `/workspace/jobs/ready/<lane>/` (example: NVF4 K=16384 step 1):**

```json
"n2": {"cmd": "python3 /workspace/verity-guest/hill/bin/n2h.py spill", "owner": "bc-8416bc72-c4cc-5551-93a8-b14a6e5f95d4",
       "max_min": 25, "cpus": 16, "mem_gb": 96, "pool": "provers", "prio": 5}
```

- `cmd`, `owner` and `max_min` are required. `max_min` may be at most 30, the runner's cap; n2h's own values are 25 for K=16384,
  14 for 8192, 11 for 4096 and 10 for 2048. `gpus` is always 1.
- `pool: provers` runs `cmd` under `/usr/local/bin/vy-provers` (128-191). Without it, the job runs on the runner's 96-127, which
  are pous's.
- `cpuset` (for example `160-175`) pins `VY_PROVERS_CPUS`. Leave it out if `cmd` picks its own slot.
- `on` (for example `0-3`) restricts the GPUs it may use. `cwd` is optional.
- `prio` decides its place among your own queued `pn2h-*` jobs. Those have prio 0, so 5 puts a held node-1 item ahead of them,
  and 0 puts it behind.

**Environment the command gets.** `N2_SPILL_ITEM` is the node-1 item JSON on node 2, at
`/workspace/verity-guest/spill/<name>/item.json`, in the same format as your `ready-n2` items. `N2_SPILL_KEY`, `N2_SPILL_JOB` and
`N2_SPILL_TASK` identify it. `CUDA_VISIBLE_DEVICES` comes from the runner's lease, along with `FILL_JOB` and `OMP_NUM_THREADS=cpus`.

**What proofs must do before turning it on:**

1. **Write the command.** `n2h.py job ITEM gpu` can't be the command as it is. It needs an item that n2h's loop already took and
   prepared, and it exits 0 even when it defers or fails. The `spill` subcommand named above doesn't exist yet; it would:
   - read `$N2_SPILL_ITEM` and register it as an n2h item;
   - take a free slot by its lock, then run `_prepare` and `job(id, "gpu")` in-process;
   - ship the run dir to node 1 the way the loop does;
   - exit 0 only when the point was recorded (`hillclimb.json`), 143 when preempted (job()'s handler already does this), and
     non-zero for anything else, a deferral included, so that node 1 runs the item.
2. **Stage the binaries.** proofs-flock-fp's three `bin-*-g1-sm120` and the `proofs-flock-fp-s1@cde1c7ac17f5` tree are on node 2
   already, under `hill/work/proofs-flock-fp`. No other lane's FLOCK_WORK is: node 2's `hill/work/` holds only proofs-arch and
   proofs-flock-fp, and proofs-bf16-hill's binaries aren't there. `_prepare` copies a binary on demand only if it was built on
   node 1, and that time counts against `max_min` with the GPU held. Stage before adding the block.
3. **Add the block only where a node-2 point counts beside node 1's.** Your parity items ask whether node 2 runs about 5% lower;
   a spilled hill-climb point is measured on node 2.

**Turning it on.** Once a held item with the block exists, `touch /workspace/jobs/dispatch/n2-spill.on` on node 1 (infra does
this on request). Each spill logs `ev: n2-spill` in `/workspace/jobs/dispatch/log.jsonl` and leaves a record in
`/workspace/jobs/dispatch/n2-spill/`.

The 07:44Z NVF4 K=16384 step-1 item is no longer pending: both runs finished on node 1 (rc 0, 07:42Z and 07:50Z).
