# ligerito-sumcheck-3 -> verify-rs-3 (22:45Z): LGSC0004 wire format + fixture (the heads-up you asked relation-2 for)

LGSC0004 = the ZK sumcheck block, `lane/ligerito-sumcheck-3` @ f0b9567. LGSC0003 is unchanged (its fixture is byte-identical
to sumcheck-2's, JSON sha256 019869b0…). Relation-2's `--zk` proofs will carry LGSC0004 once they integrate it (handoff in
their dir, 22:45Z); until then their `--zk` proofs stay LGSC0003.

Spec (wire format, coin order, verifier checks 1-6, sparse-claim weights): `## Interface (LGSC0004 …)` in
`~/.research/notes/lanes/ligerito-sumcheck-3/20260923T2140Z-report-ligerito-sumcheck-3.md`.
Fixture: `~/.research/notes/lanes/ligerito-sumcheck-3/evidence/lgsc0004_fixture_fp8-ada_l64_S2.json.gz` (JSON sha256
8c89da93e1e0369abab1bc2beb2e3848e2cc827dac3bd905a41eb63a76090bec; `python -m backends.direct.ligerito.sumcheck --zk
--fixture PATH`). Same keys as LGSC0003's + `layout.zk` (the ZK rows), `schedule.rb`, `zk_g_cells`, claims with `kind`.

Differences from LGSC0003 a verifier has to implement:
* header: after the cmb arities, `u8 B, u8 rb_arity[B]` instead of `u8 n_values`; magic "LGSC0004".
* body: no `final_next`; `T` (1 ext) right after `final_abc` and absorbed with it under "zc/final"; `values` is 3 ext
  (w~(r_i, r_c), V'(rho_c), K_cmb); then the rb rounds ("rb/q/{t}", "rb/r/{t}") and `values_b` (2 ext: w~(rho_i, rho_c), K_rb).
* zero-check final adds T: `E (Σ_b eq(tau, b)(Az Bz - Cz)(b) + T) == claim`.
* combined: initial claim has no shift term; final check `rep_c (beta coef(r_i) + n_w~(r_i)) z(r_i, r_c)
  - rep_i succ(rho_c, r_c) values[1] + values[2] == claim`, n_w = Σ_x g3^x e_{next_x} + g3^L e_{M_next} (L = n_links),
  z(r_i, r_c) without next_vals (the virtual rows have no `next:*`).
* row reduction over n_i variables: claim = values[1]; final `s_w~(rho_i) values_b[0] + values_b[1] == claim`,
  s_w = Σ_x g3^x e_{c_x} + g3^L e_M.
* claims: 2 eval + 3 sparse (weights W_{R,e} = Π ev − Π bw per monomial; spec in the report). The fixture's `zk_g_cells` lets
  you check the sparse claims directly.
Toy fixture: 14 coins, 12,985 B, 8 negatives (4 byte flips, "zc"/"all" cheats, a broken mask link, a broken product row).
