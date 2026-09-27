---
cursor:
  subagentId: "bc-ff572e70-b0e7-5094-85be-13ff9ddc4d6a"
---

lane: vllm-serving-commit · kind: handoff · from: flock-netlist · created: 2026-09-27T06:00Z · status: final ·
repo: danielreuter/verity · origin: PR #83 @ e51e2b86

# The serving row leaf M0 proves: `frame-v3-sha512` + `hm96-sha512/v1`, spec and test vector

This is the format M0's `verity/flock-circuit` proves in the circuit. Commit rows this way at serving time and M0 proves
the rows behind your roots. It is fixed at `e51e2b86`: M0's CPU and GPU selftests pass on RoPE, SiLU and both RMSNorm
templates.

Every piece is in core, and the vector below was produced with these references only:
- `verity.commitments.rowleaf`: `sha512_row_prefix`, `sha512_row_layout`, `row_leaf`, `SCHEMA_HM96_SHA512_ROW`;
- `verity.commitments.hm96.SHA512`: `commit_string`, `tree_leaf`, `salt_prefix`, `leaf_prefix`, `default_key`;
- `verity.commitments.merkle`: `CommitmentDomain(..., hash="sha512")`, `tree_levels`;
- `verity.commitments.frame_v3.FrameV3.root`.

## The spec, per row (a tensor row of `n` words, word width 16)

1. **Row bytes.** The row's `n` words, little-endian, in row order: `2n` bytes.
2. **Inner digest (`sha512/row/v1`).** `x = SHA-512(prefix ‖ row_bytes)`, 64 bytes.
   - The prefix is one 128-byte block: `"verity/sha512-row/v1\0" ‖ u8 role ‖ u8 word_bits ‖ u32be n`, zero-padded.
   - `role` is 1 for an x row (activation) and 2 for a W column; `word_bits` is 16.
   - M0 proves it from the private row, starting from the prefix block's constant midstate.
3. **Salt.** `y` is 192 bytes, fresh from the OS generator for every row. It is never reused and never published, and the
   prover needs it: keep it with the row. (The vector's salts are fixed for testing only.)
4. **Commit string (`hm96-sha512/v1`, key = its `default_key`).** The key is 256 bytes, with SHA-512 `afc5a60c…9df22`.
   - `b = x XOR M(key) · y`, 64 bytes. `M` is the 512 × 1536 GF(2) matrix of hm96 §5; `hm96.SHA512.commit_string`
     computes it.
   - `c = SHA-512(salt_prefix ‖ y)`, 64 bytes; `salt_prefix` is one 128-byte block.
   - Publish `b ‖ c`: 128 bytes per row. M0's statement takes these as its public per-row data.
5. **Tree leaf digest.** `t = hm96.SHA512.tree_leaf(key, b ‖ c) = SHA-512(leaf_prefix(key) ‖ b ‖ c)`, 64 bytes.
   `leaf_prefix` is one 128-byte block.
6. **Frame leaf (`frame-v3-sha512`, schema `hm96-sha512/row/v1`).** `leaf = H("leaf", [domain_id, uint(rank), uint(position),
   "hm96-sha512/row/v1", t])`. `rank = position = the row's index` in a range domain.

## Framing, tree and domain (frame-v3 on SHA-512)

~~~text
H(tag, parts) = SHA-512("veritor/protocol/merkle/frame/v3\0" ‖ be32(|tag|) ‖ tag ‖ Π_p (be64(|p|) ‖ p))
uint(x)       = big-endian bytes of x without leading zeros (0 → 00)
pad(r)        = H("pad",  [domain_id, uint(r)])                 for r in [n, next_pow2(n))
node(d, i)    = H("node", [domain_id, uint(d), uint(i), L, R])  d = 0 at the first merge, i = index in the new level
root          = the last level's single node; one leaf is its own root; no leaf: H("empty", [domain_id])
domain_id     = CommitmentDomain(binding (32 B), owner, positions, hash="sha512").domain_id
              = H("domain", [binding, uint(owner + 2), positions.identity_sha512(), uint(count)])
~~~

- **Binding and owner** are yours, from `vllm-v1-sha512`'s domains (what the root may not outlive). The vector uses a test
  binding.
- **Output words**, if you commit any the same way: a word leaf is `H("leaf", [domain_id, uint(r), uint(r), "u16", be16(value)])`
  under its own domain.

## Test vector

- **Where.** `notes-asset:campaigns/boolean-escape-hatch/assets/flock-netlist/serving-row-leaf-vector.json`: every
  intermediate for 3 rows of 8 words, one pad, and the tree levels. Its sha256 starts `92aa7f7764ca1a32`.
- **Independent check.** `serving-row-leaf-vector-check.py` beside it recomputes the prefix block, `x`, `c`, `t`, every frame
  leaf, the pad, the nodes and the root from the framing above with `hashlib` only, and matches.
- **Inputs.**
  - `role = 1`, `word_bits = 16`, `n = 8`; row `r`'s words are `(1000 r + 7 j) mod 2^16` for `j < 8`.
  - Salts: `y_r = SHAKE-256("verity/test-vector/salt/" ‖ u8 r)`, first 192 bytes.
  - `binding = SHA-256("verity/test-vector/serving-row-leaf/v1")`, `owner = −1`, positions `RangeIndexedDomain(0, 3)`.

  | value | hex |
  |---|---|
  | `domain_id` | `2a3548750f35dfa191d1dc1d3451adaecdf43a488418012813734f5e2711c14a1c77befd35d1f9ac0b7efd33df12d34411879bc291c4d150db2baf0f495f8b74` |
  | row 0 bytes | `000007000e0015001c0023002a003100` |
  | row 0 `x` | `8b8ffb0148d90248dd01165f327a81c8a59089d1f3d95b511789b5e589b00fa9…` |
  | row 0 `y` | `61fb00ff5c6a55fe619e4a790d1fde2d…` |
  | row 0 `b` | `098d9da03889d92e48afaab64f0d3aa9…` |
  | row 0 `c` | `617ed660feeb7653b3a6ffaae876976b…` |
  | row 0 `t` | `ca7c6e0f1a5fda34fe83c772011e0539…` |
  | row 0 frame leaf | `97763d9fd248d16dcbe1804fb26fce92…` |
  | root | `63224c8e2d219c6efa70eff6d63d19072e0cae1b529ccd162fb20e8f668dd9ee20c6a69b05b5c365bd40265e3ad7a35fa53a100c8dcf1cd4de035d9bc68a0fbe` |

## What M0 needs from you

- **Per committed tensor (a port):** the root and its leaf count, the domain (binding, owner, positions), and each row's
  `b ‖ c`.
- **Kept for the prover:** each row's words and its salt `y`.
- **What the verifier does.** It recomputes every frame leaf and the root from the published `b ‖ c` (a check of the
  commitment scheme on public data), and M0 proves in the circuit that the private row and salt give that `b ‖ c`.
- **Row sizes.** Rows are whole SHA-512 blocks after the prefix: `2n` a multiple of 128 (n a multiple of 64). Say if you
  need other widths.
