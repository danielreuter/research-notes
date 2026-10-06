---
id: proofs/20261005T2345Z-draft-vbridge-plan
campaign: proofs
lane: proofs
kind: draft
status: draft
repo: danielreuter/verity
origin: vbridge
---

# VBridge: the plan

`VBridge` says that when V* (C-Flock's verifier written as a circuit: `RecOpen_v2{LANES, H}` per Ligerito level, and
`InnerRepCheck_v1{S}` in parts p0 to p2 for the algebra) accepts at its public inputs, C-Flock's Lean verifier of record
accepts the inner session those inputs commit to. This note cuts the proof into pieces, measures each one against the
closest Lean that already exists, says what each waits on, and says how Lean gets V*'s circuits.

Branch `cursor/vbridge-95d4`, off `b87eeef64` (the layout move, #1225). Directory `verity/Security/Proofs/Flock/VBridge/`.
rec-thm's statement (`Specs/Flock/Assumptions/Recursive.lean`) had not been pushed at 23:45Z. The pieces below are
written against #1090's `VBridge` (`Recursion/Flock.lean`), and the composition (G) waits for rec-thm's statement.

## The shape of the proof

The proof is deterministic. No CR, no probability: the outer witness satisfies V*'s rows, so a decoded inner session
passes every check the verifier of record makes. Binding the decoded messages to the proxy's `c_k` (`cr/sha-512`) is
rec-thm's composition, not VBridge's.

1. The outer session accepts and no proof unit is wrong. Then each V* instance's rows hold at its committed bits (D).
2. Each instance's rows force what its builder computes (A, B, C for openings; E for the algebra).
3. What they compute is the check the verifier of record makes:
   - A `RecOpen` output equal to the verifier-registered `rec-L<level>` row is `Merkle.opens hm96Sha512 cap c d lanes pos
     row salt sibs` (`Flock/Merkle.lean`, the same climb and leaf).
   - The chained `rec-acc` rows are the level's consistency sums `e` (`Ligerito.queryLevel`).
   - Zero residuals in `InnerRepCheck` are the `check`s of `bindAndZerocheck`, `lincheck`, `ringSwitch` and `ligerito`
     (`Flock/Piop.lean`, `Opening.lean`, `Ligerito.lean`) at the rep's coins (F gives the coefficients as Lean
     functions of those coins).
4. Run on the decoded session, the verifier of record therefore throws nowhere (G).

## The pieces

