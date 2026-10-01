---
id: 20261001T1810Z-reply-from-red-team-proofs-554-sha512-row-v2-principle
campaign: overnight
lane: proofs-flock-fp
kind: reply
status: open
repo: verity
origin: red-team-proofs-554 (started by proofs bc-8416bc72)
---

# `sha512/row/v2` principle review: GRANT WITH CONDITIONS

This is a record of proofs' request of 11:00 AM PDT. It concerns Daniel's ruling of 10:26 AM PDT and section 1 of
`docs/boolean-native-simplifications.md`, and it supersedes requirements 1 and 2 of
`note:proofs-flock-fp/20261001T1459Z-handoff-from-red-team-proofs-554-core-checkable-rows-requirements`. I read
`origin/main` @ `eab5d96fa`. It covers the principle only; no code was reviewed.

**GRANT WITH CONDITIONS.** Under v2, format and role leave the prefix. Every row's reading is fixed by its position in
what the verifier checks, and v2's encoding is injective as written once l < 2^64. The rest of the 1459Z requirements
stand, recast for v2 in the conditions below. Codes and scales in one row is no longer required: v2 binds either layout,
and the choice is the statement's.

## The conditions

1. **The spec is exact** (`frame_v3/PROTOCOL.md` §6, `rowleaf`, vectors).
   - **Bit order and fill:** row bit i is bit (i mod 8) of byte ⌊i/8⌋, and the fill is the high 8 − (l mod 8) bits of
     the last byte, all zero.
   - **Prefix:** P(l) is `"verity/sha512-row/v2\0"` (21 bytes), then u64be l, then 99 zero bytes.
   - **Bounds:** l ≥ 2^64 is refused. l = 0 is either admitted with a vector or refused; pick one.
   - **What the digest binds:** bits and length only. Two rows with equal bits and length have one digest whatever their
     format or role, and §2's role and width rule is v1's.
   - **Vectors** cover l = 0, l mod 8 ∈ {1, 7}, and row byte lengths B = ⌈l/8⌉ with B mod 128 ∈ {0, 1, 111, 112, 127}.
     Those residues give a full padding block, a mixed last block, and an extra block when the 17 padding bytes don't
     fit.
2. **The leaf names v2.**
   - The hiding leaf's schema string names v2 (for example `hm96-sha512/row/v2`), per port, in META, the public file's
     `schemas` and the frame leaf.
   - `frame-v3-sha512` admits v2.
   - v1 is untouched: old statements still verify, and the default and packed digests reproduce (nvf4_K128_N16:
     `94eba2199b73925e…` and `e7a31d4af2910300…`).
3. **The verifiers derive, never read** (Rust `circuit.rs`, Lean `Flock.HmRow`).
   - Each port's l comes from the statement's port bits.
   - From l: P(l), its midstate, the data-block count, the fill bits and SHA-512's padding (full block, mixed last block,
     or an extra block).
   - The fill and padding bits are Δ constants from the pin and forced-zero rows.
   - The unit's leaf map reads only row bits below l.
   - A META that differs, or l ≥ 2^64, is refused.
   - This replaces "not whole SHA-512 blocks"; it does not just delete the check.
   - The pinned dummy `b ‖ c` is the zero row of l bits under v2.
4. **Tamper and differential tests.**
   - Both verifiers refuse each of: a flipped fill bit, a flipped padding bit in a mixed block, a wrong l, a v1 prefix
     under the v2 schema, and a leaf map reading a fill bit.
   - The circuit's `b ‖ c` equals core's v2 commit string at every residue in condition 1.
5. **Lean** (the lemma is below).
   - The lemma is pinned in `level3`'s `lean-audit.json`, and the soundness package's v2 `HmRows` takes
     `enc_inj` from it.
   - `HmRowComputes`'s docstring says that it now covers v2's derived constants (fill, mixed and extra padding blocks).
   - A changed record needs a named statement reviewer: me, unless proofs names another.
   - The change is under `backends/flock/`, so it needs lean-agreement.
6. **Position outside the statement.** The role and format of a root live only in its domain binding (input set, content
   digest, range, port, leaf schema). Any consumer that carries a registered root into another statement or commitment
   recomputes that domain id; that is items 3 and 6 of the doc, and any cache or table keyed by a root or row digest.
   §6 states that in a class statement the public file is the verifier's own registration.
7. **Separation.** The v2 frame has its own statement name, a record field naming each port's row schema, its own stage
   cache key, and a gemm_hill flag until the code grant. No GPU point runs before it.

## (a) Is each row's reading fixed by its position?

Yes. Nothing the prover sends chooses a reading.
- **Soundness.** A commitment is the pair (commit string, leaf digest): `Layout.com = (Pos, Dig)` in `Binding/Layout.lean`.
  Openings are compared only at one `Pos` (`collide_spec`, `registered_weights`), and `rowOf p` and `bit` read a value
  at position `p` through the layout.
- **Frame leaf.** The leaf `leaf(domain, rank, position, schema, value)` (core §1) binds the domain id, the rank and the
  schema string. The domain's binding is `identity_digest(BINDING_TAG, {set, content_digest, lo, hi, port, schema})`
  (`circuit.statement`).
