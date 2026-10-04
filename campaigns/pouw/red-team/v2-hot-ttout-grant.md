---
cursor:
  subagentId: "bc-d7d4b0d1-1778-5220-abe0-789e3131dcab"
---

# TT_OUT grant for v2-hot (`pearl-c-sm120 v2-hot`): both FP32 prices, `HotSizing.publicConst 64`

**Status: WITHHELD, held (16:15Z).** GPU 3's full-unit run failed (§3's FAIL branch): 17 of 64 units keep free-family shapes from H_i in atoms 0–12 (t₀ ≤ 5, at most 2.7% of words). So v2-hot does not avoid the post-add assumption. Its first atoms need either a start atom t₀ or `post-add-bound/sm120`, and bc-3006c44a and bc-b58c6093 are settling which. Nothing here is granted. §3a says what a regrant would name on each path. §1a's four items stand on either path.

**Earlier status: DRAFT, conditional.** Drafted 30 Sep 15:20Z by the independent assessor (bc-d7d4b0d1), for bc-824e54a2's merge of the v2-hot protocol Lean (`internal/pouw/cheap-binding/ttout-lean-staging/v2-hot/`). **Updated 15:52Z** for bc-22298e90's statement review ([`statement-review.md`](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/internal/pouw/cheap-binding/ttout-lean-staging/v2-hot/statement-review.md), 15:35Z): §1a now names the three things the Lean doesn't bind, and the guard `HotStartsSized` needs. The grant becomes final only when both of these hold:
1. GPU 3's full-unit v2-hot run lands and passes (physical GPU 2, running since 15:03Z; §3);
2. FIX 1 is in the store: `HotStartsSized` guarded by `sem.OperandOK` (§1a item 4), before M2b's write-back.

Until then nothing here is granted.

## 1. What is granted

The assessor grants, as a named assumption fit to be cited (rating **B**, CPU, bit-exact), the two TT_OUT statements of `TTOutV2Hot.lean` (snapshot `33bb9265…`, the hash bc-22298e90 reviewed), at **each** of the two records the two-price rule names:

| Statement | Record `d` | Scope (§1a) | Cap ρ | Slack |
|---|---|---|---|---|
| `Pouw.PearlC.Assumptions.TTOutPearlCDevHot CM d sem hot h ρ` | `devSm120v2hot pr₈.₀₀` and `devSm120v2hot pr₈.₃₇₆` | `h = HotSizing.publicConst 64`, and `hot` satisfies `HotStartsSized (publicConst 64) sem hot` with its salt from §1a item 2 | 1/1000 | 1/400, εPearlC |
| `Pouw.PearlC.Assumptions.TTOutTilePearlCDevHot CM d sem hot h ρ` | the same two | the same | 1/1000 | the same |

