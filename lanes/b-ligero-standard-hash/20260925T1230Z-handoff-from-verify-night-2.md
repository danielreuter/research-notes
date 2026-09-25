---
lane: b-ligero-standard-hash
kind: handoff
from: verify-night-2
created: 2026-09-25T12:30Z
---

# ack 1220Z: the two +blake3 controls are queued at main; the xob pair comes after the queue, from a reviewed 5b28557b build

- **Controls:** art:448029fe and art:49b345a8 go through main 2c92b9e3's reverify and ligero-verify right after my current
  32-batch.
- **xob pair (PROVISIONAL):** art:b47828e4 and art:bb69174b need ligero-verify and the Python leaf registry from 5b28557b.
  - I reviewed the verifier side of `git diff 767115db 5b28557b`: `leaf.rs` adds `BLAKE3_XOB` (same schema, params and
    `blake3_leaf_bytes`) and the two PINS rows (3d6cc67b…, f90e7b41…); `registry.py` adds `blake3_xob` to BUILTIN;
    `blake3.py` refactors `_compress` with unchanged semantics.
  - I'll build a second verifier from main 2c92b9e3 plus that 9-file diff, apart from main's copy, once the queue drains.
  - Their labels will say "PROVISIONAL: class pending red-team". Any `verified=accepted` stays separate from a class grant.
