---
id: 20260930T2004Z-handoff-from-kueue-fold-blocked-on-node2-deploy
campaign: verity
lane: infra
kind: handoff
status: open
repo: danielreuter/verity
origin: kueue-fold (bc-d5ffe46d)
---

kueue-fold, step 3 is blocked on node2-ops deploying `infra/nebius` `ce30461ac`: the Verity pool, plus scope freeze so a Build is really paused in a window (`note:20260930T1953Z-handoff-from-kueue-fold-deploy-verity-pool-ce30461a`). Node 1's GPUs are sm_120 like node 2's; PoUW overflow waits on their naming untimed jobs (`note:20260930T2003Z-handoff-from-kueue-fold-node1-overflow-contract`).
