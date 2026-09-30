---
id: 20260930T2123Z-note-from-nebius-infra-dispatcher-templates-and-commit-watchdog
campaign: one-pool
lane: infra
kind: report
status: done
repo: danielreuter/verity
origin: nebius-infra steward (bc-fd19a2fe)
---

# Node 1's dispatcher: templates at `896d14cd` and a 15-minute hang-kill on Commits (2:20 PM PDT)

1. **Templates.** node1-fill had already copied `sky/jobs/` and `sky/submit.sh` from `896d14cd` into
   `/workspace/jobs/dispatch/infra/nebius/sky/` at 2:15 PM PDT, on your 2:12 PM order. `config-run` now has three tasks
   (build, gpu, replay) with `REPLAY_DEFERRED: auto`, so a newly dispatched Commit on a tree that has PR B defers its replay to
   the CPU task. The other files match `infra/nebius` byte for byte.
2. **Hang-kill (`infra/nebius` `ac3e0ea51`, live on the dispatcher at 2:20 PM PDT).** The Commit task now watches
   `$SWEEP_DIR/$ROW/commit.log`. When the log hasn't changed for 15 minutes (`COMMIT_STALL_S=900`, polled every 30 s), the task:
   - lowers the run's timeout with `research tele set-timeout`. The runner's harness then sends SIGTERM to the Commit's process
     group (SIGKILL after 10 s) and records the attempt as `cancelled` with the reason, and the attempt is still published.
     I checked this path against the real harness.
   - if the run is still alive 5 minutes later (`COMMIT_STALL_GRACE_S=300`), kills the workload's group (`pgid` in
     status.json) and the runner.
   - exits 86. The dispatcher doesn't requeue 86 (only 99), so the replay task isn't submitted, and the row shows
     `rc: 86` in `done.jsonl` with a `commit watchdog:` line in its `row.log`.

   The first 15 minutes after the Commit starts count as quiet time too, so a Commit that writes nothing for its first
   15 minutes is stopped. Only Commits submitted from now on have the watchdog. The 3 running and 13 pending gpu Jobs were
   rendered before it.
3. **Revert.** On node 1, in `/workspace/jobs/dispatch/infra/nebius/`:
   - hang-kill only: `cp sky.bak-20260930T2120Z/jobs/config-run.yaml sky/jobs/`
   - templates too (back to the 16:20Z two-task copy): `cp sky/jobs.bak-20260930T2115Z/* sky/jobs/ && cp sky/submit.sh.bak-20260930T2115Z sky/submit.sh`
4. **Latent dispatcher bug.** This one is node1-dispatcher's to fix; I sent it to them in
   `note:20260930T2123Z-note-from-nebius-infra-dispatch-class-three-tasks`. In `dispatch.py`, `task_resources` raises for any item
   with a `class` now that `config-run` has three tasks, and that exception aborts the whole tick. No item in flight sets a
   `class`, so nothing is stuck.
