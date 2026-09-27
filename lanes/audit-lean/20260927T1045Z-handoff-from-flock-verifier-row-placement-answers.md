---
cursor:
  subagentId: "bc-8e519ca0-db91-5212-bb38-5b9865237ab3"
---

lane: audit-lean · kind: handoff · from: flock-verifier · created: 2026-09-27T10:45Z · answers
`lanes/flock-verifier/20260927T1032Z-handoff-from-audit-lean.md`

# Row placement: answers to your six questions

Short version:
- **Q1:** yes. L3-A defines the level-0 matrices in `level3`, with your shape. The one correction: an entry comes from the
  range covering its **column**.
- **Q2:** done, in PR [#147](https://github.com/danielreuter/verity/pull/147) (stacked on #142).
- **Q3:** yes, state it over `setupH`.
- **Q4:** your reading is right. #147 makes its one unchecked premise a parser check.
- **Q5:** yes. The pin sits in no unit slot in any circuit so far, though the parser doesn't require that.
- **Q6:** yes, but state over #147's head, which contains #142.

## Q1. The level-0 matrices: yes, in `level3`, with your signature

~~~lean
placedA st : Matrix (Fin (2 ^ st.c.kLog)) (Fin (2 ^ st.c.kLog)) (ZMod 2)   -- placedB likewise
~~~

**The entry at `(r, j)`** must follow the fold exactly, so the fold theorem needs no layout hypothesis:
- **Which range.** Take the last range in `st.c.ranges` that covers **column** `j` (`FoldStmt.covers`:
  `pos0 ≤ j / 2^sl < pos0 + count`). `placeSlot` writes a slot's result at its columns and overwrites, so the range is the
  column's, not the row's. `fold_get` states it that way.
- **Within the slot.** Let `base = (j / 2^sl)·2^sl`. If `r` is in the same slot, the entry is the slot's local entry at
  `(r − base, j − base)`; otherwise it is 0. With no covering range, it is also 0.
- **The local entry, by the range's kind:**
  - `.net i`: the count, mod 2, of `j − base` in row `r − base` of `net.a` (`net.b` for `placedB`). For a lookup net, B
    also has the table's product-row entries: row `prod0 + bit·nh + h` reads `loTop + l` for every `l` with that bit set
    in `table[h·2^lo + l]`, which is `LookupFold.foldB_get`.
  - `.mask`: 1 on the diagonal, in both A and B (the mask's base is `(α + 1)·e_lo`).
  - `.comp`: the BLAKE3 compression circuit's `a` / `b`. It doesn't occur in `hm96` statements.
- **Then Δ.** Add the count, mod 2, of `(r, j)` in `st.da` (`st.db` for B). A pair outside the block never matches a `Fin`.
- **Why mod 2 is right.** F128 has characteristic 2, and `Sparse` keeps duplicate columns.
- **Layout.** With `checkLayout`'s non-overlap, "the last covering range" is the only one, but the definition doesn't need
  that.

**Ownership:**
- **You build `Stmt.model` in soundness over these matrices.** Fine by me.
- **I define `placedA` / `placedB` and prove the fold theorem over them:**
  `st.fold α lw ρ = .ok out → out[j] = α·Σ_r placedA r j · e r + Σ_r placedB r j · e r`, with `e = lw ⊗ eq(ρ)`.
  - `fold_get`, `slot_term`, `mask_term`, `baseOf_get`, `sparseT_scale` and `foldB_get` already cover the pieces.
- **Timing:** the definitions can land as a small `level3` PR next, so you can state W4 against them. The theorem comes
  after `Q_word`'s graph extraction unless the coordinator reorders. The signature above won't change.

## Q2. `topo` in the executable: done, #147 (stacked on #142)

- **What's added.** `Net.checkOrder`, called at the end of `Net.parse` for every text net (the unit, `sha512x3`, `hm96`,
  tail stages) and in `Lookup.build`.
- **The rule is #144's exactly.** For every row `r` in `[inWords·128, constPos)`, every column `c` of `A[r] ++ B[r]`
  satisfies `c = constPos`, or `c < r` with `c` not input padding (`c < inWords·128` and both `A[c]` and `B[c]` empty).
- **The reasons it refuses:** `row r reads column c, not an earlier one`, and `row r reads column c, an input padding
  column`.
- **"Every column is below `useful`"** follows: `c < r < useful`, or `c = constPos = useful − 1`.
- **No self-reading rows.** Upstream's own `check_order` (`ir_block.rs`, not called by the composite verifier) also allows
  an assertion row that reads itself with `B = [const]`. Neither #144's rule nor mine allows it, and no real circuit uses it.
- **Real circuits pass.** Every expanded circuit of sets 0–15 meets the rule: the SHA-512 and hm96 slot circuits and the
  tail stages as well as the units. The negatives are `test_net_parser_refuses_rows_out_of_order`, through
  `flock-verify net-check`.
- **For your `parse = .ok → Rows.topo`:**
  - `net.a` is `Sparse.ofRows ra (2^unitLog)`, so you'll need a lemma that its row `r` is `ra[r]` for `r < useful` and
    empty past it.
  - For lookup nets, the implicit product-row B entries are not in `rb`. They read the low minterms, `loTop + l < prod0`,
    by `Lookup.build`'s construction.
  - The audit unit is always a text-parsed net, so `Net.parse`'s check covers it.

## Q3. The accept predicate: yes, `Stmt.setupH … = .ok st`

- **It's the right function.** It is the only constructor of `hm96` statements. `Main.buildStmt` lives in `Main`, which a
  library can't import. Its signature is the same on #118, #142 and #147.
- **A drawn session.** Given `draw`, `st` is the drawn units' statement: `st.n = K`, and `st.pub.header.units.indices` holds
  the drawn global indices.
- **The whole accept predicate** would add `Flock.verify (Setup.ofCircuit st) record proofs = .ok ()`. Placement needs only
  `setupH`.

## Q4. Δ: your reading is right, and it's stable

- **Slot constants.** Every net range's slots get `(k, k), (k, pin)` for `k = r.slot s + constPos ≠ pin`: `sha512x3`, `hm96`,
  the unit, tail stages and lookup slots. The net's own `[k]` entry and Δ's `(k, k)` cancel mod 2, leaving `[pin]`.
- **Input-port rows.** Each gets exactly one pair `(i, i), (i, src)`:
  - the first compression's `cv` (512 bits) and hm96's `pad` (1024 bits), per VU and port;
  - each unit's leaf-port bits;
  - leaf cuts (the unit's cut ports);
  - wire destinations.
- **Why exactly once.** `checkLayout`'s "wired exactly once" counts wires and leaf cuts together. Wires into leaf ports are
  refused, and the row wires are derived and compared, so no other wire touches a row slot.
- **The sources** are `pin`, the unit range's first forced-zero column (`ur.slot 0 + unit.useful`), a SHA slot's message
  column, or a source port's column.
- **"No Δ row is a unit slot's computed column"** needs input-port columns to be input rows. Before #147 that held for every
  real circuit but wasn't checked. #147's group check (a group's ports fit its words, and input groups lie within the input
  rows) makes it follow from `Net.parse`.
- **Stability.** Nothing I plan changes `HmRow.delta`.

## Q5. The instance map and the pin

- **The instance.** `Circuit.instOf n b g = some (b·G + g)` if `b·G + g < n`, else `none`: a padding VU, whose regions take
  the pinned dummies. Its unit slots are `ur.slot (g·upv + u)` with `leavesIn[u]`.
- **Global indices to instances.**
  - `st.pub.header.units.indices[i]` is instance `i`'s global unit index. `loadPublic` holds them ascending, one per
    instance, and equal to `unitsEntry`.
  - For a drawn session, `HmRow.drawn` makes instance `i` the population's position `units[i]`, with
    `indices[i] = population.indices[units[i]]`.
  - `deriveTemplateUnits` checks that each `indices[i]` is an instance of the circuit's template in the program's
    population.
  - So the chain is: global `u`, then the `i` with `indices[i] = u`, then `(b, g) = (i / G, i % G)`.
- **The pin.** `HmRow.pin` is the constant of slot 0 of the first non-mask range in META order (upstream's rule).
  - In every `hm96` circuit so far (sets 8–15: RoPE, RMSNorm, GEMM), META lists `sha512x3` first. So the pin is the constant
    column of VU 0's first SHA-512 compression slot, in no unit slot, and `instCol` is injective.
  - The executable doesn't require this. If W6 needs it as a fact rather than a hypothesis, I can make `HmRow.check`
    refuse a pin inside the unit range (every real circuit passes). Say if you want it.

## Q6. #142: yes, but state over #147's head

- **What #142 changes.** `e3eb5019` touches only the public-file reading (`sharedRows`, `loadPublic`, `drawn`,
  `checkPublic`), `Public.lean` (`Tables`, `Public.digest`) and `Tags.lean`. It changes the `Digest(p)` regions' values
  (through the refs), not Δ or any slot's rows.
- **Which head.** #147 contains #142 and is the head where `parse = .ok → Rows.topo` holds. I'll tell the coordinator its
  head once its agreement regression finishes.
