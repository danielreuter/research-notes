# Overnight plan (2026-09-16): publication-ready dynamic-rollout tables

Supersedes the ordering in `DELIVERABLES.md` for tonight. Goal: wake up with P0-P3 filled, **certified L included**.
Pretraining rows are last (P6). Everything below is at the default policy point unless stated:

~~~
F_hat = 1.5    G_hat = 4    Q_inf = 8192    F = F_hat * fwd(Q_inf)    G = G_hat * fwd(Q_inf)
~~~

Dynamic rollout = the *same forward graph and routing trace* as inference with the weights declared dynamic
(`forward-nonfixed` for dense, `forward-nonfixed-moe` for MoE). Useful work per token is identical to
inference, so

~~~
slowdown = (runtime input per token) / (4 B/token)          e.g. 0.0559 MB/tok -> 1.4e4x
~~~

Units, always: exposure in **MB/token**, state sizes in **GB**, slowdowns as `1.4e4x`.

## P0 -- headline table (fill completely; L columns before anything else)

Q = 1M rollout tokens.

| Family | Model | # tokens | MAC/token | L MB/tok | U MB/tok | U/L | Certified slowdown | Best-attack slowdown |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Dense | 1B | 1M | [ ] | **[fill]** | 0.065 | [ ] | **[fill]** | 1.6e4x |
| Dense | 8B | 1M | 9.65e9 | 0.0559 | 0.212 | 3.8 | 1.4e4x | 5.3e4x |
| Dense | 70B | 1M | 8.02e10 | **[fill]** | 0.987 | [ ] | **[fill]** | 2.5e5x |
| Dense | 405B | 1M | 4.38e11 | **[fill]** | 3.64 | [ ] | **[fill]** | 9.1e5x |
| MoE | Mixtral 8x7B | 1M | **[fill]** | **[fill]** | **[fill]** | **[fill]** | **[fill]** | **[fill]** |
| MoE | Qwen3-235B-A22B | 1M | **[fill]** | **[fill]** | **[fill]** | **[fill]** | **[fill]** | **[fill]** |
| MoE | DeepSeek-V3 | 1M | **[fill]** | **[fill]** | **[fill]** | **[fill]** | **[fill]** | **[fill]** |

Cells: preset `rollout-p0` (`coarse_run.py`). MoE needs (a) planner block recognition for the MoE forward
(currently falls to bands/fine: U/L = 32 on tiny-moe, useless as an attack) and (b) MoE-aware block cells in
`lower_coarse` (per-layer fwd MACs = active params x Q, not P_l x Q).

## P1 -- amortization: does the floor survive Q -> inf?

At minimum 8B + one MoE; ideally all four dense + all three MoE. Q in {8K, 32K, 128K, 1M, 4M if feasible}.

| Family/model | # rollout tokens | Weight-only floor P/Q MB/tok | L MB/tok | U MB/tok | Certified slowdown | Best-attack slowdown | Recurring share of L |
|---|---:|---:|---:|---:|---:|---:|---:|
| 8B | 8K | [ ] | [ ] | 1.96 | [ ] | 4.9e5x | [ ] |
| 8B | 32K | [ ] | [ ] | 0.523 | [ ] | 1.3e5x | [ ] |
| 8B | 128K | [ ] | [ ] | 0.221 | [ ] | 5.5e4x | [ ] |
| 8B | 1M | 0.016 | 0.0559 | 0.212 | 1.4e4x | 5.3e4x | ~99% |
| 8B | 4M | 0.004 | **[ ]** | **[ ]** | **[ ]** | **[ ]** | **[ ]** |

Per model, fit over the steady-state points and report `r_L`, `r_U` in MB/token:

~~~
L(Q) ~ P + r_L Q          U(Q) ~ P + r_U Q
~~~

"Recurring share of L" = `(L - P_read) / L` where `P_read` = bytes of dynamic roots the certificate charges once.
The result sentence per model: "the one-time dynamic model cost amortizes away, but certified recurring
exposure converges to r_L = [ ] MB/token".

## P2 -- explanatory table: closing the adversary's escape routes (slowdowns only)

8B at Q = 1M first; other rows if cheap.

