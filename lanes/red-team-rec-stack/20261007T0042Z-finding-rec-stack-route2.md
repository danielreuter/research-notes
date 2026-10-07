---
id: red-team-rec-stack/20261007T0042Z-finding-rec-stack-route2
campaign: proofs
lane: red-team-rec-stack
kind: finding
status: final
repo: verity
origin:
  - pr:1081@7321d7b9b64282de8ab3bf5a4ef5bb7e7e952e44
  - pr:1245@7b11dda7a603128b2d707a8fdba66ae8b20dfa8f
  - pr:1246@ee9bd56556c638ebf3476b5d8d501191daf504b2
  - pr:1284@7988c7a3afd61a7d6ad504d005bad8bd30c38195
  - pr:1318@1ab5ab89c9908a3a05268edb886dcf8ab7691895
  - pr:1347@c35a427d1c367c62061d630e8cd677e9e31c8881
---

# Red team, the recursion stack at its route-2 heads: GRANT all six

Reviewed by red-team-rec-stack for the proofs coordinator on 7 Oct, 00:37Z to 00:45Z. The review read git only and ran
nothing. The labels went on at 00:43Z and are on both stores. Nothing blocks. The heads are the branch tips at 00:38Z, on `main` `e7b5caa89`. My grants at the route-1 heads
are in `note:red-team-rec-stack/20261006T1720Z-finding-rec-stack`.

## Method

The own patch is `git diff PARENT_HEAD HEAD`; every new head's merge base with its parent is the parent's head. I
compared it with the granted own patch file by file, as `+`/`-` lines without `@@` numbers. The changed paths are exactly
the brief's, and every other path is identical:

| PR | head | identical paths | changed paths | verdict |
|---|---|---|---|---|
| #1081 | `7321d7b9b` | 10 of 14 | `gf2k.circuit-check.{py,json}` (new), `pins.json` (gone), `targets.py` | GRANT |
| #1245 | `7b11dda7a` | 18 of 21 | `rec_open.circuit-check.py` (new), `sidecars.py` (new), `targets.py` | GRANT |
| #1246 | `ee9bd5655` | 18 of 23 | `rec_open.circuit-check.py`, `rec_residuals.circuit-check.{py,json}` (new), `pins.json` (gone), `targets.py` | GRANT |
| #1284 | `7988c7a3a` | 20 of 22 | `rec_open.circuit-check.py` (new), `targets.py` (gone) | GRANT |
| #1318 | `1ab5ab89c` | 7 of 9 | `Flock/Tags.lean`, `verity/Security/lean-audit.json` | GRANT |
| #1347 | `c35a427d1` | 9 of 11 | `rec_residuals.circuit-check.json` (new), `pins.json` (gone) | GRANT |

## Relocations into #1163's sidecars (#1081, #1245, #1246, #1284, #1347)

Each sidecar holds exactly the binding and pins the PR had in `targets.py` and `pins.json`.

**#1081.**
- `gf2k.circuit-check.json` holds the four pins it had in `pins.json`, with the same keys and counts:
  - `Gf128Mul_v1`: 2,187
  - `Gf256Mul_v1`: 6,561
  - `GfResiduals_v1{S={5649ec091c4b}}`: 2,187
  - `GfScale_v1{L=2}`: 4,374
- `gf2k.circuit-check.py`'s `_gf2k_roots` has the same body: `bind(G.GfScale, L=2)`, and `bind(G.GfResiduals, S=S)` with
  the same S.
- `targets.py` keeps the `gf2k` import and the dict-static fix in `definition()`. It replaces the hard-coded catalog entry
  with `_gf2k_roots` in `ROOT_FUNCTIONS`, in the same catalog slot (after `_universal_roots`).

**#1245.**
- `rec_open.circuit-check.py`'s `_rec_roots` returns `definition(8, 1)`, as before. It has no pins, since RecOpen isn't
  lowered to Boolean gates.
- `_rec_roots` joins `ROOT_FUNCTIONS` in its old slot, after `_pous_roots` and before `_kernel_roots`.
- `sidecars.PACKAGES` gains `verity_flock`, which is needed for circuit-check to find a `verity_flock` sidecar at all.

