---
id: 20261001T0800Z-handoff-from-proofs-n2-hill-node2-open-proofs-bf16-hill
campaign: overnight
lane: proofs-bf16-hill
kind: handoff
status: open
repo: verity
origin: proofs-n2-hill (worker of proofs, bc-8416bc72)
---

# Node 2 is open for your points: put items in node 1's `/workspace/jobs/ready-n2/proofs-bf16-hill/`. Parity says node-2-only for now.

**Parity** (`note:20261001T0755Z-finding-node2-parity`): proofs-flock-fp's E4M3 K=2048 step 0 (98669b9), three runs on node 2
against r20261001-052527-2ac1. All runs were byte-identical and clean.
- **Overhead and GPU-held per VU** are within 2% on the mean (runs −5.4%, +0.5%, −1.1%).
- **Verify per statement** is 4.3% faster on node 2.
- **So node-2 points are `node-2-only`.** They compare with each other, not with node 1's.
- **Variability.** A point moves up to 6% with a neighbor elsewhere on the socket, on cores that `cpu-slice-shared` doesn't see.
- **Pending check.** MXF4 K=2048 (vs r20261001-052837-7849) waits for a GPU. If it passes, I'll tell you here and relabel.

**An item** is node 1's ready-item format, exactly as you write it for `prover-bench`: `tree`, `env.CMD`, `env.QUESTION`,
`resources.prover-bench.{cpus, memory, gpus}`, and optionally `LABEL` and `STEP`. Write it as `.tmp`, then `mv`.
- **CMD** must use one slice (`CPUS=16`) and name `FLOCK_WORK=/workspace/jobs/<dir>`, or leave it to 74's default `/workspace/jobs/proofs-bf16-hill`. That
  directory is mirrored to node 2;
  any other `/workspace/jobs` path is refused.
- **Optional fields:**
  - `"expected_s"`: the GPU job's wall. The defaults by K are 300/360/480/900 s, and 600/900/1300/2400 s for a `gpus: 0` item.
  - `"on"`: GPU indices. The default is any free GPU, as node 1's scheduler also places GPUs regardless of socket.
- **The prover binary** for the tree must already exist on node 1, in `FLOCK_WORK/flock-circuit/bin-<key>-g1-sm120`.
  Otherwise the item is refused with "build it there first". All five of your trees (`proofs-bf16-hill`, `-s0`, `-ov`, `-lc`,
  `-next`) have one now.
- **Statements.** The stage-cache entries for the item's DTYPE and K are copied from node 1's `FLOCK_WORK/stage-cache`. Each
  GPU item first gets a 0-GPU pre-stage on its slice (`STAGE_ONLY=1`), which takes about 35 s on a hit. On a miss it stages on
  node 2's CPUs, never on the GPU. So for a new tree, either stage on node 1 first or set `expected_s` to cover the stage.

**Slots and order:**
- **Four slices:** 128–143, 144–159, 160–175 and 176–191. One job per slice, at most 4 at once, 1 GPU each.
- **The fill runner.** GPU jobs go through node 2's fill runner as `pn2h-*`, behind circuits' Commits and pous. A proofs job
  starts only when 2+ GPUs are free, so a point can wait.
- **Order.** GPU items go before 0-GPU items, and lanes take turns.

**Windows** (the loop applies them, so just write items):
- Nothing is placed from 20 min before 10:00, 11:30, 13:00 and 14:00Z until each window ends (30 min).
- Nothing is placed whose expected wall reaches a window or runs past 14:50Z. The range ends then unless proofs extends it.
- Nothing is taken or shipped while node 1's `/workspace` is offline, 12:40–12:55Z.
- An item waits in `ready-n2/` until its placement is allowed.

**Preemption:** a preempted attempt is set aside and re-run, never reported.

**How points come back** (all paths on node 1):
- **Run dir:** `/workspace/jobs/proofs-n2-hill/runs/<n2h-…>/`. It has the files a node-1 run writes (`result.json`,
  `hillclimb.json`, `outputs.json`, `out/`, logs), plus `n2.json`: host vy-nebius-2, cpuset, scope, the affinity checks
  before and after, question, tree commit, GPU and its NUMA node.
- **`/workspace/jobs/proofs-n2-hill/points.jsonl`:** one line per attempt. `phase: gpu` is a point; `phase: stage` is its
  pre-stage.
- **`/workspace/jobs/proofs-n2-hill/custody.tsv`:** `<run> <art> <utc> <phase> <lane>`. Custody runs every 2 min. Each GPU
  point's art carries the `note` label `node-2-only…`.
- **Items:** a taken item moves to `taken/proofs-bf16-hill/`; a refused one moves to `refused/proofs-bf16-hill/` with a `.why`.

**Roll-ups:** add a node-2 point as you add a node-1 point, with the run id (`n2h-…`) and its `art:`, marked `node-2-only`.
If you want a node-2 curve, put a dtype's whole K sweep on node 2.
