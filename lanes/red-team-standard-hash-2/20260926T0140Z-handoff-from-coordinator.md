---
lane: red-team-standard-hash-2
kind: handoff
from: coordinator
created: 2026-09-26T01:40Z
---

# Review request: the new frame-v3 NVFP4 row leaf schemas sha256/row-nvfp4/v1 and blake3-keyed/row-nvfp4/v1 (main 35560c88)

Daniel adopted flock-backend's 864-byte NVFP4 row (768 code bytes, then 96 scale bytes at k = 1536) because it matches
NVFP4's code buffer + scale buffer in memory, so serving-side committers hash rows without repacking (2026-09-26 01:05Z).
- Code: `packages/verity/src/verity/commitments/rowleaf.py` (`nvfp4_row_bytes`, `sha256_row_nvfp4_prefix/layout/digest`,
  `blake3_row_nvfp4_layout/digest`, `row_leaf` accepts both schemas); spec `commitments/frame_v3/PROTOCOL.md` §4a; vectors
  `frame_v3/nvfp4_row_v1_vectors.json` (flock-backend's reference, hashlib + blake3); tests `tests/commitments/test_rowleaf_nvfp4.py`.
- Please check: the packing is injective and binds codes and scales (nibble order, scale placement); the SHA-256 prefix
  binds role, code width, k and k/16; the BLAKE3 schema's separation from blake3-keyed/row/v2 comes only from the schema
  string the tree leaf binds (same keys); any cross-schema or cross-role collision path; malformed-row refusals.
- It's a class review of the leaf schemas; no cells use them yet. B-Ligero's 5090 cell stays on Poseidon2 packing.
