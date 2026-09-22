---
id: r20-proof/red-team-zk/20260922T1013Z-report-redteam-zk
campaign: r20-proof
lane: red-team-zk
kind: report
status: closed
repo: verity-main@f96fc53
origin: verity-main@f96fc53:backends/numerical/reports/redteam_zk.md
---

# red-team-zk: the B-Ligero `COMPLETE_ZK_BACKEND` claim (run r20260922-092404-2a1b)

Lane `red-team-zk`, 2026-09-22. Target: the B-Ligero torch prover with 8b masking + 8c HM96 coin commitment
(`backends/direct/ligero/protocol.py` at main 2b5b4ed), 4096 VUs as 25 x 170, `l = 16384`, `t = 197`, `D = 6`.
Evidence run: `r20260922-100305-2b13` on vy-g3 (L40S), 227 s; raw numbers in `notes-asset:campaigns/r20-proof/assets/red-team-zk/reports/redteam_zk.json`; code in
`backends/direct/ligero/redteam/` (`q_leak`, `mask_rank`, `simulator`, `run`) and the torch-free core
`verity_numerical/redteam/ligero_q_leak.py`; fixtures `fixtures/redteam-zk/` (loader test
`tests/redteam/test_redteam_zk_fixtures.py`); ledger `ledger/red-team-zk.jsonl` (5 rows); urgent note
`note:r20-proof/red-team-zk/20260922T1102Z-finding-redteam-zk-urgent`.

## Verdict on the label

**DOWNGRADE `COMPLETE_ZK_BACKEND` -> `NON_ZK_PROOF_DIAGNOSTIC`** for r20260922-092404-2a1b (also the
`COMPLETE_HVZK_BACKEND` row of the same run).

* As a *construction* the 8b masking is not HVZK: the chain message `q` is unmasked on `H` and hands the honest
  verifier every intermediate accumulator of every VU (F1, demonstrated 16150/16150 at the real layout).
* As a protocol for the *current statement* it is trivially ZK, because the statement publishes the operands and the
  output words (`statement_digest(a, b, y16)`): the witness is a function of the public input, so no privacy label
  says anything. The campaign's ZK target (`note:r20-proof/zk-construction/20260922T0737Z-report-zk-construction` 0) is a committed-private witness; F1 is a total
  break there.
* Malicious-verifier ZK of the *implemented* protocol exists only in the programmable random-oracle model (F2), the
  assumption 8c was written to avoid.
* The soundness figure `2^-128.05` is the interactive bound; the measured mode is non-interactive (F3).

Path back: F1's one-line mask repair + a private-operand statement -> `COMPLETE_HVZK_BACKEND`; then either
`COMPLETE_ZK_BACKEND (random-oracle)` with F2 written into PROTOCOL.md 8c, or a challenge derivation that is a
function of the verifier's coins alone (`r := PRG(r1)`, `cols := PRG(r2)`) for a CRH-only simulator -- which
forbids the non-interactive reading entirely.

## Class table

