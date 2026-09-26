---
lane: flock-gpu-link
kind: handoff
from: coordinator
created: 2026-09-26T01:40Z
---

# The NVFP4 row leaves are on main (35560c88): you can build the NVFP4 layout

Daniel adopted flock-backend's 864-byte NVFP4 row (768 code bytes, then 96 scale bytes at k = 1536) as
`sha256/row-nvfp4/v1` and `blake3-keyed/row-nvfp4/v1` in `verity.commitments` (rowleaf.py, frame_v3/PROTOCOL.md §4a,
nvfp4_row_v1_vectors.json). Build the Flock NVFP4 block layout over those row bytes. red-team-standard-hash-2 is reviewing the
leaf schemas; red-team-flock reviews your layout as usual; flock-backend makes the 5090 cell. Your earlier blocker was the
missing unit circuit; say if that still stands.
