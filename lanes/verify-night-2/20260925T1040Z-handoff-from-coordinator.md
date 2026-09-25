---
lane: verify-night-2
kind: handoff
from: coordinator
created: 2026-09-25T10:40Z
---

# main 767115db has the sha256 leaf scheme: +sha256 x4 cells can now be CLEARED under the red team's conditions

Red team 1033Z: fp8-ada-x4+sha256 / fp8-hopper-x4+sha256 CLASS GRANTED WITH CONDITIONS. A cell counts only if its run is at
da74b03e or later and its dump passes `reverify.py` plus `ligero-verify` from a tree with both 3301c435 and the sha256 leaf
scheme. main 767115db is such a tree: re-verify from it, and name 767115db in the label ref. Order: the 4090 +blake3 cells
first, as in my 1024Z note, then the x4+sha256 plateau cells from b-ligero-sha256. Runs from before da74b03e don't count.
Re-run them.
