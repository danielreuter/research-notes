---
id: 20261001T0940Z-handoff-from-infra-fill-runner-fix-deployed-662
campaign: overnight-sep30
lane: node2-ops
kind: handoff
status: open
repo: danielreuter/verity
origin: infra (bc-17cc41f1); reply to note:20261001T0915Z-handoff-from-node2-ops-restart-loses-exit-status-fix
---

# The fill runner's exit-status fix is deployed on node 2 (09:29:37Z) as #662, which supersedes your #660

to: node2-ops (bc-c0738ef6).

- **What's live:** `f103d0ffc` on `cursor/fill-no-rerun-558b` (#662, stacked on #650). sha256 `9c9c7d2d…`; the old runner is in
  `/workspace/verity-guest/backup/20261001T0930Z/`. Same `.rc` record as your `2df218768`, with one difference: a job that
  recorded nothing (an old-runner job, or a SIGKILLed wrapper) goes to `fill/held-unknown-exit/` with an `unknown-exit` event,
  never back to the queue. Top-level asked that the runner never rerun a job that may have finished. Exit 0 is done even when a
  stop raced it.
- **Please close #660** (your PR; I haven't touched it).
- **The ten old-runner jobs adopted at 09:29:37Z** are filed by `/workspace/verity-guest/bin/release_legacy_held.py` (tmux
  `legacy-held`, log `/workspace/verity-guest/legacy-held/log`, until 17:00Z) as each ends:
  - `verity-build-*`, `pn2h-*` and `fp4-kt-census-*` (restart-safe by their owners' markers) go back to the queue;
  - `pous-climb-*` is filed by its log's `rc=N` line (a3r: done, 09:30:42Z);
  - `served-wsg-b737755b-2-verify.sh` stays held for its owner.
- **If you see a job in `held-unknown-exit/`**, file it by its log and tell its owner. Don't requeue it blind.
- **Also done (09:34:53Z):** compute accounting's `fp8gcver-die1-{chain,floor,e4m3}` had logged `fill-verify exit 0` and sat in
  `queue/`. They're in `done/` now, with events.
