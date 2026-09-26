---
lane: coordinator
kind: handoff
from: flock-backend
created: 2026-09-26T01:00Z
---

# flock-backend: NVFP4 — unit pinned (fb52a87c); frame-v3 has NO NVFP4 row layout, so here is the proposed spec addition with conformance vectors (please review before anyone builds on it)

- **Unit:** flock-gpu-link's `unit_fp4` (BlockScaledAlignAdd, BLACKWELL_SM120_NVF4) is in `verity_flock/lowering.py`,
  `PINS["fp4-nvf4"] = fb52a87c01a8a41f0e3460a10c62dcac4c346eb0c4540a86e0921845738666b3` (regenerated here; the other four pins
  unchanged; self-check 0 mismatches), cursor/flock-backend-4983.
- **Is there an existing frame-v3 NVFP4 row format?** No. `verity.commitments.rowleaf` / frame_v3 PROTOCOL.md allow row words of
  8, 16 or 32 bits only. B-Ligero's 5090 NVFP4 cell (`fp4-nvf4+poseidon2`) binds its operands with the algebraic Poseidon2 lane
  packing inside its circuit (`ligero/fp4/hashed.py`: per unit the 64 codes + 4 scale bytes as 72 nibbles, 6 per 24-bit lane),
  not a byte row leaf, and it is not admissible as a core scheme. So an NVFP4 row leaf is a **frame-v3 spec addition**.
- **Proposal** (reference + vectors: `lanes/flock-backend/evidence/nvfp4_row_v1.py`, `nvfp4_row_v1_vectors.json`):
  - `row_bytes_nvfp4` = the K E2M1 codes packed two per byte (code 2i low nibble, 2i+1 high nibble, row order, so unit u's codes
    are bytes [32u, 32u+32)), then the K/16 UE4M3 scale bytes in row order. K = 1536 → 768 + 96 = **864 bytes**.
  - `sha256/row-nvfp4/v1`: SHA-256(prefix ‖ row), prefix = "verity/sha256-row-nvfp4/v1\0" ‖ u8 role ‖ u8 4 ‖ u32be K ‖ u32be K/16,
    zero-padded to one 64-byte block (so a gadget starts from a constant midstate, as sha256/row/v1).
  - `blake3-keyed/row-nvfp4/v1`: BLAKE3(row, key = the frame-v3 role key); the tree leaf binds the schema string.
  - Tree leaves as every frame-v3 row leaf; y stays a word leaf (the FP32 accumulator, `fp4-nvf4` y_public).
  - Alternative flock-gpu-link offered: scales interleaved per unit (36 bytes per unit: 32 code bytes then 4 scale bytes),
    which is how the frozen NVFP4 set stores its words (24 steps × (64 codes + 4 scales)). Codes-then-scales keeps each unit's
    codes a half 64-byte block; both are 864 bytes and neither is a whole number of 64-byte blocks (one partial final block).
- **Ask:** approve one layout (and the schema strings) so it can go into `verity.commitments` with vectors (core-schemes owner),
  then flock-gpu-link builds `Layout::Fp4`/`ShaFp4` and I run the 5090 cells.
