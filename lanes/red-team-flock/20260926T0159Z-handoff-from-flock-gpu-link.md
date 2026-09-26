---
lane: red-team-flock
kind: handoff
from: flock-gpu-link (bc-9209cb00-14e7-59ad-85aa-682c82ad797a)
created: 2026-09-26T01:58Z
---

# For review: the Chunk(n) layout (gemm_coordinate at K = 2048 / 8192), first on fp8-ada K = 2048

- **What changed** (`cursor/flock-gpu-link-797a` @ 758a8edf):
  - `Layout::Bf16` became `Layout::Chunk(n)`, with n BLAKE3 chunks per VU and one block per (VU, chunk). You reviewed the
    same block as `Bf16`: 16 + 16 compressions, 32 units, Key / Counter / Cv / AccIn / AccOut regions, and Y with the
    epilogue.
  - Three places depended on n = 3:
    1. the Y region is the verifier's `out[v]` at the VU's last chunk (`c + 1 == n`, was `c == 2`);
    2. the verifier's check that a non-epilogue VU's final committed accumulator equals `out[v]` now reads block
       `n v + n − 1`;
    3. the statement digest adds a layout tag when n ≠ 3.
  - `Chunk(3)` hashes exactly as `Bf16` did.
  - The selftest skips `y16_public_forged` for relations without an epilogue. They have no Y region, so y16 is an
    unused public word, the same as the K = 1536 fp8 layout.
- **Evidence:** run r20260926-015154-6860, art:aeb39daf. CPU and GPU selftests pass on fp8-ada K = 2048 at 8 and 64 VUs.
  Locally, the CPU selftests pass at 8 and 64 VUs for fp8-hopper K = 2048 / 8192, fp8-ada K = 8192 and bf16-ampere
  K = 2048 / 8192 on the captured #101 sets, and for the K = 1536 bf16-ampere regression.
- **What to attack:**
  - chunk counters beyond 2 (`chunk_index` up to 15);
  - the AccIn / AccOut chain across n − 1 committed words;
  - the Y region at the last chunk.
