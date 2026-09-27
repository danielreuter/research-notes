---
id: 20260926T2300Z-report-private-recursion
campaign: circuit-privacy
lane: private-recursion
kind: report
status: final
repo: danielreuter/verity
origin: cursor/private-recursion-bad3
branch: cursor/private-recursion-bad3
---

CHECKPOINT 85c94e5c (00:35Z) [final] first milestone: RoPE fd02e847 session verified inside hand-built V[B] (4.52 G ANDs; fold 3.59 G = 22.7k/nonzero), 28/28 agree with Lean, 14/14 negatives rejected, swap identical; art:da941437; PR #97; $0
CHECKPOINT 128e7f2c (23:59Z) [open] V[B] (4.52 G ANDs, fold 3.59 G) accepts honest RoPE art:bd9f7efb; agrees with recorded Lean/upstream verdicts on 28/28 (D-rs, D-fc refused at decode); own negatives running; draft PR #97
CHECKPOINT 461c99e2 (23:34Z) [open] building V[B] as a program of gadget tables; gadgets pinned (SHA-256 22,573 / SHA-512 57,947 / GF128 2,187 ANDs), hm96-sha512 matches PR #93 vectors, native lincheck with my fold passes on art:bd9f7efb honest; next: V[B] builder + coin tables + witness
CHECKPOINT 748c3cd6 (23:08Z) [open] started: read spec I.1-I.10, PR #83 statement, PR #85 PROTOCOL.md; RoPE unit has 158k nonzeros (spec bound 2^16); building V[B] on recorded fd02e847 sessions (art:bd9f7efb)
# private-recursion: the smallest private-circuit prototype (inner Flock session verified inside a hand-built V[B])

Spec: Project store `docs/circuit-privacy.md` Part I (I.2, I.3, I.9). Agent bc-be25385c-8dda-5970-9cf6-7c0ce338bad3.

## Outcome (first milestone)

An inner Flock session is verified inside a hand-built V[B], and every negative is rejected.
- **The session:** PR #83's `verity/flock-circuit`, RoPE (`rope-head/neox-bf16/pair`), 8 instances, m = 23, fast100 × 2 reps,
  recorded at `fd02e847` (`art:bd9f7efb` honest, stage `art:d9837120`, compression circuit `art:04259cdd`).
- **V[B]:** 4.52 G ANDs in 1,963 batched gadget operations, digest `a901d8ca…`. It depends only on the public frame B.
- **Differential:** it agrees with the recorded Lean and upstream verdicts (`art:78ef0a6e`) on all 28 RoPE sessions.
- **Negatives:** all 14 of my own are rejected, each for the intended reason.
- **Gate level:** sampled instances of every SHA and field op agree with their Boolean circuits.
- **Swap:** two different circuits under the same B give byte-identical V[B]s and public artifact shapes.
- **Spend:** no pod, no GPU, $0. Code on PR #97, branch `cursor/private-recursion-bad3`, in new modules only
  (`backends/flock/python/verity_flock/recursion/`, tests `backends/flock/tests/test_recursion.py`).

**Evidence:** `art:da941437`, preserved. It holds the differential, the negatives, the gate-level check, the swap test,
the costs and the scripts, at commit `85c94e5c`, with refs to the session, stage, compression circuit and recorded
verdicts. A copy is in `lanes/private-recursion/evidence/`.

## What V[B] checks (spec I.3, relation 1–5)

1. `HM(Enc(C); r_c) = c`, with `hm96-sha512/v1` leaves (`recursion/hm.py`). They match PR #93's vectors byte for byte.
   `Enc(C)` is 664 KB of fixed-size bit fields.
2. **Toy Φ.**
   - The unit's listed entries are in circuit form: each reads an earlier column or the constant.
   - The constant row follows the input rows, and the unit leaves a free row.
   - Padding entries are canonical.
   - `leaves_out` is a permutation, checked by routing it into order: each output leaf is bound to exactly one unit output.
   - "C fits B" holds structurally: the fields are fixed-size.
   - A 17-bit output cannot be expressed: B fixes 16-bit leaves, as PR #83's format does.
3. `HM(m_j; r_j) = c_j` for 175 commitments: root_B, then the 87 rounds of each rep, 117.5 KB of framed bytes.
4. **The inner verifier** (PROTOCOL.md §9–§14):
   - the round framing;
   - zerocheck;
   - lincheck with the matrix fold computed from the private C;
   - ring switching and the batched target T;
   - Ligerito's final check and its Merkle openings at all three levels;
   - R1: both caps equal the committed root_B.
5. **Data binding.** The row digests and outputs the region claims read hash to the frame-v3 roots D. V[B] hashes the
   whole trees, since positions are public at this size.

**How it is built.**
- Every inner check is an affine form in the messages. Its coefficients depend only on the coins (`recursion/coins.py`,
  ported from the Lean verifier, with the sumchecks' and Ligerito's state machines evaluated on unit vectors). These
  coefficient vectors are public inputs: the spec's "coin tables" generalized to whole affine maps.
