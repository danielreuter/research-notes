---
lane: flock-gpu-link
kind: handoff
from: flock-backend
created: 2026-09-26T03:15Z
---

# flock-backend: merged your 93773ddc into the integration — our ChunkParams / pure_sha256_witness resolutions now agree (I took yours: it is ours plus the fp4 fields); NV1–NV3 next

- cursor/flock-backend-4983 @ 3d019e65 = main c79005af + my tip + your 93773ddc. `backends/flock/cuda/*`, `cuda_chunk_patch.py`,
  `flock-gpu-link-b684b12.patch` and `live/src/gpu.rs` are byte-identical to your tip. The only live/ differences are mine:
  `Req::Ping` (now **tag 9**; main's `Prime` is 8) and flock-pure's `--sessions`.
- CPU selftests on that tree (VM, 8 VUs): bf16-hopper / fp8-ada / fp8-hopper × blake3 / sha256 all pass, flock-vllm-v1 22/22.
  The GPU gate (4090, SM 89) and a replay of art:1589ffe1 run now (r20260926-031200-e58d).
- Next, after the merge request (red-team-flock-2, 0310Z): NV1 the checked outputs vs the committed y, NV2 refusing an NVFP4
  netlist with an 8-bit row layout, NV3 pinning the row schema in the statement. NV1/NV3 touch the pure_block statement
  (Σ / publics); I'll propose the change before editing your files.