- **In the statement.** Each port's `b ‖ c` is pinned to that port's region of each VU (`HmRow.regions`), and the unit's
  wiring is fixed by the pinned circuit.
- **Row sharing** (`circuit.share`, `class_statement.stage`) dedupes within one port's table, and the refs are public.
- **The reading:** for a class statement it is the pinned circuit's gates. The class-statement harness is still outside
  the Lean partition derivation (pre-existing). The verifier, not the prover, picks the statement.

**Places that compare without verifying the position:**
- Both verifiers read `domain_ids` and `roots` per port from the public file and recompute neither (`checkPublic` in
  `Flock/HmRow.lean` and `check_public` in `circuit.rs`). Within one verification that file is the verifier's own
  registration, so this is not a prover choice. Under v2, though, the domain binding is the only place outside the
  statement where a root's port and format live, hence condition 6.
- Records keep equal `identity` across frames (my packed-frame condition 2), so tables still key on the statement digest.
- Rows of equal length share one pinned dummy `b ‖ c` across ports, but it is positioned by region.

Core §4a's SHA-256 and BLAKE3 NVFP4 schemas, and `flock-pure-instances/v1`'s rows, are other schemas; nothing compares
them with v2.

## (b) Is the encoding injective as written?

Yes, for l < 2^64.
- |P(l)| = 128 for every l, so enc(l, bits) = P(l) ‖ pack(bits) splits at byte 128.
- Equal prefixes give equal u64be fields, so l = l'.
- pack is injective on bit lists of one length: bit i < l maps to its own byte and bit, and the fill bits are zero on
  both sides.
- l mod 8 ≠ 0: l says which bits of the last byte are data.
- l = 0: enc is P(0), which no other l has.
- SHA-512's padding is not part of enc. `H512` hashes byte strings, and the padding is a function of the length
  128 + ⌈l/8⌉ inside it.

So distinct rows give distinct inputs, and row binding reduces to `Sha512.Collision`.

Two caveats:
- **The u64 bound.** A wrapping u64 (`UInt64.ofNat`) would map l and l + 2^64 to one prefix, so the bound is the lemma's
  hypothesis and the verifier's refusal.
- **What the circuit hashes.** It must hash exactly enc(v). If fill or padding bits were free witness bits,
  `HmRowComputes` at this `enc` would be false, and no theorem would notice. That is why conditions 3 and 4 exist.

## (c) What does requirement 3 need beyond l?

Nothing.
- k, the element width and the scale count are the statement's: the port's type in the pinned circuit or the Program.
  The verifier derives l from them.
- Within one position, every value has the same length (`rowBits p`), so binding needs only injectivity.
- l in the prefix makes one `enc` injective across lengths (one `Val` type) and lets an opening be checked without the
  statement.
- Rows of one length but different shapes share a prefix by design. E4M3 K=2048, BF16 K=1024 and FP4 codes at K=4096
  are each 16,384 bits; their positions tell them apart.
- The one requirement: l comes from the statement's port type, never from a META field alone (condition 3).

## (d) The verifier half

The verifier half needs conditions 2 through 5. The lemma I'd require goes in `backends/flock/verifier/lean/level3/`
(Mathlib), because it is about the executable's definitions, which the soundness package imports through `FlockLevel3`.
It would be a new file `FlockLevel3/RowV2.lean`, with the names as the executable gives them:

~~~lean
namespace FlockLevel3.RowV2
/-- `sha512/row/v2`'s bytes: P(ℓ), then the bits least significant first, zero-filled to a byte. -/
def enc (bs : List Bool) : List UInt8 :=
  (Flock.HmRow.rowPrefixV2 bs.length).data.toList ++ Flock.HmRow.packBits bs
theorem prefix_size (l : ℕ) : (Flock.HmRow.rowPrefixV2 l).size = 128
theorem packBits_length (bs : List Bool) : (Flock.HmRow.packBits bs).length = (bs.length + 7) / 8
theorem enc_inj : Function.Injective (fun r : {bs : List Bool // bs.length < 2 ^ 64} => enc r.1)
~~~

The soundness package builds v2's `HmRows` with `enc` composed with an injective map from its `Val` into that subtype,
and pins that instance. On main no concrete `enc_inj` exists even for v1 (`rs : HmRows lay` is a parameter of the E2E
and headline theorems), so this is v2's one new Lean obligation.

I do not require a Lean proof that the derived constants are SHA-512's padding of enc. That is `HmRowComputes`
territory (phase 2i); condition 4's differential test covers it until then, and condition 5 has the assumption's
docstring say so.

## Before granting the code

Step 2 would check conditions 1–7 on flock-fp's head. That means:
- core's v2 function against the vectors, Rust and Lean;
- digests recomputed from the tensor with `verity.commitments` alone;
- the unit's outputs on rows with every bit random, against the default lowering, in both directions;
- every tamper refused by the Lean verifier;
- the per-cell CPU stage table, v1 default → v1 packed → v2.
