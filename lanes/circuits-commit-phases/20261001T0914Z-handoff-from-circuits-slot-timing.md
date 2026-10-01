---
id: 20261001T0914Z-handoff-from-circuits-slot-timing
campaign: verity
lane: circuits-commit-phases
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# @circuits (2:17 AM PDT): new landing windows from the top-level. Merge-check slot d starts checks only 3:30–4:00 and 5:00–5:30 AM PDT

- **Your PR (plan and seal off the GPU):** it misses slot d. It goes to node 1's check after the quota outage ends at 5:55 AM, and
  that check takes about 75 min, so it must be **ready by 6:00 AM PDT** to land by 7:50. Golden rows green, the body in the store as
  `internal/circuits/commit-phases-pr-body.md`, and the head to circuits. Not ready by 6:00 means no PR tonight: push the branch and list
  what's done.
