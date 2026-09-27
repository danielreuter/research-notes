---
cursor:
  subagentId: "bc-8e519ca0-db91-5212-bb38-5b9865237ab3"
---

lane: coordinator · kind: handoff · from: flock-verifier · created: 2026-09-27T11:20Z

# #146 at `a3e244c2`: Merkle binding now reduces to SHA-256/SHA-512 collision resistance; delta check requested

## #146
- **What the red team refused at `d4cb0b75`.** `Collision`'s node clause could be met without any hash collision, because
  a node hashes `l ‖ r` without length framing. Main has the same flaw. Their review is in the store's
  `private/red-team-reviews/pr146-merkle-collision/`.
- **The fix, at `a3e244c2`.**
  - The node clause requires four children of the digest's width.
  - `Sha256.hash_size` and `Sha512.hash_size` are proved from the definitions. The digest's last step builds 32 or 64 bytes,
    with the bytes unchanged.
  - The binding theorems take digest-width siblings, which `merkleCheck` supplies.
  - `MerkleScheme.collision_hash`: every known scheme's `Collision` is a SHA-256 or SHA-512 collision. That includes the
    hm96 salt-digest reduction (`Hm96.Default512.leaf_binding`) and `rowBytes_inj`, all on standard axioms.
- **The executable was not at fault.** It only ever hashes digest-width children. `hm96-sha512/v1` separates leaves from
  nodes. The legacy unsalted schemes don't, and binding doesn't need it. Details in the PR.
- **Byte-identical executable.** 608/608 `hashlib` vectors. Agreement with upstream on this head: set 2 61/61, set 4 62/62,
  set 12 2/2.
- **For #130:** re-pin after #146 merges.
- **Delta check requested** from bc-f0bc7e75: `lanes/red-team-flock-3/20260927T1115Z-handoff-from-flock-verifier-pr146-delta.md`.

## Also since 10:30Z
- **audit-lean's six questions are answered:**
  `lanes/audit-lean/20260927T1045Z-handoff-from-flock-verifier-row-placement-answers.md`.
- **PR [#147](https://github.com/danielreuter/verity/pull/147), stacked on #142, adds the row-order check** (`Rows.topo` in
  `Net.parse`, and the port-group bounds). Every circuit of sets 0–15 meets both.
  - Its local agreement regression got through sets 0–2 (47/47, 47/47, 61/61) before I stopped it for #146. I'll finish it
    and then tell you its head is final.
- **M0 `e226a920`** (P6) changes nothing the verifier reads beyond `967b8d06`, so #142 verifies P6's files.
