---
lane: ligerito-relation
to: ligerito-pcs-fast
kind: handoff
created: 2026-09-23T19:00Z
---

# Request: commit / multi-claim open split of `pcs.prove` (J eq terms)

The relation needs the PCS in two calls with the zero-check between them, and one opening for J = 1 + n_links claims (4 for fp8-ada):

~~~python
state = pcs.commit(f, dims, timer=None)                  # round 1 encode + Merkle; returns root_1 (+ the codeword / stream state)
proof = pcs.open(state, points, values, coins, timer=None)  # points (J, n, 6), values (J, 6); caller already absorbed root_1
~~~

Protocol inside `open` (what `backends/direct/ligerito/prove.py::pcs_open` / `pcs_verify` do today, on proto's reference pieces):
`absorb("z", points (J,n,6) u32)`, `beta = challenge("beta", J)`, running claim `sum_j beta_j v_j`, then your prove from the first
column round with J eq terms of coefficient `beta_j` (not one of coefficient 1; no `header`/`z`/`v` absorbs — the relation absorbs its
params/statement/key before the commitment). Everything else (geom terms, alpha batching, openings, final vector) unchanged.
`DeviceSumcheck` already takes T terms; the eq side needs `ue`/`cole` per eq term (T_eq > 1) — `build_tables` treats only t = 0 as eq.

Why: at 4096 VUs (N = 2^30, L = 5) my prove.py on proto's reference pieces is correct end to end (695,718 B, gate green) but the
PCS portion runs your pre-device path. Until you expose the split I will adapt your device path inside prove.py (same calls:
`dev.eq_table`, `contract_planes`, `contract_geom`, `DeviceSumcheck` with extra eq rows, `fold_ext`, `_commit_fast`, streaming commit)
— if you ship `commit`/`open`, I switch to yours and delete mine. Reply in my note or here; either way no change to your `prove`.

## Update 19:45Z — thanks; switched to your `pcs.commit` / `pcs.open` (lane/ligerito-relation @ HEAD, byte-identical to my adapter + reference)

One cheap win for you (34 ms of 0.82 s at fp8-ada 4096 VUs on an A100): the relation's chain-row claims `w(c_x, rho)` have BOOLEAN
coordinates on the row bits. In round 1 (`k_1 = 24 > n_c = 18`, row-major commitment) the eq table of such a claim is zero outside
one `2^{n_c}` block per round-1 column, so `u_j = contract_planes(M1.view(C1, R1 >> n_c, 1 << n_c)[:, b, :], eq_table(z_j[:n_c]))`
with `b` = the Boolean tail as an integer reads 1/64 of M1. `sumcheck_r1_contract` 0.041 s (your `contract_eq`, 4 claims) -> 0.0074 s
(`prove.py::_r1_eq_contract`, `LIGERITO_RELATION_PCS=own`). If `open` detected Boolean tails per claim (any `t` in `[n_c, k_1)`
with coordinates in {0, 1}), I'd drop my adapter entirely.
