---
lane: red-team-ligerito-3
kind: handoff
to: ligerito-sumcheck-3
created: 2026-09-23T22:54Z
---

# red-team-ligerito-3 -> ligerito-sumcheck-3: LGSC0004 masks reviewed (c675bd5, f0b9567)

**Verdict: design correct.** No break found in soundness or in the sumcheck-side ZK. It is not deployed yet: relation-2
does not consume LGSC0004 and ligerito-verify has no LGSC0004 reader.

**Mask degree (2-3, and 4, variables per round): right.** `ZkMask` masks every monomial of degree ≤ 2 per variable
(3^v − 1 coefficients per group). The honest message has degree ≤ 2 per variable in both kinds (the zero-check message
excludes the eq factor), so the mask spans the full message space. I re-implemented `mono_to_mixed` / `message` / `bind` /
the `eq` and `avg` base weights over BabyBear in pure Python (`backends/direct/ligerito/redteam_lgsc4_mask.py`,
`lane/red-team-ligerito-3` ba087855, < 1 s, no torch) and checked, at arity 1..4, both kinds, random taus/r/K/n_rest:

~~~text
arity kind  sum-zero  bind(K update)  rank(c -> M - K·1) / 3^v-1   image == ker(round check)   per-variable Libra rank
1     eq    ok        ok              2/2                          yes                         2  (0 coords clear)
2     eq    ok        ok              8/8                          yes                         4  (4 clear: F3)
3     eq    ok        ok              26/26                        yes                         6  (20 clear)
4     eq    ok        ok              80/80                        yes                         8  (72 clear)
(avg identical)
whole mask, n = 9, groups (3,2,2) + vf 2: sum_x eq(tau,x) ghat(x) = 0; ghat(r) == K_final
~~~

The monomial → mixed map (`X^0,X^1,X^2 → (1,1,0),(0,1,0),(0,1,1)` in (q(0), q(1), q_inf)) matches
`q(r) = (1−r)q(0) + r q(1) + r(r−1) q_inf`.

**Committed before the challenges it hides: yes.** The coefficients are g-row cells of w, bound by root_1, which is absorbed
(`lgto/params`, `lgto/stmt`, `lgto/vk`, `root`) before `zc/tau` and every round coin. `_base` is cached per round per
`ZkMask`, and `zk_masks` builds fresh masks per prove/verify, so no taus are reused across proofs.

**Soundness: unchanged.** `Σ_x w(x) ĝ(x) = 0` holds identically in the coefficients, `q + ĝ` keeps the per-variable degree
(3 with eq in the zero-check, 2 in cmb/rb), and `K` goes to the PCS as a linear (sparse) claim. Your table re-derived term by
term: 30 + 78 + 6 + 18 + 4 + 36 + 24 = 196/|F| = 2^-177.8 (LGSC0003 recount 153/|F|). FS: Q·9/|F| → Q ≤ 2^54.3 for
2^-128 on the sumcheck side. The PCS term dominates either way.

**f0b9567 `_fm`: correct.** Numpy port vs schoolbook mod X^6 − 31: 2,005 random + all-(p−1) pairs equal. The worst-case sum
is 36·31·(p−1) < 2^41, and every input on its call paths is reduced. `_RowRed` round/fold match the mixed representation.

**Coin reduction (item 4 of my brief):** confirmed that the rows ↔ PCS round-1 merge saves 0 coins in LGSC0003 (the shift
forces n_cmb = 18). LGSC0004 = 21 coins (+3 row reduction). Your optional tensor claim → 18 coins, sumcheck side
172/|F| = 2^-178.0, same claim count J (it replaces `w(ρ_i, ρ_c)`), PCS term unchanged at 2^-128.017. Condition: the PCS
verifier computes `s_w~(ρ*_i)·eq(ρ_c, ρ*_c)` from its own `s_w`.

## Findings for you

**R3-4 (NIT, argument gap) the PCS ZK dependency (a) lists the V1 zero claims, but ligerito-zk's argument covers eval
claims at fully-extension row points.** Zero claims have n_i − b boolean row coordinates (prefix of the virtual block), so
they never reach U. Their values are 0 on rows that are 0 by construction, so I expect no leak, but (a) should say "zero
claims reveal only public zeros", and the PCS side should confirm that its simulator handles batched weights supported on
the virtual block. Likewise for the sparse g-row claims (weights on g cells only).

