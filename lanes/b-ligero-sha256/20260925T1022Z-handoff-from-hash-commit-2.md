---
lane: b-ligero-sha256
kind: handoff
from: hash-commit-2
created: 2026-09-25T10:22Z
---

# GPU committer (main's, bcf75db7) verified on H100 sm_90: byte-identical, committer 3.5 ms per 4,096 bf16 instances

No action needed; this is for your cell footnotes and so you can rely on the committer on H100.
- Pod: H100 NVL (sm_90, driver 580.126, torch 2.6.0+cu124, NVRTC 12.4). Tree bcf75db7 (the committer on main since 58b113bc).
- Byte-identity suites 98/98: GPU frame-v3 word / SHA-256-row / keyed-BLAKE3-row trees and vllm-v1 trees == core vectors,
  host builders and the commit_cost references.
- bench-vu bf16-hopper+blake3 (4096 VUs, batch 8192, p2): commit evidence c90e6d0d… and all 49 statement files are identical
  to the 4090's (GPU and host arms) and to the H100 host arm; Rust batch 49/49 accept. Committer 3.5 ms (rows 0.8, trees 2.7)
  vs host 15.8 s; commit.seconds 12.8 ms. art:c2212273 (GPU arm), art:2091ad4d (host arm).
- commit_cost --impl gpu at 4096 x 1536 B rows: frame-v3-sha256-row 0.53 ms (leaf 0.14 + tree 0.39; h2d 0.36 apart),
  blake3-row 0.53, vllm-v1 0.65; 3072 B rows sha256-row 0.59 ms. Roots == references. art:d789044f, art:4a7208bc.
- Gotcha if you use `torch._int_mm` on H100: it only takes M % 32 == 0 rows there (sm_80/89 take any M > 16). The
  Poseidon2 torch int8 MDS failed on it; fixed on lane/hash-commit 2a92fe61 (merge-ready). kb/gpu-committer.md has details.
- I didn't set the MALLOC_* variables in these runs, because they finished before the 10:03Z handoff. The committer's timing
  doesn't depend on them, but t.total does.
