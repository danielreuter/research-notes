# Existing results, mapped onto the NCI draft

Draft: "Distinguishing inference from frontier training via novel communication intensity" (Notion, 2026-09-23).
Sections 1 to 11 are existing numbers; nothing there was re-run for the draft. Snapshot 2026-09-23 of `results/coarse.jsonl`
(387 rows, after merging the last pod shards `results/pod/coarse_pod_{0..7,train2_*}.jsonl`). Section 12 is new: the
closed form for the draft's `M_{L,T}`, checked against the exact solver on small instances and read off at the
draft's Kimi-K3 Gamma. It replaces the pod run planned in table 11.

Module hashes of every "current" row: lower certificate `ac6c3bb0e3` (`bounds/lower.py` + `bounds/lower_coarse.py`),
attack planner `f4baa2d7be` (`bounds/coarse.py`), `bounds/upper.py` `eab50c6955`, weight-presence certificate
`ba12ab8bf8` (`bounds/lower_wp.py`), graph extraction `332385d416`.

Regenerate:

~~~
PYTHONPATH=. .venv/bin/python -m accumulation.sweeps.final_report     # TABLE1/2, ROLLOUT_TABLES, REPORT
PYTHONPATH=. .venv/bin/python -m accumulation.sweeps.nci_projection   # tables 8-9 below
PYTHONPATH=. .venv/bin/python -m accumulation.redteam.mlt              # section 12 (add --readoff to skip the ~10 min solver check)
~~~

## 0. How our quantities map onto the draft

| Ours | Draft | Relation |
|---|---|---|
| RU (replay unit) | IU (isolation unit) | Same object: a set of non-input gates. |
| `G = G_hat * fwd(Q_inf)`, max work per RU | `Gamma`, max IU size | Same role. `fwd(Q_inf)` = checker work of one honest `Q_inf`-token session. **Our default is `G_hat = 4`, `Q_inf = 8K`, so Gamma = 4 x (one 8K session) = 32,768 short-context positions of work.** |
| `F = F_hat * fwd(Q_inf)`, max upstream work of any gate inside an RU | none | The draft has no F. Default `F_hat = 1.5` in every row. |
| Acyclic RU quotient (planner and exact solver) | Arbitrary partition, cycles allowed | Ours is a restriction of the draft's set of divisions. |
| Runtime input `I(R)` | `width(in(R) \ theta)` | Same thing. theta = committed weights (inference), or the step-0 weights (training/rollout); tokens are novel. |
| `L <= I* <= U` (bytes, whole circuit) | `NCI_avg_Gamma(C) * size(C)` | `I*` is the minimum total runtime input. |
| Slowdown = `(I*/token) / 4 B`, times `w_inf / w_C` | `NCI_avg / alpha` | Our reference is the *average* work per token of an 8K session. The draft's alpha uses the *minimum* per-position work, so the draft's slowdown = ours x `w_min / w_avg(8K)` = 0.62 to 0.92 (table 8, last column). |
| Work unit: checker Work (= MACs x 1.00 to 1.02) | gates | Ratios only, so the unit cancels. |
| `forward-nonfixed` ("dynamic rollout") | Full model evaluation with updated weights | Includes attention, norms, SwiGLU, head, which the draft's section 6.3 allows to count toward covered work. It has `M_{L,T}`'s matmuls, but with nonlinear maps between them rather than `M`'s linear chain (section 12, "Real models"). |

