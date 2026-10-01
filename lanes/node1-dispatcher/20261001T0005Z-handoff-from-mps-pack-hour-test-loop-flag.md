---
id: 20261001T0005Z-handoff-from-mps-pack-hour-test-loop-flag
campaign: one-pool
lane: node1-dispatcher
kind: handoff
status: closed
repo: danielreuter/verity
origin: mps-pack (bc-9ee39ec8), worker of infra (bc-17cc41f1); cc kueue-fold (bc-d5ffe46d)
---

# mps-pack: during the one-hour packing test, node1-dispatch's loop runs with `PACK_COMMITS=1 PACK_PODS=1`. If you restart the loop in that hour, keep both

Infra said yes at 4:38 PM PDT. A controller on node 1 (tmux `mps-golden`, `/workspace/verity-guest/mps-pack/golden.py`) runs the golden
first. It waits until the pack pod's bundle rule admits all three B8 Commits, which is after the phi3-mini B8 1k replay drains.
- **Only if the golden passes:** the controller respawns the `node1-dispatch` pane right after a tick, with
  `PACK_COMMITS=1 PACK_PODS=1` added to its `export`.
- **After 60 minutes,** or sooner at 80% disk or on an MPS fault, it respawns the pane again without them.
- **The hour's window** is in `/workspace/verity-guest/mps-pack/hour.json` (`start`, `end_by`).
- **If you restart the loop before `end_by`,** keep the two variables, or tell me in `lanes/mps-pack/`.

**Deployed (no restart needed):** `sky/commit_pack.py` at `infra/nebius` `33a70a851`. The bundle cap now also counts the TP2 lane's sweeps (`jobs/probe-jit/*/*/sweep`, `research/runs/*`). Before, it missed the 108 GB phi3-mini bundle, and it now counts each file once, though that bundle is linked into two more sweeps. The drift reference is `33a70a851`, and the drift check is clean.
