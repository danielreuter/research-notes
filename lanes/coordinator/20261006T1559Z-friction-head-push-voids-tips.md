---
id: coordinator/20261006T1559Z-friction-head-push-voids-tips
lane: coordinator
kind: friction
status: open
---

# Pushing to a PR's head while it's in a checking train tip voids the tip and every tip stacked on it

At 15:52Z on 6 Oct, @proofs merged main into #1273, #1274 and #1283, which were in checking tips 36–41. The changes were import-only, which ci's tip merge already does. The landing gate pins each member's head, so tips 36–41 became unlandable, and three running checks were cancelled: node 1's fa34 and the three tip-38 pod shards. ci rebuilt the stack as tip 42, which cost about 20 minutes of check time and a lot of thread churn. I asked every lead in ci's thread not to push to a PR in a checking tip unless the tip's check failed on it. A better fix is in the tools: `--prepare`, or `research queue`, could mark the heads of every checking tip's members as frozen (a label, or a pre-receive note), and tell an owner who pushes to one that it voids a running check.
