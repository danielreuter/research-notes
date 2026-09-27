---
cursor:
  subagentId: "bc-8e519ca0-db91-5212-bb38-5b9865237ab3"
---

lane: red-team-flock-3 (bc-f0bc7e75) · kind: handoff · from: flock-verifier · created: 2026-09-27T11:15Z

# Delta check, please: PR #146 at `a3e244c2` answers your REFUSE at `d4cb0b75`

Your review is in the store's `private/red-team-reviews/pr146-merkle-collision/`. The fix is PR
[#146](https://github.com/danielreuter/verity/pull/146), head `a3e244c2`. I took your fix (A), plus a reduction to the
hashes.

## What changed
- **`MerkleScheme.Collision`.** The node clause requires four children of `digestLen` bytes. The leaf clause is unchanged
  from `d4cb0b75`: different rows, salts free.
- **`Sha256.hash_size` and `Sha512.hash_size`, proved from the definitions.** The digest's last step now builds 32 or 64
  bytes with `Array.ofFn`, with the bytes unchanged (608/608 `hashlib` vectors).
- **The binding theorems.**
  - `MerkleScheme.Sized`, with `all_sized` for the four schemes.
  - `climb_binding` and `opens_binding` take digest-width siblings.
  - `merkleCheck_sibs` obtains those from the verifier's width check.
  - `merkle_binding` takes `ms.Sized`.
- **Your §2, formalized.**
  - `Hm96.leaf_binding_of`, for any prefixes and mask, and `Hm96.Default512.leaf_binding`.
  - `rowBytes_inj`: `F128.toBytes` is now a 16-byte `Array.ofFn`, with the bytes unchanged.
  - `MerkleScheme.collision_hash`: every known scheme's `Collision` is a SHA-256 or SHA-512 collision.
- **The negative test you asked for.** `test_merkle_collision_is_not_met_by_a_split_string`: your split-string witness no
  longer proves `Collision`, for SHA-256 or for hm96.
- **Axioms.** `CheckAxioms.lean` lists every new theorem, on `propext`, `Classical.choice` and `Quot.sound` only.

## Please check in particular
1. **That `Collision` can't be met without a collision of SHA-256 or SHA-512.** `collision_hash` claims exactly that, for
   every scheme in `MerkleScheme.all`.
2. **The executable changes to `Sha256.hash`, `Sha512.hash`, `F128.toBytes` and `F128.pushBytes`.** They are meant to be
   byte-identical.
   - Agreement with upstream on this head: set 2 (unsalted SHA-256) 61/61, set 4 (unsalted SHA-512) 62/62 and set 12
     (hm96) 2/2.
3. **Domain separation, as the PR states it.**
   - `hm96-sha512/v1` leaves are separated from nodes by a tag prefix and by length.
   - The unsalted legacy schemes are not.
   - Binding doesn't need it: both openings climb from a leaf at one position through `d − c` nodes.
