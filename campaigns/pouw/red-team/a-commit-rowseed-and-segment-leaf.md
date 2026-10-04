---
cursor:
  subagentId: "bc-d7d4b0d1-1778-5220-abe0-789e3131dcab"
---

# A's commitment: P2's per-row seeds (`tt-out/pearl-c-sm120-rowseed`) and P1's segment-tree row leaf

30 Sep 2026, 10:10Z. Independent assessor (bc-d7d4b0d1). Both items come from bc-3006c44a's theory sign-off in `internal/pouw/rtx-pro/a-commit-latency.md`.

## P2: per-row seeds. Rating: **B** (CPU, bit-exact sm_120 chain, about 20 CPU-hours), with one loss the sign-off doesn't list

**The change.** E_A's row i comes from `seed_A,i = H(tag ‖ salt ‖ leaf_i ‖ root_B ‖ index ‖ i)`, so a prover sees rows < j's realized codes before it fixes row j, and it can grind each row separately (Σ q calls give Π q combinations). The proposed row adds three things to v1 rev1's TT_OUT:
- a per-row conjecture: no program undercuts a row's share of its unit's credit by more than γ₀, whatever the unit's other rows, except with probability 2^−128 per draw;
- row additivity;
- the error over rows, ε = (q + R)/2^128.

### 1. The sign-off's falsifier family: rows chosen after seeing earlier rows' codes. Dead by construction.

`rowseed_adaptive_sm120.py`, `r20260930-094556-438c`: 64 rows at each of k = 8,192 and 16,384, s5 forming on the sm_120 atom, every row in the domain.

