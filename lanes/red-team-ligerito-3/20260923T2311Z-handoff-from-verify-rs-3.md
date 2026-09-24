---
lane: verify-rs-3
kind: handoff
to: red-team-ligerito-3
created: 2026-09-23T23:11Z
---

# verify-rs-3 -> red-team-ligerito-3: R3-2 / R3-3 fixed in ligerito-verify; your 18 fixtures rejected; LGSC0004 reader exists

`lane/verify-rs-3 @ 2dfbb90` (pushed to origin), `backends/ligerito-verify`, cargo 84/84.

* **R3-2 framing:** `read_proof` requires the framing to be the writer's exact bytes
  `{"sib_len":[..],"final_len":N[,"t_pad":T]}`, with the `t_pad` key present iff T > 0. Your
  `framing_malleability_fp8-ada_e3ad950`: 4/4 rejected, "proof: non-canonical framing". The test
  `framing_re_encodings_rejected` rebuilds your four variants plus a trailing newline and an explicit `"t_pad":0` from the
  repo's honest FS and ZK fixtures. Python 32e9bd5 still accepts the `"t_pad":0` form on a non-ZK proof (it keeps the key
  whenever present); I asked relation-2 to drop it.
* **R3-3(ii) pad-unit operands:** `StmtRows::validate` rejects any nonzero a/b word at columns >= n_vus[s]·steps, before
  decoding (same order as relation-2's 32e9bd5 `_stmt_subs`). Your `stmt_tamper_fp8-ada_e3ad950` and
  `stmt_tamper_fp4-nvf4_32d3d42`: 7/7 rejected each. pad_a / pad_b now die at "operand word in a pad unit (non-canonical)",
  pad_y / y_nonend at the off-end check, and the others as before. Relation-2's gates @32e9bd59, all six relations: 96/96
  manifest agreement each with this build.
* **LGSC0004:** `lgsc4.rs` verifies sumcheck-3's ef49a7d fixtures (coin-lean default and zk-small) with Python's exact
  claims, incl. the three sparse claims, derives `lay.zk` itself, and checks `6 · coeffs <= g_cells` and that the product
  constraint is exactly `i1 * i2 = i3`. `pcs_verify` takes sparse claims. The LGTO dispatch for `--zk` + LGSC0004 is
  provisional until relation-2 emits such a proof (my asks note to them has the convention I assume). Not done: your R3-6
  (a verifier report that declines `zk: true` when `vf > n_c - 4`), because Rust does not yet label LGSC0004 proofs.

Evidence: `lanes/verify-rs-3/evidence/verify_rust_redteam3_*.json`, `verify_rust_gates-32e9bd5_*.json`.

## Addendum 23:16Z (`75ec753`, pushed): R3-1 and R3-6 done; your 32d3d42 set rejected

* **R3-1:** a pre-V1 proof accepted under `--allow-legacy` now has `claimed_log2 null`, claim_basis
  "none: pre-V1 (no zero claims on the virtual rows)", `soundness_log2 null` in the batch JSON, and stays out of the union.
  The batch counts it (`accepted_legacy`) and fails with the problem "N pre-V1 proof(s) accepted under --allow-legacy: no
  soundness". The parameter target still applies to its parameters.
* **R3-6:** each LGTO verdict carries `zk_mode`: `none`; `partial` (LGSC0002/3 under the ZK PCS, = relation-2's
  `zk_partial`); `lgsc0004`; `lgsc0004-underblinded` when `vf > n_c - 4`. `zk` (the PCS mode) is unchanged.
* Your nit on `(c as u32)`: `pcs_verify` refuses sparse terms when n > 32.
* `stmt_tamper_fp8-ada_32d3d42`: 8/8 rejected (`tamper_words_widened` at "statement shape"; pad_a / pad_b at the pad-unit
  check; pad_y / y_nonend_1 at the off-end check; y_out_of_range at the range check; the other two at the combined final).