Common assumptions for every measured row:
- Circuits are our op graphs of Llama-3 (1B, 8B, 70B, 405B), Mixtral 8x7B, Qwen3-235B-A22B and DeepSeek-V3 shapes (`algorithms/registry.py`, `configs.py`).
- BF16 (2 B) weights and activations; 4 B per token id; rollout sequences are `min(Q_roll, Q_inf)` = 8K tokens.
- `L` is the proven dual bound of the certificate's LP/MILP (HiGHS, 180 to 600 s), never an incumbent. `U` is the cost of an explicit partition that the independent checker re-verified.
- Bounds are over divisions of the *fixed* circuit (the draft's "contains"). Extending them to arbitrary implementations is the draft's incompressibility assumption, not something we measured.

## 1. Honest inference is one IU at 4 B/token

| Model | Circuits | Tokens | I*/token | # IUs |
|---|---|---|---|---|
| 1B, 8B, 70B, 405B | `inference-dense`, `inference-session` | 8K | 4.0 B (L = U) | 1 |
| Mixtral 8x7B, Qwen3-235B-A22B, DeepSeek-V3 | `inference-moe` | 8K | 4.0 B (L = U) | 1 |
| 6 synthetic shape variants (wide, deep, FFN, many heads, attention) | both | 8K | 4.0 B | 1 |

- **Source:** `coarse.jsonl`, circuits `inference-*` at `Q_inf = 8K`, `G_hat = 4`. Acceptance checks are in `ROLLOUT_TABLES.md` (7/7 PASS).
- **Assumptions:** Γ is at least one session; theta holds all weights.
- **Status under the draft:** holds exactly (a session is one IU by construction).

## 2. Rollout (updated-weight forward): headline at our Gamma

| Model | P (GB) | MAC/token | Q_roll | L MB/token | U MB/token | Slowdown L / U (ours) | Slowdown L / U (draft's alpha) | Steady-state rate r_L / r_U MB/token (fit, Q >= 128K) |
|---|---|---|---|---|---|---|---|---|
| 1B | 3.0 | 1.77e9 | 1M | 0.0196 | 0.0382 | 4,900 / 9,600x | 3,300 / 6,500x | 0.0185 / 0.0366 (n=3) |
| 1B | 3.0 | | 4M | 0.0188 | 0.0368 | 4,700 / 9,200x | 3,200 / 6,300x | |
| 8B | 16.1 | 9.65e9 | 1M | 0.0847 | 0.125 | 21,000 / 31,000x | 16,000 / 24,000x | 0.0819 / 0.124 (n=3) |
| 8B | 16.1 | | 4M | 0.0832 | 0.125 | 21,000 / 31,000x | 16,000 / 24,000x | |
| 70B | 141 | 8.02e10 | 1M | 0.315 (MILP gap 32%) | 0.525 | 79,000 / 131,000x | 68,000 / 113,000x | 0.405 / 0.507 (n=3, r^2 0.988) |
| 70B | 141 | | 4M | 0.413 | 0.523 | 103,000 / 131,000x | 89,000 / 112,000x | |
| 405B | 812 | 4.38e11 | 1M | 1.50 | 2.11 | 375,000 / 526,000x | 345,000 / 484,000x | 0.822 / 1.50 (n=2) |
| Mixtral 8x7B | 93.4 | 1.49e10 | 1M | 0.134 | 0.226 | 33,000 / 56,000x | 28,000 / 48,000x | 0.0502 / 0.152 (n=2) |
| Qwen3-235B-A22B | 470 | 3.42e10 | 1M | provisional | provisional | not reportable | | |
| DeepSeek-V3 | 1,350 | 5.66e10 | 1M | provisional | provisional | not reportable | | |

- **Source:** `coarse.jsonl`, circuit `forward-nonfixed` / `forward-nonfixed-moe`; `ROLLOUT_TABLES.md` P0 and P1; fits in `ROLLOUT_TABLES.md` P1.
- **Policy:** Gamma = `G_hat = 4` x one 8K session; `F_hat = 1.5`; `Q_inf = 8K`.
- **Assumptions:**
  - The weights are dynamic (not in theta); inputs are the tokens plus the step-0 weights.
  - The slowdown uses equal work per token for rollout and inference.
- **Caveats:**
  - Gamma is much smaller than the draft's (table 8).
  - F is irrelevant here: measured identical at `F_hat` = 1.5, 3, 10 (table 4).
  - 70B at 1M has a 32% MILP gap, so its L sits below its 4M value.
  - For Qwen3 and DeepSeek-V3 at 1M, the planner fell back to a generic family, which gives a legal partition but not an attack; their L is from a stale hash.

## 3. Rollout cost vs rollout volume (does the weight cost amortize away?)

L / U in MB/token. `P/Q` is the weight-only floor (every dynamic weight read once).

| Model | 8K | 32K | 128K | 1M | 4M |
|---|---|---|---|---|---|
| 1B (P/Q at 4M: 0.0007) | 0.366 / 0.366 | 0.0915 / 0.0915 | 0.0277 / 0.0393 | 0.0196 / 0.0382 | 0.0188 / 0.0368 |
| 8B (0.0038) | 1.96 / 1.96 | 0.49 / 0.49 | 0.134 / 0.155 | 0.0847 / 0.125 | 0.0832 / 0.125 |
| 70B (0.034) | 17.2 / 17.2 | 4.31 / 4.31 | 1.11 / 1.14 | 0.315 (gap 32%) / 0.525 | 0.413 / 0.523 |
| 405B (0.19) | 99.1 / 99.1 | 24.8 / 24.8 | 6.26 / 6.32 | 1.50 / 2.11 | not run |
| Mixtral 8x7B (0.022) | 11.4 / 11.4 | 2.85 / 2.87 | 0.718 / 0.745 | 0.134 / 0.226 | provisional |
| Qwen3-235B-A22B (0.11) | 57.4 / 57.4 | 14.3 / 14.4 | 3.59 / 3.68 | provisional | provisional |
| DeepSeek-V3 (0.32) | 165 / 165 | 41.2 / 41.2 | 10.3 / 10.5 | provisional | provisional |

Share of L that recurs, i.e. is not the one-time weight read (`(L - root)/L`): 1B 85% at 1M and 96% at 4M; 8B 82% and 95%; 70B 57% and 92%; 405B 48% at 1M; Mixtral 33% at 1M.

- **Source:** `ROLLOUT_TABLES.md` P1 (from `coarse.jsonl`). **Policy:** as in table 2.
- **Status under the draft:** this is the draft's "P/T + recurring cost c" experiment. At our Gamma, c > 0 is certified for 1B, 8B, 70B, 405B and Mixtral.

## 4. Policy sensitivity (8B rollout, Q_roll = 1M)

| Setting | Gamma in 8K sessions | L MB/token | U MB/token | Slowdown L / U (ours) |
|---|---|---|---|---|
| Q_inf = 2K (Gamma = 4 x 2K session; sequences 2K) | 0.9 | 0.192 | 0.257 | 48,000 / 64,000x |
| **Default: Q_inf = 8K, F_hat = 1.5, G_hat = 4** | 4 | 0.0847 | 0.125 | 21,000 / 31,000x |
| Q_inf = 32K (sequences 32K) | 27 | 0.0291 | 0.0595 | 7,300 / 15,000x |
| Q_inf = 128K (sequences 128K) | ~280 | 0.0153 | 0.0306 | 3,800 / 7,700x |
| F_hat = 3 | 4 | 0.0847 | 0.125 | 21,000 / 31,000x |
| F_hat = 10 | 4 | 0.0847 | 0.125 | 21,000 / 31,000x |
| G_hat = 10 | 10 | 0.0516 | 0.0794 | 13,000 / 20,000x |
| G_hat = 1000 | 1000 | 0.0153 | 0.0153 | 3,800 / 3,800x (the whole 1M rollout is one IU: P/Q + tokens, not steady state) |

- **Source:** `ROLLOUT_TABLES.md` P4 (from `coarse.jsonl`).
- **Takeaways relevant to the draft:**
  - F never binds a forward circuit.
  - Going from `G_hat` 4 to 10 lowers U by 1.57x and L by 1.64x; the square-root law predicts 1.58x.
  - The `Q_inf` rows change both Gamma and the sequence length.

## 5. The draft's equation (6) against measured attacks

Tier 2 is the draft's rectangle model (m layers x t tokens, cost `P/t + A/m` per layer-token, `m t h <= Gamma`) evaluated on our calibrated shapes.

| Model (Q_roll = 1M, default policy) | Tier-2 prediction MB/token | Measured U MB/token | Measured / predicted | Predicted m* layers, t* tokens |
|---|---|---|---|---|
| 1B | 0.0346 | 0.0382 | 1.10 | 3.4, 155K |
| 8B | 0.119 | 0.125 | 1.05 | 4.1, 253K |
| 70B | 0.515 | 0.525 | 1.02 | 4.9, 531K |
| 405B | 1.77 | 2.11 | 1.19 | 4.6, 901K |
| Mixtral 8x7B | 0.297 | 0.226 | 0.76 | 1.7, 611K |

What the measured 8B attack at 1M does (checked plan): 34 IUs, each 3.78 x fwd(8K) of work (Gamma = 4), 4 layers x 262K tokens (median; 524K max), importing 1.74 GB of weights and 2.15 GB of activations per IU.

- **Source:** `ROLLOUT_TABLES.md` P2 (cross-check) and P3 (anatomy, `U_detail.anatomy`); model in `sweeps/analytic.py::rollout_tiers`.
- **Status under the draft:** equation (6) is confirmed empirically to within 0.76 to 1.19x. This is what justifies the projections in table 8.

## 6. Soundness validation (exact optimum on small circuits)

| Check | Cells | Violations | Notes |
|---|---|---|---|
| L <= I* (acyclic exact optimum) | 1,729 exact (+42 bracketed) | 0 | `validation.json`. L/I* median 0.75, p10 0.40. |
| **L <= I* (cycle-allowed exact optimum)** | **1,678** | **0** | Same rows' `Istar_cyclic`. Of these, 534 cells have no F (the draft's policy): 0 violations. L/I*_cyclic median 0.79. |
| U >= I* (cycle-allowed) | 998 | 0 | Every acyclic plan is also a cycle-allowed division. |
| How much cycles change I* | 1,678 | | 66 cells change, by at most 1.33x (median 1.12x among changed); 45 of the 66 are tiny multi-step training chains. |
| Registry rollout cells (tiny dense and MoE `forward-nonfixed`) | 95 | 0 | `validation_rollout.md`. Checked only against acyclic brackets. |
| Registry transformer block-term cells | 51 | 0 | `validation_block_term.md`. |
| Weight-presence certificate `L_wp`, gate-level | tiny 1 to 4 layer training | 0 | `wp_gatecheck.md`. **Its proof assumes convex (acyclic) RUs and uses F, so it does not apply under the draft.** |

- **Source:** `accumulation/results/validation*.json|md`, generated by `redteam/coarse_validation.py` at lower `df35839fdf`/`8c8626f5f6` (= combined `ac6c3bb0e3`), planner `f4baa2d7be`.
- **Status under the draft:** the rollout certificate does not assume acyclicity. It holds against the cycle-allowed optimum on every exact cell; the 95 registry rollout cells are the only part still unchecked under cycles.

## 7. Pretraining under the earlier policy (F and acyclic): U usable, L not

Multi-step `local-sgd`, Q_step = 131,072 tokens per step, steady state = marginal of K = 3 over K = 2. Penalty = slowdown normalized by training work (train/inference MACs = 3.1 to 3.3).

| Model | L per token (certificate) | U per token (attack) | Certified penalty | Attack penalty |
|---|---|---|---|---|
| 1B | 13.9 KB (L_wp) | 266 KB | 1,063x | 20,287x |
| 8B | 103 KB (L_wp) | 810 KB | 8,060x | 63,288x |
| 70B | 1.0 MB (L_wp) | 3.9 MB | 80,580x | 313,414x |
| 405B | 5.9 MB (L_wp; possibly before the knee) | 17.1 MB | 479,542x | 1,392,534x |
| Mixtral 8x7B (single step) | not available | 2.0 MB (includes first-step weights) | | 160,998x |
| Qwen3-235B-A22B (single step) | not available | 8.2 MB (includes first-step weights) | | 646,788x |
| DeepSeek-V3 (single step) | 10.3 MB | 21.8 MB (includes first-step weights) | 819,427x | 1,738,924x |

8B attack cost vs batch and Gamma (U MB/token, marginal per step of a periodic plan; `F_hat = 1.5` throughout):

| Q_step | G_hat = 1 | G_hat = 4 | G_hat = 10 | G_hat = 100 | G_hat = 1000 |
|---|---|---|---|---|---|
| 8K | 3.47 | 3.09 | 3.09 | 3.09 | 3.09 |
| 32K | 1.32 | 1.17 | 1.17 | 1.17 | 1.17 |
| 128K | 1.25 | 0.810 | 0.794 | 0.786 | 0.786 |
| 512K | 1.34 | | 0.909 | 0.859 | 0.859 |
| 1M | 1.33 | | 0.894 | 0.839 | 0.758 (analytic) |

- **Source:** `TABLE1.md` (pretraining rows) and `TABLE2.md` (K sweep, Q_step x G_hat), from `coarse.jsonl` circuits `local-sgd` and `pretrain-moe`.
- **Status under the draft:**
  - **U remains a valid attack** at the stated Gamma, because dropping F and allowing cycles only enlarges the legal set. It is probably far from optimal, though: U stops improving at `G_hat` >= 10 because `F_hat = 1.5` caps it.
  - **L is not valid.** `L_wp` rests on convexity and on F. The coarse training certificate also uses F. Use table 9 instead.
  - The circuits use SGD, not the draft's FP32 master weights with Adam.

## 8. Why the numbers change at the draft's Gamma (analytic projection, rollout)

Tier-2 rollout slowdown (ours) in steady state, with F = infinity. The Gamma columns give Gamma in units of one 8K session (`G_hat`) followed by the projected slowdown. "Whole depth" means the optimal IU holds every layer, so the cost is `P/t` and falls as 1/Gamma instead of 1/sqrt(Gamma).

| Model | Measured at G_hat = 4: L / U | Tier 2 at G_hat = 4 | Gamma = one 128K session | Gamma = draft's Kimi-K3 calibration | Gamma = one 1M session | Attention share of a 1M session | w_min / w_avg(8K) |
|---|---|---|---|---|---|---|---|
| 1B | 4,705 / 9,205x | 8,655x | 92 / 998x (whole depth) | 378 / 243x (whole depth) | 5,259 / 18x (whole depth) | 98% | 0.68 |
| 8B | 20,811 / 31,201x | 29,636x | 71 / 5,491x | 426 / 1,150x (whole depth) | 3,831 / 129x (whole depth) | 97% | 0.77 |
| 70B | 103,210 / 130,632x | 128,715x | 49 / 33,861x | 476 / 8,075x | 2,361 / 1,825x (whole depth) | 95% | 0.86 |
| 405B | 375,316 / 526,317x | 442,283x | 35 / 143,918x | 508 / 31,770x | 1,421 / 15,713x | 92% | 0.92 |
| Mixtral 8x7B | 33,419 / 56,495x | 74,359x | 52 / 19,246x | 471 / 4,998x | 2,533 / 1,126x (whole depth) | 96% | 0.85 |
| Qwen3-235B-A22B | no admissible 1M row | 169,378x | 106 / 31,214x | 345 / 16,423x | 6,241 / 2,293x | 99% | 0.62 |
| DeepSeek-V3 | no admissible 1M row | 380,585x | 87 / 78,851x | 389 / 35,366x | 4,929 / 7,361x | 98% | 0.70 |

- **Source:** `sweeps/nci_projection.py` produces `results/nci_projection.{md,json}`.
  - Session work is fitted as `fwd(T) = aT + bT^2` through the two longest calibrated sessions (`results/calibration.json`: 8K and 32K; 4K and 8K for 405B).
  - The Kimi-K3 column uses the draft's own session formula `2.1e11 T + 7.4e5 T^2` at `T = 1e6`. That is 4.52e6 minimum-work positions, transferred to each model as that many positions of its own minimum per-position work `a`.
- **Assumptions:**
  - This is an analytic attack family (an estimate of U, not a certificate). Its only validation is table 5, at `G_hat = 4`.
  - No point at `G_hat` > 10 has been measured in steady state.
  - The attacker trains at 8K context, so a max-context Gamma gives it thousands of short sessions' worth of work per IU. In full-attention models a 1M session is 92 to 99% attention; in Kimi-K3 it is 78% (from the draft's formula).

