---
id: r20-proof/b-zk-fix/20260922T1142Z-report-b-zk-fix
campaign: r20-proof
lane: b-zk-fix
kind: report
status: closed
repo: verity-main@f96fc53
origin: verity-main@f96fc53:backends/numerical/reports/b_zk_fix.md
---

# b-zk-fix: repairing the B-Ligero ZK claim after red-team-zk (F1, F2, F3)

Lane `b-zk-fix`, branch `lane/b-zk-fix` (forked from `main` 451b6e8), 2026-09-22. Target: the findings of
`note:r20-proof/red-team-zk/20260922T1102Z-finding-redteam-zk-urgent` / `note:r20-proof/red-team-zk/20260922T1013Z-report-redteam-zk` against run `r20260922-092404-2a1b` (`COMPLETE_ZK_BACKEND`, downgraded to
`NON_ZK_PROOF_DIAGNOSTIC`). Code: `backends/direct/ligero/` (`protocol.py`, `vu.py`, `run.py`, `redteam/`,
`redteam_zk.py`); protocol text: `PROTOCOL.md` 8b/8c; ledger `ledger/b-zk-fix.jsonl`. Pod `vy-g3` (NVIDIA L40S),
shared with lane b-verifier during the runs (no `--exclusive`).

Runs (every number below is from one of these):

| run id | stage | what |
|---|---|---|
| `r20260922-105112-d542` | `b_zk_fix.gates_redteam` | gate-vu `--zk` interactive and fiat-shamir (52/52 negatives, 252/252 mutations each), babybear battery (0 forgeries), `redteam/run` at the real layout (170 VUs, 25-proof configuration, 32 transcripts): F1 regression, simulator, indistinguishability; post-fix fixture at `l = 256`. The non-ZK gate, `redteam_zk.py` and `redteam_binding.py` crashed in this run on a `config_for` bug in the non-ZK path (fixed in 87db937, re-run below). |
| `r20260922-105905-2021` | `b_zk_fix.bench_modes` | `redteam_zk.py` (PASS), `redteam_binding.py` (OK), gate-vu non-ZK interactive and fiat-shamir, `redteam/run` n = 8 (statement-adaptive V*), `bench-vu` 4096 VUs (25 x 170) x 4 modes, median of 3 reps. |
| `r20260922-092404-2a1b` (b-zk) / `r20260922-100305-2b13` (red team) | -- | the "before" numbers quoted for comparison. |

## 1. What changed

**F1 -- the chain message `q` is now masked on `H`.** Before: `q_d = Q_d + Z_H s_chain_d`; `Z_H s_chain` vanishes on
every point of `H`, so `q|_H = Q|_H` and the verifier read every intermediate accumulator off the transcript. After:
`q_d = Q_d + u_d` with `u_d = u_ca + x^k u_cb`, `u_ca` uniform of degree `< k`, `u_cb` uniform of degree `< l - 1`,
the constant coefficient adjusted so that `sum_H u = l sum_{l | j} u_j = 0` (AHIV22 `u_add`; `l + k - 2` free
coefficients = the dimension of the admissible space). Both are committed rows (`chain_a`, `chain_b`: `M = m + 6D`)
and the verifier's column check is `q(eta_c) = sum_i R_i(eta_c) U_i[c] + U_ca[c] + eta_c^k U_cb[c]`; the sum-over-`H`
check is unchanged and exact. Mask-rank audit (`redteam/mask_rank.py`, explicit matrices at `l = 16, t_pad = 8`):
pre-fix `q` mask rank 23 of 38 (deficiency 15 = `l - 1`), post-fix 38 of 38.

