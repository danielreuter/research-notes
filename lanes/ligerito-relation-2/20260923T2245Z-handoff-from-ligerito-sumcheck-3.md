# ligerito-sumcheck-3 -> ligerito-relation-2 (22:45Z): LGSC0004 (ZK sumcheck) is ready to consume

Branch `lane/ligerito-sumcheck-3` @ f0b9567 (`backends/direct/ligerito/{layout.py,sumcheck.py,sumcheck_zk_test.py}`; the
fp4 `y_end` patch from your 4d9d92c is in as 3d5a731). Full spec + ZK argument + soundness: my report
`~/.research/notes/lanes/ligerito-sumcheck-3/20260923T2140Z-report-ligerito-sumcheck-3.md` (## Interface, §1, §2).
The non-ZK path (LGSC0003) is byte-identical to sumcheck-2's 1fbbe86: nothing changes for your non-ZK gates.

What `--zk` needs to do on your side (no PCS file of yours was touched):
1. `lay = layout_for(sys, l, S, zk=True)`; after `fill_z` of every sub-batch, `fill_zk(lay, z, key)` (key = a per-proof
   secret, 32 B; None = os.urandom). It fills U (8 rows), the g row, i1, i2, M (ChaCha20 mask_sampler), i3 = i1·i2 and
   M_next = shift(M). `prove`/`verify` switch to LGSC0004 on `lay.zk` (mismatch = reject).
2. Build the PCS's `RowMaskLayout` from `lay.zk`, NOT from `default_row_mask_layout`'s `[m-4, m)`:
   `uniform_rows = lay.zk.uniform` (= rows R-8..R-1, the same rows your default uses), `product_rows = (lay.zk.product,)`,
   `g_row = lay.zk.g_rows[0]`. fp8-ada: next 4079-4081, M 4082, M_next 4083, product 4084-4086, g 4087, U 4088-4095; all in
   the free region above the virtual block. The product constraint is already in `constraints(...)` (slot `lay.zk.k_product`).
3. Drop the sumcheck-side `EqSumcheckMask` / `SumcheckMask` / `libra_block_claim` for this sumcheck: LGSC0004 masks every
   monomial of every multi-variable round itself (the old 1 + dn masks leave the cross terms bare: red-team F3 in general).
   Its Libra coefficients are the first `6 · 584` cells of the g row (7200 reserved); cells >= 7200 of that row are uniform
   and free for any PCS-side use.
4. Claims from `verify` (and `proof.claims`): `EvalClaim w(r_i || r_c)`, `EvalClaim w(rho_i || rho_c)` (both extension row
   points: they reach U), and three `SparseClaim(rows, cols, weights (T, 6), value)` on the g row (T = 6 x coefficients:
   1128 / 936 / 1440 at fp8-ada) -> proto `open(..., sparse=[(f_index(rows, cols), weights, value)])`. `check_claims(lay, z,
   claims)` checks both kinds against z for your prover-side asserts.
5. V1 zero claims: `[m, m + len(lay.virt))` as you already do under ZK. Note `lay.virt` has no `next:*` in the ZK layout (the
   next rows are committed at `lay.zk.next`), so the virtual block is n_links rows shorter than the LGSC0003 one.
6. Coins per batch 21 (LGSC0003 18): +3 for the row reduction that replaces the per-link claims `w~(c_x, rho_c)` (a leak).
   Prove time on the 4090 at 4096 VUs: 0.155 s vs 0.137 s; same 14.45 GB peak; proof 15,800 B vs 11,069 B.

Optional PCS change (yours to decide; would save those 3 coins): a TENSOR claim type in the PCS,
`Σ_i s_w(i) w~(i, rho_c) = V'` with `s_w` a sparse row-weight vector (4 nonzeros: g3^x on c_x, g3^L on M) and a column
point; the batched weight's MLE at the PCS's final point is `s_w~(rho*_i) eq(rho_c, rho*_c)` (cheap). Then LGSC0004 would
send V' only and skip the row reduction. ZK needs your PCS argument to cover a claim whose row weights touch the uniform
row M (not U): I have not checked the PCS side. Say if you want it; the sumcheck side is ~20 lines behind a flag.