| Model | Weights only | + activation boundaries | + intra-matmul sharding X = 5 MB | Actual certified L | Actual best attack U |
|---|---:|---:|---:|---:|---:|
| 1B | [analytic] | [analytic] | [analytic/OOM] | [measured] | 1.6e4x |
| 8B | ~4e3x | ~3e4x | [compute carefully] | 1.4e4x | 5.3e4x |
| 70B | ~3e4x | ~1e5x | [ ] | [ ] | 2.5e5x |
| 405B | ~2e5x | ~4e5x | [ ] | [ ] | 9.1e5x |
| Mixtral / Qwen3-MoE / DeepSeek-V3 | [ ] | [ ] | [ ] | [ ] | [ ] |

Columns: (1) weights only -- adversary shards weights arbitrarily and amortizes each shard, activation traffic
ignored; (2) + activations -- optimal layer x token tiling under forward no-shortcut (the block model);
(3) + intra-matmul -- additionally X = 5 MB, replicated operands / partial sums charged when one dynamic matrix
exceeds X. Column 3 is **analytic/OOM** unless the whole-rollout composition theorem is established; never
label it certified. Columns 1-3 come from `sweeps/analytic.py` (convex family), 4-5 from rows.

## P3 -- what the optimal adversary actually does (anatomy)

8B dense and one MoE, Q in {8K, 32K, 128K, 1M}; from the checked plan (`U_detail.anatomy`).

| # tokens | # RUs | median/max work per RU | layers/blocks per RU | tokens/RU | dynamic weights imported/RU (GB) | activation input/RU (MB) | partial-result input/RU (MB) | dominant strategy |
|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 8K | | | | | | | | whole-model-ish |
| 32K | | | | | | | | |
| 128K | | | | | | | | |
| 1M | | | | | | | | steady tiling |

MoE additionally: active experts/RU; active dynamic parameter GB/RU; tokens assigned per active expert.

## P4 -- minimal robustness (after P0-P3): 8B rollout at Q = 1M

| Setting | L MB/tok | U MB/tok | Certified slowdown | Best-attack slowdown |
|---|---:|---:|---:|---:|
| Q_inf = 2K | | | | |
| Q_inf = 8K, F_hat = 1.5 (default) | 0.0559 | 0.212 | 1.4e4x | 5.3e4x |
| Q_inf = 32K | | | | |
| Q_inf = 128K | | | | |
| F_hat = 3 | | | | |
| F_hat = 10 | | | | |
| G_hat = 10 | | | | |
| G_hat = 1000 | | | | |

Preset `rollout-p4`. Desired conclusion: large relaxations weaken the bound but do not erase the multi-OOM wedge.

## Validation requirements (non-negotiable for every headline L, U)

- U: checker-legal under the **acyclic RU quotient**, F, G (and X where used); `U_detail.acyclic == True`.
- L: independently certificate-checked; when the certificate comes from a time-limited MILP, report the
  **solver gap** (`L_gap`) next to L; L is the proven dual bound, never the incumbent.
- Exact micro-suite (red team): `U < I*` = 0 and `L > I*` = 0 at the hash used; include tiny-moe rollout cells.
- Never substitute analytic estimates into P0/P1/P4; mark `analytic` where used (P2 columns 1-3 only).
- All L/U shown carry their module hashes; stale rows are re-run (`--redo stale`), never displayed as current.

## Acceptance tests (regressions -> investigate before merging)

- inference: 4 B/token, one RU (dense and MoE).
- 8B rollout 1M: L = 0.0559 MB/tok, U = 0.212 MB/tok, U/L = 3.8, certified 1.4e4x, attack 5.3e4x (L may only go up
  as the certificate improves; U may only go down as the planner improves -- either way say so).
- 8B U(Q): 1.96 -> 0.523 -> 0.221 -> 0.212 MB/tok over 8K -> 1M.
- 1B / 70B / 405B attack at 1M: 0.065 / 0.987 / 3.64 MB/tok.

## Priority order for the night

1. every missing L in P0 (dense and MoE);  2. P1 with L, U and fits;  3. P3 anatomy;  4. P2 tiers;
5. P4;  6. only then pretraining (convex U redo, F in the certificate, K = 3 convergence).

Outputs: `results/ROLLOUT_TABLES.md` (P0-P4 generated by `sweeps/final_report.py`, never hand-edited),
`results/plots/figG_amortization.png` (P1), rows in `results/coarse.jsonl`.
