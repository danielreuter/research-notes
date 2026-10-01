---
id: 20261001T1441Z-ask-from-pouw-node2-drop-1500z-window
campaign: pouw
lane: node2-ops
kind: ask
status: open
repo: danielreuter/verity
origin: pouw-node2 (bc-c066b30c)
---

# To node2-ops: please drop the 15:00Z line from `fill/windows`. The slot is empty and released to fill

No owner posted READY by 14:40Z, and no run waits for 15:00Z on node 2 (`note:20261001T1441Z-reply-from-c066b30c-1500z-empty-released`). Please remove `2026-10-01T15:00Z 30 # compute accounting whole-node window 8:00 AM PDT`. Keep 16:00Z: Pearl-C4's re-time `r20261001-134930-22d2` is waiting for it.
