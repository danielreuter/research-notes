lane: flock-netlist · kind: handoff · from: salted-leaves · created: 2026-09-26T20:34Z

# hm96-sha256/v1 is in core (PR #88): the HM96-on-SHA-256 row leaf, and the same function for your internal Merkle leaves

Daniel decided that hiding leaves are Halevi–Micali, unconditionally, with SHA-256 as the collision-resistant hash. Core now has
the scheme on branch `cursor/hm96-sha256-leaves-18a8` ([PR #88](https://github.com/danielreuter/verity/pull/88), draft):
`verity.commitments.hm96`, its spec in `hm96/PROTOCOL.md` and its vectors in `hm96/vectors.json`.

**The leaf.** It wraps any SHA-256 leaf digest `x` of the value:

~~~text
y    = 128 fresh bytes (the salt, private, stored beside the value)
c    = SHA-256( "verity/hm96-sha256/salt/v1\0" zero-padded to 64 B ‖ y )          one constant midstate, then 3 compressions
b    = x ⊕ M·y        M[i][j] = key bit (i + j), 256 × 1024 over GF(2)                  XOR only
leaf = SHA-256( ("verity/hm96-sha256/leaf/v1\0" ‖ SHA-256(key)) zero-padded to 64 B ‖ b ‖ c )   native at the verifier
~~~

**What your circuit proves for a serving row.**
- Private: the row and y.
- Public: `b ‖ c`, 64 bytes per row, where today you publish the 32-byte row digest.
- The gadget:
  - the inner digest, exactly as unsalted (`sha256/row/v1`, whose prefix block is a constant midstate);
  - 3 SHA-256 compressions for c (68,088 ANDs in the ripple-carry model);
  - the XOR network `b = x ⊕ M·y` from `hm96.rows(key)`: 135,803 two-input XORs for `DEFAULT_KEY`, and no AND.
- The verifier computes `hm96.tree_leaf(key, b ‖ c)` natively, then the tree.
- `hm96.HidingLayout(inner, key)` is the layout both sides read.

**Sizes match your reservations** (`reserved_salt_bytes` 128, `reserved_key_bytes` 160): y is 1024 bits, and the key is 160 bytes
(1279 bits, with bit 1279 zero).
- **The key is per configuration, not per leaf.** One key per tree is enough: the spec's §3 bound is a union over the leaves under
  one key. So the per-leaf 160-byte key reservation can shrink to one key per tree (the pinned `DEFAULT_KEY`, or a per-proof key
  bound before the root). Every leaf binds `SHA-256(key)`.
- **Why 1024 bits.** Your 6k + 4 sizing (HM96 Theorem 1 at k = 160) takes |x| = k; SHA-256 has |x| = 256. With the affine family
  (the offset b is a one-time pad), the leftover hash lemma gives N·2^-256 directly at |y| = 1024. With the pinned key it is
  N·2^-192, except for a 2^-64 fraction of keys, which is still 2^-128 at N = 2^64 (spec §3).

**Internal Merkle leaves (`flock-leaf/hm96-sha256`)** use the same function (spec §7):
- the inner digest is your SHA-256 column digest;
- one salt per leaf;
- one key per proof or the pinned key;
- leaf = `tree_leaf`;
- an opening is the column plus its 128-byte salt.

**One point for your statement's security fields.** Salts drawn from `ProverRng` STREAM_SALT (ChaCha20 over one OS seed) make the
hiding computational in ChaCha20; statistical hiding needs each salt from getrandom. Your masks are ChaCha20 anyway, so the choice
changes only what the leaf's hiding rests on.

**Trees.** `Hm96Sha256` configures the scheme over vllm-v1 trees (decision 3's tree). PR #83 binds frame-v3 roots today, and core
has no frame-v3 hm96 row schema. If M0 needs one, ask: it is a small addition (the frame-v3 leaf over `tree_leaf(key, b ‖ c)`
under schema `hm96-sha256/v1`).

**In-circuit ANDs per row** (22,696 per SHA-256 compression, 10,416 per BLAKE3 compression):

| row bytes | keyed-BLAKE3 row (today) | hm96 over `sha256/row/v1` | ratio |
|---:|---:|---:|---:|
| 1,536 | 260,400 | 635,488 | 2.44× |
| 3,072 | 520,800 | 1,180,192 | 2.27× |
| 4,096 | 697,872 | 1,543,328 | 2.21× |

**Vectors for a Rust port** (`hm96/vectors.json`):
- `masks`: two keys, unit salts, all-ones and an expansion;
- `leaves`: pos-leaf and `sha256/row/v1` inner digests;
- `trees`: vllm-v1 step domains.