## 9. Pretraining via the draft's coverage reduction (rho >= alpha_C s_C), at our Gamma

`s_C` is the rollout slowdown with `Q_roll = Q_step` (one weight version per step, measured). `alpha_C` = forward work / training-step work.

| Model | Q_step | Rollout L / U at Q_roll = Q_step (MB/token) | s_C: L / U | alpha_C | alpha_C s_C: L / U |
|---|---|---|---|---|---|
| 1B | 128K | 0.0277 / 0.0393 | 6,916 / 9,813x | 0.317 | 2,194 / 3,114x |
| 1B | 1M | 0.0196 / 0.0382 | 4,892 / 9,562x | 0.317 | 1,552 / 3,034x |
| 1B | 4M | 0.0188 / 0.0368 | 4,705 / 9,205x | 0.317 | 1,493 / 2,921x |
| 8B | 128K | 0.134 / 0.155 | 33,524 / 38,826x | 0.321 | 10,775 / 12,479x |
| 8B | 1M | 0.0847 / 0.125 | 21,187 / 31,201x | 0.321 | 6,810 / 10,028x |
| 8B | 4M | 0.0832 / 0.125 | 20,811 / 31,201x | 0.321 | 6,689 / 10,028x |
| 70B | 128K | 1.11 / 1.14 | 276,390 / 285,526x | 0.326 | 90,120 / 93,099x |
| 70B | 1M | 0.315 (gap 32%) / 0.525 | 78,663 / 131,267x | 0.326 | 25,649 / 42,801x |
| 70B | 4M | 0.413 / 0.523 | 103,210 / 130,632x | 0.326 | 33,653 / 42,594x |
| 405B | 128K | 6.26 / 6.32 | 1,564,463 / 1,580,977x | 0.329 | 514,855 / 520,289x |
| 405B | 1M | 1.50 / 2.11 | 375,316 / 526,317x | 0.329 | 123,514 / 173,208x |

