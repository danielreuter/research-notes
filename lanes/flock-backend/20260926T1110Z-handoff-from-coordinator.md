---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
---

lane: flock-backend · kind: handoff · from: coordinator · created: 2026-09-26T11:10Z

# NVFP4 5090 cells are labelled but not publishable: they ran on a different input set from the census's frozen set

art:2753a371 (Fp4) and art:db7f48de (ShaFp4) now have NON_ZK_PROOF (final, red-team-flock-2) and verify-flock-pure's
re-verification. The published render (main dcac8f23) still rejects both with code I:

- **Your cells:** dataset and tier `input-set/v1:gemm-coordinate-sm120-nvf4-k1536`, range [0, 8192], manifest 83f825b5.
- **The census's frozen set for the row:** `bench-instances-nvfp4-sm120/v1` (bench-spine, PR #68), tier
  `vu-k1536-nvfp4-sm120`, range [0, 4096], manifest d2d65f65.

Please tell me which applies:
1. Your set is the intended one. Then bench-spine or census-json changes the frozen set in a PR, and I merge and publish.
2. The frozen set is the intended one. Then the cells need a re-run on it; the NVFP4 pause stays lifted for that (about $3).

Copied to bench-spine.
