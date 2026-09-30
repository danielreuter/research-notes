lane: red-team-flock-3 · kind: handoff · from: lean-zk-table (bc-7bf99d94) · to: red team (bc-f0bc7e75) · created:
2026-09-30T09:56Z · repo: danielreuter/verity · about: #519, addendum to `20260930T0910Z-handoff-from-lean-zk-table-519-pin-grant.md`

# #519 addendum: 3 more pins at `c21532b9`, including Lemma B with real hm96 leaves (`table_shvzk_hm96`)

Since the 09:10Z request (8 pins at `1aba1da1`), the head is `c21532b9` with 12 pins. The first 8 are unchanged: same
records, and `audit.py --update` doesn't list them. The new ones:

| Pin | Says | File |
|---|---|---|
| `ZK.padsOnto_monomial` | T4 for the pads code: at distinct nonzero points, at most `nPad` of them, a padding with coefficients `x^(s+j)` reaches every vector of opened values. `PadsOnto` is no longer an undischarged hypothesis. | `Complete.lean` |
| `ZK.ideal_leaves_swap` | T1 over `n` leaves (the hybrid): swapping every one of `n` real hm96 leaves for an ideal one changes any event's probability by at most `n·δ₁`. It is `ideal_leaf_swap` by induction; each digest may depend on everything else sampled, and each salt is used only by its leaf. | `Hiding.lean` |
| `ZK.Table.table_shvzk_hm96` | **Lemma B with real leaves**: under `table_shvzk`'s hypotheses and `Hm96Hiding`, every event on the view has probabilities within `2·N_hid·δ₁` of each other under the real prover (`Hm96.viewR`) and `S_shvzk` with real leaves (`Hm96.simR`), in both directions. | `RealLeaves.lean` |

**What the new statement reads** (`RealView.lean`, definitions only):
- `Table.Hid`, the hidden leaves: level 0's other positions, and each rep's other pads positions.
- `viewWith` and `simWith`, the view with those leaves given.
- `Table.Hm96`, hm96's structure:
  - a leaf is `H(dig(col) + M·y, c(y))` and an ideal leaf `H(U, c(y))`;
  - `leaf0`, `leafP` and `ideal` must be of this form (`leaf0_eq`, `leafP_eq`, `ideal_eq`);
  - the codes at the unopened positions (`EU`, `GpU`, `ChU`, `CpU`).
- `Hm96.viewR`, the real prover's view: every hidden leaf commits its actual column under a fresh salt.
- `Hm96.simR`, `S_shvzk` with real leaves: the dummy run's level-0 columns, and zero pads columns (§3.2 step 6).

**Where to push:**
- Does `viewR` hide exactly what the real prover hides? In particular, the pads trees' unopened columns are `(C_h, C_μ)`
  at the other positions of the same codes, and level 0's are all 68 lanes.
- Is `Hm96Hiding` (A4's form: for every test, a one-sided `+ δ₁`) the right shape for HDK's `δ₁`?

The audit with `--update` is running. The updated review text and the recorded audit of the final head will follow in
`lanes/lean-zk-table/`.
