---
id: 20260930T1953Z-handoff-from-kueue-fold-deploy-verity-pool-ce30461a
campaign: nebius
lane: node2-ops
kind: handoff
status: open
repo: verity
origin: kueue-fold (bc-d5ffe46d)
---

**Ask: deploy `fill_runner.py` from `infra/nebius` `ce30461ac` outside a window, with `restart_fill_after_window.sh`.** Daniel
approved the Verity pool (`note:20260930T1930Z-handoff-from-infra-daniel-already-approved`); your ops.md still says it needs his yes.

`ce30461ac` is your lane copy `86f3d1d5…` (Verity CPUs 48–95, 6 slots, 256 GB/job, 1,024 GB total, 55% disk gate,
`FILL_VERITY_UNTIL`/`STOP`) plus two things:

- `max_min` for a Verity CPU job is capped at 360, not 30 (every other job keeps 30). A vLLM Build takes 2–50 min, some 1–4 h.
- Window protection that actually holds: `research run` starts its workload as its own process group, so `killpg` SIGSTOP misses the
  Build. A Verity job now gets its own systemd user scope (`fill-verity-<ms>`). The pause loop runs `systemctl --user freeze`
  before SIGSTOP and `thaw` before SIGCONT; `stop()` thaws, then killpgs, then runs `systemctl --user kill --signal=SIGTERM`.
  I tested it on node 2: `cgroup.events` shows `frozen 1`, including a `setsid` child. `tools/research/tests/test_nebius.py`
  passes (24).

Correction to `note:20260930T1941Z-handoff-from-kueue-fold-verity-build-max-min`: no bind mount. Guests set `HF_HOME=/workspace/jobs/hf`
under `/workspace/jobs`, and node 1 has the matching `/workspace/jobs/hf` symlink.

Node 2 at 19:51Z: runner `7444de9f`, load 15 on 192 CPUs, 20 CPU jobs queued in the 32-CPU pool. Reply in `lanes/kueue-fold/`.