- **Source:** `coarse.jsonl` rollout rows (current hashes, `G_hat = 4`, `Q_inf = 8K`); `alpha_C = 1 / train_over_fwd` from `calibration.json` (training-step credited MACs / forward MACs at 8K = 3.04 to 3.15).
- **Assumptions:**
  - The draft's reduction and its incompressibility assumptions.
  - A training step's work is more than Gamma, so updated weights cannot be computed inside one IU. At our Gamma this holds for `Q_step` > ~10K tokens.
  - At the draft's Kimi-K3 Gamma it holds only for `Q_step` above about 1.0 to 1.3M tokens. Frontier batches (Kimi K2: 67M) are far above that; small-batch runs are not.
- **Sanity check:** at 8B and `Q_step` = 128K, this lower bound (10,775x) sits below the direct pretraining attack of table 7 (63,288x). It is also above the earlier `L_wp` value (8,060x).

## 10. Status of every existing result under the draft

| Result | Usable as-is? | Why / what it needs |
|---|---|---|
| Inference = one IU, 4 B/token (table 1) | Yes | Definitional under the draft. |
| Rollout U, all models at our Gamma (tables 2 to 4) | Yes, as attacks at Gamma = 4 x 8K session | Every acyclic plan is a legal cycle-allowed division. |
| Rollout L, dense and Mixtral (tables 2 to 4) | Yes, at Gamma = 4 x 8K session | The certificate assumes no acyclicity and passes 1,678/1,678 cycle-allowed exact cells. The 95 registry rollout cells are not yet re-checked under cycles. |
| Equation (6) confirmation (table 5) | Yes | Within 0.76 to 1.19x on five models. |
| Qwen3 / DeepSeek-V3 rollout at 1M and 4M | No | Planner fallback (not an attack) and stale L. |
| Pretraining U (table 7) | Yes, as attacks at their Gamma | Probably loose, because F capped the planner. |
| Pretraining L (`L_wp` and the coarse training L) | **No** | Uses convexity and F. Replace with table 9 (coverage reduction). |
| Anything at the draft's Gamma (table 8) | Projection only, for the whole-model rollout | No measured steady-state point beyond `G_hat = 10`. For `M_{L,T}` itself no measurement is needed: section 12 gives the closed form with a proof, checked exactly on small instances. |
| X-cap results (`THEORY_xcap_deadend.md`, `breakdown_*.md`) | No | Retired model. |
| Peak NCI | Not computed | Our L also lower-bounds min peak NCI (peak >= average for every division). There is no peak-side attack number yet. |
| Kimi-K3 | Closed form only (table 12b) | From its published shapes. No op graph in `configs.py`, and none is needed for `M_{L,T}`. |

