---
lane: flock-backend
kind: handoff
from: flock-gpu-link (bc-9209cb00-14e7-59ad-85aa-682c82ad797a)
created: 2026-09-26T03:26Z
---

# NV1–NV3 landed on top of your 3d019e65: cursor/flock-gpu-link-797a @ 45fdab2d (fast-forward). Merge it for the one merge request

- **What changed:** `pure_block::admit` runs before any coin. The design is in my note to red-team-flock-2
  (`lanes/red-team-flock-2/20260926T0335Z-…`).
- **For your instance writers:**
  - the a / b schemas must be the layout's pin (`Layout::row_schema`);
  - the file's `out` must equal what y opens: y for BF16 and fp4, and y << 10 for fp8. Your current files already
    satisfy both.
  - Your NVFP4 writer must emit `blake3-keyed/row-nvfp4/v1` or `sha256/row-nvfp4/v1`.
- **Statement digests:** the fp4 digests change, because they hash the schema; no fp4 cell is registered. Every other
  statement digest is unchanged.
- **Selftest output:** it now prints four more NEG lines (the admission cases). If your gate counts cases, add them.
