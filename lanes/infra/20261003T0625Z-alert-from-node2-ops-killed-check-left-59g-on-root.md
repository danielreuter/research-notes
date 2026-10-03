---
id: 20261003T0625Z-alert-from-node2-ops-killed-check-left-59g-on-root
campaign: verity
lane: infra
kind: report
status: open
repo: danielreuter/verity
origin: node2-ops (bc-c0738ef6)
---

to: infra (bc-17cc41f1), for whoever owns `tools/check`. Not urgent; I've left everything in place.

# On node 2, a killed `check` left a 59 GB Lean-audit scratch on `/` (root is 63% full)

- **Alert (06:07Z):** `/` is 63% full (154 of 247 GB, 94 GB free). This is the first root alert. `/workspace` is fine (2.3 TB free), and so is the Qwen3-235B download, which writes to `/workspace/jobs/hf`.
- **Cause:**
  - `~/.cache/verity-check/` holds two `lean-audit-scratch-*` dirs, `tools/check/lean_audit.py:328`'s `mkdtemp`.
  - `yp5pj7io` (61 GB) belongs to the check running now (`r20261003-055703-86e3`, since 05:58Z, `--by` bc-8ece7cde).
  - `azkehmu9` (59 GB) is from `r20261003-030801-94eb` (same `--by`). That run was stopped by SIGTERM (rc 143) at 03:10:58Z, and the dir's newest file is from 03:10:57Z. No process has it open.
  - `_audit`'s `finally: give_back(); rmtree(work)` doesn't run when Python dies of SIGTERM, so each killed check leaves its scratch behind. It also never gives back the warm dependencies `WarmDeps.take` moved into it.
- **Why I didn't delete it:** the dir holds the warm Lake dependencies (moved, not copied). Deleting it throws them away, and someone who knows `WarmDeps` might want to move them back instead.
- **Headroom:** the live check frees its 61 GB if it ends cleanly. A second killed check would leave about 34 GB free on `/`. When root fills, everything on the node breaks, `/tmp`, the journal and logins included.
- **Suggested (the owner's):**
  - Turn SIGTERM into `SystemExit` in `check`, so the `finally` runs.
  - Sweep stale `lean-audit-scratch-*` at start: give their dependencies back, then remove the dir, when no live process holds it (a lock file in the dir works).
  - Or put the scratch and the dependencies under `/workspace` on node 2.
- **Mine:** I'll delete `azkehmu9` on your word, or move its dependencies back if you say how.
<<<<<<< HEAD

**Update 07:12Z:** both scratch dirs are gone, `azkehmu9` included (I don't know who removed it), and `/` is 15% used. There's nothing left to delete. The cause, a SIGTERM skipping `_audit`'s `finally`, is still there.
=======
>>>>>>> e716ba1b (notes sync 2026-10-03T06:30Z: 1 paths)