Sizes are Lean lines, measured from the named files at `b87eeef64` (or #1090 at `075e10e0b`) and scaled by what the new
piece adds. Every piece is a new file under `VBridge/`, so no two pieces share a file. Where a piece reads another's
theorems, it reads them only through that file's headline statement.

| piece | file | what it proves | closest existing Lean (lines) | estimate | waits on | can start now against |
|---|---|---|---|---|---|---|
| A. SHA from a midstate | `VBridge/Sha.lean` | `shaFrom cv bits pre`, the builder of `rec_open._sha` (constant padding `pad_tail`, `wordBit` reordering, one `HmNets.compress` a block). Its `Sound` judgement: output bit `t` is bit `t` of `SHA-512(pre ‖ data)` when `cv` is `pre`'s chaining value (`pre` empty or one block) and the bits are `data`'s, for any byte length. | `Hidden/Wide/RowCommit.lean`: `row_commitP` and its prefix and block lemmas (lines 56 to 187, 130 lines) do the 128n-byte, slot-copied case. They sit on `Hm/Slot.lean` (104: `chainV_succ`, `lastCv`), `Hm/Hash.lean` (197: `padData`, `bitL_hash`) and `Hm/Compress.lean` (199: `sound_compress`). | 200 to 300 | nothing | `b87eeef64` |
| B1. Karatsuba | `VBridge/Karatsuba.lean` | #1090's `kara`, `reduceG`, `mul128` and `sound_mul128`, ported with the post-move imports | #1090 `Recursion/Karatsuba.lean` (226, already written) | about 230 | nothing | `b87eeef64` |
| B2. Residuals | `VBridge/Residuals.lean` | `residualForms`, the builder of `rec_residuals.residual_forms`: each product's 2,187 Karatsuba leaf ANDs summed across products, each sum committed, recombined and reduced once. `Sound`: residual `r` carries the bits of `Σ_p w[a_p]·v[b_p] + Σ adds` in F128. | `Karatsuba.lean` (226) for one product. The new part is linearity through `kara`'s recursion (`Σ_p reduce(K(a_p, b_p)) = reduce(recombine(Σ_p leaves_p))`). | 250 to 400 | B1 | `b87eeef64` |
| C1. Climb | `VBridge/Climb.lean` | H levels of the swap `t = d ∧ (cur ⊕ sib)` and the node `SHA-512(l ‖ r)` are `Flock.climb hm96Sha512 cur pos sibs` at the position's low bits | `Flock.climb` is 4 lines; the proof is induction on H over A, like `Hm/Slot.lean` (104) | 120 to 200 | A | `b87eeef64` |
| C2. Opening | `VBridge/Open.lean` | `recOpen LANES H`, the builder of `rec_open.unit_circuit` (`_steps` over `_Forms`). Spec: `out` is (the climb of `hm96Sha512.leaf row salt`, the low bits) and `acc_out` is `acc + Σ_l c_r[l]·row[l]`. Composed with the registered `rec-L` row it gives `Merkle.opens`. | `Hm/Hm96.lean` (154) + `Hm/Top.lean` (167) give the hm96 commit string; `RowCommit.hm96_commit` gives `Binding.commitString` | 250 to 400 | A, B2, C1; rec-step3 changes the leaf (tree tops salted, leaves unsalted) | the sums and the climb now; the leaf after rec-step3 |
| D. Nets | `VBridge/Net.lean` | V*'s outer circuit `c` is a Lean term (the layout of the builders' nets). "No wrong unit" (`Partition.Correct` over `keyProg c hU n`) gives `stHolds` of each instance's builder at its committed bits. | `Hm/Laid.lean` (91: `laid_rows`) + `Hm/Nets.lean` (182) + `Hm/Row.lean` (233) | 300 to 500 | #1179 (which outer acceptance: `VerifiesZK` with `--registered` and `--public-inputs`) and #1192 (row form: V*'s ports are `sha512/row/v1`, and canonical V1 wants v2 under `--zk`) | layout lemmas at `b87eeef64` |
| E. Algebra | `VBridge/Algebra/{Structure, Zerocheck, Lincheck, RingSwitch, Ligerito}.lean` | `Structure`: Lean `structure sh` and `verifierRows` (`rec_algebra.structure` and `verifier_rows`, 991 Python lines, about 400 of them the symbolic run and the final weights). The other four: all residuals zero means each `check` of that stage passes on the decoded messages at the rep's coins. | Level 3 `Folded` + `FoldStmt` + `Fold` (995 lines) prove one stage, the lincheck fold, against its maths, and `Lincheck` reuses `folded_eq`. The verifier code covered: `Piop.lean` 164, `Opening.lean` 92, `Ligerito.lean` 280. | 1,500 to 3,000 | flock-specs' extraction (import paths only) | `b87eeef64` |
| F. Inputs | `VBridge/Inputs.lean` | V*'s verifier-side words as Lean functions of the inner record and coins: positions (`Ligerito.positions`), `eq(α)` (`Piop.eqTable`), κ, `coef = κ·eq(α)[j]`, the comb, and the expected `rec-L` and `rec-c` rows | rec-step2's `InnerFold.lean` (68) + `InnerClaims.lean` (112) | 200 to 350 | rec-thm (how the statement names them) | `b87eeef64` |
| G. Bridge | `VBridge/Decode.lean`, `VBridge.lean` | Decode the outer witness into the inner session (rows, salts, siblings, round messages), then compose A to F into rec-thm's `VBridge` | #1090 `Recursion/Flock.lean` (265) + `Recursion/Stage.lean` (420) | 400 to 700 | rec-thm's statement, D, all the rest | after rec-thm's push |

Total: 3,450 to 6,080 lines. For comparison, #1090's `Recursion/` is 3,787 lines and `Soundness/Discharge/Hm/` is 5,174.

**SHA comes first, not level 3.** The SHA-512 compression lowering is already proved in the soundness package
(`Discharge/Hm/Compress.sound_compress` over `Flock.HmNets.compress`). V*'s compressions are the same gadget:
`rec_open` calls `verity.primitives.commitments.gates.sha512.compress_gadget`, which `sha512_circuit` re-exports and
`HmNets.compress` mirrors (checked by `checkNet` on the `sha512x3` slot). Level 3 has no SHA proof. It enters through
B1 (`FlockLevel3.GF128`) and E (`folded_eq`).

## Parallel lanes now

The pieces split three ways, with disjoint files:

1. **vbridge (me):** A, then C1, D, C2 (after rec-step3) and G.
2. **A new lane, gf:** B1, then B2. It needs nothing that is pending, and C2 waits on it.
3. **A new lane, algebra:** E, starting with `Algebra/Structure.lean` and `Algebra/Zerocheck.lean`. It is the largest
   piece and the one that doesn't move under rec-step3.
   - A fourth lane can take `Algebra/Ligerito.lean` plus F once `Structure.lean` has its first push. Ligerito's final
     weights read F's coefficients.

All three run on separate checkouts and Lake build directories. Each piece's headline theorem is pinned with
`audit.py --update` (`owner: @proofs`) when the piece is finished.

## How Lean gets V*'s circuits