## 11. Why update, and how

| Issue | Effect on the numbers | Fix | Cost |
|---|---|---|---|
| **Gamma**: the draft's Gamma is one max-context session; ours is 4 x 8K session | Largest effect by far. At the Kimi-K3 calibration (`G_hat` ~ 350 to 510), the projected rollout slowdown falls 10 to 36x (8B: 29,600x to 1,150x). At a 1M session of the same model it falls 28 to 480x. | **Done analytically (section 12); pod run dropped.** The bound for `M_{L,T}` depends only on (d, L, Gamma, widths), so it is a closed form, proven, and checked against exact optima on 35 small instances, including the switch to the whole-depth regime. | None left for `M_{L,T}`. |
| **Cycles** | None on the exact panel (0/1,678). Remaining: 95 registry rollout cells. | Re-run the rollout registry cells of `redteam/coarse_validation.py` (`validation_rollout.md`) with the cycle-allowed exact solver. | Local, about 1 hour. |
| **No F** | Rollout: none (measured). Training: L invalid; U loose. | Training L: use table 9 (coverage). Training U: re-run the planner with F = infinity at the draft's Gamma. | Table 9: done. U: pod run. |
| **alpha normalization** (minimum vs average work per position) | Multiply our slowdowns by 0.62 to 0.92. | Apply the factor (done in tables 2 and 8). | None |
| **Kimi-K3** | Table 12b: 3,000 to 9,200x on `M_{L,T}` with no routing assumption, 30,000 to 62,000x with balanced routing. Training (coverage 1/3): at least 1,000 to 3,100x, or 10,000 to 21,000x. | Done, from its published shapes. Open: the routing statistic `rho_eff` (table 12b notes), which moves the answer by up to sqrt(26.7) = 5.2x. | Routing statistics from a small run, not graph extraction. |
| **Draft's `M_{L,T}` definition** | As written (a^0 = d-wide novel input, square d x d layers) it gives 79,000x at the Kimi-K3 Gamma. 99% of that is the a^0 input charge; with token-derived a^0 it is 550x, covering 1.5% of a training step. | Derive a^0 from the token (or charge the token's width). Use the model's real per-layer weight count and MACs per position instead of d^2 (rho = W / h for MoE). State the balanced-routing assumption. | Writing |
| **Draft's own sections 6.2 to 6.3** | Not a data issue. They still use `X`, `F`, compartments, `Q = 4,500` and equations (8) to (11) in X units, which contradicts the NCI definitions earlier in the draft. | Rewrite equations (9) to (11) in NCI units: `rho >= (c / w_C) / alpha`, with `c` the recurring input per token and `w_C` the work per token. | Writing |

## 12. `M_{L,T}` in closed form, checked on small instances, read off at the Kimi-K3 Gamma

New on 2026-09-23. The bound depends only on the circuit's shape, so no model execution or graph extraction is involved.

**Circuit.** The draft's `M_{L,T}`: `L` layers of `d x d` weights `W_l`, `T` positions. Output `(l, t, i)` is a chain of `d` multiply-add gates; gate `(l, t, i, k)` reads `W_l[i, k]`, `a^{l-1}_t[k]` and the previous partial sum. theta is empty. Widths: `b_w` per weight, `b_a` per activation and partial sum. Two input conventions:
- *literal*: `a^0_t` is a `d`-wide novel input, as the draft writes it;
- *token*: `a^0_t = e(token_t)` is computed inside the circuit from a `b_tok`-wide token.

**Closed form.** Gamma is counted in MACs; costs are per MAC.

~~~
phi(Gamma) = min over 0 < W <= W_max of ( b_w W / Gamma + b_a d / W )
           = 2 sqrt(b_w b_a d / Gamma)             if sqrt(b_a d Gamma / b_w) <= W_max    (the IU is shallower than the network)
           = b_w W_max / Gamma + b_a d / W_max     otherwise                              (the IU spans the whole depth)

