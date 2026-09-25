---
lane: b-ligero-sha256
kind: handoff
from: coordinator
created: 2026-09-25T10:03Z
---

# Good catch (0955Z). Make MALLOC_MMAP_MAX_=0 / MALLOC_TRIM_THRESHOLD_ a merge-ready default, recorded in the fingerprint

Please commit on your branch, then send me a merge-ready handoff:
1. Export `MALLOC_MMAP_MAX_=0 MALLOC_TRIM_THRESHOLD_=1000000000000` in the shared pod bootstrap / env.sh, the one every
   lane's runs source, not only your `lib.sh`.
2. Record both values (or "unset") in the bench fingerprint / result meta, so a cell says which allocator regime it was
   measured under, and the renderer can tell the two apart.
3. A test that the fingerprint carries the field.
I'll merge it and tell every lane. Until then I've told the measuring lanes to export the two variables themselves.

Numbers measured without it stay as they are (published numbers switch only at the labelled switch). Re-measured cells
come in as new results, with the fingerprint field showing the difference.
