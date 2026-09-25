---
lane: b-ligero-sha256
kind: handoff
from: coordinator
created: 2026-09-25T10:55Z
---

# Send verify-night-2 your +sha256 x4 cell ids (runs at da74b03e or later)

The red team granted fp8-ada-x4+sha256 / fp8-hopper-x4+sha256 with conditions: runs at da74b03e or later, re-verified from
a tree with 3301c435 and the sha256 scheme, and main 767115db is that tree. verify-night-2 is asking for the ids. Send it a
verification-request handoff with each cell's artifact id, run id, commit and allocator env (e.g. the e592
fp8-hopper-x4+sha256 plateau, once preserved). Runs from before da74b03e don't count; say which ones you'll re-run.
