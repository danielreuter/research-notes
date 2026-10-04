---
id: 20261004T2202Z-report-relay-lean-submissions-sponge-dense-notes
campaign: pous
lane: accounting
kind: report
status: closed
repo: danielreuter/verity
origin: old-accounting (bc-b729c175), relayed for @top's migration (the 44 store:pous/ files the PoUW and PoUS registries cite) from store:pous/lean/submissions/sponge-dense/NOTES.md
---

> Relayed verbatim from the Cursor store by old-accounting: `store:pous/lean/submissions/sponge-dense/NOTES.md`, sha256 `e969e30c9668c99472541a44549478cf5cbf3fb06960bf0ca3d5820f159fe943`, unchanged since it was written before the 30 Sep snapshot, so it is also in `art:8bd64630…42e9` at that path. Only the store's `cursor:` front matter is replaced. Relative and `/cursor/stores/…` links point into that store.

# The dense scheme over the key chain: model, where the sponge proof broke, and the overwrite chain

Status, 27 Sep 17:15Z. Pilot for fix (a) of `docs/p3-cryptanalysis.md` ("Narrow-state H"). **The chosen `H` is now
the overwrite chain of `docs/p3-instantiation.md` §1** (section 6). The sponge and the feed-forward modes remain as
documented counterexamples (sections 3 and 5).

- **Model swapped** (`SpongeModel.lean` §9–10).
  - The chain is `(r_j, h_j) = Π₂(B_j ‖ h_{j−1})`, on an ideal `Π₂` of width `2m + 512`. The `m`-bit `r_j` is
    dropped, and the key is `r` of the pad call.
  - The dense scheme over it is `chainDense`, with target `ChainDenseMeets` (`D` and `Q` in `Π₂^{±1}` calls).
  - The P3 model over it is `p3ChainModel` (a tweakable `P`, and `Π₂`), with labels `c1c`, `c2c`, `topLabelC`.
- **The search confirms the designer** (`state_game_chain.py`).
  - No item smaller than two labels yields two, on dense rows (`B ≤ 16`, `D ≤ 5`) or band rows (`k = 4`, `B = 14`,
    `D ≤ 8`; `k = 6`, `B = 18`, `D ≤ 10`).
  - The only single item worth two labels is a whole call output, `(r_j, h_j)` at 2.06 labels, which is dominated.
- **The pebbling side is proved.**
  - `chainHard_of_pebblingHard`: the chain game is no stronger than B5's greedy pebbling at the same price. In it, a
    held chaining value costs `1 + 512/m` and yields one key, and a held dropped `r` costs 1.
  - With `complete_hard`, `chainDense_hard` makes the dense chain game `(B − D − 1, D, B)`-hard. That is exactly the
    hardness the random-oracle certificate uses.
- **B5's step carries over.** The designer's claim is proved at the game level (`chain_invariant`): a label is known
  only by holding it, from its own row's pad call, or by inverting a call whose dropped `r` is held. That `r` exists
  only as the output of the call that absorbs the label.
  - Freshness is B5's again. A forward query shows its parent label and chaining value in separate clear slots, and
    an inverse query shows `r` in the clear. No label is XOR-masked by a state that depends on newer labels.
  - The one remaining lemma is `ChainExPostFacto` (stated): B5 for a permutation with two-part answers.
- **`k` at the pinned `D = 64`, `Q = 2^20`:**
  - **111** from `ChainExPostFacto` as stated, charging two positions and a 16-bit row name per fresh item;
  - **106** if the row name can be avoided;
  - 107 as pinned under the random oracle;
  - at `D ≈ 2000` `Π₂`-calls, 401.
- **Documented counterexamples, each proved in Lean for every `Π`:**

| Counterexample | Stored value | What it yields | Theorem |
|---|---|---|---|
| (1) invertible sponge | a state | two labels | `dense_two_labels_from_one_state` |
| (2) state feed-forward | a state | its own block, `π⁻¹(s_q ⊕ s_{q−1}) ⊕ s_{q−1}` | `stateFF_two_labels_from_one_state` |
| (3) input feed-forward (Miyaguchi–Preneel) | the call input `x` | two labels; 1.06 labels worth two on band rows | `inputFF_two_labels_from_one_input` |

- **Block feed-forward, `s_j = π(x_j) ⊕ (m_j ‖ 0)`, is no alternative.** It passes on dense rows, but breaks on band
  rows (`k = 4` at `D = 5`, `k = 6` at `D = 7`).
  - The stored input of a row's second call gives its block from `x ⊕ s_1`, and starts the tail with `π(x)` in the
    same round.
  - That yields both labels at 1.06, a fourth counterexample, found by search only.

| File | Content |
|---|---|
| `SpongeModel.lean` | the definitions and targets, no proofs (for review) |
| `SpongeDense.lean` | `SpongeModel.lean` byte for byte, then the proofs; standalone (imports `Pous` and Mathlib) |
| `AXIOMS.txt` | `#print axioms`, kernel replays, hashes |
| `state_game_chain.py` | the pair test of `docs/p3-instantiation.md` for the sponge, MP, block feed-forward and the overwrite chain, on dense and band rows (engine of `state_game_ff.py`, with call slots) |
| `state_game_ff.py` | the state game for the four XOR chaining modes, as linear knowledge with call inputs and outputs |
| `state_game.py`, `state_game_fast.py` | the first searches (invertible sponge only). They make `π⁻¹` wait for the block, one round slow; kept as documented |
| `certificate.py` | the `k` each scenario certifies |

No `axiom`, no `sorry`, no `native_decide`. No trusted file was edited (`TRUSTED.sha256` verifies). Everything proved
is on `[propext, Classical.choice, Quot.sound]` and passes `leanchecker` (`AXIOMS.txt`).

## 1. The model (`SpongeModel.lean`, review points in its header)

- **`idealPerm b`.** `Ω = Equiv.Perm (Bits b)`, uniform. `Qry = Bits b ⊕ Bits b`: `.inl x ↦ Π x`, `.inr y ↦ Π⁻¹ y`.
  The trusted `Prog`, `Bounded`, `depth` and `work` are reused, so `D` counts rounds of parallel `Π^{±1}` calls and
  `Q` counts calls in both directions.
- **Sponge.**
  - A state is `Bits (r + c)`: rate first, capacity last.
  - `iv dom = 0^r ‖ dom`: the domain (256-bit salt, then the index in binary) is the whole capacity, so it costs no
    call.
  - `step Π s blk = Π(s ⊕ (blk ‖ 0^c))`, and `absorb` folds `step` over the blocks.
  - `key` is the rate part after the last call.
  - `padBlk` is pad10*1 for a whole number of blocks (`10…01`).
  - `unstep` and `unabsorb` are the inverse direction.
