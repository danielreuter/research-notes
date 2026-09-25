---
lane: blake3-80gb
kind: handoff
from: hash-commit-2
created: 2026-09-25T10:22Z
---

# GPU committer (main's, bcf75db7) verified on A100 80GB sm_80: byte-identical, committer 5.7 ms per 4,096 bf16 instances

No action needed; this is for your cell footnotes and so you can rely on the committer on the A100.
- Pod: A100 80GB PCIe (sm_80, driver 580.159, torch 2.6.0+cu124, NVRTC 12.4). Tree bcf75db7 (the committer on main since 58b113bc).
- Byte-identity suites 98/98 and neighbour suites 326 passed / 1 skipped: GPU frame-v3 word / SHA-256-row / keyed-BLAKE3-row
  trees and vllm-v1 trees == core vectors, host builders and the commit_cost references.
- bench-vu bf16-hopper+blake3 (4096 VUs, batch 8192, p2; I didn't run bf16-ampere, which needs the frozen instance set):
  commit evidence c90e6d0d… and all 49 statement files are identical to the 4090's and the H100's, GPU or host committer;
  Rust batch 49/49 accept. Committer 5.7 ms (rows 1.6, trees 4.1) vs host 27.2 s; commit.seconds 15.8 ms.
  Artifact ids are in lanes/hash-commit-2/20260925T0932Z-report-hash-commit-2.md (registered 10:2xZ).
- commit_cost --impl gpu at 4096 x 1536 B rows: frame-v3-blake3-row 0.85 ms (leaf 0.25 + tree 0.61; h2d apart),
  sha256-row 0.84, vllm-v1 0.87; 3072 B rows blake3-row 0.84 ms. Roots == references.
- I didn't set the MALLOC_* variables in these runs, because they finished before the 10:03Z handoff. The committer's timing
  doesn't depend on them, but t.total does.
