---
id: 20260930T2340Z-handoff-from-node2-ops-g084-spurious-failure-rerun
campaign: verity
lane: kueue-fold
kind: handoff
status: open
repo: danielreuter/verity
origin: node2-ops (bc-c0738ef6)
---

# kueue-fold: `cov-g084` succeeded. Its `failed/` entry comes from my runner restart; please make `n2_build.sh` a no-op on rerun

- **The Build passed:** `verity-build-vllm-epoch-run-cov-g084.sh` ran `r20260930-224925-efaf` from 3:48 PM PDT, with rc 0,
  `SUCCESS` and validation `passed`.
- **Why it's in `failed/`:** my fill-runner restart for the switch (4:17 PM PDT) adopted it while it ran. An adopted job's exit
  code can't be read, so the runner requeues it (`adopted-exit`), on the design that a finished job's rerun is a no-op.
- **The rerun wasn't a no-op:** the item file `/workspace/verity-guest/items/vllm-epoch-run-cov-g084.json` had already been consumed,
  so `n2_build.sh` failed with `ROW: unbound variable`, rc 1, twice.
- **Please:**
  1. Move `fill/failed/verity-build-vllm-epoch-run-cov-g084.sh` to `done/` yourself, if you agree. I haven't touched it.
  2. Make `n2_build.sh` exit 0 when its item is gone and a passing run for it exists, so a rerun after adoption is a no-op.
- **Before you've fixed it:** I have one more runner restart planned, turning on the NUMA 0 fill after the 5:00 PM canary. I'll
  wait for a moment with no Verity Build running, or tell you first.

The PoUW jobs adopted in the same restart (GPU chunks and CPU verifies) handled it correctly, with `more` or a no-op rerun.

- **10:58 PM PDT, the same bug on a preemption:** `verity-build-vllm-epoch-run-cov-m004-2.sh` was preempted (rc 143) at 10:58 PM. Its reruns failed with rc 1 because `items/vllm-epoch-run-cov-m004-2.json` was gone (`n2_build.sh` line 161, `ROW` unbound). So `n2_build.sh` consumes its item at start, and **any preemption or requeue turns into a failure.** The first run, `r20261001-045505-6289`, has no result line in its log, so check whether it finished. Keep the item until the Build passes, or make the rerun pick it up again.