**#1246.**
- `rec_residuals.circuit-check.py` binds `RR.definition({"gf": S, "ports": [["m0", 1], ["m1", 128]]})` with the same S.
- `rec_residuals.circuit-check.json` holds `InnerRepCheck_v1{S={046a3fe0d3f7}}` at 2,187 ANDs, as `pins.json` did.
- `targets.py` keeps the `rec_residuals` import. `rec_open`'s sidecar gets #1246's docstring edit.
- The two sidecars both define `_rec_roots`. `targets._root_bindings` collects one entry per binding file, each under its
  module prefix, so both run.

**#1284.** It makes the same docstring edit ("four compressions (the plain leaf's two and the level's two)"), now in
`rec_open.circuit-check.py`.

**#1347.** It makes the same rename in the sidecar: `InnerRepCheck_v1{S={046a3fe0d3f7}}` becomes
`InnerRepCheck_v2{S={046a3fe0d3f7}}`, still at 2,187 ANDs.

**The `GfResiduals_v1` pins are unchanged.**
- `5649ec091c4b` is now in `gf2k.circuit-check.json`, with the same count.
- `5a0897f6f55a` is in `catalog/tests/test_boolean_gf2k.py`'s `PINS` table: (10935, 64064, 0, `88e6a6e2…`). That file,
  its `PINS` block and `gf2k.py` (blob `45880e0f`) are byte-identical at `845827f20`, `7321d7b9b`, `c35a427d1` and
  `1ab5ab89c`.
- The digest `88e6a6e2…` is the one my route-1 probe computed for `GfResiduals{S}`.

## #1318

**`Tags.lean`.**
- At the parent `7988c7a3a`, the file is byte-identical to `main`'s, #1383's tags included.
- The head adds exactly `leafSchemePlain`, `withPlainLeaves`, `plainLeaves` and `circuitPlainLeaves`. That block is
  line-identical to the granted one. No definition is removed: 39 definitions become 43.
- The only `all` edit appends `circuitPlainLeaves`, taking the list from 20 entries to 21. #1383's
  `circuitF5df3bbc, circuitF5df3bbcSelftest, circuitTypesF5df3bbc, circuitTypesF5df3bbcSelftest` line is context and is
  kept.

**The coin derivation is SHA-512.** `circuitPlainLeaves` is `circuit.withPlainLeaves`. After #1383, `circuit` is
`identityHidden false`, whose default `coinDerivation` is `"sha512 (verity.randomness)"`. `withPlainLeaves` sets only
`leaf_scheme`, `hashes.merkle`, `merkleLeaf` and `pinnedLeafScheme`, so the one new tag names SHA-512 coins.

**`lean-audit.json`.** Parsed as JSON, the own patch changes the same 8 leaves as the granted one, with the same before
and after values:
- `reads/Flock.Verify`: its `digest`, and the definitions `Flock.Setup`, `Flock.Setup.ofCircuit`,
  `Flock.Setup.openedSalts` (new), `Flock.instInhabitedSetup.default` and `Flock.verifyRep`;
- `reads/Proofs.Flock.Soundness.Refine.Rep`: its `digest` and `FlockSoundness.Refine.shapeOf`.

The only textual extra is the top-level `"four_names": ["Nci", "NetTiming"]`, moved from line 248 to the end of the file
with an equal value. It is a key reorder, not a change, and the union didn't need it.

## Merges

`git merge-tree --write-tree` of every head onto its parent's new head and onto `origin/main` `e7b5caa89` is clean, and
each one reproduces the head's tree.

## Non-blocking

- **#1318's `four_names` move** is presumably `audit.py --update`'s key order. If a check compares the lock's bytes, the
  route-2 lock replay will say which placement is canonical. Either way, it carries no content.
- **Friction:** this relabel round caught nothing. Every change is a relocation that keeps the bytes of each binding and
  pin, or a JSON key reorder. A `carry` that compared bindings and pins by key, and JSON by value, would have carried all
  six without a review.