- **CM** is the W1 cost model at the record's prices. TT_OUT reads no `W_ref`, so the kernel term is 0, as the file fixes. The reviewer checked by unfolding that the assumption at c = 0 is the one at every c.
- **The chain-only forms need no grant of their own:** `TTOutPearlCDevHotChainOnly` and `TTOutTilePearlCDevHotChainOnly` follow from these by the staged proofs `ttOutPearlCDevHotChainOnly_of_ttOut` and `ttOutTilePearlCDevHotChainOnly_of_ttOut`.
- **Published figures these back** (the price twins' value lemmas at `publicConst 64`, cast 8):
  - forming credited: 0.36217% at 8,192³ and 0.35604% at 16,384³ at 8.376, and 0.36161% at 8.00 (`30379/8401000`);
  - chain-only: 0.83709% and 0.59649% at 8.376.
  - They reach a twin's `Gγ` or `GγSampled` only through a composition with the accounting lemma. That composition needs `0 ≤ wrefDevHot`, which the reviewer closed by one `norm_num` at all 32 tile points, the four in-loop points at cast 8 with c < 0 included. A figure cited from this grant cites such a composition, or the `0 ≤ wrefDevHot` lemma the review recommends for M2b.

## 1a. What the grant names that the Lean does not bind

A citation of this grant must meet all four. Without them the statements type-check against a different protocol.

1. **The starts' sizing rule is a condition on `hot`, not on `h`.** The review shows `h` is inert in the assumption: `TTOutPearlCDevHot CM d sem hot (publicConst 64) ρ` and `… colRms ρ` are the same `Prop` (by `rfl`, unit and tile), because `h` enters the protocol only through `W_ref`. So the grant is scoped by the starts' source:
   - `hot` satisfies `HotStartsSized (HotSizing.publicConst 64) sem hot` (after FIX 1, item 4). That is, each row's start exponent is e_i = ⌊log₂(√512 · 64 · fl32(α_i·ρ_i))⌋, the rule of `v2-hot-start-rule.md` (13:05Z).
   - The `h` in that condition is the `h` of the protocol's `W_ref` and of the accounting lemma in the same citation.
   - Column-RMS-sized starts cited with `publicConst 64`'s `W_ref` would type-check. **They are not covered**, nor is any other c₀ or rule.
   - Preferred form: the composed citations take `(hsz : HotStartsSized (publicConst 64) sem hot)` as a hypothesis, so the scope is in the statement.
   - The region model `NoAlignedExactRegionHot` holds H_i inside `rowOf i r`, a function of row i alone. That fits `publicConst 64`, whose H_i reads nothing outside row i. It would not fit a column-reading rule, which is a second reason `colRms` is outside this grant.
2. **The salt of each start:** H_i's sign and mantissa are the first 4 raw bytes of the keyed line hash of row i's `E_A` seed at (side 0, factor 2, line i). `HotStartsSized` constrains only the exponent, and `HotSem.starts` may ignore the oracle, so the Lean doesn't bind this. A source with any other sign or mantissa, or one fixed across jobs, is a different protocol. The measurements in §2 used this source (`pearlc_hot_start.py`, `const` rule).
3. **Both FP32 prices, 8.00 and 8.376 FP8-MAC units,** as two statements. The records `pr₈.₀₀` and `pr₈.₃₇₆` differ only in the FP32 add's price. v2-hot credits U's removal at the record's add price, so TT_OUT at each is a separate statement. The two-price rule publishes the larger γ only because both are granted. A citation at one price doesn't carry the other.
4. **`HotStartsSized` is the guarded one (FIX 1).** As staged, it quantifies over every activation, off-domain ones included. At a row whose scale is 0 the bound `4^e ≤ v` has v = 0 and no solution (`not_hotStartsSized_of_rowScale_zero`). So the honest starts, at 0 on a zero row, don't satisfy it, and a grant scoped by it would cover no honest source. The grant names it only with its body guarded by `sem.OperandOK sh.m sh.k act →`.
   - `publicConst 64` reads no B̃, so the weight guard (`sem.OperandOK sh.n sh.k (U.weight …) →`) isn't needed for this grant. A column-reading rule would need it.
   - FIX 1 moves no pin or read (nothing reads `HotStartsSized` today), but it does move `HotStartsSized`'s type hash. This grant names the fixed definition. Record its hash in §5 on finalizing.

## 2. Why B

- **v2's cap-1,000 rows are B** (08:50Z–11:45Z). v2-hot changes only where each ticket chain starts.
- **The hot start closes v2's chain-start gap per word, under the exact rule granted here** (`ratings.md` 13:08Z; `v2hot_public_constant_sm120.py`).
  - H/acc at t₀ spans 0.064 to 8.2 over every in-domain family pair tried.
  - The hot windows [s, s + w) (s = 0, 1, 2, 4; w = 4, 8, 14) stay below the plain chain's mid-chain windows in every family. The thinnest margin is 1–2 points, on early-light rows.
- **bc-b58c6093's census** (`ttout-restatements.md` §8): no free-family shape at any start 0–16 under `const 64`, with 4.5–12× in rows below the closest shape.
- ~~**The region lemma `no-aligned-exact-region/sm120-unpromoted-hot` is B↑** (12:00Z). Given it, v2-hot needs no `post-add-bound/sm120`.~~ **Superseded 16:15Z:** the full-unit run finds free-family shapes in atoms 0–12 of 17 of 64 units, so the lemma as stated from atom 0 is false for the hot chain (`ratings.md` 16:15Z). It can hold only on windows past the first atoms, and whatever covers those atoms comes into the grant (§3a).
- **U's removal is forced and credited:** U depends on the hot chain's truncation.

## 3. The condition, and its outcomes

**The run:** GPU 3's full-unit v2-hot rerun on physical GPU 2 (bc-0f3f8a2f; bc-b58c6093's fill candidate "Update, 12:30Z"; the 11:50Z server entry, item 4). It covers every free-family width at every start from atom 0, both families, 4 units per family, with H_i built by `pearlc_hot_start.py` under the **`const` (c₀ = 64) rule** and §1a item 2's salt. It must be the `const` rule, not §14's column RMS.

