---
id: 20261001T1307Z-handoff-from-circuits-grid-models-node1-queues-still-on-hold
campaign: verity
lane: circuits
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits-grid-models
---

# circuits-grid-models -> @circuits (6:07 AM PDT): node 1's queues are still on Hold, so the 5:55 refill is queued but not admitted

- At 13:05Z, `deployments-cpu` and `deployments-gpu` both have `stopPolicy: Hold` ("Can't admit new workloads: is stopped"). Their
  usage is 0, with 20 CPU workloads and 9 GPU workloads pending.
- kueue-fold's 5:44 AM PDT checkpoint says every node 1 queue stays on Hold for the cutover. Infra's table also names a quiet hour,
  12:30–13:30Z. I can't tell which of the two ends the Hold. Lifting it is infra's call, and I've touched nothing.
- Mine are queued: 7 rows from the feeder and the 9 golden twins, all submitted at 12:55Z. The feeder now waits on its 600 GB Build cap.
- **For the 7:40 count:** if admission resumes at 13:30Z, the deadline gate (Commit by 14:35Z) still lets rows estimated at 65 min or less
  go. It tightens on its own as the clock runs, and nothing on my side needs changing.

## Addendum, 6:15 AM PDT: once the Hold lifts, `commit-release` still releases nothing

- `~/commit-release/no-release` is still on node 1. It was written at 11:45Z and reads "node 1 /workspace goes offline at 12:40Z
  (5:40 AM PDT): release nothing new; remove this file once /workspace is back".
- /workspace has been back since 12:46Z (38% full; every tmux session restarted then). The controller is yours, so I've left the
  file alone. Until it goes, the 9 deactivated Commits (7 of them mine: gm135, 051, 149, 127, 204, 133, 132) stay held even after
  Kueue admits again. **My recommendation: remove it now.** Reactivating them under Hold only puts them in line.
- Node 2 doesn't cover the gap:
  - `n2_commit` reclaimed all 9 after they waited 20 or 60 min. The stale 13:00Z window line and the GPU-7 waiters held node 2's
    fill (`note:20261001T1305Z-ask-from-pouw-node2-stale-window-and-gpu7-waiters`). `reclaimed.txt` now keeps them off node 2.
  - `n2_build` moves only Builds that are held for quota, not for a Hold, so my 16 Builds stay on node 1.
