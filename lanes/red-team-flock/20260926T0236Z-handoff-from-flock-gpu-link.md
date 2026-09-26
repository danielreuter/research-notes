---
lane: red-team-flock
kind: handoff
from: flock-gpu-link (bc-9209cb00-14e7-59ad-85aa-682c82ad797a)
created: 2026-09-26T02:35Z
---

# For review, early: the fp4-nvf4 layouts (Fp4 over blake3-keyed/row-nvfp4/v1, ShaFp4 over sha256/row-nvfp4/v1)

These are ready at `cursor/flock-gpu-link-797a` @ 7b3ba797. CPU selftests pass at 8 and 64 VUs. The 5090 GPU run is waiting
for stock, and the timings will follow.

- **Row:** the adopted 864-byte NVFP4 row: 768 code bytes (code 2i in the low nibble), then 96 UE4M3 scale bytes.
- **Fp4** (k_log 20, block = VU):
  - Each role is ONE keyed-BLAKE3 chunk of 14 compressions.
  - Blocks 0–12 are full. Block 13 has block_len 32, CHUNK_END | ROOT | KEYED_HASH flags, and message words 8–15 as
    constant 0.
  - Key, counter 0, block_len and flags are per-slot constants, as in fp8's layout.
  - The root output (out_lo of slot 13 / 27) is a **Digest region whose value the verifier computes itself**, from its
    instance: `blake3::keyed_hash(row_key, row)`. There are no chaining-value publics.
- **ShaFp4** (k_log 21):
  - Each role is one SHA-256 chain from the midstate of `sha256_row_nvfp4_prefix(role, 1536)`.
  - The chain runs over 13 row blocks and a final block. That block's words 0–7 are row bytes 832–863 (big-endian), and
    words 8–15 are the constant padding: 0x80000000, zeros, and the bit length 7,424.
  - The digest region is the verifier's SHA-256 digest.
- **Units** (24 per VU, at 2^13 positions 56.. for Fp4 and 112.. for ShaFp4):
  - The x / W code operands (256 bits each) copy message half-block u % 2 of block u / 2.
  - The scale operands (unit bits 544–575 for x, 576–607 for W) copy message word u % 16 of block 12 + u / 16. They are
    little-endian for BLAKE3 and big-endian for SHA-256.
  - c_in(0) is forced to +0; the chain is inside the block.
  - The netlist is fp4-nvf4 fb52a87c (flock-backend's pin), with 608-bit inputs.
- **What to attack:**
  - the partial final block: block_len 32, the ROOT flag, and the constant zero words;
  - the scale-word copies, in both endiannesses;
  - the digest regions as the only binding of the row to the witness;
  - the dummy blocks: zero rows, which are valid NVFP4 (scale 0 is finite).
- **Selftest changes:** the negatives now tamper each layout's own last block of role 0, instead of a hardcoded slot 15.
  `wrong_block_len` toggles 64 and 32. `chunk_value_forged` is skipped where there are no chaining-value publics.
