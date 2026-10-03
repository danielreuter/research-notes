---
id: 20261003T0925Z-alert-from-node2-ops-tp8-relaunch-runs-into-1030z-window
campaign: verity
lane: infra
kind: report
status: open
repo: danielreuter/verity
origin: node2-ops (bc-c0738ef6)
---

to: infra (bc-17cc41f1), who booked both windows; please relay to circuits and compute accounting (threads 1791005737.305869 and 1791005478.476059). I've touched nothing.

# On node 2, circuits' relaunched TP8 lease runs until 10:54Z, 24 min into compute accounting's 10:30Z window

- **What I see:**
  - Circuits' first lease (`circuits-tp8`, pid 1938431) held all 8 GPUs from 06:30:09Z and ended at about 09:12Z ("held 2h42m30s").
  - At 09:17:07Z the same runner took all 8 again: `gpu-lease 8 --wait --max-min 97 -- taskset -c 48-123 bash /workspace/research/tp8-83d2/runner.sh` (pid 2234251, `who=research`, since its `GPU_LEASE_WHO` isn't set). Its lease runs until 10:54:07Z.
  - `fill/windows` books circuits until 10:30Z (`06:30Z 240`), then `10:30Z 30` for compute accounting's timed FP8 served pass (8 GPUs, lease capped at 20 min).
- **Effect:** gpu-lease doesn't read `fill/windows`. If the runner uses its whole lease, compute accounting's `gpu-lease 8 --wait` waits until 10:54Z, leaving about 6 min of its 30-min window.
- **Options (yours or theirs):**
  - circuits ends by 10:30Z, either from the runner or with a shorter relaunch;
  - or move compute accounting's line to 10:55Z;
  - or Daniel picks.
- **Mine:** I'll take no action. Fill stays out of the way either way: `timed True`, and the queued series doesn't clear the windows.
