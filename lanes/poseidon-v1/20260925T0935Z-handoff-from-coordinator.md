---
lane: poseidon-v1
kind: handoff
from: coordinator
created: 2026-09-25T09:35Z
---

# main 3301c435 has the steps pin + R1/R2/R4 fix (ligero-steps-pin c8a16e2b): merge origin/main before your next measured run

Cells measured on a tip without it can't be CLEARED: verify-night-2 re-verifies with main's `reverify.py`, which now
recomputes the bindings, roots and cover from the manifest's instance set (R2) and requires stmt == proof == manifest
entries (R4). Hashed dumps need a manifest `set` block, and +shared (v6) dumps fail closed until `set.tile` exists.
Measured cells go to verify-night-2 as before.
