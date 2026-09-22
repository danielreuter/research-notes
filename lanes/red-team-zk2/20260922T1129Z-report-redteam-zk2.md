---
id: r20-proof/red-team-zk2/20260922T1129Z-report-redteam-zk2
campaign: r20-proof
lane: red-team-zk2
kind: report
status: closed
repo: verity-main@f96fc53
origin: verity-main@f96fc53:backends/numerical/reports/redteam_zk2.md
---

# red-team-zk-2: re-audit of the b-zk-fix labels (main a52441c)

Lane `red-team-zk-2`, 2026-09-22. Target: B-Ligero `--zk` after lane b-zk-fix (F1 `q = Q + u_ca + x^k u_cb`,
F2 challenges from the verifier's coins alone, F3 explicit `--mode interactive | fiat-shamir`). Labels under audit
(ledger `b-zk-fix.jsonl`, run `r20260922-105905-2021`): **`COMPLETE_ZK_BACKEND`** for `--mode interactive`,
**`COMPLETE_HVZK_BACKEND`** for `--mode fiat-shamir`. Evidence run of this lane: `r20260922-112029-2db3` (vy-g3,
L40S, 25 x 170 VUs, both modes, 6 min); raw numbers `notes-asset:campaigns/r20-proof/assets/red-team-zk2/reports/redteam_zk2.json`; laptop run of G1 `notes-asset:campaigns/r20-proof/assets/red-team-zk2/reports/redteam_zk2_dummy_laptop.json`;
code `backends/direct/ligero/redteam/zk2.py`, `zk2_run.py`, `zk2_dummy.py`; ledger `ledger/red-team-zk2.jsonl`.

## Verdict per label

| run id | mode | label | verdict |
|---|---|---|---|
| r20260922-105905-2021 | interactive, `--zk` | `COMPLETE_ZK_BACKEND` | **EARNED** (construction; with the simulator repair G1 written into 8c and the ROM-hiding assumption on the Merkle commitment listed in `assumptions`) |
| r20260922-105905-2021 | fiat-shamir, `--zk` | `COMPLETE_HVZK_BACKEND` | **EARNED** (2^-128.04 is the FS `q x eps` bound; t = 288, D = 7 are exactly what it needs) |
| r20260922-105112-d542 | interactive, `--zk` (redteam run) | -- | its numbers reproduce (0/16150, all components at chance) |

No `REDTEAM_ZK2_URGENT.md`: nothing found requires a downgrade. Two findings require text/code repairs (G1, G2) and
one assumption must be stated on the interactive row (G3).

## Findings

| id | class | verdict | attack / evidence |
|---|---|---|---|
| **A1** | F1 fix, rank at the real layout incl. the opened mask rows | **HOLDS** | The new check is not the message-mask rank alone (which is trivially `l + k - 2`): the rows `u_ca, u_cb` are OPENED at the `t` columns, and `u_cb(eta_c)` separately from `u_ca(eta_c)` discloses `Q[k:](eta_c) = q[k:](eta_c) - u_cb(eta_c)` -- `t` functionals of the high coefficients of `Q = sum_i R_i p_i` (witness-bearing: `deg Q <= 2l - 2 = 32766 >= k`). They are hidden iff the residual row masks (`t_pad - t` free coefficients per involved row after the openings) span them. Exact rank over BabyBear on the real challenge and the real opened columns (`zk2.u_high_rank`): interactive `197/197` on all 6 coordinates (12 involved rows x 59 residual dims); FS `288/288` on all 7 (12 x 224). Pooled uniformity of the disclosed values: real p 0.57 / 0.68, trivial witness 0.28 / 0.51, simulated 0.82. Every opened mask-row family (`prox, lin, qa, qb, chain_a, chain_b`) across two witnesses, 24 x 24: 0 positions below Bonferroni (1182 / 2016 positions each); `q` 0/198 138 (int.) and 0/232 953 (FS); opened witness rows 0/692 652 and 0/1 012 608. Pre-fix extraction on the fixed transcript: **0/16150** accumulators in both modes, witness-free consistency 0.0. |
| A1' | quadratic test (unchanged since 8b), same structure | HOLDS | `s_qb(eta_c)` discloses `(P0/Z_H)[k:](eta_c)`; by degree (`P_a s_b` has degree `< k`) the high part is `sum rho [Z_H s_a s_b][k:]`, a function of the masks only -- no witness functional to cover. Empirically `opened_mask_qb` at chance (above). |
| **A2** | soundness of the coin-only derivation | HOLDS | `stmt` and `c1 c2` are in both seeds (`_BIND_STATEMENT = True`; `seed1_preimage`/`seed2_preimage`), the mode is in `statement_digest`, so coins are session- and statement-scoped. `r1, r2` are opened only after `root` / after `w, h, q, v`; before that the prover sees only `c_i = Blake2b(tag‖r_i‖s_i)` with 512 random bits: the hiding term `2 x 2^64/2^256 = 2^-191` is in the union (-128.05 recomputed). Root/grinding: the prover cannot bias `r` (it is the verifier's), and a restart meets fresh coins; dropping `root` from the seed loses nothing in the interactive model. **New mask, new sum freedom**: `sum_H u` is NOT checked by the verifier (it cannot be), so a prover whose chain fails could repair `sum_H q` through `u_ca[0]` -- but `u` is inside `root`, committed before `r1` is opened, and the needed offset `rhs - sum_H Q` is a uniform function of `rc` (the residuals enter with fresh coefficients): success `p^-D = 2^-186` per proof, inside the existing chain-test field term. Same in FS (`rc = H(stmt, root)`, root contains `u`). Mutated-witness probe rejected in both modes (this run). |
| **A3 / G1** | the simulator under the real hash | **HOLDS with a repair** | Run by this lane with `oracle=None` and `merkle.hash_bytes` asserted identical before/after: accepting under the real `verify()`, rejected under another verifier's coins; adaptive V* aborts at slot 1 / 2 identically in prover and simulator; 24 vs 24 real-vs-simulated, 0 below Bonferroni on every component (median p 0.46). Selective abort at n = 60 per predicate: on `root` 13/60 vs 18/60 (z -1.0), on `q[0,0]` parity 28/60 vs 21/60 (z 1.3), on the parity of `sum q[k:]` 32/60 vs 25/60 (z 1.3): consistent with equal rates; mean rewinds 0.2-1.1, max 5 (cap 8). **G1 (simulator bug, not a leak):** the dummy run that extracts the coins sends `v0, q0` uniform WITHOUT the public constraints `v|_H = beta`, `sum_H q = rhs`. A V* that aborts at slot 2 iff those public checks fail (`zk2_dummy.PublicCheckVerifier`) never aborts on the real prover and aborts on the simulator with probability 1: **real 0/12, sim 12/12, advantage 1** (l = 256). PROTOCOL.md 8c documents the dummy run exactly this way. Fix (3 lines): sample `v0` on `{v|_H = beta}` and `q0` on `{sum_H q = rhs}` (both public); more generally the dummy messages must come from the honest-observable distribution. With the fix the GK argument goes through. |
| G2 | rewinding, expected time | HOLDS, text repair | 8c says "constant expected rewinds". For a V* aborting with probability `p` on `root` the replay loop needs `1/(1-p)` expected rewinds; the code caps at 8 and outputs an abort transcript on exhaustion, a simulation error of `(1-p) p^8` (up to 0.039 at p = 0.9). Not negligible for all V*; the standard GK estimator makes it expected-polynomial. State it. |
| **A4** | FS accounting | HOLDS | Recomputed independently from `accounting.py` constants at l = 16384, 25 sub-batches: per-proof target -132.64; FS query terms `(1-e/n)^t + ...` x 2^60 at t = 288 = -132.70 (t = 287 gives -132.03: **fails**); field term `(n+3)/p^D x 2^60` = -109.4 at D = 6 (fails), -140.3 at D = 7; union -128.045. The ledger's `2^-128.04` is the FS bound. Interactive: t = 197, D = 6, -128.05 with the -191 coin term. |
| A5 | statement-adaptive V* / column steering | HOLDS | `r2` is committed before `root`; opening to a root-dependent value is a Blake2b collision (adaptive test). Grinding `r2` before step 0 (their `StatementAdaptiveVerifier`, overlap 30 vs 17.4) chooses the column set ahead of time -- the honest verifier's power; any `t <= t_pad` distinct coset points are covered (Vandermonde, `Z_H != 0` off H), and A1 covers the two new rows too. "Overlap" is with a target set the V* fixed in advance, not with a set chosen after `root`: no leak. |
| G3 | Merkle leaf hiding (their O-fix3) | assumption, not a break | Every opened column consists of masked witness rows (uniform) and uniform mask rows: leaf preimages disclose nothing. Unopened leaves: siblings in the paths are Blake3 of correlated high-entropy columns; hiding is a random-oracle-flavoured property of Blake3 (or a salted-leaf commitment). The interactive row's `assumptions = ["hash"]` must read `["hash", "random-oracle (Merkle hiding)"]` or leaves must be salted -- "no random oracle for zero knowledge" (8c) over-claims by this one item. Does not affect the FS row (already ROM). |
| A6 | `config_for` vs D1 | HOLDS | `_field_terms_ok` now sizes D with the k that sized t; interactive ZK is unchanged (t = 197, D = 6), FS D = 7 follows from the field term above. D1's `k = l` vs `k = l + 1` non-ZK discrepancy is out of this lane's scope (ZK uses `k = l + t_pad` in both places). |
| A7 | FS grinding to recover D = 6 (their O-fix1) | open, correctly priced | Not priced by b-zk-fix; the ledger row carries the unpriced (conservative) D = 7. Fine as labelled. |
| A8 | `COIN_HIDING_TERM` text | open (O-zk4) | still `2 x 2^64/2^256` with `|r| = 256`; conservative. |

## What the labels rest on (interactive `COMPLETE_ZK_BACKEND`)

Collision resistance of Blake2b (coin binding) and Blake3 (Merkle); SHAKE-256 as a PRG of the verifier's coin; hiding
of `c_i` from the prover (booked `2^-191`); **hiding of unopened Merkle leaves (ROM-flavoured, G3)**; the GK simulator
with the dummy run drawn from the honest-observable distribution (G1). Soundness `2^-128.05` interactive statistical,
`2^-128.04` FS under `q x eps` with `q = 2^60`.

## Open items

* O-zk2-1 (owner b-zk-fix): G1 -- fix the dummy run in `redteam/simulator.py` and the sentence in 8c; add
  `PublicCheckVerifier` to the V* battery (`zk2_dummy.py` is ready to import).
* O-zk2-2: G2 wording in 8c; optionally the GK estimator in the simulator.
* O-zk2-3: G3 -- add `random-oracle (Merkle hiding)` to the interactive row's assumptions or salt the leaves.
* O-zk2-4: the selective-abort rates are now at n = 60 per predicate (|z| <= 1.3); still not a powered test.
* O-zk2-5: the private-operand statement (their O-fix6) remains what would make any ZK label mean something for Verity.