**F2 -- interactive challenges are functions of the verifier's coins alone.** `r, rho, rc = SHAKE(H("c1|v2" || stmt
|| c1 c2 || r1))`, `cols = H("c2|v2" || stmt || c1 c2 || r2)`: neither `root` nor `w, h, q, v` enters. The simulator
therefore knows every challenge after the rewind and before it builds anything; `redteam/simulator.py` no longer
programs the hash (an empty `ProgrammableOracle` is installed only to count hits: 0). Soundness argument
(PROTOCOL.md 8c): `r1, r2` are the verifier's, sampled before `root`, hidden by `c_i` until the prover has committed
the message the coin must follow, not biasable by the prover -- so `r`, `cols` are uniform and independent of the
prover's messages exactly as the public-coin analysis needs; `stmt`, `c1 c2` in the seed are domain separation.
The statistical interactive bound is unchanged (`t = 197`, `D = 6`, union `2^-128.05`).

**F3 -- two explicit, mutually exclusive modes.** `Config.mode` (`run.py --mode interactive | fiat-shamir`; bound
into the statement digest; `prove`/`verify` reject the other mode's coin usage). Interactive: `prove(coins=V)` and
`verify(coins=V)` are *required* (`bench-vu` samples the verifier's `Coins` per sub-batch and verifies with them);
`depth = 3`. Fiat-Shamir: no step 0 (the HM96 step is a no-op there), challenges `H(stmt, root)` /
`H(stmt, root, w, h, q, v)`, transcript without coins, `depth = 1`; `soundness()` multiplies every statistical term
by `2^60` (`note:r20-proof/zk-construction/20260922T0737Z-report-zk-construction` 3.3, `zk_cost.fiat_shamir_reparameterisation`) and `config_for` re-sizes:
`t = 288`, `t_pad = 512` (Lemma 4.15), **`D = 7`** (with `D = 6` the field terms `(n+3)/p^6 x 2^60 = 2^-110` break the
target -- a structural cost the red team's `t ~ 279` estimate did not include). `--no-coin-commitment` is removed.
The accountant's output (`mode`, `bound_model`, `hash_assumption`, `zk_statement`, `fiat_shamir_queries_log2`,
terms) is in every `result.json` under `workload_fingerprint.security`.

## 2. F1: leak test before / after

| | before (red team, `r20260922-100305-2b13`) | after (`r20260922-105112-d542`) |
|---|---|---|
| accumulators recovered from `q` (real witness, 170 VUs, `l = 16384`) | **16150 / 16150** | **0 / 16150** |
| trivial witness | (all zero, recovered) | 0 / 16150 |
| fixture `l = 256`, 2 VUs | 190 / 190 | 0 / 190 (`fixtures/redteam-zk/q_leak_fixed_l256_2vu.json`, `expected_recovery: none`; loader test passes) |
| witness-free consistency fraction (real transcript) | 1.0 | 0.0 (8/8 transcripts) |
| `q` mask rank / admissible dim | `k - 1` / `l + k - 2` (deficiency `l - 1`) | `l + k - 2` / `l + k - 2` |
| two-witness per-position chi2 on `q` (32 vs 32, 198 138 positions) | -- (marginals blind to the leak) | 0 below Bonferroni |
| honest proof verifies | yes | yes (gate-vu `--zk`: 16 VUs accept; 52/52 negatives, 252/252 mutations rejected -- interactive AND fiat-shamir; non-ZK 52/52, 252/252 in `r20260922-105905-2021`; battery 0/83 forgeries) |

## 3. F2: simulator results per V* model (`redteam/run.py`, real layout, `r20260922-105112-d542`, n = 32; statement-adaptive in `r20260922-105905-2021`, n = 8)

| V* | real prover | simulator | verdict |
|---|---|---|---|
| honest V | accepts | transcript accepted by the real `verify()` under the **real hash**; `oracle_points_programmed = 0`, `programmed_hits = 0`, 0 rewinds, 1.1 s; rejected under another verifier's coins ("coins are not this verifier's step-0 coins") | CRH-only simulator demonstrated |
| adaptive V* (opens slot 1 to `f(root)` / slot 2 to `f(root, w, h)`) | aborts at slot 1 / 2 having sent `root` / `root, w, h, q, v` | identical abort transcript | same |
| statement-adaptive V* (grinds `r2` over 64 candidates before step 0 against a target column set, using `stmt` and its own `c`) | see run 2 (below) | see run 2 | legal coin choice; simulated like any coins |
| selectively aborting on `root[0] < 64` (slot 1) | 8/32 aborts | 3/32 aborts (expected 0.25 both; `root0` is uniform in both worlds; n small -- O-zk3 stays open) | no witness dependence possible |
| selectively aborting on the parity of the first accumulator read off `q` | 0/8 | 0/8 | the predicate no longer sees the witness (F1) |
| indistinguishability, 32 vs 32, per position | opened witness rows 692 652, mask rows 7 092, `w` 99 840, `h` 101 370, `v` 99 840, `q` 198 138 positions | **0 below Bonferroni on every component** (median p 0.47) | |
| `q` distinguishers | witness-free fraction real 0.0 / sim 0.0; known-witness 0 / 0 of 16150 | advantage ~0 | was advantage 1 |

`redteam_zk.py` (`r20260922-105905-2021`): PASS -- equivocation aborts at both slots before any opened column;
committed adversarial coins (zero / ground) give real-vs-simulated `p > 0.05` on every message; the Fiat-Shamir-mode
proof is rejected by the interactive verifier. Note: with the coin-only derivation a statement-aware verifier *can*
steer its column set (ground overlap 30 vs 17.4 at chance): this is allowed (the interactive verifier owns its
coins; any `t <= t_pad` columns are masked) and the test now reports rather than bounds the overlap.

## 4. F3: the two modes at B = 4096 (25 x 170) on the L40S, median of 3 (`r20260922-105905-2021`)

| run (`--mode`, `--zk`) | prover s (median of 3) | ms/VU | `overhead.vs_native_peak` | verifier s | transcript MB | depth | t | D | t_pad | union bound | peak GB |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ZK interactive | 1.394 | 0.340 | 3.45e7 | 0.911 | 122.4 | 3 | 197 | 6 | 256 | 2^-128.05 (statistical) | 3.52 |
| ZK fiat-shamir | 1.500 | 0.366 | 3.72e7 | 1.071 | 165.3 | 1 | 288 | 7 | 512 | 2^-128.04 (q x eps, q = 2^60, PROM) | 3.54 |
| non-ZK interactive | 1.366 | 0.333 | 3.38e7 | 0.967 | 110.8 | 3 | 196 | 6 | -- | 2^-128.25 (statistical) | 2.80 |
| non-ZK fiat-shamir | 1.437 | 0.351 | 3.56e7 | 1.049 | 149.8 | 1 | 285 | 7 | -- | 2^-128.59 (q x eps) | 2.81 |

Overhead is `contract.overhead(seconds_per_vu, K)` as in every ledger row (native peak = the campaign's L40S BF16
constant). ZK costs +2% (interactive) over its control; the FS re-parameterisation (`D = 7`, `t = 288`) costs +7.6%
prover, +18% verifier, +35% transcript over interactive ZK -- the fused D-generic kernels absorb `D = 7` cheaply.
Caveat: `b-verifier` shares vy-g3; no `--exclusive`, so these medians may include contention.

Before (b-zk `r20260922-092404-2a1b`, FS-with-prover-nonce run priced with the interactive bound): ZK 1.41 s
(0.345 ms/VU), non-ZK 1.37 s (0.334 ms/VU), verifier 0.96 s, 122.3 MB, `t = 197`, `D = 6`.

## 5. Labels per run id (ledger `b-zk-fix.jsonl`)

| run id | mode | proof_class | why |
|---|---|---|---|
| `r20260922-105905-2021` ZK interactive | interactive, `--zk` | `COMPLETE_ZK_BACKEND` | malicious-verifier ZK under CRH only: unprogrammed simulator accepted by the real `verify()` (honest, adaptive, aborting, statement-adaptive V*), leak 0/16150, negatives/mutations/battery rejected |
| `r20260922-105905-2021` ZK fiat-shamir | fiat-shamir, `--zk` | `COMPLETE_HVZK_BACKEND` | HVZK via 8b masking; NIZK in the programmable ROM only; soundness by the `q x eps` rule |
| `r20260922-105905-2021` non-ZK interactive | interactive | `NON_ZK_PROOF_DIAGNOSTIC` | no masking |
| `r20260922-105905-2021` non-ZK fiat-shamir | fiat-shamir | `NON_ZK_PROOF_DIAGNOSTIC` | no masking |

Supporting runs: `r20260922-105112-d542` (gates, negatives 52/52, mutations 252/252, `redteam_battery`, `redteam/run.py`
leak regression + simulator, fixture `q_leak_fixed_l256_2vu.json`); `r20260922-105905-2021` also re-ran `redteam_zk.py`
(PASS) and `redteam_binding.py` after the `config_for` fix. `python -m verity_numerical.bench.ledger check` passes.

Every ZK row notes: the current statement publishes `a, b` and `y16` (`statement_digest`), so privacy is vacuous
for this statement; the ZK claim is about the construction (masking + coins + derivation) and becomes meaningful
once operands are committed (auth-integration LEAF_V2). No private-operand statement was implemented.

## 6. What remains open

* O-fix1. FS-mode cost: `D = 7` and `t = 288` are forced by the `2^60` rule; grinding (`note:r20-proof/zk-construction/20260922T0737Z-report-zk-construction` 3.3) could
  recover bits and keep `D = 6`; not priced here.
* O-fix2. The selective-abort-on-`root` rates (8/32 vs 3/32) are noise-level at this n (both worlds hash a uniform
  root); a larger n would close it (red team O-zk3).
* O-fix3. Unopened Merkle leaves are hidden by Blake3 of a uniform column (random-oracle hiding); statistically
  hiding salted leaves (HM96) are not implemented, so the interactive ZK claim still carries that one ROM-flavoured
  hiding assumption on the *commitment*, not on the challenge hash.
* O-fix4. `COIN_HIDING_TERM` is still written as `2 x 2^64 / 2^256` (red team O-zk4; conservative over-count).
* O-fix5. The unit-level (`gate`) non-ZK path was not re-run after the `config_for` fix (the chain gates were); the
  unit prover shares `config_for` and `prove`, so it is expected to pass -- unverified in this lane.
* O-fix6. A private-operand statement (operands committed, not published) is what would make any ZK label mean
  something for Verity; out of scope here.

## 7. Status after red-team-zk-2 (lane b-zk-fix-2, branch `lane/b-zk-fix-2`, run `r20260922-113615-2dfa`, vy-g3)

red-team-zk-2 (`note:r20-proof/red-team-zk2/20260922T1129Z-report-redteam-zk2`) EARNED both labels for `r20260922-105905-2021` and required three repairs; all
three are on `lane/b-zk-fix-2`:

* **G1 (simulator bug, fixed).** The dummy run of `redteam/simulator.py` sent `v0, q0` uniform without the public
  constraints `v|_H = beta`, `sum_H q = rhs`. Their `zk2_dummy.PublicCheckVerifier` (aborts at slot 2 iff a public
  check fails) separated the worlds with advantage 1: **before** real 0/12, sim 12/12 (`notes-asset:campaigns/r20-proof/assets/red-team-zk2/reports/redteam_zk2_dummy_laptop.json`,
  l = 256). Fix: after `V*` opens `r1` the round-1 challenges are known, so the dummy `v0` is drawn on `{v|_H = beta}`
  and `q0` on `{sum_H q = rhs}` (`_sample_v` / `_sample_q`, shared with the fake-tableau build; `w0, h0` are uniform in
  the honest world already). **After** (`r20260922-113615-2dfa`): l = 256, n = 24: real 0/24, sim 0/24, advantage 0;
  real layout l = 16384 (170 VUs), n = 6: real 0/6, sim 0/6. `PublicCheckVerifier` is now in the `redteam/run.py`
  V* battery (`aborting_on_public_checks`, asserted 0/0). The rest of the suite at the real layout re-passes:
  honest V accepted under the real hash, 0 oracle points programmed; statement-adaptive V* same columns real vs
  simulated, both accepted; adaptive V* slot 1 / 2 aborts identical; abort-on-root 4/24 vs 7/24 (expected 0.25);
  abort-on-`q` 0/6 vs 0/6; indistinguishability 24 vs 24: 0 positions below Bonferroni on every component
  (median p 0.46-0.47); leak 0/16150. (The "before" could not be re-run inside the same run id: the shipped tree
  carries no git history; the red team's laptop number is the before.)
* **G2 (text).** PROTOCOL.md 8c no longer says "constant expected rewinds": against a V* aborting on the replay with
  probability `p` the GK loop needs `1/(1-p)` expected rewinds; `max_rewinds = 8` outputs an abort transcript on
  exhaustion, a simulation error of `(1-p) p^8` (up to 0.039 at p = 0.9). The GK estimator is not implemented. Also in
  the interactive ledger row's note.
* **G3 (assumption).** The interactive `COMPLETE_ZK_BACKEND` row now carries `assumptions = ["hash", "random-oracle
  (Merkle hiding)"]`: the unopened Merkle leaves are unsalted `Blake3(column)`, so their hiding is ROM-flavoured. 8c's
  "no random oracle for zero knowledge" was replaced by exactly that item, with the cost of salting (+32 bytes hashed
  per leaf, +32 t bytes per proof in the openings, ~0.1 % of the transcript) -- not implemented.

Open after this: O-zk2-4 (abort-rate tests still unpowered, n = 24 / 6 here), O-zk2-5 / O-fix6 (private-operand
statement), the GK estimator, salted leaves.