| # | Class | Verdict | Evidence (real layout unless noted) |
|---|-------|---------|-------------------------------------|
| 1a | Opened columns | **HOLDS / NO-LEAK** | Mask row `s_j` has `t_pad = 256` free coefficients; the map `s -> (Z_H(eta_c) s(eta_c))_{c in cols}` on the 197 actually opened columns has rank 197 (exact, BabyBear). No coefficient of `s_j` is disclosed by any message (`w, v, h, q` carry their own mask rows). Two witnesses x 48 transcripts, 692 652 positions, chi2 with Bonferroni: 0 positions below threshold (median p 0.486). |
| 1b | `w` | HOLDS | Mask `s_prox` is the identity on `F^k`: admissible dim = mask rank = `k`. 0 / 99 840 positions. |
| 1c | `v` | HOLDS | Admissible dim `k - l = t_pad`; mask `Z_H s_lin` rank `t_pad`. Two-witness test shows 96 598 / 99 840 positions differ -- expected: `v|_H = beta` is *public* (statement-dependent), it is not a leak; real-vs-simulated 0 / 99 840. |
| 1d | `h` | HOLDS | Admissible dim `2k-1-l`; mask `s_qa + x^k s_qb` rank `k + t_pad - 1 = 2k-1-l`. 0 / 101 370. |
| 1e | `q` | **ACCEPTED-LEAK (F1)** | Admissible dim `l + k - 2`; mask `Z_H s_chain` rank `k - 1`: deficiency `l - 1 = 16383` per coordinate (explicit matrices at `l=16, t_pad=8`: 38 vs 23, deficiency 15 = l-1; formula at real size). `q|_H = Q|_H`; walking each VU from `c_0 = 0` with the verifier's `rc`: 6 equations / 3 unknowns per step, all consistent, **16150/16150 accumulators recovered exactly** (5.8 s), 190/190 at `l=256` (fixture). Per-position chi2 does *not* see it (0/198 138 below threshold): the leak is a linear function of the witness, invisible to marginal tests -- the linear-algebra test the brief asked for is what finds it. |
| 2a | Simulator, honest V | **BROKEN as written / HOLDS in PROM (F2)** | `simulator.py` against the real `verify()`: accepting transcript with the oracle programmed at 2 points (`H(stmt,c,root,r1)`, `H(stmt,c,root,w,h,q,v,r2)`); the same transcript under the real hash: `column challenge mismatch`. Real vs simulated, 48 x 48, 1.2 M positions across all components: 0 below Bonferroni. `q` distinguishers: witness-free consistency 1.0 (real) vs 0.0 (simulated) on 8/8; known-witness 16150 vs 0: advantage 1. |
| 2b | Adaptive V* (coins as a function of `root`) | HOLDS | Prover aborts (`CoinOpeningError`) at slot 1 and slot 2; simulator outputs the identical abort transcript. Opening to a second value = BLAKE2b collision (`2^-128`). |
| 2c | Selectively aborting V* | HOLDS on `root`; **inherits F1 on `q`** | Abort iff `root[0] < 64`: real 19/48, sim 14/48 (expected 0.25; `root` is a hash of a fresh tableau in both, difference not significant at n=48). Abort as a function of the recovered first accumulator's `f` parity: fires for the real prover iff that witness bit is 1 and never for the simulator (advantage 1 whenever the bit is 1; in the run the bit was 0, rates 0/0 -- the run's predicate choice was uninformative, the mechanism is F1 itself). |
| 3 | Coin commitment | HOLDS (brief's premise corrected) | `c = BLAKE2b-256("ligero-b/coin|v1|" ‖ r ‖ s)`, `r, s` **32 bytes each** (not 64-bit r): binding `2^-128`; hiding term `COIN_HIDING_TERM = 2 x 2^64/2^256 = 2^-191` is written as if `r` were 64 bits -- a conservative over-count under the ROM bound, but the derivation text is wrong. `(c1, c2)` are absorbed into both challenge seeds ahead of `root` and into the transcript; not in `statement_digest` (correct: they are transcript, not statement). `root` depends on nothing V* controls (masks from the prover's own ChaCha key; V*'s first message is `c`, a commitment). |
| 4 | Coins entropy / deployment model | **MODEL MISMATCH (F3)** | Challenges are `SHAKE(H(stmt, c, root, r1))` and `H(stmt, c, root, w, h, q, v, r2)`: functions of the prover's commitments and the verifier's coin, so a V* handing `r_i` in advance buys nothing (the prover cannot precompute past `root`). But `bench-vu` runs `prove(coins=None)`: the prover samples its own `r1, r2` = Fiat-Shamir with a prover-chosen nonce (unbounded restarts). ZK claim (interactive V*) and soundness figure (NI run) are in different models. |
| 5 | Witness-dependent control flow | HOLDS | Only witness-dependent branches: the `check=True` self-asserts (degree of `h`, degree and sum of `q`; off in the bench) and `CoinOpeningError` (V*-dependent). Mask sampling `_uniform_symbols` rejects on the *random stream* only (`u < 2p`, ChaCha20/SHAKE), never on a witness-derived value. |
| 6 | Accounting | HOLDS (one misplaced term) | `irs_query = -132.69`, union over 25 = `-128.05`, recomputed from constants (`irs_query_term_check_log2 = -128.0495`). `coin_commitment_hiding = -191` sits in the *soundness* union though it is a privacy term (harmless, conservative). O1 (`row_coeffs` geometric) is the A-GPU prover's; B-Ligero draws uniform `r` per row in `_challenge1`, so neither the masked linear tests' proximity bound nor the ZK argument is affected. |

## F1 in one paragraph

`q_d = Q_d + Z_H s_chain_d` (protocol.py "ZK masking"; PROTOCOL.md 8b "chain mask Z_H s_chain (sum over H = 0)").
The mask vanishes at every point of `H`, so `_fold_to_H(q, l)` gives the verifier `Q_d(h_j) = sum_i coef[d,i,j] W[rows_i][j]`
exactly for every column `j`: with the link/start/end coefficients `rl, rs, re` it recomputes, and the public
`c_0 = 0` per VU, `sum_x rl_x[d,j] c_x[j+1] = known_d(c[j]) - Q_d(h_j)` is a 6 x 3 full-rank system per step.
Fix (owner b-zk): mask `q` with a uniform polynomial `u` of degree `< l + k - 1` with `sum_H u = 0`
(`u - (sum_H u)/l`), committed as a row and opened like the others; the verifier's column check becomes
`q(eta_c) = sum_i R_i(eta_c) U_i[c] + u(eta_c)`. AHIV22's `u_add`. Cost: one more `D`-row family.

## Open items

* O-zk1. After the F1 fix, regenerate `fixtures/redteam-zk/q_leak_l256_2vu.json` with the fixed prover and set
  `expected_recovery: "none"` in the manifest; the loader test then asserts the recovery *fails*.
* O-zk2. The `q` leak composes with the two-witness class-1 test only through linear algebra; per-position
  statistics are structurally blind to it. Future hiding audits should include a "recover the witness by solving the
  verifier's own checks" step per message, not only marginals.
* O-zk3. Selective-abort quantification on `root` was run at n = 48 (19 vs 14 aborts). Not a leak mechanism (the
  root is a hash of fresh randomness in both worlds), but a larger n would close the 2-sigma gap.
* O-zk4. `COIN_HIDING_TERM`'s comment ("q / 2^|r|, q = 2^64") describes 64-bit `r`; `COIN_BYTES = 32`. Rewrite the
  derivation or shrink `r` -- either is fine, they should agree.
* O-zk5. The b-zk ledger rows quote an interactive bound for a non-interactive run (F3). Either re-run with
  `verify(coins=own)` semantics declared, or re-parameterise under the FS rule (`t ~ 279`, `t_pad = 512`).