literal:  I* / T >= L d^2 min(phi, b_a / d),                             W_max = L d^2
token:    I* / T >= (L-1) d^2 min(phi, b_a / d) - d b_a + b_tok,         W_max = (L-1) d^2
attack:   IU = block of m layers x Gamma / (m d^2) positions; per position, sum over blocks of b_w s^2 d^4 / Gamma
          (s = block depth), plus d b_a per block entry (b_tok for the bottom block under the token convention)
~~~

- The first branch is the draft's equation (6), with `P = b_w d^2`, `A = b_a d`, `h = d^2`. It depends only on the width `d` of the cut between layers and on the widths. It does not depend on `L` or on layer size.
- Layer size enters only once one IU spans the whole network.
- Lower bound and attack coincide up to rounding `m` to an integer (literal), and up to `(L/(L-1))^2` (token): 1.02 at `L = 93`.

**Proof of the lower bound** (literal convention). Take an IU `R` holding `W_R` distinct weights and doing `N_R <= Gamma` MACs. Cycles are allowed, and nothing below uses convexity.
1. At one position each weight feeds exactly one MAC, so `R` does at most `W_R` MACs per position.
2. Call position `t` *deep* in `R` if `R` completes some output chain at `t`. Take the lowest such layer `l*`. That chain needs all `d` activations of layer `l*-1` at `t`. No chain of layer `l*-1` is complete in `R`, so each of those activations is either read or produced by a partial chain that reads a partial sum. Each deep `(R, t)` therefore costs at least `d` reads of `b_a`.
3. At a non-deep position, every activation `R` uses comes with a read, and each activation feeds at most `d` MACs. That is at least `b_a / d` per MAC.
4. On the deep part, steps 1 and 2 give `cost(R) >= b_w W_R + b_a d N_R / W_R`. By AM-GM with `W_R <= W_max` and `phi` decreasing, this is at least `N_R phi(N_R) >= N_R phi(Gamma)`. Summing over IUs gives the bound.

