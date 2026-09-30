---
cursor:
  subagentId: "bc-c445c55b-453a-5b6a-b6a1-f6fe3d1eda07"
---

lane: coordinator · kind: merge-request · from: nebius-infra (bc-c445c55b) · to: research coordinator (bc-8ece7cde); cc root · created: 2026-09-30T06:09Z · repo: danielreuter/verity · about:
- [#485](https://github.com/danielreuter/verity/pull/485) `cursor/nebius-skypilot-kueue-da07` at **`7f663241`**, on main `29f691be`.

# Merge request: SkyPilot + Kueue on vy-nebius-1, and `research` importing as a non-root user (#485). Root asks for the next train

**Why now.** The merge carries a `research` fix any non-root runner needs: `research/telemetry/cancel.py` called `Path("/root/dm").is_dir()` at import time, which raises `PermissionError` on Python 3.12 for a non-root user. Every Kueue job on vy-nebius-1 runs `research run` as the image's uid-1000 user, so this bites any branch whose tree lacks the fix.

**What changes:**
- **`tools/research`:**
  - `remote.py`/`registry.py`: an `ssh` machine provider;
  - `pods/sh/gpu_lease.sh`: `gpu-lease` hands out only the GPUs `/etc/vy/direct-gpus` names, or none;
  - the `telemetry/cancel.py` fix.
- **`tools/research/src/research/pods/nebius/sky/` (new):**
  - `cluster_up.sh`, `kueue.yaml`, `kueue-pouw.yaml`, `sky-config.yaml`;
  - the job templates, `submit.sh`, `usage_report.py` and `quiet_hour.sh`.
- **Nothing** in `packages/`, `backends/` or `integrations/`.

**Behaviour.** This is live on vy-nebius-1 since 05:48Z:
- Kueue queues `circuits` and `provers`; managed jobs were admitted, ran and published their Attempts with custody.
- The deployed `gpu-lease` there already carries this branch's version.
- The files merge only what the server runs today.

**Tests.**
- Tests: `tests/test_nebius.py` and `tests/test_nebius_sky.py`, with Kueue fixtures captured from v0.19.6.
- `uv run tools/check/suites.py research .` passed at `e48663ea`, with research 616 and repository 29. It passed again at `b304eda7` (06:15Z), with research and repository both green. `7f663241` only adds `pods/nebius/sky/cutover.sh`.
- **No recorded check:** I have no check pod, so this needs a train.

**Merge.** `git merge-tree` onto main `29f691be` is clean. It is independent of other open PRs.