- Private × private products remain in only two places: the zerocheck's final `a·b`, and the fold.
- The fold looks up the coin-table value at each entry's private row and column. Two Beneš networks with prover-set
  switches check the lookups (`recursion/memcheck.py`): each tag-1 output must repeat its predecessor, and the first must
  be a table row.
- V[B] is a program of batched ops (`recursion/program.py`). Each costly op is one table of one gadget:
  - SHA-256 and SHA-512 compressions at 22,573 and 57,947 ANDs, the Bristol Fashion counts;
  - a GF(2^128) Karatsuba multiplier at 2,187 ANDs;
  - Beneš switches at 1 AND per bit.
- The builder sees only the frame, so the program digest is a function of B.

## Staging choices (all reversible; spec I.9 allows the first two)

- **V[B] is hand-built**, not generated from Lean (R2). It is written as coefficient forms rather than as the Lean
  functions' control flow. The differential test is what ties it to the Lean verifier.
- **No outer proof yet**, and so no zero knowledge (see "Blocker for the outer proof").
- **Hidden messages are applied after the fact** to recorded sessions (`recursion/witness.py`). Each `c_j` commits to what
  the record says was sent: the retained bytes, else the proof's bytes if they hash to the recorded digest, else the
  digest itself. The live mode needs flock-live changes: handoff `note:20260927T0020Z-handoff-from-private-recursion` to
  flock-netlist.
- **The private/public split:**
  - **Private (C):** the unit slot type's matrices (157,841 entries) and its row count, `leaves_in`, `leaves_out`, and the
    padding outputs.
  - **Public (B):** the block shape, the protocol slots (the keyed-BLAKE3 row compressions, the mask), their glue, the unit
    grid (64 slots of 2^13), the unit's port rows, the region layout, and the data trees' shape.
- **Proof trees are SHA-256**, as in the recorded sessions. SHA-512 is a parameter (`Bounds.hash_len`), and no SHA-512
  session exists yet. The inner protocol is fast100 × 2 reps, not the single-run profile of I.2.
- **The round-0 statement digest is left unconstrained.** It is a hash of the circuit file, so in the private track c binds
  the statement instead. A live private-track statement should absorb c there.

## Differential (V[B] vs the recorded Lean and upstream verdicts, art:78ef0a6e)

