---
id: 20261001T0612Z-draft-from-kueue-fold-cutover-script-fixes
campaign: one-pool
lane: infra
kind: draft
status: open
repo: danielreuter/verity
origin: kueue-fold (bc-d5ffe46d)
---
# Cutover plan: three job-script fixes from `infra/nebius` onto node 1's dispatcher and both nodes' `n2_build.sh` (11:15 PM PDT)

**What changes.** Only job scripts. No Kueue object, no node setting, and nothing on node 2's freeze list changes.
1. **`config-run.yaml`, replay task** (`dfe17f6aa`): when the Commit's `commit/verdict.json` has no `replay_deferred`, the task exits
   0. A Commit with no `replay_deferred` replayed on its GPU; a deferred Commit always records the key
   (`note:20260930T2310Z-finding-from-n2-commits-rc12-replays-mixed-template-chains`). A deferred verdict with no bundle still fails
   with rc 12.
2. **`n2_build.sh`** (`c332e1685`, `3dd19c6a1`):
   - a finished Build's rerun is a no-op, because `run` writes `items/KEY.done` (node2-ops 2340Z);
   - an MoE checkpoint's Build gets the 256 GiB cap (cov-g080-r1 was OOM-killed 8 times at 66 GB, node2-ops 03:40Z).

**Where:**
- (1) goes to `/workspace/jobs/dispatch/infra/nebius/sky/jobs/config-run.yaml` on node 1, with a `.bak-<UTC>` beside it. New
  replay Jobs read it; running ones keep their script.
- (2) goes to `/workspace/verity-guest/bin/n2_build.sh` on both nodes, with backups. Jobs that start after the copy run it.

**When:** at once, outside a node-2 window: `n2_build.sh` is copied only while `status.txt` says `timed False, window waiting False`.

**Check:**
- (1): `bash -n` on the extracted task, plus a check with three verdicts (no key exits 0; key with 0 bundles and a broken file
  still replay).
- (2): a rerun with `.done` exits 0, and one with no item and no record exits 2.
- `test_nebius*` pass (67).

**Rollback, in one step:** copy the `.bak-<UTC>` files back.

**Exposure:** one pending Commit on the old template, `vllm-staging-bug/fix-g211`. Its replay now exits 0 instead of a spurious
rc 12.

## Addendum, 11:32 PM PDT: restart node 1's lease controller on `a98736cbd`

- **What changes:**
  - holders never borrow: the pool is capped at `provers`' nominal GPU quota less its other admitted Workloads. `provers` has borrowed
    1 since `90599edad`, and Kueue can reclaim a borrowed holder mid-lease. With the quota unread, the pool doesn't grow;
  - an expired or outside-pool lease held by a host process gets SIGTERM to its owner pid.
- **The dry run on node 1:** it read the ClusterQueue and 306 Workloads. `provers` can give 2 GPUs unborrowed. Pool 0, 8 fenced,
  no events.
- **How:** the tmux `n1-lease` loop restarts with the new file (backup `n1_lease.py.bak-<UTC>`). Fences outlive the controller, so
  every GPU stays fenced through the restart.
- **Rollback:** restore the backup and restart the loop.
- **Then:** one host-process smoke test, `gpu-lease 1 --wait --max-min 5 -- nvidia-smi -L` as research on node 1, the wrapper
  `cluster submit` gives a node-1 GPU job on `cursor/n1-gpu-executor-9bf0`. It is about 2 min of one `provers` GPU at priority `dev`.