Extensions:
- **Token convention.** Restrict any division to layers `2..L`. That is a division of a literal `M_{L-1,T}`. Its cost exceeds the original only by layer-1 outputs that were free inside their producing IU: at most `T d b_a`. Tokens and layer-1 weights are paid on top.
- **MoE.** Step 1 becomes "at most `W_R / rho` MACs per position", with `rho` = weights per layer / MACs per position per layer. This holds *if* every IU must hold all experts of the layers it covers (balanced routing). Then `phi = 2 sqrt(b_w b_a d rho / Gamma)`. Without that assumption, `rho = 1` is still a theorem for the MoE, because a position uses each held weight at most once.
- **Gate unit.** The draft counts multiplies and adds separately (2.1e11 gates per token = 2 x 104B activated parameters). So Gamma in MACs is half the gate count, and `size(M)` is 2 gates per MAC. Splitting a multiply from its add costs an extra `b_a` read, which is never cheaper here.
- **Scope.** These bound divisions of `M` itself (the draft's "contains"). Extending to "implements" is the draft's incompressibility assumption.
- **Real models.** A real model puts norms, activations, residuals and attention between its matmuls, so it does not literally contain `M`'s linear chain.
  - Step 1 carries over unchanged.
  - Step 2 needs every per-position cut between consecutive matmuls to be at least `d` wide. The residual stream suggests it is, but this is argued, not proven, once attention mixes positions.

### 12a. Exact optimum vs closed form (small instances)

| d | L | T | b_w / b_a (B) | a^0 | Gamma (MACs) | gates | closed-form LB | exact I* | proven optimal | best rectangle (m x t) | I* / LB | formula regime |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 4 | 1 / 1 | literal | 2 | 16 | 16.00 | 24 | yes | 24 (1 x 2) | 1.50 | no |
| 1 | 4 | 4 | 1 / 1 | literal | 4 | 16 | 16.00 | 16 | yes | 16 (2 x 2) | 1.00 | yes |
| 1 | 4 | 4 | 1 / 1 | literal | 8 | 16 | 11.31 | 12 | yes | 12 (2 x 4) | 1.06 | yes |
| 1 | 4 | 6 | 1 / 1 | literal | 4 | 24 | 24.00 | 24 | yes | 24 (2 x 2) | 1.00 | yes |
| 1 | 4 | 6 | 1 / 1 | literal | 6 | 24 | 19.60 | 20 | yes | 20 (2 x 3) | 1.02 | yes |
| 1 | 4 | 6 | 1 / 1 | literal | 12 | 24 | 13.86 | 14 | yes | 14 (4 x 3) | 1.01 | yes |
| 1 | 6 | 4 | 1 / 1 | literal | 3 | 24 | 24.00 | 32 | no (bound 29) | 32 (3 x 1) | 1.33 | no |
| 1 | 6 | 4 | 1 / 1 | literal | 6 | 24 | 19.60 | 20 | yes | 20 (3 x 2) | 1.02 | yes |
| 1 | 6 | 4 | 1 / 1 | literal | 9 | 24 | 16.00 | 18 | yes | 18 (2 x 4) | 1.12 | yes |
| 1 | 6 | 4 | 1 / 1 | literal | 12 | 24 | 13.86 | 14 | yes | 14 (3 x 4) | 1.01 | yes |
| 1 | 3 | 8 | 1 / 1 | literal | 3 | 24 | 24.00 | 32 | no (bound 29) | 32 (3 x 1) | 1.33 | no |
| 1 | 3 | 8 | 1 / 1 | literal | 6 | 24 | 19.60 | 20 | yes | 20 (3 x 2) | 1.02 | yes |
| 1 | 3 | 8 | 1 / 1 | literal | 12 | 24 | 14.00 | 14 | yes | 14 (3 x 4) | 1.00 | yes |
| 1 | 4 | 6 | 2 / 1 | literal | 4 | 24 | 24.00 | 36 | yes | 36 (2 x 2) | 1.50 | no |
| 1 | 4 | 6 | 2 / 1 | literal | 8 | 24 | 24.00 | 26 | yes | 28 (2 x 3) | 1.08 | yes |
| 1 | 4 | 6 | 2 / 1 | literal | 12 | 24 | 19.60 | 20 | yes | 20 (2 x 6) | 1.02 | yes |
| 1 | 4 | 6 | 1 / 2 | literal | 4 | 24 | 33.94 | 36 | yes | 36 (2 x 2) | 1.06 | yes |
| 1 | 4 | 6 | 1 / 2 | literal | 8 | 24 | 24.00 | 24 | yes | 24 (4 x 2) | 1.00 | yes |
| 1 | 4 | 6 | 1 / 2 | literal | 12 | 24 | 20.00 | 20 | yes | 20 (4 x 3) | 1.00 | yes |
| 2 | 2 | 4 | 1 / 4 | literal | 4 | 32 | 64.00 | 96 | yes | 96 (1 x 1) | 1.50 | no |
| 2 | 2 | 4 | 1 / 4 | literal | 8 | 32 | 64.00 | 64 | yes | 64 (2 x 1) | 1.00 | yes |
| 2 | 2 | 4 | 1 / 4 | literal | 16 | 32 | 48.00 | 48 | yes | 48 (2 x 2) | 1.00 | yes |
| 2 | 3 | 2 | 1 / 4 | literal | 6 | 24 | 48.00 | 64 | yes | 72 (1 x 1) | 1.33 | no |
| 2 | 3 | 2 | 1 / 4 | literal | 12 | 24 | 39.19 | 40 | yes | 40 (3 x 1) | 1.02 | yes |
| 2 | 2 | 4 | 1 / 2 | literal | 4 | 32 | 32.00 | 64 | no (bound 60) | 64 (1 x 1) | 2.00 | no |
| 2 | 2 | 4 | 1 / 2 | literal | 8 | 32 | 32.00 | 48 | yes | 48 (1 x 2) | 1.50 | no |
| 2 | 2 | 4 | 1 / 2 | literal | 16 | 32 | 32.00 | 32 | yes | 32 (2 x 2) | 1.00 | yes |
| 2 | 2 | 3 | 1 / 1 | literal | 4 | 24 | 14.00 | 36 | no (bound 34) | 36 (1 x 1) | 2.57 | no |
| 2 | 2 | 3 | 1 / 1 | literal | 8 | 24 | 14.00 | 26 | yes | 28 (1 x 2) | 1.86 | no |
| 1 | 4 | 4 | 1 / 1 | token | 4 | 20 | 13.00 | 19 | yes | 24 (1 x 2) | 1.46 | yes |
| 1 | 4 | 4 | 1 / 1 | token | 8 | 20 | 9.49 | 14 | yes | 16 (2 x 2) | 1.48 | yes |
| 1 | 3 | 6 | 1 / 1 | token | 4 | 24 | 13.00 | 21 | yes | 24 (3 x 1) | 1.62 | yes |
| 1 | 3 | 6 | 1 / 1 | token | 8 | 24 | 10.00 | 15 | yes | 15 (3 x 2) | 1.50 | yes |
| 2 | 2 | 3 | 1 / 4 | token | 10 | 30 | 11.00 | 27 | yes | 27 (2 x 1) | 2.45 | no |
| 2 | 2 | 3 | 1 / 4 | token | 20 | 30 | 11.00 | 19 | yes | 19 (2 x 2) | 1.73 | no |

- **Result:**
  - The closed-form lower bound holds in 35/35 instances: 31 proven optimal, and the other 4 have a proven solver bound at or above it.
  - In the formula regime (`phi <= b_a / d`), `I* / LB` is 1.00 to 1.13 for literal inputs (19 instances) and 1.46 to 1.62 for token inputs (4 instances). The token gap is the `(L/(L-1))^2` slack at `L` = 3 or 4.
  - Outside the regime (tiles smaller than about `(b_w / b_a) d^3`) the bound is valid but loose: 1.33 to 2.57.
  - `I*` equals the best uniform rectangle in 29/35. In the other 6, mixed tile shapes beat it by 7 to 21% at small `T`.
- **Source:** `redteam/mlt.py` writes `results/mlt_check.json` and `results/mlt.md`.
  - Exact `I*` comes from CP-SAT (OR-Tools 9.15, 8 workers, 120 s cap) over all divisions: cycles allowed, work cap Gamma only (no F, no X).
  - The model uses restricted-growth symmetry breaking and a warm start from the best rectangle. It allows at most `2N / Gamma + 1` IUs, which loses nothing: merging two IUs whose works sum to at most Gamma never costs more.
  - Every returned division is re-verified with `exact/solve.py` (`is_legal`, `partition_cost`). "Best rectangle" enumerates uniform `m x t` tilings.
- **Why not our coarse L / U:** they work on op graphs of whole models. Here the circuit is gate-level and small, so the exact optimum is available directly.

### 12b. Read-off at the draft's Kimi-K3 Gamma

| Circuit | b_w / b_a (bits) | optimal IU: layers x positions | novel bits per position: LB / U | slowdown NCI/alpha: LB / U | alpha_C = size(M) / size(step) | training rho >= alpha_C x LB |
|---|---|---|---|---|---|---|
| draft's M_{L,T} as written: 93 square 7168x7168 layers, a^0 = d-wide novel input | 16 / 16 | 93 x 9.9e+07 | 1.15e+05 / 1.15e+05 | 79,283x / 79,283x | 0.015 | 1,203x |
| draft's M_{L,T} as written: 93 square 7168x7168 layers, a^0 = d-wide novel input | 4.25 / 16 | 93 x 9.9e+07 | 1.15e+05 / 1.15e+05 | 78,895x / 78,895x | 0.015 | 1,197x |
| same, a^0 derived from the 32-bit token | 16 / 16 | 93 x 9.9e+07 | 785 / 801 | 539x / 550x | 0.015 | 8x |
| same, a^0 derived from the 32-bit token | 4.25 / 16 | 93 x 9.9e+07 | 232 / 236 | 159x / 162x | 0.015 | 2x |
| Kimi-K3 matmul weights, routing fully clusterable (rho = 1: IU holds only active weights) | 16 / 16 | 47 x 8.9e+06 | 2.94e+05 / 3.01e+05 | 9,180x / 9,390x | 0.334 | 3,063x |
| Kimi-K3 matmul weights, routing fully clusterable (rho = 1: IU holds only active weights) | 4.25 / 16 | 93 x 4.5e+06 | 9.67e+04 / 9.88e+04 | 3,020x / 3,086x | 0.334 | 1,008x |
| Kimi-K3 matmul weights, balanced routing (rho = 26.7: IU holds all experts of its layers) | 16 / 16 | 12 x 3.5e+07 | 2e+06 / 2.05e+06 | 62,385x / 64,153x | 0.334 | 20,813x |
| Kimi-K3 matmul weights, balanced routing (rho = 26.7: IU holds all experts of its layers) | 4.25 / 16 | 19 x 2.2e+07 | 9.74e+05 / 9.88e+05 | 30,417x / 30,847x | 0.334 | 10,148x |

- **Source:** `redteam/mlt.py --readoff` writes `results/mlt_readoff.json`. LB is the closed-form bound above. U is the best block tiling of the network into `m`-layer blocks, each IU filled to Gamma.
- **Assumptions:**
  - **Gamma** is the draft's Kimi-K3 calibration: one 10^6-token session = 2.1e11 x 10^6 + 7.4e5 x 10^12 = 9.5e17 gates = 4.75e17 MACs. **alpha** = 32 bits / 2.1e11 gates. For the Kimi-K3 rows, `size(M)` per position equals alpha's 2.1e11, so the slowdown is simply (novel bits per position) / 32.
  - **Kimi-K3 shapes** (arXiv 2607.24653; HF `config.json`): 93 layers, `d` = 7168, 2.78T total and 104.2B activated parameters.
    - Per layer: 30.2B matmul weights (896 routed experts x 3 x 3584 x 3072 = 29.6B, plus about 0.6B of attention, shared experts, latent projections and router) and 1.13B MACs per position (16 routed experts plus the dense parts).
    - `rho = 30.2 / 1.13 = 26.7`. Embedding lookup is excluded.
  - **Cut between layers** is `A = d` = 7168 values at `b_a`. Kimi-K3's Block AttnRes carries up to 9 block representations across layers, so the true cut is wider, which would raise the sqrt branch by up to 3x. Not counted.
  - **Widths:** bf16 throughout; or MXFP4 weights (4.25 bits including the shared scale) with a bf16 residual cut. Kimi-K3 uses MXFP4 for expert weights after post-training quantization, and those are 98% of the weights an IU holds.
  - **Coverage** `alpha_C = size(M) / size(training step)`, taking a step as 3 x forward gates at short context (our calibration: 3.04 to 3.15). Not measured for Kimi-K3.
    - Attention is not part of `M`: it is extra computation in D. It lowers coverage at long context, since it is 78% of a 1M session.
  - **Positions per IU:** the attack needs at least that many positions per weight version to fill its IUs (e.g. 3.5e7 in the balanced bf16 row). With fewer, the attack only gets more expensive. The lower bound is per IU, so it holds at any `T`.
- **Reading the rows:**
  - **Rows 1-2 (the draft's `M` as written).** 99% of the 1.15e5 bits per position is the `a^0` input charge (7168 x 16 bits). The draft's activation-incompressibility assumption fails at `l = 0`: `a^0` can be recomputed from the 32-bit token and the embedding row. So that charge is not real.
  - **Rows 3-4 (square layers, token inputs).** Square 7168 x 7168 layers hold 4.8e9 weights: 1/22 of Kimi-K3's activated and 1/580 of its total matmul weights. One IU holds the whole network for 1e8 positions, so the slowdown is only 160 to 550x. Coverage is 1.5%, so these rows say almost nothing about training. "Matrices the size of Kimi-K3's" has to mean Kimi-K3's per-layer weights.
  - **Rows 5-6 (`rho = 1`).** A lower bound for Kimi-K3's weights with no routing assumption: 3,000 to 9,200x on `M`, and at least 1,000 to 3,100x for training.
  - **Rows 7-8 (`rho = 26.7`).** 30,000 to 62,000x on `M`, and at least 10,000 to 21,000x for training. This needs balanced routing: no adversary can group 2e7 to 4e7 positions that avoid a large share of each layer's experts across 12 to 19 consecutive layers.
- **The one quantity worth measuring** is `rho_eff` = weights an IU must hold / MACs per position, per layer. The slowdown scales as `sqrt(rho_eff)` in the sqrt branch.
  - It comes from routing statistics of a small run: for the most clustered set of that many positions, what fraction of each layer's experts do they touch?
  - Under random top-16-of-896 routing, every expert is touched, so `rho_eff = rho`. Kimi-K3's Quantile Balancing equalizes expert loads per batch, but that does not stop an adversary from clustering subsets of positions.
