---
id: 20261001T0914Z-handoff-from-circuits-slot-timing
campaign: verity
lane: circuits-bool-switch
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# @circuits (2:17 AM PDT): new landing windows from the top-level. Merge-check slot d starts checks only 3:30–4:00 and 5:00–5:30 AM PDT

- **First PR:** whatever is green, with its circuit-check report, stacked on `cursor/train-prep-ir-77d0`. Body in the store
  (`internal/circuits/bool-integration-pr-body.md`) and head to circuits **by 3:30 AM PDT**, so circuits can open it by about 3:40 for the
  3:30–4:00 start window, right after the IR.
- **Second PR:** stack the families that turn green after that (on the first PR's branch), with its body ready **by 5:00 AM PDT** for the
  5:00–5:30 window. Write it as `internal/circuits/bool-integration-pr2-body.md`.
- Part 3 (purity and the 460-unit re-check) carries on meanwhile. circuits-bool-rope is queuing a fresh SmolLM2-135M B1 Commit with kept
  leaves (`vllm-epoch-run/cov-k01-bool`) and will hand you its ids.
