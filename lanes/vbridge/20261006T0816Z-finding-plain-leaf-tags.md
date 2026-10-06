---
id: vbridge/20261006T0816Z-finding-plain-leaf-tags
campaign: proof-service
lane: vbridge
kind: finding
status: active
repo: danielreuter/verity
origin: bc-8416bc72 (proofs)
cursor:
  subagentId: "bc-5d1693f8-59d6-5a38-89a1-48bfd0365a30"
---

# The Lean verifier's tag set for a recursive session's inner statement (`flock-leaf/sha512-unsalted`), and which `partial def` escapes the accept path reaches

Question (P4 of note:verity-root/20261006T0550Z-report-proof-service-implementation): can Lean `verify` accept rec-step3's
inner session (#1284, plain SHA-512 leaves, ZK off) under its own statement, and does VBridge's piece G, at the rep level,
reach any `partial def` escape?

## The tag set

Branch `cursor/flock-plain-leaf-tags-95d4` at `1b9bdd83c56db41dbb2a1c9ad1c122b6118c08b5`, on #1284's
`cursor/rec-step3-95d4`. It adds the statement `verity/flock-circuit+plain-leaves`, which is `Tags.circuit` with plain
leaves. Swapping only `merkleLeaf` and the pinned leaf scheme was not enough, for two reasons:

- The statement digest hashes the identity, and upstream's `identity(c)` writes the leaf scheme into it twice: in
  `leaf_scheme`, and in `hashes.merkle`, which becomes "sha512 (every Ligerito level)". `Tags.withPlainLeaves` rewrites
  both fields.
- The pinned patch has written `opened_salts` into every opening since `2908d078`. For plain leaves the vector is empty
  (a u64 count of 0). Lean's old rule, "salt size 0 means no field", misread the field and failed with
  "recursive_caps: length 0, want 6" (run `r20261006-065052-f085`). The fix is a new field, `Setup.openedSalts`. It is set
  on every statement with hm96 rows, and the parser reads the empty vector when it is set. `631567f7`'s openings, which
  carry no such field, still parse as before.

`verify --zk` refuses the new statement and exits 2, as upstream's `--zk` refuses plain leaves. The check is
`Tags.plainLeaves`, a def that compares `pinnedLeafScheme` with the pinned object. I made it a def, not a new field, so
that Security's `Flock.Tags` records stay as they are.

## Evidence

Run `r20261006-070214-54f3` checks the k4096s3 inner session (`--coins os`) on node 1:

| Case | Verdict |
| --- | --- |
| Honest session, new statement | accepted in 2:22.57, max RSS 3.1 GB |
| Same session, `--statement verity/flock-circuit` | refused at setup |
| Same session, `--zk` | refused, exit 2 |
| Byte 428233 of rep0 flipped | rejected: "S17: circuit/rep0: the proof is not the one the server received" |

The statement digest is `59130006…6546`.

The Lean audits:

- Run `r20261006-071311-b0d6` audits Security. It passes: 6873 declarations, 1747 guarantees.
- The same run builds Proofs and replays 57435 declarations. Proofs fails only its `runs` check, because of the
  `--cwd clone` PYTHONPATH bug that #1286 fixes.
- Run `r20261006-075425-d9b4` audits the verifier. It passes: 5562 declarations, 7 guarantees.

Pytest: 35 passed and 1 skipped, then 98 passed and 1 skipped. The skips are opt-in slow tests.

## The pinned-record change

Security's `lean-audit.json` changes the records of the 111 guarantees that read `Flock.Verify`, and of
`Refine.Rep.shapeOf`, which `rep_refines` ties to `verifyRep`'s shape. No signature changed. Only the definitions those
statements read changed, by the new field `openedSalts`. Under Daniel's 2026-10-03 ruling, no statement reviewer is
needed. Because the change touches the verifier, merging needs a red-team grant and `lean-agreement`.

## `partial def` escapes on the accept path

I walked `getUsedConstantsAsSet` from each root, over the verifier's 25 `partial def` escapes:

| Root | Escapes it reaches |
| --- | --- |
| `Flock.verifyRep`, `Setup.ofCircuit`, `Zk.verifyRep`, `Partition.derivedCommitted` | none |
| `Flock.verify` (session level) | `Flock.canon`, through U1's unit-draw comparison (`Draw.lean:379`) |
| `Stmt.setup` | `Flock.canon` (the statement digest) |
| `verifyCmd` (the CLI) | 12, all in the partition and program checks |

`verifyCmd` reaches these 12: `canon`, `Qcall.cut`, `Qword.DCut.units`, `owner`, `locate`, `Program.domainError`,
`Ty.leaves`, `Ty.ofJson`, `Program.resolve`, `fnRefs`, `getDef` and `Extract.evalDef`.

G concludes at `verifyRep`, so VBridge needs no change. A theorem at the session level would need `Flock.canon` to be
total. That is a small verifier PR of its own. @proofs ruled at 08:34Z that it is not for tonight: G stays at the rep
level, and @proofs schedules the session-level follow-up (`Flock.canon` total, then a theorem at `Flock.verify`) after
14:00Z.

The tag set is draft PR #1318, under review by red-team-plain-leaves.

## Still to do

- V*'s staging registers `coef`. Today `rec_outer.py` stages it as a public input; it should become a value the verifier
  registers from its own coins, at about LANES hm96 compressions per opening.
- VBridge pieces D, F and G. F and G take the inner statement with `openedSalts := true`.
- Restack after the 09:00Z rename.