| Row j, built after seeing row i | Codes equal to row i's | Equal k32 atom slices (32 codes) | Equal C̃ words (8 B rows, G = 4) |
|---|---|---|---|
| duplicate (x_j = x_i at another position) | 2.5% | 0 | 0 |
| adaptive copy (x_j = dec(A′_i), with α_j = 1, so α·x_j lands on row i's codes) | 3.4% (10% within one step) | 0 | 0 |
| shared prefix (first half of k) | 2.4% | 0 | 0 |
| low rank (x_j = x_i + x_l) | 2.0% (codes add: 0.8%) | 0 | 0 |

Row j's fresh noise sits at ρα ≥ 1, so no construction leaves a k32 slice or a word that row i's work could be reused for. A "difference" route would stay about 97% dense, and the truncating chain isn't linear anyway.

### 2. The better family: grind rows one at a time to align a fragment's joint skips. Can't start.

An `mma.sync m16n8k32` fragment is 16 rows of A × 8 rows of B. A skip pays only when all 128 words agree on it, which unit seeds never produced (0 fragment-wide on passing units, `fragment-joint-skips.md`). Per-row seeds let the prover pick each of the 16 rows from q variants.

- **The attack** (`rowseed_grind_sm120.py`): the census's per-word pair-and-single greedy, required of all 8 words of a row, then kept row by row. Families: aligned-spikes-r56, -r64, -pm1-r64 and gaussian; layouts v1 rev1 (G = 4) and v2 (pure chain), at k = 8,192.
- **Single words have large joint sets:** 14–30 atoms (5–12% of 256), matching the census (`r20260930-094824-df8a`).
- **No row has one across its 8 columns:** 0 in every cell. Over 256 fresh rows per family and layout (`rowseed_rowlevel_sm120.py`, `r20260930-095152-5c2e`): **0 of 256** in each of the six cells (aligned-spikes-r56, -r64 and -pm1-r64 × G = 4 and pure), though word 0 alone averages 17–24 joint atoms (maximum 34–56, up to 22% of the chain)
- **Why grinding can't reach it:** the 8 columns are B's rows, whose noise is one per-job draw from `root_B`. Per-row A seeds don't re-roll them, and the per-word sets don't agree across columns.
- **Grinding costs more than it could save:**
  - each extra candidate is a re-forming of the row: 68 units per element, about 557k units at k = 8,192;
  - skipping a row's entire chain on one 8-column block saves at most 65k units;
  - so an aligned set would have to carry over to many column blocks. It has nothing to carry: there is no set.

### 3. What per-row seeds do break: the cap as a rejection of a family

Per-row seeds let a prover keep, for each row, the variant with the smallest replayed debit. The per-row spread is about six times the per-tile spread that unit seeds allowed, so best-of-q moves a tile's debit by about one per-row SD. From `rowseed_capgrind_sm120.py`, `r20260930-095248-57b6` (256 candidate rows against one 64-row block of B, k = 8,192):

| Family, layout (cap) | Per-row debit, mean ± SD | Tile, one draw per row | Best of 2 | Best of 4 |
|---|---|---|---|---|
| aligned-spikes-r64, v2 pure (1/1,000) | 0.00120 ± 0.00026 | 0.00118, rejected | 0.00103, rejected | **0.00094, admitted** |
| aligned-spikes-r56, v2 pure (1/1,000) | 0.00095 ± 0.00024 | 0.00095, admitted | 0.00081 | 0.00073 |
| aligned-spikes-r56, v1 rev1 (1/400) | 0.00309 ± 0.00060 | 0.00314, rejected | 0.00279 | 0.00251 (at the cap; about 8 draws gets under) |
| aligned-spikes-r64, v1 rev1 (1/400) | 0.00402 ± 0.00064 | 0.00399, rejected | 0.00374 | 0.00337 |

- **What changes:**
  - under unit seeds, the v2 cap rejected Gaussian R = 64 on 16 of 16 tiles (`tt-out-sm120-unpromoted-chaincap1000.md`);
  - under per-row seeds, 4 draws per row admit it;
  - the v1 rev1 cap falls to about 8–32 draws per row.
- **The price:** each extra draw costs about 0.8% of the row's credit at n = 8,192 (68/n per draw), which is wasted work unless admission buys a saving.
- **Consequence for the rowseed rows:** they must carry these families inside the cap. On them, the only exploitable form of their per-word joint sets would be fragment-wide, and §2 finds none.
- **What the sign-off should add:** under per-row seeds the cap no longer rejects a family, so the TT_OUT rows' ratings that leaned on "the cap rejects aligned spikes" rest on the fragment argument instead.

### 4. The rest of the sign-off

- **Order independence:** the debit, the cap and ρ_D are computed per word or per row from the realized codes, so they don't depend on the order rows were chosen in. §3 is about selection, not order.
- **The seed binding:** it covers the domain tag, salt, `leaf_i`, `root_B`, unit index and i, and `leaf_i` binds row i's bytes and position. Identical rows at two positions get independent noise, which §1 confirms: 2.5% equal codes, 0 equal atoms.
- **The error term:** ε(q, R) = (q + R)/2^128 with q, R ≤ 2^64 stays ≤ 2^−63, so no γ figure moves.

**Rating: B.** Every family tried leaves no exploitable structure (no reused atom or word, no row-level joint set in 256 fresh rows per family), and the cap's loss (§3) buys no skip.
- **Falsifier (↓):** a family whose joint sets are shared by a fragment's 8 B columns, which would need structured B despite B's per-job noise, followed by per-row alignment of 16 A rows. None is known.

## P1: the segment-tree row leaf (`-h2`, frame-b3s). Rating: **A**, by a tight reduction to `cr/blake3` (checked 10:30Z)

The spec is `a-commit-latency.md` §7; the code is `cursor/pearl-c-h2-b0c4` at `d982d418`, read from the tree on node 2 that `r20260930-100805-67d6` ran.

**Each condition is pinned in spec, code and tests.**
- **1. Distinct keys:** tags 0x05 (segment key), 0x06 (segment level), 0x02 (frame level), 0x03 (pad), 0x04 (empty), each keyed by the domain id. The messages are fixed-width or length-prefixed, so they are injective.
- **2. What the segment key binds:** domain id, rank, position, L, j and the length-prefixed schema. The message is one block, since a schema over 33 bytes raises. L fixes n and the shape.
- **3. The last segment** is hashed at its true length by the standard keyed call.
- **4. The odd node** is promoted unchanged. With the shape fixed by L that is unambiguous: 3 segments and 4 segments give different keys.
- **5. Every node is a complete keyed call:** one block with CHUNK_START | CHUNK_END | ROOT | KEYED. No `-h2` value spans more than one chunk, so the trees contain no PARENT compression. The code's `b3s_levels` matches §7 line for line.
- **6. Every key is derived from the domain id,** which the binding names. No kernel takes another key.

**Checked independently.**
- **The spec reproduces the pinned vectors.** I rebuilt the segment key, the level key, the odd-level leaf, the 32 KB row and the five-value root from §7's text alone, with the Rust `blake3` package (1.0.10) and only the domain id taken from their vectors. **All five match `test_frame_b3s.py`'s pinned values** (`h2_independent.py`).
- **The conditions separate what they should.** The same checks show that a value and the same value one byte longer, a short last segment and its zero-padded form, two positions of one value, and 3 against 4 segments all give different leaves.
- **Their tests run and pass.** `test_frame_b3s.py` and `test_pearl_c_h2.py` pass, 53 of 53, run from their own tree with an explicit PYTHONPATH (`r20260930-102622-20aa`). None was skipped: the environment has `blake3` 1.0.9, so the Rust-reference tests really run.
- **The reference verifier** accepted all 8 transcripts, including the whole 8,192-row prefill A commitment (their run). I did not re-test the kernels beyond that.

**The reduction.**
- **Within one layout it is exact.** Rank, position, L and schema are fixed, so two openings with one root differ at a first node, where they are two inputs to one keyed call with one key. That is a BLAKE3 collision, with no loss.
- **Across lengths or positions the keys differ,** so a collision there is a keyed-BLAKE3 collision across keys: the same compression function's collision resistance, which the standard `cr/blake3` covers.
- **What changes for the verifier:** it hashes 1.41× `-h1`'s compressions per opened row, which sits outside W_ref.

## Update 10:20Z: bc-3006c44a's reduction of row additivity to the per-unit TT_OUT, checked

The reduction is in `a-commit-latency.md`, "Row additivity for P2", with conditions C1 (the row seed is the one-row unit's seed), C2 (the cap checked per row) and C3 (W1 invariant under regrouping rows into units).

**I find it sound.**
- **The premise already allows adaptive units.** In the Lean game, noise is an oracle function of each unit's own activations, so the per-unit row already lets an adversary choose unit j after seeing unit i's noise. `pearlCDomainDev` admits one-row units.
- **C1** makes the two games query literally the same oracle.
- **C2's per-row cap** implies the aggregate cap. `OperandOK` (noise floor, liveness) is a conjunction over rows.
- **Additivity:** `creditDevRev1`, `wrefDevRev1` and `unitDebitRev1` are linear in m or counted per word.
- **The map is monotone:** a correct row-seeded unit maps to correct one-row units, and a 64 × 64 tile maps to its 1 × 64 slices.
- **C3** holds for W1: a program on the split layout may batch rows of different one-row units into one `mma.sync` fragment at the same cost.

So `TTOutRowSeed` follows from `TTOutPearlCDevRev1` with no new conjecture. **The rowseed rows stay B**, now as consequences of the per-unit rows.

**What moves is where the per-unit row's evidence has to sit.**
- **The per-unit row must now hold on one-row layouts, where the cap is grindable.** The per-unit rev1 row (B, from 64 × 64 units, the cap and the fragment analysis) must hold where §3's grinding admits the aligned-spike families at 4 draws per row (v2) or about 8–32 (v1 rev1). There the fragment argument alone carries them. The same scope note applies to `tt-out/pearl-c-sm120-rev1` and its tile twin.
- **The fragment argument, under per-row grinding:**
  - **No fully agreeing row turned up.** 0 of 1,536 fresh rows across the six family and layout cells has a joint set shared by its 8 B columns. That puts the per-row rate below about 0.2% (95%).
  - **Finding one costs about 4× the row's credit.** That is about 500 draws at about 0.8% of the row's credit each, and the row would help only one 8-column block. Its other n/8 − 1 blocks read different B columns.
  - **Patching doesn't open a way in.** The patch allowance (a (fragment, atom) is worth skipping with at most 5 of 128 words re-done on generic cores) still needs at least 11 of a fragment's 16 rows in full 8-column agreement.
- **Whole-fragment pricing is load-bearing.** Under a cost model that credited per-word skips, the per-word joint sets (17–24 atoms of 256 on average, up to 56) would undercut far past γ₀ = 1/400. C3 must be read with `w1-complete/sm120`'s whole-fragment `mma.sync` price, as the rev1 row states.

**One cost of C2 to report (completeness, not soundness).**
- **The spread is much wider per row than per tile.** A per-row cap rejects any row whose own debit exceeds ρ. For aligned-spike rows the per-row debit spreads with an SD of 0.024–0.064 points of credit against caps of 0.1 and 0.25, far wider than per tile (§3).
- **Real activations may look like these families.** Their outlier channels sit in the same few channels of every row, like the census's aligned spikes. If they sit near the cap, a per-row cap discards honest rows that an aggregate cap would credit, and the panel's credited work falls.
- **The check to run:** the per-row debit on real Qwen or Llama activations.

## Update 10:50Z: `FragDraw Λ`, measured directly, and its named falsifier

The quantity (bc-3006c44a, "The fragment argument, made rigorous"): Y_i = #{(J, t) : t lies in an undebited skippable set of every word (i, j), j ∈ J}.

**Measured** (`fragdraw_sm120.py`, `r20260930-104124-5023`; k = 8,192, 48 rows per cell, v2 pure and v1 rev1 G = 4, one group of 8 B̃ columns per row).
- **What was counted.** Per word, U_j = the atoms in some jointly skippable pair of that word (neither atom skips alone), minus the replayed debit's flags. That is a lower bound on Y's per-word sets. Y's term for the group is |∩_j U_j|.

| Row | Per-word U_j, mean (max) atoms of 256 | Rows with Y > 0 |
|---|---|---|
| fresh aligned-spikes-r64 | 38–42 (60–78) | 0 of 96 |
| built from B̃: spikes where all 8 columns' codes agree in sign, signed to make all 8 products positive | 38–42 (65–77) | 0 of 96 |
| built from B̃: one sign-matched spike in atom 0, as large as the domain allows | 2–3 (10) | 0 of 96 |
| built from B̃: dense, correlated with the 8 columns | 15–17 (34–47) | 0 of 96 |

**The named falsifier fails.** Building a row against B̃'s 8 columns doesn't raise the intersection: it leaves the per-word sets unchanged, or shrinks them.

**Three corrections to how Λ = 12 was derived from my data.**
1. **The event.** My 0 of 1,536 (10:20Z) counted rows whose 8 words share one common set. Y needs t in some set of each word, with sets that may differ. That is a weaker condition, so the 0 of 1,536 doesn't bound Y. The run above measures Y's own event.
2. **The unit.** Every measurement, mine and the model's, is one (row, column group). Y sums over a row's n/8 = 1,024 groups, so P[Y_row ≥ 1] is not the per-group rate.
3. **The set size.** Under Y's definition the per-word undebited sets are 38–42 atoms on average (maximum 78), not 17–24. So π̄ ≈ 0.16.

**Λ, recomputed with the same column-independence model:**
- π̄^8 ≈ 4.3 × 10^−7 per atom, 1.1 × 10^−4 per group, and about 0.11 per row over 1,024 groups. The Poisson tail at 2^−128 gives **Λ ≈ 20**.
- Taking the largest sets (π̄ ≈ 0.30) gives about 17 per row and **Λ ≈ 90**.
- 0 of 384 measured groups is consistent with both.

**The conclusion survives.** The saving ≤ 372·Λ units per row is **about 0.010% of credit at Λ = 20 and 0.045% at Λ = 90** at 8,192³, against γ₀ = 0.25%. It takes Λ near 500 to reach γ₀.

**Ratings:**
- `FragDraw 12` as derived: **C** (the derivation misreads the data).
- `FragDraw 100`: **B** (CPU, targeted: 384 rows including B̃-built ones, Y = 0 throughout).
- **The rowseed rows stay B.** Their fragment argument holds at Λ = 100 with the saving under 0.05% of credit.
