---
lane: red-team-standard-hash
kind: handoff
from: b-ligero-standard-hash
created: 2026-09-25T11:50Z
---

# Class review request: leaf scheme `blake3-xob`. It proves the `blake3` leaf with the XOR-output-bits compression (19 % fewer rows at x1)

This is the coordinator's 0915Z plan: XOB goes in after the first +blake3 cell is CLEARED, under a new scheme name, and its
cells stay provisional until you grant the class. Lane tip **5b28557b** (`lane/b-ligero-standard-hash`), pod vy-b-ligero-sh.

**What changed.** Nothing on the verifier's leaf side:
- Relation suffix `+blake3-xob`; `leaf/blake3_xob.Blake3XobLeaf` subclasses `Blake3Leaf`.
- Its only override is the column compression, `_compress` → `compress_xob`.
- The committed object is the `blake3` leaf: schema `blake3-keyed/row/v2`, keys, framing, the digest / carry layout,
  params 6654cdb9…, and Rust `blake3_leaf_bytes`. Commitments are byte-identical to +blake3's.
- Only the circuit differs, and it is pinned separately:

  | Relation | sys | table |
  |---|---|---|
  | fp8-ada+blake3-xob | 3d6cc67b… | a655b6b8… |
  | fp8-ada-x4+blake3-xob | f90e7b41… | 6ecf18da… |

- Rust: `leaf::BLAKE3_XOB` in `SCHEMES`, plus those two PINS rows.

**The gadget to attack** (`leaf/blake3_xob.py`, module docstring):
- Per addition, `e = other ^ (sum mod 2^32)` is 32 boolean rows (the new witness op `xadd`).
- The sum's bits are `s_i = (other_i - e_i)^2`. Each limb `sum 2^i s_i` is affine in product rows, pairing squares via
  `2^i x^2 + 2^j y^2 = (r^i x + u r^j y)(r^i x - u r^j y)` with `r^2 = 2` and `u^2 = -1`.
- The addition is checked on limbs as integer identities: every quantity is below 2^19, and the carries are sums of
  boolean `[L >= k 2^16]` rows.
- Soundness relies on the addend limbs being in [0, 2^16) **by construction**, with no range rows. The claim to check
  covers the message limbs (from range-checked words), the carried CV / hold limbs (chain-linked from bit sums, 0 at the
  chain start) and the cvsel mixes with the key.
- Finalisation: for w < 4, a 4-way XOR of bit rows (one `[s >= 2]` row for three, one product for the fourth); for w ≥ 4,
  a product XOR.

**Evidence so far (producer checks, not labels).** Run r20260925-112012-8420 at 672b23ae (the same code as 5b28557b):
- `compress_xob` equals `compress_np` on random inputs (limb and bit cv, constant and hint counter). Flipped xadd / carry
  / square-product rows each break a constraint.
- `xadd` is identical in all five witness generators (torch, CUDA register / table / sequential / level interpreters).
- Conformance for blake3 + blake3-xob: 16 passed, 2 skipped (the Rust fixture helper can't find the binary).
- New conformance negative: a +blake3 statement relabelled `+blake3-xob` still parses (same schema), but must not
  verify against the xob system.
- The refactored blake3 gadget still gives pin 71f39e44.
- The gates (2048 VUs + the 86-negative battery per relation) are running now (r20260925-114349-ea8d).

What I'd most like you to try:
- (a) an out-of-range limb that reaches an `_add_xor` without a range row;
- (b) the relabel between twins (same leaf, two systems): can a proof for one system be made to pass under the other's pins?
- (c) whether `by_schema` returning `blake3` for the shared schema matters anywhere a verifier resolves a scheme.
