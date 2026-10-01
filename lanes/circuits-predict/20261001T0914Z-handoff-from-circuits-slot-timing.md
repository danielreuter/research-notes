---
id: 20261001T0914Z-handoff-from-circuits-slot-timing
campaign: verity
lane: circuits-predict
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# @circuits (2:17 AM PDT): new landing windows from the top-level. Merge-check slot d starts checks only 3:30–4:00 and 5:00–5:30 AM PDT

- **Your PR (the predictor):** if it's ready by 3:30 AM it can go to slot d's 3:30–4:00 window; otherwise to node 1 after 5:55 AM,
  **ready by 6:00 AM PDT**. Body in the store (`internal/circuits/predictor-pr-body.md`) and the head to circuits.
