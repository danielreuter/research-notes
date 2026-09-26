---
lane: flock-backend
kind: handoff
from: coordinator (bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628)
created: 2026-09-26T03:10Z
---

# Addendum to 02:40Z: take flock-gpu-link's newer tip

flock-gpu-link is now at `0bb25e8a`, which adds the NVFP4 layouts `Fp4` / `ShaFp4` on the row-nvfp4 leaves (its 02:58Z note).
Merge that tip instead of 758a8edf, so one integration carries everything. Main is now `7289e3ad`, with PRs #47, #49, #51 and
#52 in. Merge that too. Run the gate once on the result, and include one NVFP4 CPU selftest.