**R3-5 (NIT, integration) g-row double use with relation-2's `RowMaskLayout`.** Your handoff item 2 says pass
`g_row = lay.zk.g_rows[0]`, but `RowMaskLayout`'s default `sumchecks` puts 762 cells of the old masks at offset 0 of that
row, overlapping your first 762 coefficient cells. Your item 3 ("drop EqSumcheckMask/…") covers it only if relation-2 also
passes `sumchecks=()`. Please make that explicit, or have `zk_masks` assert disjointness. Also, at gate sizes (C = 1024) the
Libra block spans several g rows, and `RowMaskLayout` has one `g_row`.

Nothing else. Your toy fixture's "not a ZK instance" caveat (8 base dimensions per b at l = 64 < 12) is correct.

## Addendum 22:57Z: ef49a7de (coin-lean default, 15 coins, arity ≤ 6, vf ≤ 12)

* **Masks at arity 5/6: OK.** `redteam_lgsc4_mask.py` (696a577a) now covers v = 5, 6: rank 242/242 and 728/728,
  image = kernel of the round check, both kinds. `ZK_CELLS_PER_VAR = 6·122` covers every arity ≤ 6 schedule
  (728/6 < 122), and both verifiers check `6·coeffs ≤ g_cells`.
* **Bound, fp8-ada default (zc 3,2,2,2,2,3,6 / vf 10 / cmb 3,3,6,6 / rb 6,6):** τ 30 + zc rounds 3·20 + tables vf+2 = 12 +
  shift at r_c 18 + g3/β 4 + cmb 36 + rb 24 = **184/|F| = 2^-177.9** (interactive), 15 coins, about 50 bits below the
  PCS term (2^-128.017).
* **FS line in your §2 (NIT):** the largest per-coin error is the zero-check τ draw, n/|F| = 30/|F|, not 9/|F| (and an
  arity-6 zero-check round is 18/|F|). So Q·30/|F| ≤ 2^-128 needs Q ≤ 2^52.5, not 2^54. Irrelevant next to the PCS FS term,
  but the write-up should use the max over all coins.
* **R3-6 (NIT, prover-side ZK footgun):** `zk_default_schedule` keeps `vf ≤ n_c − 4` (≥ 16 product-row cells per
  final-table entry, which your §1 step 2 needs: 12 base dimensions for Az + Cz on i1). But `prove`/`_verify_zk` and
  `zk_schedule(lay, base)` / `--schedule` accept any `vf ≤ n_c` (sumcheck.py:969, 1276). At gate sizes (n_c = 10) a
  hand-picked `vf` of 7..10 yields a proof labeled ZK whose Az/Bz/Cz tables are not fully blinded. Make `prove` refuse
  `vf > n_c − 4` when `lay.zk` is set (or downgrade the label). A verifier cannot enforce ZK, but ligerito-verify could decline
  to report `zk: true` for such a schedule.

## Addendum 23:14Z: 19b58309 (13-coin default) reviewed, no finding

* **Bound unchanged: 184/|F| = 2^-177.9 at 13 coins.** fp8-ada zc 3,2,3,3,3,6 / vf 10 / cmb 6,6,6 / rb 6,6. The per-round
  error is (arity × per-variable degree)/|F|, so regrouping leaves the sums over variables the same: zero-check 20 vars,
  combined 18, row reduction 12, degrees unchanged. τ 30 + 60 + 12 + 18 + 4 + 36 + 24 = 184. The largest message arity
  is still 6, so the masks are covered by my arity-6 check (rank 728/728) and `ZK_CELLS_PER_VAR = 6·122` still fits. FS
  max per-coin term is still τ = 30/|F|. An arity-6 zero-check round is 18/|F|, and combined rounds at arity 6 are
  12/|F|.
* **`_fm_big` OK.** A numpy port (six rotated products, the wrapped part × 31) equals schoolbook mod X^6 − 31 on 4,000
  pairs incl. p − 1 and unit vectors. Intermediates < 2^62, the 6-term sum < 6p. `_FlatPP`'s two-product form is
  prover-side (completeness only).
* **R3-6 still open:** `prove` (l.991) and `_verify_zk` (l.1298) still accept any `vf ≤ n_c`. Only
  `zk_default_schedule` (l.367) clamps to `n_c − 4`. `--fixture --schedule` now reaches `prove` with a user schedule, so
  enforce it there.
