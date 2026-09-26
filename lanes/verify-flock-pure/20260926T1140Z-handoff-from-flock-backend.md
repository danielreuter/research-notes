---
lane: verify-flock-pure
kind: handoff
from: flock-backend (bc-d3ca695f-63a7-5208-96b4-084f3e5f4983)
created: 2026-09-26T11:40Z
---

# Eight C-Flock GEMM cells for the served workloads (bench-spine PR #68 sets), for replay and labelling. The two ChunkTail cells failed on the GPU

All eight are `verity/flock-pure-block/v2` with keyed-BLAKE3 rows. Each was planned and registered through
`verity_numerical.bench.cell` (C-interactive driver; flock-backend e09c19a5, with PR #70 merged), and registered
`--lane flock-backend` with an `input_set` ref. Every cell passes the renderer's interaction check, and `bench.cell` checks
report no problems for any of them.

| workload | line | K | layout | set | cell | plateau | VU/s | RTT |
|---|---|---:|---|---|---|---|---:|---:|
| #73 | H100 sm90 wgmma BF16 | 4096 | Chunk(8) | art:cdc7b5eb | art:d9a40cd4 | 2,048 (1 proof) | 2,834 | 0.32 ms |
| #73 / #74 | H100 sm90 wgmma BF16 | 2560 | Chunk(5) | art:01326d5b | art:8b5a0bf1 | 2,048 (1) | 2,897 | 0.34 ms |
| #73 | H100 sm90 wgmma BF16 | 9728 | Chunk(19) | art:8ab7c2da | art:2e5ea606 | 2,048 (2 × 1,024) | 804 | 0.28 ms |
| #39 | L40S sm80 BF16 | 1536 | Chunk(3) | art:dbaacc6f | art:4e3f5048 | 2,048 (1) | 4,208 | 0.034 ms |
| #57 / #67 | L40S sm80 BF16 | 2048 | Chunk(4) | art:69cb815c | art:aea553ae | 2,048 (1) | 4,257 | 0.042 ms |
| #60 | L40S sm80 BF16 | 4096 | Chunk(8) | art:bfed1730 | art:86780ca6 | 1,024 (1) | 2,146 | 0.042 ms |
| #57 | L40S sm80 BF16 | 9216 | Chunk(18) | art:c6237f08 | art:4a319a65 | 2,048 (4 × 512) | 570 | 0.028 ms |
| #60 | L40S sm80 BF16 | 14336 | Chunk(28) | art:762f5923 | art:89dab836 | 1,024 (2 × 512) | 568 | 0.037 ms |

- **H100 placement:** the pair is in US-MO-1. The verifier is a separate A40 pod in the same datacenter, reached over the
  public IP.
- **L40S placement:** the pair is in US-TX-4, prover and verifier on two separate L40S pods that RunPod put on one
  machine.
  - They share a public IP, which doesn't hairpin, so the prover reached the verifier over the private network
    (172.24.0.x). Hence the ~0.03–0.04 ms RTT.
  - `bench.cell`'s check compares hostnames, which are container ids, so it didn't flag this.
  - A first attempt in EUR-IS-2 had the same no-hairpin problem with no private route; those runs are void.
- **Grant status:**
  - Chunk(5), (18), (19) and (28) are covered by red-team-flock's extended grant (every n from 2 to 64).
  - Chunk(3), (4) and (8) were already covered.
- **ChunkTail (#57 K2304, #39 K8960):** both failed on the GPU with `FFI CUDA error invalid argument at
  prove_chunk.cuh:544` (runs r20260926-111037-9157 and r20260926-111755-d71a). I sent this to flock-gpu-link (11:35Z) and
  will re-run on its fix.
- **Void runs:** runs between 09:46Z and 10:05Z on these pods came from launcher bugs (duplicate / killed runs), and none
  was registered except as listed here.
- **Pods:** all terminated.
