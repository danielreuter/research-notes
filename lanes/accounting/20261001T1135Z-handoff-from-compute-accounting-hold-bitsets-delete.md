---
id: 20261001T1135Z-handoff-from-compute-accounting-hold-bitsets-delete
campaign: verity
lane: accounting
kind: handoff
status: open
repo: danielreuter/verity
origin: compute-accounting (bc-e90634dd)
---

# For bc-4323a347: HOLD the v2-hot bitsets delete. My 4:35 AM yes is withdrawn

From compute accounting, 4:36 AM PDT. The top-level: `pouw/gpu3-fp8/out` was explicitly held, and deletes there need Daniel's
yes. Node 2 is at 48% against a 52% hold, so there's no emergency.
- **Don't delete anything under `/workspace/pouw/gpu3-fp8/out/`.** I checked at 4:34 AM PDT: nothing had been deleted
  (`v2hot` 513G, `v2hot-cancel` 33G, `fix2` 193G).
- **I write-protected `v2hot`, `v2hot-cancel` and `fix2`** (`chmod a-w` on their 98 directories) as a guard. Leave that as it is.
- **The delete runs only if node 2's disk reaches 50% before Daniel wakes, about 9:20 AM PDT,** and only for paths whose results
  have a verified `art:` id in the store. If it reaches 50%, tell me first and I'll restore write.
- It goes on Daniel's morning list as a decision.
