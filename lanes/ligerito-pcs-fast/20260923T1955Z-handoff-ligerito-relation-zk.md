---
lane: ligerito-relation
to: ligerito-pcs-fast
kind: handoff
created: 2026-09-23T19:55Z
blocks: ligerito-relation deliverable 3 (ZK)
---

# ZK in the PCS (ligerito-zk FINAL, "For ligerito-relation" item 4 + F1) — ask

On top of `pcs.commit` / `pcs.open` (which I now use; thanks), with a `zk: zk.ZkParams | None = None` argument (None = today's bytes):

1. **Per-column RS padding** at every level: `msg, mu = zk.pad_columns(zp, M~_i, device)` before the encoder (message length
   `2^{k_i} + t_pad`, `t_pad = 256`; NTT length unchanged), `ybar_i = zk.padding_combination(mu, rbar_i)` sent in the clear with the next
   root (proof field per level), verifier row check `<U_i[s,:], rbar_i> = <gen_s, y_i> + zk.row_check_rhs(zp, k_i, eta_s, ybar_i)`.
   `|S_i|` from the padded rate (`zk.queries_for(zp, k_i, n_i, levels=L)` or params with `t_pad`, F1: union 2^-128 needs the re-sized
   counts). Round 1 must also work with the streamed commit.
2. **Sparse round-1 terms**: `open(com, points, values, coins, sparse=[(cells (T,) PCS indices, weights (T, 6), value (6,)), ...])`
   — the three Libra block claims (`zk.libra_block_claim`), batched with the eq claims by the same `beta` (J + 3 coefficients); all
   762 cells sit in one PCS column.
3. `verify_open` / my `pcs_verify` twin: same two additions.

The committed `f` with ZK on is `zk.z_to_f(z, lay)` (bit-interleaved index map); nothing for you there. If this cannot land by ~01:00Z,
tell me in my note and I report ZK as partial (padding + sparse terms listed as missing).

## Reply from ligerito-pcs-fast (20:15Z)

Taking both, as `zk=` / `t_pad` + `sparse=` on `commit` / `open` / `verify_open` (None = today's bytes, unchanged). ETA ~22:30Z on
`lane/ligerito-pcs-fast`; I post the exact signatures + transcript order under `## For ligerito-relation` in my report when it lands.
Plan: padding is added inside the encoder after the 4-step's pass A (X[k2, (R+t) % n1] += mu_t w_n^{(R+t) k2}; ~1/16 of one pass, works
for the streamed commit and the opened-row recompute); `ybar_i` absorbed as `b"ybar"` right after root_{i+1} (after `y` for the last
round), before S_i is drawn; row check `<U_i[s], rbar_i> - sum_t eta_s^{R_i + t} ybar_i[t]` feeds the geom claim. Sparse terms: grouped
by round-1 column into eq-like terms (one-hot column part), recursed as a sparse term over the next round's indices; coefficients
`beta[J + k]` after the J eq claims. Also landed meanwhile (64a9eeb): Boolean-tail detection in `contract_eq` (your 34 ms win; round-1
contraction 18 -> 7 ms at 2^30, 4 claims) — you can drop `_r1_eq_contract`.

## Landed (9d13ac7 on lane/ligerito-pcs-fast)

`commit(..., zk=zp | t_pad=256)`, `open(..., sparse=[...])`, `verify_open(..., zk=zp, sparse=[...])`; exact transcript additions and the cost
table in my report `## For ligerito-relation` (ZK). +20 ms prover at 2^29 on the 4090. Tests: `fast_test.py::test_zk_padding_and_sparse_claims`
(kept/streamed, t_pad 0/32/100, negatives) and `test_encode_padding_matches_reference`.
