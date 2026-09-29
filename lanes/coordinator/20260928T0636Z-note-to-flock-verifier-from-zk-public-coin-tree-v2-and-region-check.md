---
cursor:
  subagentId: "bc-b483c71e-c321-599b-b63b-e4cc0dccb710"
---

# To flock-verifier, from zk-public: two specs for the Lean verifier (keyed coin tree, region-word check)

The red team granted the public-circuit ZK proof (`docs/zk-proof-public.md`) with conditions. The coordinator asked for two
protocol changes whose verifier side is yours. Both specs are written for implementation.

## 1. The keyed coin tree, `coin-tree/hm96-sha512/v2` (`docs/coin-tree-v2.md`)

The prover's fresh 32-byte nonce in `Hello` prefixes every hash of the verifier's coin tree, and the verifier answers
`Hello` with its root and a fresh hm96 key for the session's tree. The Lean verifier checks session records, so its part is
the spec's §7:
- a coin source for `coin-tree/hm96-sha512/v2` in `helloOf` (`Flock/Statement.lean`), which takes the prover's nonce;
- S2/R7 (`Flock/Record.lean`): build `Hello` with the record's `coins.nonce`, and compare byte for byte;
- the record's `coin_tree.nonce` equal to it, and `coin_tree.key` with bit 2047 zero.

Re-checking the openings isn't needed for soundness, since the commitment protects the prover. If the Lean verifier ever
serves coins itself, the spec's §4–§6 and its test vectors apply unchanged. The M1 lane has the Rust side.

## 2. The region-word check (`docs/region-word-check.md`)

Refuse a statement in which a column shares a 128-bit word with a region's columns without being one of them, unless its
combined $A$ and $B$ rows (the slot type's row plus Δ, entries cancelling in pairs, as `addDelta` already sums them) are
both empty.
- **Where:** `Stmt.setupH` (`Flock/HmRow.lean`), after `HmRow.delta` and `HmRow.regions`.
- **What it touches:** today only a tail stage's `Out` region is partial, for example a GEMM coordinate's 16 bits in a word.
  The `Digest` regions and the unit-range `Out` cover whole words.
- **Tests:** in the spec, including a negative circuit and a Δ pair that cancels.

## Status

Both await the red team's statement review. The keyed tree's session key is my addition for soundness. **Update (06:42Z):
the coordinator decided to keep it, so check the record's `coin_tree.key` as §7 says.** Daniel may reverse that in the
morning, so it still helps if the key check is easy to drop. Questions to me here.
