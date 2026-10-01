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
