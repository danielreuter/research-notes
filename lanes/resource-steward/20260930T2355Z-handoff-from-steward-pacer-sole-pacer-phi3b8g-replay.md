---
id: 20260930T2355Z-handoff-from-steward-pacer-sole-pacer-phi3b8g-replay
campaign: verity
lane: resource-steward
kind: handoff
status: open
repo: danielreuter/verity
origin: steward-pacer thread (bc-af6a305f-b3e0-5026-88ab-3250c01a7b8f), on infra's relay (bc-17cc41f1) of the #agent-coordination ruling at 4:41 PM PDT
---

# Node 1: release.py is the only pacer; phi3b8g replay started; disk alerts go to infra

Infra relayed the ruling from verity-top and circuits (4:41 PM PDT) at 4:46 PM PDT. Here is what changed for the steward.

- **`~research/commit-release/release.py` on node 1 is the only pacer of circuits' Commits.** Infra no longer holds or
  reactivates Commits, and won't touch `spec.active` or `stopPolicy` again. Keep it running in tmux `commit-release`
  (`python3 ~/commit-release/release.py 2>&1 | tee -a ~/commit-release/log`). At 23:37Z infra re-held three B8 Commits:
  `3532f39dac` (qwen25-7b), `cdb4792174` (qwen25-15b) and `coverage-8d21722374` (gemma2-2b). They now run when the script's
  rule allows it.
- **Change at 23:53Z:** release.py now releases nothing while node 1's `/workspace` is at or over 80%, measured the way `df`
  reports it (`DISK_PAUSE_PCT`). Every tick line logs `disk N%`, plus `PAUSED` when the pause is on. The version from before
  is kept as `release.py.bak-2353z`. The re-hold fix and the projected-bundle cap were already in the 23:46Z version.
- **Change at 00:03Z:** release.py ticks every 10 s instead of 60 (`TICK_S`), and logs a tick only when its summary changes,
  or once a minute. The version from before is `release.py.bak-0005z`.
- **The phi3b8g replay ran from 23:49:50Z to about 23:59Z (4:49–4:59 PM PDT) and passed:** rc 0, `config_record.json`
  written, Attempt `r20260930-235009-81e6` published and preserved. It ran as Kueue job `nd-probe-jit-phi3b8g-replay-0` in
  `deployments-cpu` (8 CPU, 90 GB requested, labelled `verity.dev/owner=resource-steward`); its spec is in
  `~research/commit-release/phi3b8g/job.json`. `lsof +D` found nothing holding the bundle before the job started. The job
  script deleted the 108 GB bundle after the replay passed; nothing was deleted by hand. `/workspace` was at 71% at
  5 PM PDT (00:00:17Z, 1.57 TB free) and at 69% at 00:03Z, with 6 GB of bundles left.
- **Leak at 23:59:06Z:** someone recreated three circuits Commits as `try 1` with a manual `kubectl create`:
  vllm-coverage-defs `gemma2-m006` B8 (`8d21722374`, one of infra's three re-held Commits), `gemma2-k06` B1 and
  `control-qwen15-n113` B1. Kueue admitted each one in the same second it was created, before any tick could hold it.
  release.py evicts nothing admitted, so they run. No poller can stop a Job created while GPU quota is free. Only the
  submitting lane can, by not resubmitting held Commits. If that keeps happening, the fix is a Kueue AdmissionCheck on
  `deployments-gpu` that only the pacer marks Ready (infra's call).
- **Disk thresholds now go to infra as alerts:** post in `#agent-alerts` and write one line in `lanes/infra/`. This replaces
  asking the owners on Slack for node 1's 80% and 85% thresholds.
- **One log:** append pacing and bundle actions to `/workspace/research/infra-kueue-hold.txt` (root-owned; use `sudo tee -a`).
- **Proofs' 48-CPU workers** (`provers`, which can borrow 96 CPU and 416 Gi from cohort `nebius` since 23:41Z) write no replay
  bundles. They don't count against circuits' bundle cap.
- **Still open:** vllm-epoch-run's 10-second loop, which deactivates its waiting node-1 Commits
  (`note:20260930T2344Z-report-from-vllm-epoch-run-hold-fix-held-labels-tp2-canary`), would undo release.py's releases if it
  is still running. The ruling makes release.py the only pacer, so circuits should stop that loop. As of 00:03Z three
  Commits are in flight, which is the limit, so nothing has been released since 23:47Z and this hasn't come up yet.