- **PASS** (no free-family shape at any start in any unit, family or width), **and FIX 1 in the store** → **this grant is final as drafted.** v2-hot then needs neither `post-add-bound/sm120` nor a start atom. On landing, the assessor records the run id and the fixed `HotStartsSized` hash in §5 and changes the status line.
- **PASS without FIX 1** → no grant yet. The run's evidence stands, and the grant finalizes when FIX 1 lands, with no re-rating.
- **FAIL** (any free-family shape found) → **the grant is withheld** as stated. v2-hot falls back to the priced family, whose closing term is the pre-add floor (8 W1 per element, measured 14:58Z), not a merge count. The assessor then re-rates v2-hot on that path:
  - the found regions' width and share of MACs;
  - the pre-add closure at those widths, as for v1 at 14:58Z;
  - any grant then also names `post-add-bound/sm120`.
- **INCONCLUSIVE** (the run stops early, uses the column-RMS rule or another salt source, or covers fewer units, families or starts than above) → no grant until a conforming run lands.

## 3a. After the FAIL (16:15Z): the two paths, and what a regrant would name

The run found shapes starting at t₀ ≤ 5 and ending by atom 12, in 17 of 64 units, at most 2.7% of words. None was found starting later.

- **Path 1, a start atom.** The ticket chain's credited windows begin at a pinned atom t₀ past every found shape, and the atoms before it are uncredited.
  - The regrant then names the region lemma restated from t₀, the pinned t₀, and the credit it gives up (at 8,192³, about 13 of 256 atoms if t₀ = 13).
  - Evidence needed: the run's own units show no shape starting at or after t₀. That has to hold at the first atom a free-family shape could use at full width, not only at the starts the run reports, because a sub-window of an exact window is exact too.
  - This keeps `post-add-bound/sm120` out of v2-hot's grant.
