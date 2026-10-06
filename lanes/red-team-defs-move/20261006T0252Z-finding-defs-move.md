---
id: red-team-defs-move/20261006T0252Z-finding-defs-move
campaign: proofs
lane: red-team-defs-move
kind: finding
status: final
repo: verity
origin: check:r20261006-004654-ea26@7b410fbf6
---
# Red team, the Lean layout move's two changed definition hashes: GRANT (meaning unchanged, both)

Reviewed 7:52 PM PDT, 5 Oct, by red-team-defs-move (agent bc-367fc3e6-5fd6-5773-bb76-040caaf1a77a) for the proofs
coordinator. The claim is lean's verdict "defs-unchanged" (art:6059ec16, runs r20261006-014944-4935 and
r20261006-020436-9916) on the move #1225 (`main` 88f5cc533 -> 7b410fbf6, landing check r20261006-004654-ea26).

- `FlockSoundness.Model.Arith.Correct` (824c4021 -> 1187cbda): **GRANT**, meaning unchanged.
- `FlockSoundness.RepDoomedW` (185fd70a -> 9d0549f9): **GRANT**, meaning unchanged.

Evidence: art:98514134a98ab2ea3b46a01ff2a6e6d6bfe39ca42d019f93b716eeff42927900 (scripts, outputs, probe sources, README).
My run is r20261006-023815-a5d6 (vy-nebius-1, its own clone, `LEAN_CACHE=off`). It rebuilt `FlockSoundness.Defs` from
88f5cc533's verifier tree, placed under `old/`, and `Proofs.Flock.Soundness.Defs` from 7b410fbf6, both from source.

## What I checked, independently of lean's tools

1. **The hashes themselves.** I dumped the audit's canon (`Facts.lean` `readCanon`, unchanged across the move) for
   every member of both groups from both builds. `audit.py`'s `digest` reproduces all four recorded hashes. The groups
   the records hash are {`Correct`, `Correct.mk`} and {`RepDoomedW`}. The old terms with only the two instance-path
   rewrites have canon text identical to the new build's for every member, so they hash to 1187cbda and 9d0549f9.
   Nothing else changed, at the level the records see.
2. **Claim 1 (one instance path, 8 sites): confirmed.** Lean's two `pp.all` prints differ in exactly 8 token runs
   with no normalisation but whitespace: 7 `Semifield.toCommSemiring (Field.toSemifield (ZMod.instField 2 _))` ->
   `CommRing.toCommSemiring (ZMod.commRing 2)` and 1 `DivisionRing.toRing (Field.toDivisionRing …)` -> `CommRing.toRing …`.
   Its `rewrite_check.py`, rerun, passes. Wording: the 8 are print positions (`#print RepDoomedW` 2, `#print Correct` 4,
   `#check Correct.mk` 2). In the kernel terms the records hash, there are 4 sites: 2 in `Correct.mk`'s type and 2
   in `RepDoomedW`'s value.
3. **Claim 2 (same meaning): confirmed, by the kernel.** `Lean.Kernel.isDefEq` is true for both instance pairs, and
   for each member's type and value against its rewrite. `addDecl` of `old = rewritten := Eq.refl old` is accepted
   for every changed part. A control, `(0 : ZMod 2) = 1`, is refused by both checks. Lean's `Defeq.lean` states equality of the
   whole instance terms (each projection at the sites then agrees by congruence) with `with_reducible_and_instances
   rfl` in an `example`. My `addDecl` check doesn't depend on that `example` reaching the kernel.
4. **Claim 3 (cause 15f0987a0): confirmed.** In the old build the only import path from `FlockSoundness.Defs` to
   `Mathlib.Algebra.Field.ZMod` runs through `ArkLib…CapacityBounds` (then JohnsonLower.BinaryBasics, then Mathlib.FieldTheory.Finite.Basic).
   No other direct import reaches it, and the new `Defs` doesn't reach it at all. Correction to the brief: `Defs.lean`
   is R098, not R100. Its third import line changed (CapacityBounds -> `Mathlib.Algebra.Polynomial.Degree.Defs`).
   Its body is byte-identical, and so are the other 11 modules of its in-package closure, module prefix aside. Pins,
   toolchain and `leanOptions` are equal. `Arith.Correct` is declared in `Defs.lean`; `Model/Basic.lean` declares `Arith`.
5. **Claim 4 (the evidence): confirmed.** Lean's source commits 65f23f0a and 99304e96 are 7b410fbf6 with nothing
   changed outside `old/` and `probe/`. Their `old/` is 88f5cc533's verifier tree (tree 43eae82d), and their probe
   blobs are the art's sources. All seven of lean's probe outputs come out byte-identical when rerun on my builds.
6. **Other definitions: confirmed.** The 201 guarantees that read `Proofs.Flock.Soundness.Defs` read 4446 definitions
   (counted by module). 4444 match an old record's hash, and only these two don't. The old soundness record's 4964
   definitions are all in the merged record, 4962 unchanged. The old *level3* record differs from the merged one on 7
   `Flock.*` definitions (`Flock.Net`, `Flock.F256`, `Flock.Kind`, …). That isn't a change: their sources are
   byte-identical (the verifier package has no dependencies), and the old soundness record already held the merged
   record's hashes for them. A record's per-definition hash digests the generated members (`.mk`, `.match_n`, …) that
   its own guarantees read, so two packages' records can disagree on the same constant. Any cross-record hash
   comparison will show such false changes.

Nothing blocks. The label on r20261006-004654-ea26 is beside lean's.
