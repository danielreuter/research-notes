---
id: 20261001T0826Z-handoff-from-infra-pr-captain-649-after-647
campaign: overnight-sep30
lane: coordinator
kind: handoff
status: open
repo: verity
origin: infra (bc-17cc41f1)
---

PR captain: **#649** (`cursor/n2-spill-558b` @ `ecfc4b3b9`) is ready. It's the first step of "one queue both nodes read": node 1's
dispatcher spills a GPU Job that Kueue has held for 2 min to node 2's fill queue. It's stacked on #647 (itself on #496), so the
order is #496, #647, #649; #645 is independent after #496. The nebius tests pass (163 passed, 1 skipped). It has been live on
node 1 since 08:19Z with the flag off.
