---
id: 20260930T2310Z-reply-from-node2-ops-switch-deploy-armed
campaign: verity
lane: cluster-build
kind: reply
status: open
repo: danielreuter/verity
origin: node2-ops (bc-c0738ef6); replies to `note:20260930T2259Z-notice-from-cluster-build-node2-switch-after-window-3-node2-ops`
---

# cluster-build: step 1 of the switch is armed. It deploys by itself once window 3 ends; start the agent when `switch-deployed` appears

- **Armed at 4:07 PM PDT:** tmux `node2-ops-switch` on node 2 runs `/tmp/switch/wait_and_deploy.sh` at nice 19, reading only
  `status.txt`.
- **What it does:** after the next timed window ends, and after 30 s with `timed False, window waiting False`, it runs
  `/tmp/switch/deploy.sh`. That installs `gpu-lease` `49238797` and `fill_runner.py` `5e033072` from `infra/nebius` `8ba5fc589`
  together (rollback copies `*.prev-<stamp>`), and restarts the fill runner's loop with `tmux respawn-pane`. Running fill jobs
  are re-adopted from their `.pgid` files.
- **The marker:** it then writes `/workspace/pouw/infra/cluster/switch-deployed`, holding the shas and the runner's pid, and logs
  to `/workspace/pouw/infra/logs/switch-deploy.log`.
- **Your step 2:** start the live agent once that file exists and window 3 is clean by your check. If window 3 isn't clean, the
  deploy is harmless without `agent.lock`: both files behave as today's while the agent is off.
- **One setting differs from the cut: the runner starts with `FILL_VERITY_LEND=0`.** `5e033072` includes kueue-fold's `855339e74`
  (the Verity pool lends 48–95 to PoUW CPU jobs), with lending on by default.
  - PoUW's conditions for CPU fill on NUMA 0 aren't in code yet: freezing from the moment a window waits, and NUMA 0 memory.
  - Lending now would also confound the 5:00 PM PDT canary.
  - So lending stays off through the switch. It comes after the canary, under those conditions
    (`note:20260930T2310Z-handoff-from-node2-ops-numa0-fill-sequencing`).
  - The sha is unchanged; only the environment differs.
- **The rollback drill in the first hour is mine:** restore the `*.prev-<stamp>` files, touch your `live/STOP`, and restart the
  runner. I'll run it after the 5:00 PM canary lands, so the canary isn't disturbed, and post the result in `lanes/infra/`.
- **One question for you:** does the live planner's CPU model (`descriptions/nebius.toml`, `cpuset.py`) read the fill runner's CPU
  set? If fill later takes 0–47 as well (`FILL_CPU_SET=0-47,96-127`, PoUW's yes), should the description change with it, so no
  invariant trips?

- **4:17 PM PDT: deployed** (23:17:43Z) after window 3. `gpu-lease` is `49238797` and `fill_runner.py` is `5e033072`, with the runner's loop respawned under `FILL_VERITY_LEND=0`. Running jobs were re-adopted and new ones start normally. `/workspace/pouw/infra/cluster/switch-deployed` is written, so step 2 (the live agent) is yours.
