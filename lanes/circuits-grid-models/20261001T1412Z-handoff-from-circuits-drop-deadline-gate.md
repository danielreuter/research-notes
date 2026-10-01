---
id: 20261001T1412Z-handoff-from-circuits-drop-deadline-gate
campaign: verity
lane: circuits-grid-models
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# @circuits (7:12 AM PDT): yes, drop the deadline gate now

Daniel's rule is that 7:50 is a deadline, not a stop, and GPUs stay full. Held rows gain nothing for the count, and idle GPUs cost us. Drop
`deadlines` now, keep the estimate ordering so rows that can still count stay at the front, and keep the burst caps while Kueue and the pacer
(8 in flight until 7:50, then 6/4) bound the GPUs. At 7:40 AM PDT, write the counts for the 7:50 check: deployments ended on both nodes since the
grid began, models, families, and failures by named cause. I've re-asked infra to add the 9 models to PACK_MODELS; submit the `-pk2` twins once
they're listed.
