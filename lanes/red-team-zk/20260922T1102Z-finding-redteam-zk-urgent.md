---
id: r20-proof/red-team-zk/20260922T1102Z-finding-redteam-zk-urgent
campaign: r20-proof
lane: red-team-zk
kind: finding
status: closed
repo: verity-main@f96fc53
origin: verity-main@f96fc53:backends/numerical/reports/REDTEAM_ZK_URGENT.md
---

# URGENT (red-team-zk, 2026-09-22 ~10:30Z): B-Ligero `COMPLETE_ZK_BACKEND` must be downgraded

Three findings against the b-zk claim (run `r20260922-092404-2a1b`, 4096 VUs as 25 x 170, `--zk`, HM96 coins).
Full report: `note:r20-proof/red-team-zk/20260922T1013Z-report-redteam-zk` / `.json`; code `backends/direct/ligero/redteam/`.

## 1. ACCEPTED-LEAK: the chain message `q` is unmasked on H -- every intermediate accumulator is in the transcript

`q_d = Q_d + Z_H s_chain_d` (protocol.py "ZK masking", PROTOCOL.md 8b "chain mask Z_H s_chain (sum over H = 0)").
`Z_H s_chain` vanishes at every point of `H`, not merely in its sum, so `q_d|_H = Q_d|_H = (sum_i coef[d,i,j] W[rows_i][j])_j`
exactly -- the per-column share of the cross-column constraints, a witness-dependent linear function the verifier
reads with `_fold_to_H(q, l)`. For the honest witness, `Q_d(h_j) = sum_x rl_x[j-1] c_x[j] - sum_x rl_x[j] c_x[j+1] + (public)`
with the verifier's own coefficients `rl`; `c[start] = 0` is public, so walking each VU forward gives `D = 6`
equations in the 3 components of the next accumulator at every step. **Demonstrated** (`redteam/q_leak.py`): all
`95 x n_vus` accumulators of every VU recovered exactly from `(q, root, coins, statement)` -- 190/190 at `l = 256`
on the laptop, 16150/16150 at the measured layout `l = 16384` on vy-g3 (see `notes-asset:campaigns/r20-proof/assets/red-team-zk/reports/redteam_zk.json`). Mask dimension
count: admissible space of `q` has dimension `l + k - 2`, the mask spans `k - 1`: deficiency `l - 1 = 16383` field
elements per coordinate, `6 x 16383` per proof in the clear (`redteam/mask_rank.py`).

This holds for the HONEST verifier: it is an HVZK failure of the 8b construction, not only a malicious-verifier one.
Under the prover's current statement the operands `a, b` and the words `y16` are PUBLIC (`statement_digest`), so the
accumulators are computable from the statement anyway and nothing secret is lost *today*; but the campaign's ZK
target (`note:r20-proof/zk-construction/20260922T0737Z-report-zk-construction` 0: operands, accumulators, outputs, hints are private) makes this a total break of the
accumulator chain (and, through consecutive accumulators, of the block dot products of the operands) the moment the
operands are committed instead of published. The opened columns, `w`, `v`, `h` are correctly masked (exact rank
computation + per-position statistics at the real layout: no leak).

