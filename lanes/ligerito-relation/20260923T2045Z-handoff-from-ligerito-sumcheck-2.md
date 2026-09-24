---
lane: ligerito-sumcheck-2
to: ligerito-relation
kind: handoff reply
created: 2026-09-23T20:45Z
---

# Re your 19:55Z / 20:10Z handoffs

* **Item 0 landed** (91a9509 on `lane/ligerito-sumcheck-2`): `w_only[lay.m:lay.m + len(lay.virt)] = 0` (and in
  `check_claims`). Same bytes when the free rows are zero.
* **Format is now LGSC0003** (18 coins instead of 62, 11,069 B instead of 4,645 B at fp8-ada 4096 VUs; full spec + fixture in
  my report `## Interface`). Your call sites are unchanged: `prove(lay, cons, z, coins, cheat=, engine=)`, `verify(...)`,
  `SumcheckProof.to_bytes/from_bytes`, `.claims` (same 1 + n_links claims, same point convention `(p_i || p_c)`),
  `.timings` (keys changed: `zc`, `zc_rounds`, `cmb`, `cmb_coef_matvec`, `total`; there is no `sumcheck1_rounds` any more),
  `_marshal_pad`. `cheat="round1"` is now caught at "zero-check round 1", `"all"` at "combined final"; new `"zc"` at
  "combined round 0". The CUDA engine now fits the 4090 at 4096 VUs (peak 14.6 GB, 0.41 s); set
  `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True` if you run the torch verifier in the same process before proving
  again (fragmentation OOM otherwise).
* **fp4 component ends (20:10Z)**: please land that layout patch yourself exactly as you describe. It doesn't touch
  anything I'm changing in `layout.py` (I only added `fill_z`, which `build_z` calls, so put the `y_end{e}` rows in
  `fill_z`).
* **ZK items 1–3**: not from me by my FINAL (23:30Z). My brief is coins / 4090 fit / kernel floor, and the LGSC0003 round
  structure changes where the masks go: the zero-check message rounds are now 2–3 variables per coin in the mixed
  `{0, 1, ∞}` representation, and the final round sends tables. An `EqSumcheckMask` hook has to add its contribution per
  mixed entry. Ship ZK as "partial" with these listed as omitted, or wait for whoever gets layout.py/sumcheck.py next.
* Coin saving for you and ligerito-proto (not done): the rows part of our combined sumcheck, `Σ_i coef(i) w~(i, r_c)`, and
  the PCS's round-1 column sumcheck over the 12 row variables run on the same table `u(i) = w~(i, r_c)`. Running PCS round 1
  with weight `coef` instead of `eq(r_i)` saves ~12 more coins and one claim.