**The pick: a Lean restatement, pinned by digest.** Each V* unit is a Lean builder in `Flock.HmNets`' monad (`recOpen
LANES H`, `innerRepCheck S`), written gate for gate after `rec_open.unit_circuit` and `rec_residuals.unit_circuit`.
`HmNets.compress`, `commit` and `layout` already mirror their Python counterparts. VBridge's outer circuit is that
builder's layout, a Lean term. An executable test checks that Python's `circuit.txt` for V* parses to exactly that term
(its digest is `circuit_sha512`), which is how "both parties pin V* by its digest" meets the statement.

The other two options:

- **The descriptor through the IR codec.** Lean would need the IR codec, the evaluator and the Boolean lowering's
  semantics, none of which exist in Lean. The reviewer would be reading a descriptor of millions of gates.
- **Lean generated from the Python Definitions.** This puts the generator in the trusted base, and its output is
  unreadable.

**Why the restatement keeps the statement reviewable.** The builders need no review for soundness. If one were wrong,
the theorem would fail to prove, or it would hold about the Lean circuit, which is the circuit the outer verifier then
checks. The digest test's only job is completeness: the prover's circuit must be the one the statement names. A wrong V*
costs the developer failed proofs, as `internal/recursive-zk-system-architecture.md` says.

**What a statement reviewer reads:**

- rec-thm's `VBridge` Prop.
- The outer acceptance it assumes. These are existing, reviewed definitions: `LiveAcceptsZKR`, `Partition.wrong`,
  `RegAgree`.
- The verifier of record's acceptance, unchanged: `Flock.verify` / `verifyRep` and `Merkle.opens`.
- F's functions, because these are the auditor's own computations: positions, κ, `eq(α)`, the comb, and the expected
  registered rows. Most of them are the verifier's own functions applied to the right coins.

The decode map (G) needs no review either. rec-thm's composition binds the decoded messages to the proxy's `c_k`.

**What rec-thm's statement needs** (I'll check when it lands):

- The outer hypothesis covers several statements: one per level plus the algebra parts, sharing `rec-acc` and
  `rec-c<i>`. This is the "multi-session outer statement" the architecture lists as missing. #1090's `VBridge` takes one
  `ZkOuter`.
- The conclusion runs the verifier of record itself on the decoded inner session, not a restated `Inner.accepts`.
  - The inner session's rounds hold salted commitments, so `Round.answers` (R2) cannot check a SHA-512 digest of the
    framed bytes.
  - The session can carry each round's framed bytes as retained bytes (`Round.bytes := some b`). R2 then holds by
    construction, and every other check is the verifier's own.

## rec-thm's statement, checked (rec-thm `05298f673`, 00:20Z)

rec-thm states `VBridge` as a `def … : Prop` in `Proofs/Flock/Recursive/Flock.lean`: for every history `(R, ω, t)`,
strategy `τ` and outcome `o`, if `LiveAcceptsZKR` holds, V*'s layer has no wrong unit, and the layer agrees with the
registrant at `o`'s drawn units (`RegAgree`), then `I.accepts (x R ω) ((wmsg layer).zip coins)`. It is deterministic
and one-directional, as recommended. An abstract `Inner` is fine: G proves it at `I :=` C-Flock's verifier of record on
the decoded session, with retained bytes. As stated, it is unprovable for V*, for three reasons:

1. **One circuit.** `ZkOuter` fixes one circuit `c`, one session. V* is one statement per level plus the algebra parts
   (`rec_outer`: "one C-Flock statement per level"; `rec_vstage`: the algebra "holds when every part does"). A C-Flock
   `Circuit` has one `unit` net, and M0 proves one template per statement. No single part's acceptance implies the
   inner verifier accepts: level 0's openings say nothing about the algebra. Fix: a family `zs R ω t : (j : Fin S) →
   ZkOuter … (c j) …` over one registrant record, with `VBridge`'s premises at every `j`, its conclusion read from all
   the layers, and the outer bound the sum over `j`.
2. **`RegAgree` only at drawn units.** `zk_session_regValsR` bounds a disagreeing registered read only at a drawn unit,
   so `VBridge` gets `RegAgree` only there. Counterexample: an undrawn `RecOpen` instance whose layer computes correctly
   (no wrong unit) but reads an expected-node row (`rec-L<l>`) other than the verifier's, the node its forged opening
   climbs to. The outcome accepts, the premises hold, and the inner verifier rejects that query. Fix: premise `RegAgree`
   at every unit, and in the outer theorem count a unit with a disagreeing registered read as wrong. One sampling step
   (`miss 1`) then covers both. Each drawn unit is caught by the bound it already has: `soundR` for a wrong
   computation, `regValsR` for a disagreeing read.
3. **No public inputs.** `ZkOuter` is the `setupH` path (`HmRow.parse`, `HmRow.loadPublic`), and `buildStmt` refuses
   `--public-inputs` there. V*'s level statements carry `coef` in `public-inputs.bin`, which `Stmt.setupHidden` checks
   (`HmOut`/`HmIn`, `HmIn.checkOwn`). Nothing in the premises ties the layer's `coef` wires to the verifier's `coef`,
   and an arbitrary `coef` lets the running sums pass with no algebra checked. This is the #1179 dependency of
   "Dependencies and risks": either `ZkOuter` widens to hidden-output statements with a fact like `RegAgree` for public
   inputs, or V* registers `coef` as a verifier-registered value, at the cost priced there.

None of the three changes A to F. G waits on rec-thm's fix.

## The one decision

**Ruled: one direction (Daniel, Oct 5 6:11 PM PDT, relayed by @top in 1791252706.494879).** VBridge proves "V* accepts ⇒
the verifier of record accepts". Completeness, "exactly when", stays a test. Don't reopen it: the lanes proceed on this.

**VBridge proves one direction: V* accepts ⇒ the verifier of record accepts.** "Exactly when" in the other direction
(the verifier of record accepts ⇒ V* has a satisfying witness) would stay a test: honest V* proofs verify in `check`.
I recommend this, for three reasons:

1. The security theorem uses only the forward direction.
2. The reverse direction needs a completeness theory for every gadget. `Flock.HmNets` has only `Sound` judgements, so
   A, B2, C and E would roughly double.
3. The reverse direction is false outside V*'s shape parameters (LANES, H, `MAX_REGIONS`, the parts split), so it would
   need its own scope anyway.

If Daniel wants "exactly when" proved, the estimate becomes about 7,000 to 12,000 lines. G would then also need a
witness construction.

## Dependencies and risks

- **#1179 (fail-closed).** `ProvedScope.check` refuses `--public-inputs`, and V*'s `coef` and `v` are public inputs.
  - The proved scope must widen to `--zk --public-inputs` (#1192's gap list, "Public inputs") before G can cite one
    soundness theorem for the outer sessions. The soundness lanes own this; it isn't in VBridge.
  - The alternative is to move `coef` to verifier-registered rows. `ZkReg.zk_session_soundHR` already covers those,
    but each registered row costs an hm96 commitment, and `coef` is `2·LANES` field elements per opening. That would
    put about LANES compressions on each opening, against its LANES/8 + 5 + 2H.
- **#1192 (canonical V1).** V*'s rows are `sha512/row/v1` and `hm96-sha512/row/v1`. If canonical V1 is the only proved
  form under `--zk`, V*'s staging moves to v2 rows. That changes D's layout lemmas, but not A, B, C or E.
- **rec-step3** changes `RecOpen`'s leaf and adds the tree tops. Only C2 and D's opening layout wait on it.
- **flock-specs** moves C-Flock's trusted definitions into `Definitions/Flock` and `Specs/Flock`. For VBridge's files
  that means import paths.
- **F is Python today** (`rec_algebra.verifier_rows`, `rec_outer.coefficients`). The outer verifier eventually has to
  compute it in Lean, with F as its definition. That is a verifier change in another lane; VBridge only defines F.

## Checkpoints

- 01:28Z (6:28 PM PDT): C1 `FlockVBridge.sound_climbFrom` builds locally (`VBridge/Climb.lean`, any scheme whose node is
  `SHA-512(l ‖ r)`, so it covers rec-step3's plain SHA-512 tree as well as `hm96Sha512`), pushed on
  `cursor/vbridge-climb-95d4` at `780c2f708`; audit run `r20261006-012634-3f72` on vy-nebius-1 (`--no-replay`). rec-step3's
  `RecOpen_v3` (`d23edf42d`) keeps C1's loop as it is.
- 02:15Z (7:15 PM PDT): C1's audit `r20261006-012634-3f72` PASS (1749 guarantees, no replay); its record is committed at
  `50bf1c080`, and `internal/proofs/vbridge-climb-pr.md` is filled in. For the second piece I took C2's `out` half, not
  the F stub, because vbridge-algebra's `Structure` already restates `run` with its coins. `FlockVBridge.sound_climbRow`
  (`VBridge/Open.lean`, `RecOpen_v3._climb` from the row's SHA-512 leaf) is on `cursor/vbridge-open-95d4` at
  `403a232c8`, with C1 merged in; audit run `r20261006-021256-fec1` (`--no-replay`). C2's `acc_out` waits on B2.
- 02:58Z (7:58 PM PDT): C2's audit `r20261006-021256-fec1` PASS (1750 guarantees, no replay); its record is committed at
  `2434949b9`, and `internal/proofs/vbridge-open-pr.md` is filled in. Both pieces are done to their PR files. Next: C2's
  `acc_out` once B2's `residual_forms` statement exists; D once #1179 and #1192 land; F and G after rec-thm.
