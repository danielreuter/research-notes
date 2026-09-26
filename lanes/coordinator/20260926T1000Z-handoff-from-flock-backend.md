---
lane: coordinator
kind: handoff
from: flock-backend (bc-d3ca695f-63a7-5208-96b4-084f3e5f4983)
created: 2026-09-26T10:00Z
---

# C-Flock GEMM cells for the served workloads are staged on CPU: 5 ready, 5 more ready once a red-team grant covers their Chunk(n), 2 need a new layout

**Code:** cursor/flock-backend-4983 @ 75207d9d.
- `gemm_coordinate.py` lowers any K whose rows are whole BLAKE3 chunks, at least two, with a per-proof CN2 limit. It now
  covers NVFP4, SHA-256 rows at K = 1536, and sm80 / sm90-wgmma BF16. `granted()` reports a Chunk(n) that falls outside
  red-team-flock's n ∈ {2, 4, 8, 16}.
- The C-interactive driver now sends the input set with both runs (`SET=` plus `research run --send`) and passes `LEAF`.
- Tests: bench + flock, 427 passed.

**Staging:**
- **Input sets:** bench-spine's PR #68 sets, all synthetic, 2,048 VUs each.
  - `write_set` over all 2,048 VUs of every whole-chunk set re-chains each VU under the relation's model, and every one
    equals the set's y.
  - A CPU selftest at 8 VUs passes all 26 cases for each layout.
- **Plans:** `lanes/flock-backend/evidence/gemm-workloads/plans/*.json` (placeholder addresses).
- **Launch script:** `evidence/gemm-workloads/launch.sh l40s|h100 [grant]`, one script taking the GPU type as argument.
  - It creates a prover plus a same-DC verifier (at most one pod per name, `pod1.sh`).
  - Per cell, it re-plans with the real addresses, then runs `bench.cell launch`, waits, and runs `bench.cell register`.

| workload | GPU / semantics | K | row | layout | per proof (CN2) | status |
|---|---|---:|---|---|---|---|
| #39 | L40S sm80 BF16 | 1536 | 3 chunks | Chunk(3) | 2,048 (≤ 10,922) | **ready** |
| #39 | L40S sm80 BF16 | 8960 | 17.5 chunks | — | — | **needs layout** |
| #57 | L40S sm80 BF16 | 2048 | 4 | Chunk(4) | 2,048 (≤ 8,192) | **ready** |
| #57 | L40S sm80 BF16 | 2304 | 4.5 | — | — | **needs layout** |
| #57 | L40S sm80 BF16 | 9216 | 18 | Chunk(18) | 512 (≤ 1,820) | **needs grant** |
| #60 | L40S sm80 BF16 | 4096 | 8 | Chunk(8) | 1,024 (≤ 4,096) | **ready** |
| #60 | L40S sm80 BF16 | 14336 | 28 | Chunk(28) | 512 (≤ 1,170) | **needs grant** |
| #67 | L40S sm80 BF16 | 2048 | 4 | Chunk(4) | same set and cell as #57 K2048 | **ready** (shared) |
| #73 | H100 sm90 wgmma BF16 | 2560 | 5 | Chunk(5) | 2,048 (≤ 6,553) | **needs grant** |
| #73 | H100 sm90 wgmma BF16 | 4096 | 8 | Chunk(8) | 2,048 (≤ 4,096) | **ready** |
| #73 | H100 sm90 wgmma BF16 | 9728 | 19 | Chunk(19) | 1,024 (≤ 1,724) | **needs grant** |
| #74 | H100 sm90 wgmma BF16 | 2560 | 5 | Chunk(5) | same set and cell as #73 K2560 | **needs grant** (shared) |

- **needs grant:**
  - The code already takes these. `Layout::of` accepts up to 64 chunks, and CPU selftests pass at Chunk(5), (18), (19)
    and (28).
  - They are outside red-team-flock's Chunk(n) grant (n ∈ {2, 4, 8, 16}), and the GPU prover hasn't run them.
  - They need either a grant extension to all n with 2 ≤ n ≤ 64 (the layout code is n-generic), or a red-team pass on
    n = 5, 18, 19 and 28.
  - Budget GPU memory below m 35 on the L40S: hence 512 VUs per proof at n = 18 and 28.
- **needs layout, for K = 8960 (17,920-byte rows) and K = 2304 (4,608-byte rows):** a `Chunk(n, tail)` layout. The rows
  are n whole chunks plus a final partial chunk of 512 bytes, which is 8 BLAKE3 blocks and 16 units instead of 16 blocks
  and 32 units. What it needs:
  - a last block per VU with 8 compression slots and 16 unit slots, the rest dummy;
  - CHUNK_START / CHUNK_END flags and the counter on the partial chunk exactly as BLAKE3 sets them, with block_len 64
    for its last block, since 512 is a multiple of 64;
  - the chunk-CV tree unchanged;
  - a layout tag in the statement digest;
  - a new admission case in NV3 / CN3;
  - a red-team pass.
  - Alternatively, zero-padding to whole chunks is not an option: the row leaf hashes the exact bytes.
- **Cost estimate for the ready cells:**
  - L40S pair (L40S prover plus a cheap same-DC verifier, about $2/h): build, then 3 cells at about 4 minutes each, so
    about 25 minutes and **about $0.8**.
  - H100 pair (about $4.5/h): 1 cell, about 15 minutes, **about $1.1**.
  - **Total about $2.** The four needs-grant cells add about $1 on the same pods (`launch.sh … grant`).
- **NVFP4:** both cells are done (0945Z handoff).
