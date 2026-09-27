---
cursor:
  subagentId: "bc-9e538dc5-64c5-5aad-b845-7ae98c178569"
---

lane: flock-soundness · kind: finding · status: done (03:55Z: proved at `6dc1cd07`, see `ligerito_sound`) · repo: danielreuter/verity · branch `cursor/flock-soundness-8569` · PR #89

# The Ligerito phase: proof plan against `Model.ligerito`, error terms, effort

`ligerito_phase` is the last lemma under `rep_sound`. The other three phases and the shared list size are proved
(commits `4c5b3f41`, `1c19d3d7`, `05447b40`).

**Goal.** Assume `hMCA : BCHKS25Thm46` and `DOp` for the opening's output `(T, b)`, i.e. every level-0 codeword near
`C₀` has `Σ_y f_M(y)·b(y) ≠ T`. Then:

`value (· = true) (ligerito A sch T b C₀) ≤ ofReal (L₀/qF + ligeritoError sch.levels)`.

## 1. The argument, step by step, with its term

The claim at every point is `s = Σ_{remaining vars} ĝ(·)·W(·)`, where:
- `g` is the current level's committed F-table, viewed as a multilinear function;
- `W` is a verifier-known weight that accumulates `b̂`, out-of-domain eq weights and consistency weights.

**The doomed invariant at level ℓ:** for every message `M'` within level ℓ's radius of the committed table `C_ℓ` (a list
of at most `L_ℓ = 25·2^{r_ℓ}`, from `closeMsgs_card_le` generalized to every level), the claim is false for `M'`.