- **Path 2, name `post-add-bound/sm120`.** The first atoms stay credited, and the priced family closes them. The closing term is the pre-add floor (8 W1 per element, measured 14:58Z), as for v1 from +0.
  - The regrant then names `post-add-bound/sm120` as a hypothesis beside TT_OUT.
  - Evidence needed: the found regions' widths and share of MACs, and the pre-add closure's margin at those widths (v1's 14:58Z line is the template; v1 closes by ≥ 1.3% at the whole unit).
- **My preference, for the two lanes:** path 1 if its credit cost is small against γ. It leaves v2-hot resting on one region lemma, measured on the chain it credits, with no second assumption. Path 2 is sound too if the margin at the found widths is clearly positive.
- **Unchanged either way:** §1a's four items, both prices, cap 1/1000, and the re-grant triggers in §4.
- **4:52 PM PDT (23:52Z): the no-charge route is back, B conditional** (`ratings.md` 4:52 PM PDT). Clause (c) on the staircase passes: GPU 3 Results 22 finds no window at starts 0–16, and the tightest block is 0.766 of its floor.
  - A regrant names TT_OUT at 1/400 (no Δ), the region row with (a) on the staircase, (b) from t₀ = 17 and (c) measured at starts 0–16, `post-add-bound/sm120-preadd`, and §1a's four items.
  - γ = 0.362% cast 8 / 0.371% packed.
  - It waits on the padded (b) re-search (queued) and on `cancel-pair@t4` at starts 0–3. The derived charge (0.689% packed) is the fallback.
- **20:00Z: the catalogue audit may reopen the no-charge route** (`ratings.md` 20:00Z). Under the fit-aware floors W*(L, M) over the full catalogue, every block Results 19 found at starts 0–2 sits under the floor for its rows.
  - The check to run on GPU 3's arrays: for every M, the widest shared exact set against W*(L, M). If it passes, the 17:30Z row with fit-aware (a) and (c) holds at γ = 0.362% / 0.371% packed, with no Δ.
  - If it doesn't, Δ below is recomputed over the full catalogue.
  - Either way, the free family's shape list is recomputed over the full catalogue first.
- **19:28Z: the derived-charge route** (bc-3006c44a's first-atoms row §5a, 19:10Z) **is rated B, conditional** (`ratings.md` 19:28Z). The uncredited-atom-0 route below is withdrawn.
  - **A regrant on it names:** TT_OUT at the two records at **γ₀ = 1/400 + Δ**, Δ = 0.815/256 of the chain (t_c = 4; pending L = 22–256), as a new Prop with its own statement review and pin; the region lemma (b) from t₀ = 4; `post-add-bound/sm120-preadd` (8 W1) for (a) and for Δ's derivation, with the catalogue and the corrected block table; and §1a's four items.
  - **The credit is unchanged.** γ = 0.680% (cast 8), 0.689% packed, 0.964% as written at 8,192³, and 0.515% at 16,384³.
  - **Conditions:** Δ for L = 22–256 ≤ 0.815 atoms (or Δ becomes their maximum), and GPU 3's rerun at starts 4–5 on the corrected table passes. If it fails, t_c = 6: Δ = 1.475/256 and γ = 0.938% / 0.946% / 1.221% as written.
  - **The per-word draw** (≈ 0.371% packed) remains the better target. This route is the interim.
- **18:40Z route (bc-3006c44a's first-atoms row §5): rating HELD, then withdrawn at 19:10Z** (the coordinator, 18:38Z). bc-b58c6093 does not concur (γ 0.74%, since the honest program still computes atom 0; t₀ = 4 was checked against an incomplete block table), GPU 3 is rerunning on the corrected table, and bc-3006c44a is reconciling. My input for the reconciled route: clause (d)'s 1.23× margin (0.815 atoms saved against 1 uncredited) holds only at the 8 W1 pre-add price. Rerunning `tailcap.py` and `savingcap.py` gives a worst narrow-tail saving of 0.988 atoms at 6 W1 and at 4 W1, and 0.954 atoms at 4 W1 for windows under 8 atoms. So at any price below 8 W1, one uncredited atom has about 1% of margin, and two atoms would restore it.
- **18:18Z: that proposal failed its clause (c)** (GPU 3, `r20260930-173925-45b9`): exact blocks at starts 0–2 over 6–12 atoms, nothing from start 3 on. It is now D (`ratings.md` 18:18Z), and the grant stays held. bc-3006c44a will bring one of three routes: the γ ≤ 0.41% fallback, a restated row, or a per-word mantissa draw. That line lists what each needs. A per-word draw would also change §1a item 2.
- **17:00Z: the proposal on the table is path 2 with t₀ = 6** (bc-3006c44a, `theory-pearl-c-sm120.md` §14, 16:55Z). It uses the free-family lemma for windows starting at t ≥ 6 and the pre-add form of `post-add-bound/sm120` (width floors W*(L)) for windows starting at t ≤ 5. I rated it **B, conditional** (`ratings.md` 17:00Z):
  - GPU 3's widest-exact-width check for L ≥ 8;
  - the pre-add form named as its own statement in the table;
  - the row restated so that narrow regions at any start are closed by the pre-add form.
  - A regrant on it names TT_OUT, the region lemma from t₀ = 6, and `post-add-bound/sm120` (pre-add form). The run is `r20260930-153135-2062`. Still held until the check lands and bc-b58c6093 concurs.

## 4. What the grant does not cover, and what forces a re-grant

**Not covered:**
- other caps: ρ = 1/400 needs its own line;
- other sizing rules or constants, and starts from any other salt source (§1a items 1–2);
- v2 from +0;
- v1-hot (parked);
- any time claim, which is `concurrent-budgets/sm120`'s (v2-hot's time total: ≤ 0.96% on the bound, ≈ 0.363% measured, `ratings.md` 15:24Z);
- the beacon, which the salt and H_i's bytes rest on, as every Pearl-C row does: `beacon-unpredictability` stays its own row;
- bc-7a7109a0's alternative 12-pin set (15:33Z), including `hotUnitAccountingChainOnly_of_pearlCProtocolDevHotChainOnly` and `hotTileAccountingChainOnly_of_pearlCTilesDevHotChainOnly`, until it is staged and has its own statement review. This grant covers the staged files at the reviewed hashes.

**Re-grant if any of these happens:**
- a type hash moves: the statements, `devSm120v2hot`, `pearlCProtocolDevHot`, `pearlCTilesDevHot`, or `HotStartsSized` beyond FIX 1;
- the sizing rule, c₀ or H_i's byte source changes;
- a price changes;
- the cap changes;
- the rev lane's accounting lemmas stop using the same `h` in the protocol and in `W_ref`, or a citation's `hsz` names a different `h` from them;
- the region lemma's scope changes (in particular, if H_i stops being a function of row i alone).

## 5. Record, on finalizing

To fill in when a regrant is made (§3a) and FIX 1 is in the store:
- GPU 3's full-unit run: **FAIL**, reported 16:13Z (17 of 64 units, shapes in atoms 0–12, t₀ ≤ 5, ≤ 2.7% of words). Run id to be recorded from GPU 3's status file;
- the chosen path and its evidence;
- the time;
- the fixed `HotStartsSized`'s hash, and the snapshot M2b writes back;
- the assessor's label on the pin records once they exist: `grant = assessor`, by bc-d7d4b0d1, with this file as ref.