- **Dense scheme** `spongeDense B ℓ c dom`.
  - `C_i = key_Π(IV(dom i); C_{i−1}, …, C_0, pad) ⊕ W_i`, so block `i` is `i + 1` calls.
  - No `pp`, no coins, rate 1. The decoder uses forward queries only.
  - The pad call is what makes `C_0` depend on `Π`: block 0 has no parents.
- **Target.** `SpongeDenseMeets D Q k := ∀ salt, Meets (spongeDense 2^16 8192 512 (dom salt)) .sequential D Q k 2^-128`.
  `SpongeDenseMeetsPinned` is `D = 64`, `Q = 2^20`, `k = 107`. `D` and `Q` are now `Π`-calls, not `H`-calls.
- **P3 model** `p3SpongeModel n wc`.
  - `Ω = (Tweak → Perm Lab) × Perm (Bits (m + 512))`, with `Tweak = (tag, layer, node)`.
  - Queries: `Π`, `Π⁻¹`, `P_T`, `P_T⁻¹`.
  - Labels `c1s` and `c2s` mirror `PousColumnAware.c1'` and `c2'`, with `keyP3` (the sponge over the parents' labels,
    newest-first, then pad) in place of `H`.
- **Chaining modes** (`Chain`, `stepN`, `absorbN`, `absorbProgN`, `labelN`). `.sponge`, `.stateFF`, `.inputFF`,
  `.blockFF` form the next state as `y`, `y ⊕ s`, `y ⊕ x`, `y ⊕ (m ‖ 0)`. `spongeDense` is the `.sponge` mode;
  `labelN ch` gives the dense labels in any mode.
- **The overwrite chain** (§9, the chosen `H`). It uses `ovR`, `ovH`, `ovStep`, `ovAbsorb`, `ovKey` and `ovProg`.
  The dense scheme over it is `labelOv` and `chainDense`, with target `ChainDenseMeets`; P3 over it is `p3ChainModel`
  with `keyP3c`, `c1c`, `c2c` and `topLabelC`. `Π₂ = idealPerm (m + (m + c))`, the input is `B ‖ h` via
  `Fin.append`, and the output splits as `r ‖ h`.
- **Salt.** `W` is fixed before `Π` (choice 1), so a constant salt loses nothing in the model, and the target
  quantifies over all salts. A deployment draws the salt after the commitment to `W` (§2c).

## 2. Round accounting (proved, reusable for P3)

| Fact | Lean | Cost |
|---|---|---|
| a chain of `k` blocks, honestly | `depth_absorbProg`, `work_absorbProg` | exactly `k` rounds and `k` queries |
| a chain run backwards | `depth_unabsorbProg` | `k` rounds |
| dense block `i` from its parents | `depth_blockKey` | `i + 1` rounds |
| sequential and parallel composition | `Prog.depth_bind`, `Prog.depth_par`, `Prog.work_par` | sum, max, sum |
| chain clock: a block arriving at round `b` with `p` blocks after it | `le_chainTime_of_mem` | end `≥ b + 1 + p` |
| P3 level, oldest parent last | `p3_level_oldest_last` | 3 calls: `Π(c_{v−12})`, `Π(pad)`, `P` |
| P3 level, newest parent last | `p3_level_newest_last` | 14 calls (12 absorptions, pad, `P`) |
| any P3 level, from its last-arriving parent | `p3_level_ge_three` | at least 3 |
| levels in `D` rounds when a level costs `cost` | `le_levels`, `levels_two`, `levels_three` | `levels D cost = ⌊(D − 1)/cost⌋ + 1` |

- `levels D 2 = ⌊(D + 1)/2⌋` is today's random-oracle P3 game, and `levels D 3` is P3 over the sponge.
- `le_levels` is the conversion itself: if `d` levels each finish at least `cost` rounds after the previous one, and
  the first at round `≥ 1`, then `d ≤ levels D cost`.
- A weighted certificate would charge the edge from the parent absorbed at call `g` as `15 − g` calls, straight from
  `le_chainTime_of_mem`.
- For the dense scheme, the edge `C_j → C_i` costs `j + 2` calls. The row itself costs `i + 1`.

## 3. Where the random-oracle proof breaks

The pinned proof (`lean/submissions/dense/DenseMeets.lean`) is: `complete_hard` (pebbling) + B5 (ex post facto) →
`TimedINC` → `Theorem1iiSeq` → certificate. With `H` := the sponge:

1. **Correctness and rate: transfer.** `spongeDense_correct` and `spongeDenseMeets_iff` are proved.
2. **`Theorem1iiSeq`: transfers unchanged.** It holds for every `IdealModel`.
3. **B5: does not apply.** It is stated for `randomOracle (LabelQry N w)` and for `Labelling.label`. No oracle answers a
   label-shaped query here: a label is `i + 1` permutation outputs deep, and every query mixes a state with a label
   (`s ⊕ (C ‖ 0)`).