| Model step | Why it stays doomed | Term (`Accounting/Bound.lean`) |
|---|---|---|
| Level-0 OOD (§13.3 step 2): `z₀`, `y₀`, `β₀` | For each `M`, `(T − ⟨f_M, b⟩) + β₀·(y₀ − f̂_M(z₀)) = 0` holds for at most one `β₀` | `L₀/qF` (in `εLig`) |
| `foldRounds` (each level, K coins via `drawK`) | Sumcheck over K per list element: `2/|K|` per round, times the list | `lanes·2L/qK` in `foldError` |
| MCA (same coins) | For `r` outside a set of size `a/|K|` per row pair, a fold close to a codeword comes from rows jointly close on one set (BCHKS25 Thm 4.6, `mcaError` of `AffineLineGenerator`, over K with the level's domain embedded). Paper Lemma 9's row union gives `2^{k−i−1}` pairs at round `i` | `(2^k − 1)·a/qK` in `foldError` |
| Next commitment `C_{ℓ+1}` plus two OODs (`twoOod`) | Two distinct list elements agree at two random points in `F^μ` with probability at most `(μ/|F|)²` (`μ = logCols + lanes`). So at most one list element matches both OOD answers | `pairs(L')·(μ/qF)²` |
| The OODs' `β₁`, `β₂` | Elements that miss an OOD answer: adding `β·(claim − truth)` keeps the claim false except for one `β` each | `2L'/qF` |
| Queries on level ℓ (`queryAndBatch`) | The unique OOD-consistent `M'*` either is the split-fold of a level-ℓ list element (then the sumcheck part is already false), or, by MCA, the fold of `C_ℓ` is `γ`-far from `M'*`'s encoding. Then the stratified queries miss the disagreement with probability at most `(1−γ)^Q`, by AM–GM over each summand's strata with `lo_balanced` | `(√ρ + η)^Q` (`queryError`), once per level |
| Consistency coins `α` | A nonzero vector of per-query mismatches, weighted by `eq(α)`, is a nonzero polynomial of degree `⌈log2 Q⌉` | `L'·⌈log2 Q⌉/qF` |
| Claim batching `β` | As for the OODs | `L'/qF` |
| Last level (`lastLevelError`) | Folds, queries against the clear residual `yr`, `α`, `β`; no list | `foldError L + queryError + ⌈log2 Q⌉/qF + 1/qF` |

The final check (§13.6) accepts only if `s` equals `Σ_y res[y]·(yr[2y] + u·yr[2y+1])`. The invariant makes that false,
because `res[y]` is the accumulated weight `W` at `(orig ‖ bits y)`. That identity is pure algebra:
- `cff(c) = 1 + c·(1 + u)` is the split coordinate's weight `(b ? u : 1)`, extended at `c`;
- `Π(1 + z + f)` is `eq(z, f)` in characteristic 2;
- the consistency factor is `MLE(X̂(ω_q))(p) = Π_i (1 + p_i·(1 + Ŵ_i(ω_q)))`, which follows from `Arith.Xhat`'s product
  form (§13.4).

## 2. What it needs beyond today's development

- **One new `Arith.Correct` fact:** `ofLimbs` is a bijection `F × F → K`, so `drawK` is uniform on K. I have asked lane
  `flock-verifier` for it (`note:20260927T0200Z-handoff-from-flock-soundness-arith-facts`).
- **A bridge from VCVio's `Pr{let x ←$ᵗ S}[·]` to `prCoin`**, to apply `mcaError`.
- **Generic lemmas.**
  - The list size at every level: reuse `ListSize` with the level as a parameter.
  - The K-valued fold rounds with a list: like `value_lincheckRounds_le`, but with a list invariant.
  - Stratified queries.
  - α batching over `eqList`: a nonzero polynomial of degree `⌈log2 Q⌉`.
  - β batching: `prCoin_linear_le`.
- **The weight algebra and the final-check identity.** This is the largest single piece.
- **The game assembly through `recursiveRounds`**, by recursion on the level list, matching `ligeritoError`'s
  recursion.

## 3. Effort and order

Roughly 3,000–4,000 lines of Lean, about as much as the rest of the development. In order:
1. generic lemmas (list size per level, `drawK`, β and α batching, stratified queries);
2. the MCA bridge and the per-round fold lemma;
3. the weight algebra and the final-check identity;
4. the per-level transition lemma;
5. the assembly.

Items 1 and 2 are independent of the weight bookkeeping and can start now.

**Open points to settle while writing:**
- `foldError` uses `max(L_ℓ, L_{ℓ+1})`. The sumcheck needs only `L_ℓ`, so the model's bound is conservative, and the
  proof may use either.
- The message after the last challenge is absorbed but unused (§13.3). It needs no term.
- The level-0 OOD claim has no round message (`split = none`). Its weight enters `W` directly.

## 4. Progress and the weight bookkeeping design (update, 2026-09-27 02:55Z)

**Proved and pushed** (all on the standard axioms only):

| Lemma | File | What it covers |
|---|---|---|
| `card_close_le` | `ListSize.lean` | the list size at every level |
| `value_drawK_le` | `LigeritoCoins.lean` | uniform `K` coins, via `Arith.Correct.ofLimbs_bijective` |
| `prCoin_fromMsg_le` | `LigeritoCoins.lean` | a round over `K` |
| `prCoin_eqList_le` | `LigeritoCoins.lean` | α batching |
| `prCoin_positions_miss_le` | `LigeritoQueries.lean` | stratified queries: `(1 − δ)^Q` |
| `prCoin_mca_le`, `rowsAgreeOn_of_fold`, `rowsAgreeOn_of_foldAll`, `foldAllRows_eq_sum` | `LigeritoMCA.lean` | the BCHKS25 coin bound and the fold rounds' agreement |
| `value_foldRounds_mca_le` | `LigeritoMCA.lean` | the folds' MCA events: `(2^k − 1)·ε` |
| `prCoin_level_mca_le` | `LigeritoLevels.lean` | every fast100 level meets the assumption, with `ε = mcaA/qK` |
| `value_twoOod_collide_le` | `LigeritoOOD.lean` | out-of-domain binding: `pairs(L)·(μ/|F|)²` |
| `value_foldRounds_sum_le`, `value_foldRounds_sum_invariant` | `LigeritoFolds.lean` | the folds' sumcheck part against a list: `k·2L/|K|` |

**The weight bookkeeping (remaining).**
- **The claim.** At every point it is linear in the current table: `s = Σ_y embed(g(y))·W(y)`. Here `g` is the level's
  table (the split F-table, or its K-valued fold) and `W : ℕ → K` is the claim's weight.
- **Doomed.** For every list element `M` of the current level, `s ≠ Σ_y g_M(y)·W(y)`.
- **The transformations**, each matching one model step:
  1. **Level 0.** `W₀(y) = embed b(y) + embed β₀·eqList(z₀, y)`, from `ligerito` steps 1–2.
  2. **Folds** (`foldRounds`). Both `g` and `W` fold, lowest variable first (`foldLoL`), and `value_foldRounds_sum_le`
     does the work. The folded table of `M` is its `eq`-weighted row sum, which ties it to `foldAllRows` and the MCA
     lemmas.
  3. **Split** (the next commitment). `G(y) = g(0,y) + u·g(1,y)` and `W^s(b, y) = (b ? u : 1)·W(y)`. Folding the split
     coordinate at `c` gives `cff(c) = 1 + c·(1 + u)`, in characteristic 2.
  4. **An out-of-domain claim.** `W += embed β·eqList(z, ·)` on the new table, and `s += β·y` (`twoOod`).
  5. **The consistency claim.** `W += embed β·(b ? u : 1)·Σ_j eq(α)_j·X̂_·(ω_{pos_j})`, where `e` comes from the opened
     rows (`queryAndBatch`). The multilinear extension of `c ↦ X̂_c(ω)` at `p` is `Π_i (1 + p_i·(1 + Ŵ_i(ω)))`, by
     `Arith.Xhat`'s product form and one general identity: `Σ_c eq(p, c)·Π_i f_i(bit_i c) = Π_i ((1+p_i)·f_i(0) +
     p_i·f_i(1))`.
- **The final-check identity.** After the last folds, `W_final(y) = res[y]` of `Model.finalCheck`:
  - `bHat(orig ‖ bits y)·Π cff` is transformation 1, carried through every fold and split;
  - the out-of-domain terms and their `scale` come from transformation 4, with the later splits' `cff` factors;
  - the consistency terms come from transformation 5.
- **The per-level transition.** From doomed at level ℓ to doomed at level ℓ+1 (or to rejection at the last level), with
  error `midLevelError ℓ ℓ'` (or `lastLevelError ℓ`). It runs through the steps in this order:
  1. folds: sumcheck plus MCA;
  2. next commitment and its list;
  3. out-of-domain binding;
  4. the out-of-domain batching coins;
  5. queries;
  6. α;
  7. β.

  The one non-algebraic case is the query step. If the unique out-of-domain-consistent `M'` is not the split-fold of a
  level-ℓ list element, MCA plus `rowsAgreeOn_of_foldAll` make the fold of `C_ℓ` `γ`-far from `M'`'s level-ℓ
  encoding, and `prCoin_positions_miss_le` applies.
- **Order of the remaining work:**
  1. the general product identity, plus the `cff` and `X̂` corollaries;
  2. the weights as functions of `LigState`, and their step lemmas;
  3. the final-check identity;
  4. the per-level transition;
  5. the recursion over `recursiveRounds` and `ligerito_phase`.