| sessions | Lean | upstream | V[B] |
|---|---|---|---|
| honest, retained, lig-claim-nonce, lig-query-nonce | A | A | A |
| r-break | R (S13) | R | R (S18/R1: caps differ) |
| 19 re-digested mutants (zc, lc, rs, lig, rep1-*) | R | R | R, at the check each mutant breaks |
| zc-final-c | R (CEvalMismatch) | R | R at witness decoding: D-fc |
| rs-nonce | R (grinding ≠ 0) | R | R at witness decoding: D-rs |
| retained-edited | R (R2) | R | R (R2: a message does not open) |
| retained-not-digest | R (S12) | A (declared D4 in PR #85) | R (R2) |

28 of 28 agree with Lean. **D-fc and D-rs** are the two proof fields that are neither messages nor query answers:
`final_c_eval`, a function of round1_c at z, and the ring switch's grinding nonce, fixed at 0. V[B] has no such inputs,
so the witness decoder refuses a proof in which they are not what the protocol fixes.

## Own negatives (spec I.9's list)

| negative | V[B]'s failing checks |
|---|---|
| Enc(C) one entry off; c commits to C | C does not open c; lincheck |
| a different C registered (C' opens c); the session is C's | lincheck only: the inner transcript does not accept for another C |
| gptj-pairing C (other leaf maps) | lincheck |
| an entry reading a later column, added twice so the fold is unchanged | Φ circuit form only |
| a leaf bound to two outputs | Φ permutation; the region claim |
| the constant row is an input row | Φ (row, circuit form); lincheck |
| a non-canonical padding entry (witness edit) | C does not open c; Φ canonical; lookup |
| a message byte flipped, including a free field | R2: the message does not open its commitment |
| two c_j swapped; a wrong salt; a wrong c | R2 / C does not open c |
| an output bit flipped in the witness | the outputs do not hash to D; lookup |
| a false statement (the output flipped, D recomputed) | ring-switch claim mismatch (the Out region) |

Not covered here, because they are offline record checks rather than parts of V[B]: a coin not derived from the seed, a
commitment recorded after its coin, and a data root registered late.

## Costs, measured against spec I.7 (both reps, m = 23)

| component | spec I.7 | measured | why |
|---|---|---|---|
| matrix fold | ~5,000 ANDs/nonzero; RoPE ~0.1 G | **3.585 G** (22.7k ANDs per nonzero, 11.4k per rep) | 157,841 private nonzeros, not ~20k; two Beneš lookups of 2^18 × 271 bits (1.31 G each), per-entry products (0.86 G), leaf and constant terms (0.10 G) |
| Ligerito openings | 0.5–1.7 G per table and rep (SHA-512) | 0.342 G (SHA-256, 3 levels, 395 queries per rep) | smaller schedule at m = 23 |
| field arithmetic | 0.1–0.5 G | 0.10 G | affine forms: about 44k products per rep |
| round commitments | 1–10 M | **100 M** | 56.7 KB of framed bytes per rep; the 16 ring-switch vectors alone are 32 KB |
| binding C | 453 ANDs/byte | 301 M for 664 KB | as estimated |
| IO binding | ~2.3 M per range | 71 M, plus 10 M for region values | whole frame-v3 trees recomputed (512 output leaves) |
| Φ | linear, plus a sort | 16 M | |
| **total outer** | **1–2.5 G** | **4.52 G** | |
| outer ÷ inner | 1–2.5× | about 540× at 8 heads; about 5× estimated at the spec's 2^10 heads | V[B] is nearly fixed per table |

Not measured at this milestone: outer proving time and Lean verification time, since no outer proof exists yet.

- **V[B]'s inputs:** 16.2 Mbit public (dominated by the coin tables) and 122.5 Mbit of witness inputs.
- **Native evaluation:** 7 s. The coin tables take 19 s, on this VM's 4 CPUs.

## Findings that change the spec

1. **B's nonzero bound.** RoPE's pair unit has 157,841 private nonzeros, about 25 per row, against B's ≤ 2^16. The
   prototype uses 2^16 A-entries plus 2^17 B-entries.
2. **The fold dominates the outer proof.** It costs 3.6 G, not 0.1 G, and the outer is 4.5 G, not 1–2.5 G. Holography,
   public slot types or sparser lowerings matter already for RoPE, not only "for templates with millions of private
   nonzeros".
   - Cheaper exact variants exist:
     - a merge network for the row side, which is sorted: about −0.65 G;
     - per-row prefix sums instead of per-entry products: about −0.7 G;
     - sparser B rows in the lowering, which cut the cost linearly.
   - The per-nonzero cost is in the spec's upper range (11.4k per rep against 2,500–10,000). Two lookups per nonzero plus a
     product explain it.
3. **Round commitments cost 100 M, not 1–10 M.** The ring switch sends 128 elements per claim.
4. **Field arithmetic is at the spec's low end** (0.10 G). Nearly every inner check is linear in the messages with
   coin-only coefficients, so V[B]'s public inputs should be those coefficient vectors.
5. **The outer proof needs cross-table private glue.** V[B] is a session of gadget tables joined by private ports.
   PR #83's statement keeps every copy constraint inside one block, and a 4.5 G-AND verifier cannot fit in one
   ≤ 2^26-bit block. Flock's region-equality and shift glue, planned in scoping M0 but not built, is the dependency.

## Scope ruling (Daniel, 2026-09-27 00:14Z)

Serving-time side channels (inspectors, timing, power) are out of scope. Circuit privacy covers only what proofs and
commitments reveal. Timing padding stays inside the proof protocol: the round schedule is fixed by B, which V[B] already
has (175 commitments of 64 bytes for every C under these bounds). Nothing here designs for oblivious serving.

## Next

- **The outer proof:** a glued multi-table Flock statement for V[B] (needs 5 above), then M1/M2 masking (R3).
- **The live hidden-message mode and a SHA-512 session:** flock-netlist, handoff above.
- **A second template's real inner session** under the same B, for the full swap test (proof lengths and rounds).
- **Generate V[B] from the Lean verifier (R2).**
- **Fold optimizations** (finding 2).

## FINAL

~~~text
tip: cursor/private-recursion-bad3 @ 85c94e5c (base main@748c3cd6)        merge-with: none
known-failures: none    pod: none created; $0
artifacts: art:da941437 (inputs used: art:bd9f7efb art:d9837120 art:04259cdd art:78ef0a6e)
~~~

The first milestone of the private-circuit prototype is reached: an inner session verified inside V[B], with the
negatives rejected. PR #97 is a draft. Handoff sent: `note:20260927T0020Z-handoff-from-private-recursion` to flock-netlist
(the live hidden-message mode and a SHA-512 session). Handoffs received: none. The lane stops here, as its brief asks;
resuming means the outer proof and the items under "Next".

## Desk costing, 2026-09-27 01:30Z: the wiring evaluation inside V[B] ($0, no code)

Written as Project store `docs/circuit-privacy.md` I.11. Cost model: `evidence/scripts/costmodel.py`, which reproduces the
prototype's measured Ligerito and fold costs. All figures cover both reps.

| option | V[B] cost |
|---|---|
| (a) in-circuit fold, at $S$ ($Z = 2^{18}$) | 2.6–3.5 G per sampled wiring, best variant, binding included; linear in min(k, n): 112 G at k = 32, 3.6 T at k = 1024 |
| (b) holography: c commits to Enc(C)'s bit columns | 0.8–2.2 G, nearly flat in k: one sumcheck of degree 2 log R + 2, then one salted Ligerito opening of c inside V[B] |

SPARK would cost 2–4.6 G and needs per-run O(Z) commitments. Keeping the outer verifier small needs V[B] laid out as
repeated gadget tables with structured glue, which comes to a few million field operations per proof.

Recommendation: (b), moved into R3/R4, with the glued multi-table outer statement first.
