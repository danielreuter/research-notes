---
id: 20261007T1636Z-note-from-nebius-infra-n1-loops-restarted
campaign: verity
lane: infra
kind: finding
status: open
repo: danielreuter/verity
origin: nebius-infra steward (bc-fd19a2fe)
---

# Node 1 is back; I restarted its dispatcher and pacer in tmux (9:36 AM PDT)

Node 1 has been up since 16:21Z. The new deadline is `1791990000 2026-10-14T15:00:00Z daniel-2026-10-07T1601Z`. Node 2 was
still not answering ssh at 16:32Z.

The reboot dropped the research user's tmux sessions, so the dispatcher (last tick 14:54Z) and the Commit pacer (last tick
14:55Z) were down. At 16:33:07Z I restarted both as research, the way they ran before:

- tmux `node1-dispatch`: `dispatch.py loop --every 60`, with `restart_loop.sh`'s env and `KUBECONFIG`. It ticks every
  minute.
- tmux `commit-release`: `sky/release.py`, output to `~/commit-release/log`. It ticks with "waiting 2: cov-n051-2
  cov-n050-2".

**If you bring these up as the `vy-node1-dispatch` / `vy-commit-release` units instead, stop my tmux sessions first.** Two
pacers would both release onto the same queue. (`/etc/vy/env/` doesn't exist on node 1, so those units can't start as written
yet.)

I didn't start anything else. Other tmux-run services may still be down, such as circuits' controller and the alert pull.
The `vy-*` systemd timers are all active.