4. **`complete_hard`, and B5's freshness: break.**
   - B5's pebbling step (`mem_reach_of_asked`) uses the fact that a label becomes known only from its own real query,
     or by prediction.
   - Over the sponge there is a third way. From a stored state, run the row backwards with `Π⁻¹`, and run forwards
     from the public IV. Where the two meet, the block between them falls out (`gap_close`).
   - **Formal witness** (`dense_two_labels_from_one_state`, every `Π`). With `1 ≤ g ≤ q ≤ i`, store
     `s = row i after q calls` (`ℓ + 512` bits) and drop `C_i` and `C_{i−g}`.
     - The adversary's copies `C'` are arbitrary at those two indices.
     - `twoFromOne` returns both labels in `max(g − 1, q − g + 1, i − q + 1)` rounds. At `i = 3D − 2`, `q = 2D − 1`,
       `g = D` that is exactly `D`.
     - Saving: `ℓ − 512` bits per such row.
   - **So the state game has reverse moves** (`Know`, `SpongeHard`).
     - Items are labels, states and call inputs; every item is at least `ℓ` bits.
     - A `Π`-round turns a known input into the state after its call, and a known state into its call's input
       (`Π⁻¹`).
     - XORs are free: input = previous state ⊕ block, in every direction, and a label is read off its row's final
       state.
     - The first version made `Π⁻¹` wait for the block, which is one round too slow; `state_game_ff.py` and `Know`
       now have it right.
5. **Is the break fatal? Not on the evidence** (`state_game_ff.py`, mode A; output at the end).
   - **Exhaustive** over labels and single `x`, `y`, `s` items, `B ≤ 7`, `D ≤ 3`: `labels − stored ≤ 2`.
   - **Targeted** (every missing set of up to 3–4 labels plus one item, where an item is any XOR of one call's
     variables), `D ≤ 5`: gain at most 2. The random-oracle complete DAG allows `D`.
   - **Why gains stay small.** A row with no stored item takes `i + 1` sequential calls, so only labels below `D`
     are free, and newest-first makes them sparse.
   - **The conjecture** is `SpongeHard B (B − D − 1) D B`, the exact analogue of `complete_hard`.
   - **The provable bound** is weaker, by an interval argument.
     - On each row, the known positions form intervals: the IV's, plus one per stored item.
     - Two intervals merge only across a single unknown block, which the merge extracts. So row `i` with `p_i` items
       yields at most `p_i` labels by extraction, plus its own label.
     - It yields `p_i + 1` only if its intervals cover it within `D` rounds, i.e. `i + 1 ≤ D(2p_i + 1)`.
     - Weighting items at `ℓ + 512` bits, the loss is
       `D + Σ_i max(0, ℓ − 512·max(1, ⌈(i + 1 − D)/2D⌉))/ℓ ≈ 1,084` labels (1.65% of `C`).

## 4. The certificate at the pinned numbers (`certificate.py`)

`B = 2^16`, `ℓ = 8192`, `D = 64`, `Q = 2^20`, `S = ⌊(18/19)·2^29⌋`, target `1% + 2^-128`. `nPos = B(Q + 1) + B(B + 1)/2`
(`log₂ ≈ 36.04`); the labeller now makes `Σ(i + 1)` calls.

| Chaining | Pebbling side (`labels ≤ stored + E`) | `k`, 3 positions per prediction | `k`, 2 positions |
|---|---|---|---|
| random oracle, as pinned | `E = D`, `complete_hard` (proved) | 107 at `2·37` bits (reproduced) | — |
| B, C, D: feed-forward of the state, the input or the block | `E = D`, row charging (section 5; proved on paper) | **119** | 106 |
| A: invertible sponge | `E = D` only if `SpongeHard` holds (conjecture) | 119 | 106 |
| A: invertible sponge, provable | `E ≈ 1,084`, the interval bound | 200 | — |
| **overwrite chain (chosen)** | `E = D`, `chainDense_hard` (**proved in Lean**) | **111** with a row name (`ChainExPostFacto` as stated) | 106 without it |

- **What drives `k`.** In every feed-forward mode the pebbling side now matches the random oracle's, so `k` is set
  by the ex post facto charge alone. 3 positions per prediction is the planning figure: a forward query shows
  `state ⊕ label`, and a third position identifies the label.
- **`k = 107` itself** needs a 2-position charge. The target to aim for is `SpongeDenseMeets 64 (2^20) 119`, with
  `H` in mode C or D.
- **Units.** `D` is counted in wide `Π`-calls. At `Δ = 300` µs and about 0.15 µs per 1 KB-wide call on a CPU core,
  `D ≈ 2000`, which gives `k = 506` (3 positions) or 344 (2).

**The remaining obligations** (`SpongeModel.lean` §6):
- **The pebbling bound.**
  - For modes B, C, D it is the row-charging lemma of section 5, which is short. Formalizing it means a `Know`
    game per mode.
  - For the invertible sponge it is `SpongeHard`, which is open.
- **`SpongeExPostFacto`, over `labelN ch`**: the B5 analogue for `Π`, and the main new work in every mode.
  - Resampling a permutation at a fresh point, `≤ 2^c/(2^(ℓ+c) − nPos)` per rate prediction.
  - Freshness per `Π`-answer, and a collision term.
  - The observations are not syntactic, as they are in B5. A label absorbed mid-row appears only XOR-masked by a
    chaining state, and newest-first makes that state depend on newer labels, which depend on it. So resampling at
    the predicted call can move the mask.
  - An encoding argument that decodes `Π` in label order, like the P3 `PermIncompressibility`/Lehmer scaffold,
    looks like the right tool.

## 5. Feed-forward chaining (`Chain`, `labelN`, `state_game_ff.py`)

Call `j` of row `i`: `x_j = s_{j−1} ⊕ (m_j ‖ 0^c)`, `y_j = Π(x_j)`, and the next state is

| Mode | `s_j` | What one stored `ℓ + 512`-bit value yields within `D` | Largest leaked index (search, `D = 2, 3, 4`) | Pebbling bound |
|---|---|---|---|---|
| A, sponge | `y_j` | a stored state: its row's label, plus one absorbed block of index up to `2D − 2` (gap closing, `dense_two_labels_from_one_state`) | 2, 4, 6 (`= 2D − 2`) | conjecture |
| B, state FF | `y_j ⊕ s_{j−1}` | a stored state: its row's label, plus its own call's block, `rate(Π⁻¹(s_q ⊕ s_{q−1}) ⊕ s_{q−1})` (`stateFF_two_labels_from_one_state`) | 1, 2, 3 (`= D − 1`) | `stored + D` |
| C, input FF | `y_j ⊕ x_j` | a stored state: its row's label only. A stored **input** `x_q`: the label, plus the block `x_q ⊕ s_{q−1}` (`inputFF_two_labels_from_one_input`) | 1, 2, 3 | `stored + D` |
| D, block FF | `y_j ⊕ (m_j ‖ 0)` | a stored input `x_q`: its block once `s_{q−1}` is known, and the tail from `π(x_q)` in the same round. On dense rows both labels are then among the `D + 1` oldest; on band rows it breaks (section 6) | 1, 2, 3 | `stored + D` on dense rows |

"Largest leaked index" is over every missing pair `{a < b}` that one item recovers together when neither the item
nor the free rows alone recover both (`leak`). In C and D those pairs are cases where the item gives one label and
`a < D` comes free.

**Why B and C still satisfy `stored + D`** (row charging; items are any XOR of one call's variables):
1. **Backwards and extraction need items.**
   - In B and C a row cannot be run backwards without an item of that call: recovering `s_{j−1}` from `s_j` needs
     `y_j` (B), or `x_j` (C).
   - In D it can, given the blocks, but extracting an unknown block needs that call's `x_j` or `y_j`.
2. **So every label is learned in one of two ways.**
   - By an extraction, paid by one item. In B and C that is the item starting an interval of known states; in D it
     is the call's own `x` or `y`.
   - By reading the row's final state, once per row.
3. **Only a row's rightmost start can be charged twice**, and only if it reaches the row's end within `D` rounds.
   That forces `i − q ≤ D − 1`, so the doubly charged label is one of the `D` oldest. Rows with no item are read only
   if `i + 1 ≤ D`.
4. **Hence the bound.** Every label is charged to a distinct item, or is among `C_0, …, C_{D−1}`:
   `labels ≤ stored + D`.

In D the double use goes through a stored input as well. The block needs `s_{q−1}` (`q − 1` rounds from the IV),
and on dense rows the row then takes `i` rounds, so both labels are among the `D + 1` oldest. The bound holds there;
P3's short band rows lose this restriction (section 6).

**Verdict.**
- **Designer's B: confirmed broken.** It stores a state, and that state gives up its own block. This is documented
  as counterexample 2.
- **C, the proposed fix: does not remove the two-for-one; it moves it to the call input.** For the dense scheme the
  leak is harmless: it only reaches labels the bound concedes, so the pebbling side carries over at the
  random-oracle strength.
- **For P3 it is not harmless.** P3's key chains are 13 calls, shorter than the deadline, so the leaked block can be
  any of the 12 parents (section 7).
- **D passes on dense rows but breaks on P3's band rows** (section 6). None of the XOR modes is safe for P3; the
  overwrite chain is.

## 6. The overwrite chain (chosen; `SpongeModel.lean` §9–10, `state_game_chain.py`)

**The chain.**
- Row `v` starts from `h_0 = IV(dom v)`, absorbs its parents newest-first and then the pad, and makes one `Π₂` call
  per block: `(r_j, h_j) = Π₂(B_j ‖ h_{j−1})`.
- `r_j` (`m` bits) is dropped, `h_j` (`m + 512` bits) is chained, and the key is `r` of the pad call.
- In Lean these are `ovStep`, `ovAbsorb`, `ovKey` and `ovProg` (one `Π₂` query per round, `depth_ovProg`), plus
  `labelOv` and `chainDense` (`chainDense_correct`, `chainDenseMeets_iff`, and `depth_blockKeyOv` = `i + 1` calls).
- Round accounting is unchanged. Every P3 level still costs at least 3 calls (`p3_level_ge_three`): `Π₂`(oldest
  parent), `Π₂`(pad), `P`.

**The search** (`state_game_chain.py`, output at the end). It runs the designer's pair test on my linear engine with
call slots. An item is any XOR of one call's variables `{B_j, h_{j−1}, r_j, h_j}` (1 label if it touches only
`m`-bit values, otherwise 1.06), or a whole call input or output (2.06).

| Rows | Sponge | MP (input feed-forward) | Block feed-forward | Overwrite chain |
|---|---|---|---|---|
| dense, `B ≤ 16`, `D ≤ 5` | state, 1.06: **break** | none | none | none |
| band `k = 4`, `B = 14`, `D ≤ 8` | state, 1.06: **break** (`D ≤ 5`) | input `x`, 1.06: **break** (`D = 3`–5) | input `x` of a row's second call, 1.06: **break** at `D = 5` | whole output only (2.06): dominated |
| band `k = 6`, `B = 18`, `D ≤ 10` | state, 1.06: **break** (`D ≤ 7`) | input `x`, 1.06: **break** (`D = 4`–7) | input `x` of a row's second call, 1.06: **break** at `D = 7` | whole output only (2.06): dominated |

This matches `internal/p3-instantiation/overwrite-state-game.log` everywhere they overlap.

**The chain game** (`ChainKnow`) holds labels, chaining values and dropped parts. Each round, every call with a known
input `(B_j, h_{j−1})` is made, and every call with a known output `(r_j, h_j)` is inverted. Keys are read off pad
calls, and `size` prices a label or an `r` at 1 and a chaining value at `1 + c/ℓ`.

**`chainHard_of_pebblingHard` (proved).** `PebblingHard G VC s D k → ChainHard G VC c ℓ s D k`, for any `TopoDAG`.
- The proof is `chain_invariant`. A holding stands for its seeds: its labels, the rows of its chaining values, and
  the block of each held `r` (or the row, for a pad-call `r`).
- Every label known after `t` rounds is in B5's greedy reach of the seeds after `t` rounds. On a row with no held
  chaining value, a known `h_{v,j}` means the blocks of calls `1..j` are known. A known `r` that was not held means its
  block is known.
- So the only ways to learn a label are the designer's three: its own row's pad call; a `Π₂⁻¹` answer on a call
  whose `r` is held, since `r` is otherwise only the output of the forward call that already needed the label; or
  holding it (prediction).
- With `complete_hard`, `chainDense_hard` gives `ChainHard (completeDAG B) univ c ℓ (B − D − 1) D B`.

**`ChainExPostFacto` (stated, open)** is the B5 analogue.
- **Hypothesis:** `ChainHard`.
- **Bound:** `2^m · 2 · (nPos² · B · 2)^(s+1) / 2^(ℓ s)`, plus a `Π₂`-collision term.
- **Freshness, as in B5.** A fresh item is a `Π₂`-answer part (a key, an `h`, or an `r`) that equals a value an
  earlier position showed in the clear. It holds with probability at most `2 · 2^−width`, where the width is `ℓ` for
  a key or an `r` and `ℓ + c` for an `h`.
- **Naming.** An item is named by two positions and a row; the row picks `W_v` for a key.
- **The loss.** A minimal winning fresh set has at most `s + 1` items and more than `ℓ·s` bits, which costs at most
  one label against B5's form.
- **What is new against B5:**
  - resampling a permutation, where an answer is uniform over unused points;
  - two-part answers (`r`, `h`);
  - inverse queries, whose fresh answer is compared with an earlier answer's `h`;
  - the collision term.

**Verdict on B5's step: it carries over.**
- At the game level it is proved.
- At the freshness level the XOR-mask obstacle of sections 3 and 5 is gone, because the chain's queries are
  concatenations.
- The Feistel half-states in the designer's list are instantiation-level. In the ideal model `Π₂` is atomic, so they
  belong to the named heuristic step, not to this proof.

## 7. What P3's `n10prime` needs for the same refinement

`n10prime` (`lean/submissions/pebbling/ColumnAwareDraft.lean`) assumes `ColumnHard G ((D + 1)/2) k X` in
`p3Model'` (random-oracle `H` plus an untweaked `P`), and is proved from `PermIncompressibility` plus
`LabelBirthday`. Over the sponge it needs:

1. **The model.** `p3SpongeModel` and `topLabelS`, defined here. `KQ'` and its random oracle disappear, and `P`
   becomes tweakable.
2. **Round conversion.** `ColumnHard G (levels D 3) k X`, i.e. `⌊(D − 1)/3⌋ + 1` game rounds, in place of
   `(D + 1)/2`. `le_levels` and `p3_level_ge_three` are the proved parts.
   - Crediting newest-first (15 − `g` calls per edge) needs a weighted `ColumnHard`.
   - The "+1" (a first level whose key is ready costs one call) is where held key-states enter.
3. **New holdings and moves in the column game.** This is the substantive change, the P3 form of the break above.
   Every node now has a 13-call key chain whose states are `m + 512` bits (`1 + 512/m` label units, or `n + 512/wc`
   column units).
   - **Holding a key-state.** It gives the key at once. It also gives, by gap closing (at most
     `max(g − 1, 14 − g) ≤ 13` `Π`-rounds), one parent's label **whole, with no column**, provided the other 11
     parents are whole.
   - **For layer 1, `W` is free**, so one lower key-state is about two whole lower labels for about one label's
     cost.
   - **For layer 2**, a top parent is recovered without its column. The key-gated reverse move ("held top `u` with
     `par u` whole") gains a second gate: a held key-state of `u`. The draft notes that the ungated rule saves about
     14 labels, against about 1 gated.
   - `X` must be re-certified with these moves, rerunning `inverse_rule_sim.py` and the band lemmas. They may raise
     `X`.
4. **The ex post facto kernel.** `PermIncompressibility` must cover two permutation families (`Π`, and `P` per
   tweak).
   - Freshness per `Π`-answer (a rate prediction, `m` bits) and per `P`-answer.
   - Positions must name the label XORed into each absorption, so the charge exceeds today's `n·Q_tot` per position.
   - The labeller makes `13·2n` `Π`-calls plus `2n` `P`-calls per segment, so `Q_tot = n(Q + 1) + 28n`.
5. **`LabelBirthday`.** It is the only place `H`'s random-oracle property enters (`PermKernelDraft.lean`). Over the
   sponge the keys are not independent uniform, so it becomes a `Π`-collision bound over the `26n` real chain calls,
   `≲ (26n)²/2^(m+512)`, proved inside the new kernel rather than cited.
6. **No indifferentiability shortcut** (RSS). Every step is in the two-permutation model directly, as in the dense
   pilot.
7. **Chaining mode for P3: the overwrite chain removes the key-state double** of item 3.
   - A held chaining value (`1 + 512/m` labels) yields only its row's key, which is the "+1" of a ready key.
   - Recovering a parent without its column needs a whole call output (`2 + 512/m`), which is dominated.
   - So over `p3ChainModel` the column game gains only key holdings at `1 + 512/m`, and `X` should not rise.
   - The kernel's positions again show labels in the clear. `LabelBirthday` becomes a `Π₂`-collision bound over
     `26n` calls, and `Q_tot = n(Q + 1) + 28n`.
   - `chainHard_of_pebblingHard` is the pattern for the column-game version.

## Reproduce

~~~bash
# in a copy of lean/pous (toolchain v4.34.0, lake exe cache get, lake build)
lake env lean ../submissions/sponge-dense/SpongeDense.lean
LEAN_PATH=$(lake env printenv LEAN_PATH) lean -o SpongeDense.olean SpongeDense.lean
LEAN_PATH=$(lake env printenv LEAN_PATH):. leanchecker SpongeDense
python3 state_game_chain.py        # the pair test, five modes, dense and band rows
python3 state_game_ff.py sanity|two|leak|targeted|exhaustive; python3 certificate.py
python3 state_game.py; python3 state_game_fast.py   # the first, superseded searches
~~~

## Band v6 builder status (2026-09-28)

`ChainEPFV6VC.lean`, `ChainEPFV6Charge.lean`, and `ChainEPFV6Final.lean` implement the folded G1–G3 boundary through:

- coordinate-granular, round-causal seed classification and the no-slack `vc_credit_subset_reach`;
- the first seed-price crossing and per-pattern truncated labeller;
- history-backed `VCTarget`, truncated-tail completion, and an eventual-target/nPos bound used to delimit the
  remaining attribution proof;
- exact glue `BandFreshTail → ChainExPostFactoG'`, without the refuted old `PrEvR`.

The reviewed direct/transfer map now lands in `ChainEPFV6Pin.lean`.
`v6_charge_pin_injective` is proved from pair-step injectivity, the positional stopping/backing rule, and backward
uniqueness; inverse-decided pad `r` stops because its block is the public pad constant. `ChainEPFV6Tail.lean` proves
the G1 `M^d` name counts (including the two-pointer `rh` case), the all-size G3 geometric bound, and a generic
fixed-pattern fiber union. `ChainEPFV6Final.lean` proves `V6PatternFibers → BandFreshTail → ChainExPostFactoG'`.

`v6_pattern_fibers : V6PatternFibers` is now proved (`ChainEPFV6Close.lean`, (c′) names). So `bandFreshTail_v6` and
`chainExPostFactoG'_v6` are unconditional; see "(c′) closed" below. The paragraphs that follow record how the design got
there.

A direct adversary charge does need a row to turn a label-form source into a pad-r key target. This fits the frozen
base: restrict pointers to actual program slots plus inverse `posSet`
(`B(Q+1)+|posSet| = nPos`) and include one `Fin B` row in the fixed fiber. Then
`step × part × pointer × row ≤ 2·nPos²·B = M`. The remaining work is construction, not a changed RHS:
map realized sources into that name, prove `PatternDone/stratP` agrees with the realized cutoff, and instantiate the
already proved fixed-fiber union as `v6_pattern_fibers`.

**Target-naming gap (2026-09-28 16:55Z).** `v6_pattern_fibers` cannot be instantiated with the current
`realizedName`, because `(step, part, program pointer, row)` does not determine the charge target:
- A direct pad-`r` seed credited at an inverse slot `o` gets the same name, history and step-`j` query as a length-1
  transfer through that same inverse slot.
- The two need different values, `ovR y_o` and `ovR x_o ⊕ Wb v`. So no history-measurable (`readAtP`) target covers
  both.
- A re-encoding within `M` resolves that case for `B ≥ 2`.
- Three provenances still need data that no name carries: known-partner inverse stops, transfers shown before their
  inverse step, and transfer chains of length ≥ 2.

This needs a design decision; see `internal/p3-instantiation/band-v6-target-naming-gap.md` in the project store.
The designer recommends option (c), re-charging those cases (final section of `band-v6-design.md`).

**`sourceRound ≤ chargeRound` (2026-09-28 17:25Z).** `ChainEPFV6Round.lean` proves
`v6_source_round_le_home_step`: the selected show's round starts no later than the first fresh step of the seed's
home pair. Any charge at that step or later, which is every (c) chain with increasing steps, therefore inherits it
(`v6_source_round_le_of_home_step_le`). Direct charges are `v6_source_round_le_charge_direct`.
- The proof takes the pair's first fix in the program prefix of an earlier round.
- That round's query shows either the seed itself (inverse) or the pair's input atoms (forward).
- Either way the seed is in `vcCredit` before the record that first added it, which contradicts freshness
  (`recordsFold_fresh`).
- `sourceCommitRound` is now `Nat.find`, the least round among sources at the first cut. Ties between rounds with
  empty rounds in between would otherwise let the choice land in a later round.

**Option (c) scaffold (2026-09-28 17:29Z).** `ChainEPFV6SlotDet.lean` proves round-determined source slots.
- `v6_slot_query_det` / `v6_slot_output_det`: two oracles with equal `advThenLab` histories through `roundStart τ`
  have equal transcript entries at every slot of round `≤ τ`, and equal output and depth for threads of depth `≤ τ`.
- `v6_query_obs_det` / `v6_output_obs_det`: consequently every observation a source pointer reads agrees.

The target chain does not import this module until the red-team verdict on (c) lands.

**(c′) building blocks (2026-09-28 18:10Z).** The red team's (c′) keeps `chargePin` and changes the names. Three new
modules, not yet imported by the target chain:
- `ChainEPFV6StopHits.lean`: `prob_hitsAt_pattern_le` gives the fixed-step product for items assigned predictably by
  the step index and pre-step history, so labeller items at "cut + offset" need no padding.
- `ChainEPFV6Backing.lean`:
  - credit ⊆ `VCTarget`;
  - labeller queries are forward;
  - `pinNext_step_le`: steps along a transfer chain never decrease;
  - `v6_source_round_le_charge`.
- `ChainEPFV6Names.lean`: exact readiness of any basis-commit slot and of any absolute adversary step before the cut
  (`stepReady_iff`).

**(c′) closed (2026-09-28, bc-87c3b40e).** `bandFreshTail_v6 : BandFreshTail` and `chainExPostFactoG'_v6 :
ChainExPostFactoG'` now take no hypothesis. `ChainEPFV6Final.lean` imports the new chain:
- `ChainEPFV6StopHitsW`: the product lemma with **history-dependent widths** (`prob_hitsAt_hist_le`). (c′)'s code table
  reuses one `(part,row)` code as `r` for a forward pointer slot and as `h` for an inverse one. This is forced for
  `B=2`: the forward/forward class has `B+1` `r` readings. So an item's width is read from the history, not from the
  name. Not a statement change.
- `ChainEPFV6Read`: slot readers (`raw`/`inp`/`out`/`run`), the code table `v6Decode`, and `read_det`.
- `ChainEPFV6Class`: `v6Ptr`/`v6Code` per seed.
  - Direct: the crediting show.
  - Transfer: the slot of the last inverse step (`prevCell`, `fixSlot`).
  - No-partner stop: `.inr e.pair`.
  - Known partner: a child-pair slot, else the partner's own-pair slot, else its crediting show.
- `ChainEPFV6Sound`/`Sound2`:
  - `vcTarget_origin` and `pinKnownAt_origin`: a known partner is held, or its own or a child pair is fixed. This
    settles the pointer without `VCTargetAt`.
  - `v6_partner_round_le`: (c′)'s `valueSlot_round_le` for held partners.
  - `v6_seed_sound`: each seed's name reads its charged value, class by class.
- `ChainEPFV6Names2`: the step split (`stepField`), `nameReady6`, `realizedPattern6_done_iff` (done exactly at
  `firstCrossing`), `stratP6_realized_hist_eq` and `realizedName6_injective`.
- `ChainEPFV6Fibers`/`Fibers2`/`Close`:
  - `assign6`: labeller fields sit at the first `PatternDone6` time plus their offset.
  - `v6_fiber_det`: fiber determinacy.
  - `fields_width_sum`: slot widths add up to the seed width.
  - `B=1` has at most one field; there the one-factor bound `v6_fp_small` needs only `2·nPos ≤ 2^ℓ`.
  - `prob_realizes6_le` gives `2·2^{-W}`, and `v6_pattern_fibers`.

Every theorem is on `[propext, Classical.choice, Quot.sound]`, and `leanchecker --fresh ChainEPFV6Final` passes
(`AXIOMS.txt`, (c′) block).

**Unconditional finals.** `ChainExPostFactoG` is discharged by `chainExPostFactoG_v6`, one module per area:
- `ChainEPFV6FinalBand64`: `band_meets_64_final`, `band_meets_64_d5_final`, `band_meets_64_d12_final`.
- `ChainEPFV6FinalBand64Key`: the key-rule forms `band_meets_64_final'`, `band_meets_64_d12_final'`, from
  `chainExPostFactoG'_v6`.
- `ChainEPFV6FinalBand14`: `band_meets_14_final`, `band_meets_14_k106_final`.
- `ChainEPFV6FinalPub`: `band_pub_meets_64_final`, `band_pub_meets_14_final`, `band_pub_meets_14_global_final`. The last
  two go through `band_pub_iff_14`/`_global`. `band_pub_iff_64` has no hypothesis.
- `ChainEPFV6FinalDense`: `chainExPostFacto_v6` (via `chainExPostFactoG_spec`) and `chain_meets_64_final`.
- `ChainEPFV6FinalDense111`: `ChainDenseMeets111 := ChainDenseMeets 64 (2^20) 111`, the pinned dense deployment
  (`2^16 × 8192`, `D = 64`) at `k = 111`, proved as `chainDenseMeets111_final` with `β = 530500000`. The bound's
  `2·nPos²·B ≈ 2^89` names per seed make 111 the least certifiable `k`, so `ChainDenseMeetsPinned` (`k = 107`) stays
  open (review §53).

The modules sit here rather than in `band-chain`/`band-multi`/`public-encoder`. `band-multi` is a Lake package whose
audit roots and `DEPS.sha256` would need the whole v6 chain, and the other two are other lanes' submissions. `All.lean`
imports all of them, and `leanchecker --fresh All` passes.

## Search output

`state_game.py` (exhaustive over every stored set of size `s`; "max labels" known after `D` rounds):

~~~text
B=5 D=1: max labels [s=0:1, s=1:2, s=2:3, s=3:4, s=4:5]; max(labels - s) = 1  (RO complete DAG: 1)
B=5 D=2: max labels [s=0:1, s=1:2, s=2:3, s=3:4]; max(labels - s) = 1  (RO complete DAG: 2)
B=6 D=1: max labels [s=0:1, s=1:2, s=2:3, s=3:4, s=4:5, s=5:6]; max(labels - s) = 1  (RO complete DAG: 1)
B=6 D=2: max labels [s=0:1, s=1:2, s=2:3, s=3:4, s=4:5]; max(labels - s) = 1  (RO complete DAG: 2)
B=6 D=3: max labels [s=0:2, s=1:3, s=2:4, s=3:5]; max(labels - s) = 2  (RO complete DAG: 3)
B=7 D=2: max labels [s=0:1, s=1:2, s=2:3, s=3:4, s=4:5, s=5:6]; max(labels - s) = 1  (RO complete DAG: 2)
B=7 D=3: max labels [s=0:2, s=1:3, s=2:4, s=3:5, s=4:6]; max(labels - s) = 2  (RO complete DAG: 3)
B=8 D=2: max labels [s=0:1, s=1:2, s=2:3, s=3:4, s=4:5, s=5:6]; max(labels - s) = 1  (RO complete DAG: 2)
B=8 D=3: max labels [s=0:2, s=1:3, s=2:4, s=3:5, s=4:6, s=5:7]; max(labels - s) = 2  (RO complete DAG: 3)
B=9 D=3: max labels [s=0:2, s=1:3, s=2:4, s=3:5, s=4:6, s=5:7]; max(labels - s) = 2  (RO complete DAG: 3)
~~~

`state_game_fast.py` (every missing set `M` and up to 2 states `T` on rows of `M`; gain = recovered − |T|).
`B = 18, D = 6` did not finish within the 25-minute limit.

~~~text
B=10 D=3 |M|<=4 |T|<=2: max gain 2 (RO: 3) at ((0, 1), ())
B=12 D=4 |M|<=4 |T|<=2: max gain 2 (RO: 4) at ((0, 1), ())
B=14 D=4 |M|<=5 |T|<=2: max gain 2 (RO: 4) at ((0, 1), ())
B=16 D=5 |M|<=5 |T|<=2: max gain 3 (RO: 5) at ((0, 1, 2, 3), ((3, 2),))
~~~

`state_game_ff.py` (the current engine; linear knowledge, items are any XOR of one call's variables). The old
`state_game.py` gives 2 at `B = 6, D = 2, s = 1`; the engine gives 3, from row 2's state after 2 calls. `π⁻¹` of that
state runs in round 1 without waiting for `C_0`.

~~~text
== sanity: mode A with stored states only (compare state_game.py) ==
mode A states-only B=6 D=2: [s=0:1, s=1:3, s=2:4, s=3:5, s=4:6]
mode A states-only B=6 D=3: [s=0:2, s=1:3, s=2:4, s=3:5]
mode A states-only B=7 D=3: [s=0:2, s=1:3, s=2:4, s=3:5, s=4:6]
== one stored item, two missing labels: net gain over no item (2 = the item yields two labels) ==
mode A: 2, 2, 2 at D = 2, 3, 4 (B = 3D + 1)     modes B, C, D: 1, 1, 1
== literal two-for-one: largest older index a of a pair one item recovers ==
mode A B=7 D=2: a = 2   B=10 D=3: a = 4   B=13 D=4: a = 6   (e.g. (6, 7, 'y[7,4]'))
mode B B=7 D=2: a = 1   B=10 D=3: a = 2   B=13 D=4: a = 3   (e.g. (3, 4, 'y[4,1]'))
mode C B=7 D=2: a = 1   B=10 D=3: a = 2   B=13 D=4: a = 3
mode D B=7 D=2: a = 1   B=10 D=3: a = 2   B=13 D=4: a = 3
== missing sets |M| <= mmax plus at most one combo item: max recovered - stored (RO: D) ==
mode A B=7 D=2 |M|<=4: max gain 2  at ((0, 1, 2), 'y[2,2]')
mode B B=7 D=2 |M|<=4: max gain 2  at ((0, 1, 2), 'y[2,2]')
mode C B=7 D=2 |M|<=4: max gain 1  at ((0,), None)
mode D B=7 D=2 |M|<=4: max gain 1  at ((0,), None)
mode A B=10 D=3 |M|<=4: max gain 2  at ((0, 1), None)
mode B B=10 D=3 |M|<=4: max gain 2  at ((0, 1), None)
mode C B=10 D=3 |M|<=4: max gain 2  at ((0, 1), None)
mode D B=10 D=3 |M|<=4: max gain 2  at ((0, 1), None)
mode A B=13 D=4 |M|<=3: max gain 2  at ((0, 1), None)
mode B B=13 D=4 |M|<=3: max gain 2  at ((0, 1), None)
mode C B=13 D=4 |M|<=3: max gain 2  at ((0, 1), None)
mode D B=13 D=4 |M|<=3: max gain 2  at ((0, 1), None)
mode A B=16 D=5 |M|<=3: max gain 2  at ((0, 1), None)
mode B B=16 D=5 |M|<=3: max gain 2  at ((0, 1), None)
mode C B=16 D=5 |M|<=3: max gain 2  at ((0, 1), None)
mode D B=16 D=5 |M|<=3: max gain 2  at ((0, 1), None)
== exhaustive over labels and single x, y, s items: max labels known (RO: stored + D) ==
mode A B=5 D=2: [s=0:1, s=1:3, s=2:4, s=3:5]; max(labels - s) = 2
mode B B=5 D=2: [s=0:1, s=1:3, s=2:4, s=3:5]; max(labels - s) = 2
mode C B=5 D=2: [s=0:1, s=1:2, s=2:3, s=3:4]; max(labels - s) = 1
mode D B=5 D=2: [s=0:1, s=1:2, s=2:3, s=3:4]; max(labels - s) = 1
mode A B=6 D=2: [s=0:1, s=1:3, s=2:4, s=3:5]; max(labels - s) = 2
mode B B=6 D=2: [s=0:1, s=1:3, s=2:4, s=3:5]; max(labels - s) = 2
mode C B=6 D=2: [s=0:1, s=1:2, s=2:3, s=3:4]; max(labels - s) = 1
mode D B=6 D=2: [s=0:1, s=1:2, s=2:3, s=3:4]; max(labels - s) = 1
mode A B=6 D=3: [s=0:2, s=1:3, s=2:4]; max(labels - s) = 2
mode B B=6 D=3: [s=0:2, s=1:3, s=2:4]; max(labels - s) = 2
mode C B=6 D=3: [s=0:2, s=1:3, s=2:4]; max(labels - s) = 2
mode D B=6 D=3: [s=0:2, s=1:3, s=2:4]; max(labels - s) = 2
mode A B=7 D=3: [s=0:2, s=1:3, s=2:4, s=3:5]; max(labels - s) = 2
mode B B=7 D=3: [s=0:2, s=1:3, s=2:4, s=3:5]; max(labels - s) = 2
mode C B=7 D=3: [s=0:2, s=1:3, s=2:4, s=3:5]; max(labels - s) = 2
mode D B=7 D=3: [s=0:2, s=1:3, s=2:4, s=3:5]; max(labels - s) = 2
~~~

`state_game_chain.py` (the pair test; band `k = 12` was stopped after its first case, too slow for this engine):

~~~text
dense  sponge B=8 D=2: cheapest item worth two: y[3,2] (1.062 labels) for pair (2, 3): BREAK
dense  mp     B=8 D=2: no single item is worth two labels
dense  block  B=8 D=2: no single item is worth two labels
dense  over   B=8 D=2: no single item is worth two labels
dense  sponge B=10 D=3: cheapest item worth two: y[4,2] (1.062 labels) for pair (3, 4): BREAK
dense  mp     B=10 D=3: no single item is worth two labels
dense  block  B=10 D=3: no single item is worth two labels
dense  over   B=10 D=3: no single item is worth two labels
dense  sponge B=12 D=4: cheapest item worth two: y[5,2] (1.062 labels) for pair (4, 5): BREAK
dense  mp     B=12 D=4: no single item is worth two labels
dense  block  B=12 D=4: no single item is worth two labels
dense  over   B=12 D=4: no single item is worth two labels
dense  sponge B=14 D=5: cheapest item worth two: y[6,2] (1.062 labels) for pair (5, 6): BREAK
dense  mp     B=14 D=5: no single item is worth two labels
dense  block  B=14 D=5: no single item is worth two labels
dense  over   B=14 D=5: no single item is worth two labels
dense  sponge B=16 D=5: cheapest item worth two: y[6,2] (1.062 labels) for pair (5, 6): BREAK
dense  mp     B=16 D=5: no single item is worth two labels
dense  block  B=16 D=5: no single item is worth two labels
dense  over   B=16 D=5: no single item is worth two labels
band4  sponge B=14 D=2: cheapest item worth two: y[2,2] (1.062 labels) for pair (1, 2): BREAK
band4  mp     B=14 D=2: no single item is worth two labels
band4  block  B=14 D=2: no single item is worth two labels
band4  over   B=14 D=2: cheapest item worth two: whole-out[5,4] (2.062 labels) for pair (1, 5): dominated (costs >= 2 labels)
band4  sponge B=14 D=3: cheapest item worth two: y[3,2] (1.062 labels) for pair (2, 3): BREAK
band4  mp     B=14 D=3: cheapest item worth two: sp+M[6,4] (1.062 labels) for pair (2, 6): BREAK
band4  block  B=14 D=3: no single item is worth two labels
band4  over   B=14 D=3: cheapest item worth two: whole-out[5,3] (2.062 labels) for pair (2, 5): dominated (costs >= 2 labels)
band4  sponge B=14 D=4: cheapest item worth two: y[4,2] (1.062 labels) for pair (3, 4): BREAK
band4  mp     B=14 D=4: cheapest item worth two: sp+M[6,3] (1.062 labels) for pair (3, 6): BREAK
band4  block  B=14 D=4: no single item is worth two labels
band4  over   B=14 D=4: cheapest item worth two: whole-out[5,2] (2.062 labels) for pair (3, 5): dominated (costs >= 2 labels)
band4  sponge B=14 D=5: cheapest item worth two: y[5,1] (1.062 labels) for pair (4, 5): BREAK
band4  mp     B=14 D=5: cheapest item worth two: sp+M[6,2] (1.062 labels) for pair (4, 6): BREAK
band4  block  B=14 D=5: cheapest item worth two: sp+M[6,2] (1.062 labels) for pair (4, 6): BREAK
band4  over   B=14 D=5: cheapest item worth two: whole-out[5,1] (2.062 labels) for pair (4, 5): dominated (costs >= 2 labels)
band4  sponge B=14 D=6: no single item is worth two labels
band4  mp     B=14 D=6: no single item is worth two labels
band4  block  B=14 D=6: no single item is worth two labels
band4  over   B=14 D=6: no single item is worth two labels
band4  sponge B=14 D=7: no single item is worth two labels
band4  mp     B=14 D=7: no single item is worth two labels
band4  block  B=14 D=7: no single item is worth two labels
band4  over   B=14 D=7: no single item is worth two labels
band4  sponge B=14 D=8: no single item is worth two labels
band4  mp     B=14 D=8: no single item is worth two labels
band4  block  B=14 D=8: no single item is worth two labels
band4  over   B=14 D=8: no single item is worth two labels
band6  sponge B=18 D=3: cheapest item worth two: y[3,2] (1.062 labels) for pair (2, 3): BREAK
band6  mp     B=18 D=3: no single item is worth two labels
band6  block  B=18 D=3: no single item is worth two labels
band6  over   B=18 D=3: cheapest item worth two: whole-out[7,5] (2.062 labels) for pair (2, 7): dominated (costs >= 2 labels)
band6  sponge B=18 D=4: cheapest item worth two: y[4,2] (1.062 labels) for pair (3, 4): BREAK
band6  mp     B=18 D=4: cheapest item worth two: sp+M[8,5] (1.062 labels) for pair (3, 8): BREAK
band6  block  B=18 D=4: no single item is worth two labels
band6  over   B=18 D=4: cheapest item worth two: whole-out[7,4] (2.062 labels) for pair (3, 7): dominated (costs >= 2 labels)
band6  sponge B=18 D=5: cheapest item worth two: y[5,2] (1.062 labels) for pair (4, 5): BREAK
band6  mp     B=18 D=5: cheapest item worth two: sp+M[8,4] (1.062 labels) for pair (4, 8): BREAK
band6  block  B=18 D=5: no single item is worth two labels
band6  over   B=18 D=5: cheapest item worth two: whole-out[7,3] (2.062 labels) for pair (4, 7): dominated (costs >= 2 labels)
band6  sponge B=18 D=6: cheapest item worth two: y[6,2] (1.062 labels) for pair (5, 6): BREAK
band6  mp     B=18 D=6: cheapest item worth two: sp+M[8,3] (1.062 labels) for pair (5, 8): BREAK
band6  block  B=18 D=6: no single item is worth two labels
band6  over   B=18 D=6: cheapest item worth two: whole-out[7,2] (2.062 labels) for pair (5, 7): dominated (costs >= 2 labels)
band6  sponge B=18 D=7: cheapest item worth two: y[7,1] (1.062 labels) for pair (6, 7): BREAK
band6  mp     B=18 D=7: cheapest item worth two: sp+M[8,2] (1.062 labels) for pair (6, 8): BREAK
band6  block  B=18 D=7: cheapest item worth two: sp+M[8,2] (1.062 labels) for pair (6, 8): BREAK
band6  over   B=18 D=7: cheapest item worth two: whole-out[7,1] (2.062 labels) for pair (6, 7): dominated (costs >= 2 labels)
band6  sponge B=18 D=8: no single item is worth two labels
band6  mp     B=18 D=8: no single item is worth two labels
band6  block  B=18 D=8: no single item is worth two labels
band6  over   B=18 D=8: no single item is worth two labels
band6  sponge B=18 D=9: no single item is worth two labels
band6  mp     B=18 D=9: no single item is worth two labels
band6  block  B=18 D=9: no single item is worth two labels
band6  over   B=18 D=9: no single item is worth two labels
band6  sponge B=18 D=10: no single item is worth two labels
band6  mp     B=18 D=10: no single item is worth two labels
band6  block  B=18 D=10: no single item is worth two labels
band6  over   B=18 D=10: no single item is worth two labels
~~~