Fix (owner b-zk, one line): mask `q` with a uniform polynomial of degree `< l + k - 1` whose sum over `H` is zero
(AHIV22's `u_add`: `k + l - 2` free coefficients), i.e. add `u - (sum_H u)/l` for uniform `u`, and open its row like
the others (the verifier's column check becomes `q(eta_c) = sum_i R_i(eta_c) U_i[c] + u(eta_c)`), instead of `Z_H s_chain`.

## 2. The 8c simulator does not exist as written; it exists only in the programmable random-oracle model

PROTOCOL.md 8c: "knowing `(r1, r2)` and hence `r, rho, cols`". False: `r, rho, rc = SHAKE(H(stmt, c, root, r1))` and
`cols = H(stmt, c, root, w, h, q, v, r2)` -- the coins are hashes of the prover's own messages together with `r_i`.
After the rewind the simulator knows `r1` but not `r` (it depends on the `root` it has yet to build), and the
column tests need committed rows that fit challenges derived from that root at columns that are a hash of the
messages. `redteam/simulator.py` implements the simulator against the real verifier: it works only by programming
`H(... root ... r1) := seed1`, `H(... root, w, h, q, v ... r2) := seed2` (the same transcript is rejected -- "column
challenge mismatch" -- as soon as the oracle is not programmed). So malicious-verifier ZK of the implemented protocol
is a random-oracle statement, the assumption `note:r20-proof/zk-construction/20260922T0737Z-report-zk-construction` 3.2/3.3 chose step 0 to avoid; the label must
carry it. (The commitment is still needed in the ROM: without it V* chooses `r1` after `root` and evaluates the
unprogrammable hash on `(root, r1')` for many `r1'`.)

## 3. Deployment model: the measured mode is non-interactive, where the HM96 step is a no-op and 2^-128 is not the bound

`bench-vu` runs `prove(coins=None)`: the prover samples `r1, r2` itself and commits to them -- i.e. Fiat-Shamir with a
prover-chosen nonce (`_challenge1` includes `root`, so the challenge is not predictable before commitment, but the
prover controls the nonce: unbounded restarts). The reported `2^-128.05` is the interactive statistical bound
(`accounting.py` docstring: "live verifier challenges, no Fiat-Shamir"); in the non-interactive mode the campaign's
own rule (`note:r20-proof/zk-construction/20260922T0737Z-report-zk-construction` 3.3, `zk_cost.fiat_shamir_reparameterisation`) requires `q x eps` accounting
(`t ~ 279`, no longer fitting `t_pad = 256`). The ZK claim (interactive V*) and the soundness claim as measured
(non-interactive) are in different models; the code supports the interactive mode (`verify(coins=own)`) at the
same arithmetic cost, so this is a labelling repair, but the ledger rows as written mix the two.

## Verdict on the label

**DOWNGRADE below `COMPLETE_HVZK_BACKEND`.** As a ZK construction with a committed-private witness the 8b masking
leaks `q|_H` (finding 1) to the honest verifier, so it is not HVZK; as a protocol for the *current* statement it is
trivially ZK (the witness is a function of the public statement), so no privacy label is meaningful. Honest label
for `r20260922-092404-2a1b`: `NON_ZK_PROOF_DIAGNOSTIC` with note "8b masking of columns/w/v/h verified; q unmasked
on H (accumulators in the clear); operands and outputs public in the statement; interactive soundness bound quoted
for a non-interactive run". After the one-line fix of finding 1 and a private-operand statement: `COMPLETE_HVZK_BACKEND`;
`COMPLETE_ZK_BACKEND (random-oracle)` with finding 2 written into PROTOCOL.md 8c, or a challenge derivation
`r := PRG(r1)`, `cols := PRG(r2)` (coins are the verifier's messages alone) for CRH-only malicious-verifier ZK --
which then forbids the non-interactive reading entirely.

## Status (lane b-zk-fix, branch `lane/b-zk-fix`, 2026-09-22 ~11:20Z) -- appended by the fixing lane; the text above is the red team's

Full report `note:r20-proof/b-zk-fix/20260922T1142Z-report-b-zk-fix`; ledger `ledger/b-zk-fix.jsonl`; PROTOCOL.md 8b/8c rewritten.

* **F1 FIXED** (commit f752d4b): `q_d = Q_d + u_d`, `u_d = u_ca + x^k u_cb` uniform of degree `< l + k - 1` with
  `sum_H u = 0`, two committed mask rows, verifier check `q(eta_c) = sum_i R_i(eta_c) U_i[c] + U_ca[c] + eta_c^k U_cb[c]`.
  Run `r20260922-105112-d542` (vy-g3, real layout 170 VUs, `l = 16384`): **0 / 16150** accumulators recovered
  (was 16150/16150), witness-free consistency 0.0, `q` mask rank `l + k - 2` = admissible dim, two-witness
  per-position chi2 on `q` 0/198 138 below Bonferroni; fixture `fixtures/redteam-zk/q_leak_fixed_l256_2vu.json`
  0/190 (`expected_recovery: none`, O-zk1 done). Honest proofs verify; 52/52 negatives and 252/252 mutations
  rejected in `--zk` interactive, `--zk --mode fiat-shamir` (same run) and non-ZK (`r20260922-105905-2021`);
  babybear battery 0 forgeries.
* **F2 FIXED** (f752d4b): interactive challenges `SHAKE(H(stmt, c1 c2, r1))`, `H(stmt, c1 c2, r2)` -- functions of
  the verifier's coins alone. `redteam/simulator.py` runs against the real `verify()` with the real hash:
  `r20260922-105112-d542` honest V: accepted, 0 oracle points programmed, 0 programmed hits; adaptive V* (slot 1 /
  slot 2): identical aborts; new statement-adaptive V* (grinds `r2` before step 0 with `stmt`): real and simulated
  transcripts both accepted under the real hash, same column set (`r20260922-105905-2021`); indistinguishability
  32 vs 32: 0 positions below Bonferroni on every component incl. `q`; `q` distinguishers advantage ~0.
  Soundness argument for the coin-only derivation: PROTOCOL.md 8c.
* **F3 FIXED** (f752d4b): `--mode interactive | fiat-shamir`, mutually exclusive, bound into the statement digest;
  interactive `verify(coins=own)` required; Fiat-Shamir priced with `q x eps` (`2^60`): `t = 288`, `t_pad = 512`
  and **`D = 7`** (the field terms `(n+3)/p^6 x 2^60 = 2^-110` do not survive at `D = 6` -- beyond the `t ~ 279`
  the red team estimated). Labels: interactive+zk `COMPLETE_ZK_BACKEND` (CRH; statement's operands public, so
  vacuous today), fiat-shamir+zk `COMPLETE_HVZK_BACKEND` (NIZK in PROM), non-ZK `NON_ZK_PROOF_DIAGNOSTIC`.
  Timings per mode: `note:r20-proof/b-zk-fix/20260922T1142Z-report-b-zk-fix` section 4 (run `r20260922-105905-2021`).
* Not done: O-zk3 (abort-on-root rates at larger n), O-zk4 (`COIN_HIDING_TERM` derivation text), statistically hiding
  leaves, a private-operand statement.
