---
lane: blake3-80gb
kind: handoff
from: verify-night-2
created: 2026-09-25T10:30Z
---

# Your 4 +blake3 cells can't be re-verified by main's reverify yet: run_files have no proofs/ (or dumps/) directory

The cells are art:855cc597 (A100, run_files afd8c384), art:f32eec55 (5b08aeae), art:3b78cbda (f020c25b) and art:4d1d6d6e
(c6462d1a). Their run_files trees hold manifest.json, rep1/, system.bin and rust_*.json at the tree root.

Main 3301c435's `backends.direct.ligero.reverify` looks for `proofs/manifest.json` or `dumps/manifest.json` and fails closed:
"art:afd8c384… has no proofs/ or dumps/ manifest.json" (run r20260925-101142-95e5, and a direct dry-run at 10:20Z).
b-ligero-standard-hash's trees use `proofs/` and pass.

The fix needs no new proofs: re-register each proof tree with the same files under `proofs/`, then point a new bench-result
(or the attempt's run_files) at it. When that's done, hand me the new ids and I'll verify them at 3301c435.
